#!/usr/bin/env python3
"""lane-report: turn a lane's worktree into the report contract, with the safety rules enforced in code.

What it enforces, in order:
  1. Empty diff  -> STATUS refused, no matter what the lane's final message says.
  2. FILES scope -> if --files is given and the lane touched anything outside it, or touched
                    executable config (package.json, Makefile, conftest.py, CI, ...), VERIFY is NOT run
                    and STATUS is partial. Lane-written code must never execute before a human-grade
                    read of the diff decides it is safe.
  3. Deletion    -> a FILES path the spec asked the lane to modify that comes back deleted with nothing
                    written (deletion-only diff) is STATUS refused and VERIFY is not run (#53).
  4. VERIFY      -> re-run by this script inside `codex sandbox` (workspace-write: no network, writes
                    confined to the worktree). Gradle needs a loopback socket for its lock listener,
                    which the sandbox denies; for Gradle commands (or --verify-network) the sandbox
                    keeps writes confined but opens the network, and says so in `how` and GAPS (#53).
                    Pass --unsandboxed-verify only when the architect has already read the diff.
  5. --commit    -> commit the lane's diff on its behalf (the lane cannot: worktree git metadata lives
                    outside its sandbox), so salvage and merge have a real commit (#53).
  6. Evidence    -> the report is written to the task's run dir as report.json (earlier ones become
                    report-<n>.json), every VERIFY command appends a record to verify.jsonl, and raw
                    stdout/stderr land in verify-<n>.out/.err, full and separate. On timeout the partial
                    output is kept and the process group is killed. A VERIFY piped through grep/tail/head
                    is flagged `filtered` because its exit status may be masked (Wave 4, T43).

Exit codes: 0 complete, 2 partial, 3 refused, 4 timeout/unavailable (via --status-hint).
Python stdlib only.

Examples:
  python3 lane-report.py --worktree ../wt/task --lane "gpt-5.6-luna @ high" \
      --files src/rosterService.ts --files src/__tests__/rosterService.test.ts \
      --verify "npm test" --final /tmp/lane-final.txt --objective "Add roster service tests"
  python3 lane-report.py --worktree ../wt/task --lane "gpt-5.6-sol @ max" --status-hint timeout --json
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

TMP_DIRNAME = ".tri-lane-tmp"  # per-worktree scratch for sandboxed VERIFY; never counted as a lane change

# Paths whose modification by a lane means VERIFY must not run automatically.
EXEC_CONFIG = (
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Makefile", "justfile",
    "pyproject.toml", "setup.py", "setup.cfg", "conftest.py", "pytest.ini", "tox.ini", "noxfile.py",
    "jest.config", "vitest.config", "playwright.config", "vite.config", "webpack.config", "rollup.config",
    "babel.config", ".babelrc", "tsconfig", "gradle", "build.gradle", "settings.gradle", "Podfile",
    "Package.swift", "Cargo.toml", "go.mod", "Dockerfile", "docker-compose", ".husky/", ".github/",
    ".gitlab-ci", ".circleci/", "scripts/", "bin/", ".claude/", ".agents/", ".codex/", "AGENTS.md",
    "CLAUDE.md", "GEMINI.md", ".env", "firebase.json", ".firebaserc",
)


def sh(cmd, cwd: str, timeout: int, shell: bool = False) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=shell, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout}s"
    except FileNotFoundError as e:
        return 127, str(e)


def tail(text: str, n: int) -> str:
    lines = text.rstrip().splitlines()
    return "\n".join(lines[-n:])


def is_exec_config(path: str) -> bool:
    p = path.lower()
    base = p.rsplit("/", 1)[-1]
    for e in EXEC_CONFIG:
        el = e.lower()
        if el.endswith("/"):
            if p.startswith(el) or ("/" + el) in p:
                return True
        elif base == el or base.startswith(el + ".") or base.startswith(el) and el.endswith("config"):
            return True
    return False


def in_scope(path: str, allowed: list[str]) -> bool:
    for f in allowed:
        f = f.strip().rstrip("/")
        if path == f or path.startswith(f + "/"):
            return True
    return False


import re as _re

def gradle_safe(cmd: str) -> str:
    """Inside the sandbox Gradle cannot open daemon sockets or reach the network (HoopTrace, Vendly f10).
    Force no-daemon and offline on every gradle invocation unless already present."""
    def sub(m):
        return m.group(0) + " --no-daemon --offline"
    if "--no-daemon" in cmd:
        return cmd
    return _re.sub(r"(?:^|(?<=[\s;&|(]))(\./gradlew|gradlew|gradle)\b", sub, cmd)


def needs_network(cmd: str) -> bool:
    """Gradle's FileLockContentionHandler binds a loopback UDP socket; the sandbox denies it even with
    --no-daemon --offline (java.net.SocketException: Operation not permitted). Observed on an Android monorepo, #53."""
    return bool(_re.search(r"(?:^|[\s;&|(/])(gradlew?|gradle)\b", cmd))


FILTER_RX = _re.compile(r"\|\s*(grep|tail|head|sed|awk|cut|sort|uniq|wc)\b|\|\|")


def is_filtered(cmd: str) -> bool:
    """A VERIFY whose exit status can be masked by a pipe or an `||` fallback (s2-flow-fix hid an xcodebuild failure behind grep)."""
    return bool(FILTER_RX.search(cmd))


def _run_capturing(argv, cwd: str, timeout: int, env=None, shell: bool = False) -> tuple[int, str, str, bool]:
    """Run, keep stdout and stderr separate, kill the whole process group on timeout, keep partial output."""
    p = subprocess.Popen(argv, cwd=cwd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                         text=True, env=env, start_new_session=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out or "", err or "", False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), 15)
        except Exception:
            pass
        try:
            out, err = p.communicate(timeout=10)
        except Exception:
            try:
                os.killpg(os.getpgid(p.pid), 9)
            except Exception:
                pass
            out, err = p.communicate()
        return 124, (out or "") + f"\n[timeout after {timeout}s; partial output kept]", err or "", True


def run_verify(cmd: str, wt: str, timeout: int, unsandboxed: bool, writable: list[str], network: bool = False) -> dict:
    """Returns {exit, stdout, stderr, how, duration_s, timed_out, rewritten_command, sandbox}."""
    original = cmd
    if not unsandboxed:
        cmd = gradle_safe(cmd)
    network = network or needs_network(cmd)
    t0 = time.time()
    if not unsandboxed and shutil.which("codex"):
        # cwd is the worktree; codex sandbox treats cwd as the writable workspace. (-C would require --permission-profile.)
        # /tmp is excluded from the sandbox; TMPDIR points inside the worktree so test runners still have scratch space
        # on the project volume (the system volume filled and stalled lanes on 2026-09-03).
        # Toolchain caches (~/.gradle, ~/.npm, ...) are added as writable roots, physical paths only, or builds cannot
        # take their locks and the lane can never verify itself (HoopTrace, 2026-09-03).
        tmp = Path(wt) / TMP_DIRNAME
        tmp.mkdir(exist_ok=True)
        env = dict(os.environ, TMPDIR=str(tmp), GRADLE_OPTS=(os.environ.get("GRADLE_OPTS", "") + " -Dorg.gradle.daemon=false").strip())
        roots_cfg = "sandbox_workspace_write.writable_roots=" + json.dumps(writable)
        argv = ["codex", "sandbox", "-c", "sandbox_mode=workspace-write", "-c", "sandbox_workspace_write.exclude_slash_tmp=true", "-c", roots_cfg]
        if network:
            argv += ["-c", "sandbox_workspace_write.network_access=true"]
        argv += ["--", "sh", "-c", cmd]
        rc, out, err, timed_out = _run_capturing(argv, wt, timeout, env=env)
        shutil.rmtree(tmp, ignore_errors=True)
        how = f"codex sandbox workspace-write, /tmp excluded, {'NETWORK OPEN (Gradle lock listener needs loopback; writes still confined)' if network else 'no network'}, writable: {writable or 'worktree only'}"
        sandbox = {"profile": "workspace-write", "network": network, "writable_roots": writable, "tmp_excluded": True}
    elif not unsandboxed:
        return {"exit": 126, "stdout": "", "stderr": "codex binary not found; refusing to run VERIFY unsandboxed (pass --unsandboxed-verify to override)",
                "how": "not run", "duration_s": 0.0, "timed_out": False, "rewritten_command": cmd, "sandbox": None}
    else:
        rc, out, err, timed_out = _run_capturing(cmd, wt, timeout, shell=True)
        how = "UNSANDBOXED (architect accepted the risk)"
        sandbox = {"profile": "none", "network": True, "writable_roots": ["*"], "tmp_excluded": False}
    return {"exit": rc, "stdout": out, "stderr": err, "how": how, "duration_s": round(time.time() - t0, 2), "timed_out": timed_out,
            "rewritten_command": cmd if cmd != original else None, "sandbox": sandbox}


def resolve_run_dir(wt: str, task: str | None, explicit: str | None) -> Path | None:
    """The task's run dir: --run-dir, else <git-common-dir>/tri-lane/run/<task> with the task from the lane branch or the worktree name."""
    if explicit:
        p = Path(explicit)
        p.mkdir(parents=True, exist_ok=True)
        return p
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import lane_run  # noqa: E402
        t = task or lane_run.task_from_worktree(wt)
        if not t:
            return None
        return lane_run.run_dir(t, cwd=wt)
    except Exception:
        return None


def persist(rd: Path, report: dict, verified_full: list) -> dict:
    """report.json (previous becomes report-<n>.json), verify.jsonl append, verify-<n>.out/.err. Returns paths."""
    written = {"report": None, "verify": [], "verify_jsonl": None}
    rd.mkdir(parents=True, exist_ok=True)
    prev = rd / "report.json"
    if prev.exists():
        n = 1
        while (rd / f"report-{n}.json").exists():
            n += 1
        prev.rename(rd / f"report-{n}.json")
        report["attempt"] = n + 1
    else:
        report["attempt"] = 1
    report["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    existing = [p for p in rd.glob("verify-*.out")]
    idx = len(existing)
    vj = rd / "verify.jsonl"
    with open(vj, "a") as fh:
        for v in verified_full:
            idx += 1
            so, se = rd / f"verify-{idx}.out", rd / f"verify-{idx}.err"
            so.write_text(v["stdout"]); se.write_text(v["stderr"])
            rec = {k: v[k] for k in ("command", "rewritten_command", "exit", "duration_s", "timed_out", "filtered", "how", "sandbox")}
            rec.update({"cwd": report.get("WORKTREE"), "commit": report.get("COMMIT"), "attempt": report["attempt"], "at": report["generated_at"],
                        "stdout_path": str(so), "stderr_path": str(se), "cache_key": None})
            fh.write(json.dumps(rec) + "\n")
            written["verify"].append(str(so))
    written["verify_jsonl"] = str(vj)
    prev.write_text(json.dumps(report, indent=2))
    written["report"] = str(prev)
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worktree", required=True, help="path the lane ran against")
    ap.add_argument("--lane", required=True, help='as executed, e.g. "gpt-5.6-luna @ high" or "gemini-3.8-flash-high"')
    ap.add_argument("--objective", default="", help="one-line objective from the spec")
    ap.add_argument("--files", action="append", default=[], help="paths the spec allows the lane to touch (repeatable; dirs allowed)")
    ap.add_argument("--verify", action="append", default=[], help="VERIFY command to re-run (repeatable)")
    ap.add_argument("--verify-timeout", type=int, default=600, help="seconds per verify command (default 600)")
    ap.add_argument("--unsandboxed-verify", action="store_true", help="run VERIFY outside codex sandbox; only after the diff has been read")
    ap.add_argument("--verify-network", action="store_true", help="keep the sandbox but open the network for VERIFY (automatic for Gradle commands)")
    ap.add_argument("--commit", action="store_true", help="commit the lane's diff in the worktree on its behalf (lane/<task> branch) when the diff is non-empty and not refused")
    ap.add_argument("--writable", action="append", default=[], help="extra directory the sandboxed VERIFY may write (repeatable). Toolchain caches (~/.gradle, ~/.npm, ...) are added automatically")
    ap.add_argument("--no-toolchain-caches", action="store_true", help="do not auto-add detected toolchain caches as writable roots")
    ap.add_argument("--final", help="file holding the lane's final message")
    ap.add_argument("--base", help="ref the lane branched from (e.g. main, dev, or a SHA). Diff is measured against it, so committed lane work counts. Default HEAD = uncommitted only")
    ap.add_argument("--status-hint", choices=["timeout", "unavailable"], help="the wrapper already knows the lane hit its cap or was unavailable. A timeout with a non-empty diff is still evaluated; the overrun is recorded in GAPS")
    ap.add_argument("--tail", type=int, default=40, help="lines of verify output to keep (default 40)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of the text contract")
    ap.add_argument("--task", help="task slug for the run dir (default: from the lane/<task> branch or the worktree name)")
    ap.add_argument("--run-dir", help="where to persist report.json / verify.jsonl (default: <git-common-dir>/tri-lane/run/<task>)")
    ap.add_argument("--no-persist", action="store_true", help="do not write report.json / verify.jsonl (tests of the pure contract)")
    args = ap.parse_args()

    wt = str(Path(args.worktree).resolve())
    rc_top, top = sh(["git", "rev-parse", "--show-toplevel"], wt, 30)
    if rc_top != 0:
        print(f"lane-report: {wt} is not a git worktree", file=sys.stderr)
        return 4
    rc_main, main_dir = sh(["git", "rev-parse", "--git-common-dir"], wt, 30)
    common = str(Path(wt, main_dir.strip()).resolve()) if rc_main == 0 else ""
    if common and str(Path(common).parent) == wt:
        print(f"lane-report: refusing: {wt} is the main checkout, not a lane worktree", file=sys.stderr)
        return 4

    ref = "HEAD"
    gaps: list[str] = []
    if args.base:
        rc_b, _ = sh(["git", "rev-parse", "--verify", "--quiet", args.base + "^{commit}"], wt, 30)
        if rc_b == 0:
            ref = args.base
        else:
            gaps.append(f"--base {args.base} is not a commit in this worktree; measuring uncommitted changes only")
    _, stat = sh(["git", "diff", "--stat", ref], wt, 60)
    _, porcelain = sh(["git", "status", "--porcelain"], wt, 60)
    _, names = sh(["git", "diff", "--name-only", ref], wt, 60)
    untracked = [l[3:] for l in porcelain.splitlines() if l.startswith("??") and not l[3:].startswith(TMP_DIRNAME)]
    touched = sorted({l.strip() for l in names.splitlines() if l.strip() and not l.strip().startswith(TMP_DIRNAME)} | set(untracked))
    changed = bool(touched)
    _, name_status = sh(["git", "diff", "--name-status", ref], wt, 60)
    deleted = sorted({l.split("\t", 1)[1].strip() for l in name_status.splitlines() if l.startswith("D") and "\t" in l})
    deleted += [l[3:] for l in porcelain.splitlines() if l.startswith(" D") or l.startswith("D ")]
    deleted = sorted(set(deleted))
    # a spec file the lane was asked to modify that comes back deleted, with nothing else written: worse than an empty diff (#53)
    spec_files = [f for f in args.files if not f.endswith("/") and not (Path(wt) / f).is_dir()]
    deleted_spec = [d for d in deleted if d in spec_files]
    deletion_only = changed and set(touched) <= set(deleted)

    lane_said = ""
    if args.final and Path(args.final).exists():
        lane_said = tail(Path(args.final).read_text(errors="ignore"), 3).strip()

    verified: list[dict] = []
    verified_full: list[dict] = []
    out_of_scope = [p for p in touched if args.files and not in_scope(p, args.files)]
    exec_cfg = [p for p in touched if is_exec_config(p)]

    if args.status_hint == "unavailable" or (args.status_hint == "timeout" and not changed):
        status = args.status_hint
        gaps.append(f"wrapper reported {status}")
    elif not changed:
        status = "refused"
        gaps.append("empty diff with clean exit: treat as refusal, not success; check AGENTS.md pins and the spec preamble")
    elif deleted_spec or deletion_only:
        status = "refused"
        gaps.append(f"VERIFY not run: deletion-only diff for {deleted_spec or deleted}: the lane deleted what it was asked to modify and wrote nothing back. Restore from the base and resubmit with a corrected spec")
    elif out_of_scope or exec_cfg:
        status = "partial"
        if out_of_scope:
            gaps.append(f"VERIFY not run: lane touched files outside FILES: {out_of_scope}")
        if exec_cfg:
            gaps.append(f"VERIFY not run: lane touched executable config: {exec_cfg}. Read the diff; if safe, re-run with --files widened or --unsandboxed-verify")
    else:
        status = "complete"
        if args.status_hint == "timeout":
            gaps.append("lane hit its wall-clock cap; the diff it left was evaluated anyway. Check LANE SAID for whether it considered itself finished")
        if not args.verify:
            gaps.append("no VERIFY command supplied; the report carries no evidence")
            status = "partial"
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            from lane_toolchains import writable_roots  # noqa: E402
            writable = writable_roots(wt, args.writable) if not args.no_toolchain_caches else [str(Path(p).expanduser().resolve()) for p in args.writable if Path(p).expanduser().exists()]
        except Exception as e:  # never let cache detection block a report
            writable = []
            gaps.append(f"toolchain cache detection failed: {e}")
        for cmd in args.verify:
            v = run_verify(cmd, wt, args.verify_timeout, args.unsandboxed_verify, writable, args.verify_network)
            v["command"] = cmd
            v["filtered"] = is_filtered(cmd)
            verified_full.append(v)
            verified.append({"command": cmd, "exit": v["exit"], "how": v["how"], "duration_s": v["duration_s"], "timed_out": v["timed_out"],
                             "filtered": v["filtered"], "output_tail": tail(v["stdout"] + ("\n" + v["stderr"] if v["stderr"] else ""), args.tail)})
            if "NETWORK OPEN" in v["how"]:
                gaps.append("VERIFY ran with the sandbox network open (Gradle lock listener); writes stayed confined. Read the diff for network use before trusting it")
            if v["filtered"]:
                gaps.append(f"VERIFY `{cmd}` is piped through a filter or an || fallback; its exit status may be masked. Read verify-<n>.err")
            if v["timed_out"]:
                gaps.append(f"VERIFY `{cmd}` hit its {args.verify_timeout}s timeout; partial output kept")
            if v["exit"] != 0:
                status = "partial"
    commit_sha = None
    if args.commit and changed and status in ("complete", "partial", "timeout"):
        sh(["git", "add", "-A", "--", ".", f":(exclude){TMP_DIRNAME}"], wt, 60)
        rc_c, out_c = sh(["git", "-c", "user.email=tri-lane@cure", "-c", "user.name=tri-lane", "commit", "-qm", f"lane: {args.objective or args.lane} [{status}]"], wt, 120)
        if rc_c == 0:
            _, sha = sh(["git", "rev-parse", "--short", "HEAD"], wt, 30)
            commit_sha = sha.strip()
        elif "nothing to commit" not in out_c:
            gaps.append(f"--commit failed: {out_c.strip()[:160]}")
    if lane_said and changed and ("no changes" in lane_said.lower() or "did not modify" in lane_said.lower()):
        gaps.append("lane's final message disagrees with the diff")

    report = {
        "LANE": args.lane,
        "STATUS": status,
        "BASE": ref,
        "OBJECTIVE": args.objective,
        "CHANGES": stat.strip() or "(none)",
        "TOUCHED": touched,
        "OUT_OF_SCOPE": out_of_scope,
        "EXEC_CONFIG_TOUCHED": exec_cfg,
        "VERIFIED": verified,
        "LANE_SAID": lane_said or "(no final message captured)",
        "COMMIT": commit_sha,
        "GAPS": gaps,
        "WORKTREE": wt,
    }
    if not args.no_persist:
        rd = resolve_run_dir(wt, args.task, args.run_dir)
        if rd is None:
            gaps.append("report not persisted: no run dir could be resolved (pass --task or --run-dir)")
        else:
            try:
                report["PERSISTED"] = persist(rd, report, verified_full)
            except Exception as e:  # evidence is additive; never turn a report into a crash
                gaps.append(f"report not persisted: {e}")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"LANE       {report['LANE']}")
        print(f"STATUS     {report['STATUS']}")
        print(f"OBJECTIVE  {report['OBJECTIVE']}")
        print(f"CHANGES    (vs {ref})")
        print("  " + report["CHANGES"].replace("\n", "\n  "))
        if untracked:
            print("  untracked: " + ", ".join(untracked))
        if out_of_scope:
            print("  OUT OF SCOPE: " + ", ".join(out_of_scope))
        if exec_cfg:
            print("  EXEC CONFIG TOUCHED: " + ", ".join(exec_cfg))
        print("VERIFIED")
        if not verified:
            print("  (not run)")
        for v in verified:
            print(f"  $ {v['command']}  -> exit {v['exit']}  [{v['how']}]")
            print("  " + v["output_tail"].replace("\n", "\n  "))
        print(f"LANE SAID  {report['LANE_SAID']}")
        if commit_sha:
            print(f"COMMIT     {commit_sha} (on the lane branch; merge from there)")
        print("GAPS       " + ("; ".join(gaps) if gaps else "none"))
    return {"complete": 0, "partial": 2, "refused": 3}.get(status, 4)


if __name__ == "__main__":
    sys.exit(main())
