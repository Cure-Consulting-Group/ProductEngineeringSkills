#!/usr/bin/env python3
"""lane-report: turn a lane's worktree into the report contract, with the safety rules enforced in code.

What it enforces, in order:
  1. Empty diff  -> STATUS refused, no matter what the lane's final message says.
  2. FILES scope -> if --files is given and the lane touched anything outside it, or touched
                    executable config (package.json, Makefile, conftest.py, CI, ...), VERIFY is NOT run
                    and STATUS is partial. Lane-written code must never execute before a human-grade
                    read of the diff decides it is safe.
  3. VERIFY      -> re-run by this script inside `codex sandbox` (workspace-write: no network, writes
                    confined to the worktree). Pass --unsandboxed-verify only when the architect has
                    already read the diff and accepts the risk.

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


def run_verify(cmd: str, wt: str, timeout: int, unsandboxed: bool, writable: list[str]) -> tuple[int, str, str]:
    """Returns (exit, output, how)."""
    if not unsandboxed and shutil.which("codex"):
        # cwd is the worktree; codex sandbox treats cwd as the writable workspace. (-C would require --permission-profile.)
        # /tmp is excluded from the sandbox; TMPDIR points inside the worktree so test runners still have scratch space
        # on the project volume (the system volume filled and stalled lanes on 2026-09-03).
        # Toolchain caches (~/.gradle, ~/.npm, ...) are added as writable roots, physical paths only, or builds cannot
        # take their locks and the lane can never verify itself (HoopTrace, 2026-09-03).
        tmp = Path(wt) / TMP_DIRNAME
        tmp.mkdir(exist_ok=True)
        env = dict(os.environ, TMPDIR=str(tmp))
        roots_cfg = "sandbox_workspace_write.writable_roots=" + json.dumps(writable)
        argv = ["codex", "sandbox", "-c", "sandbox_mode=workspace-write", "-c", "sandbox_workspace_write.exclude_slash_tmp=true", "-c", roots_cfg, "--", "sh", "-c", cmd]
        try:
            p = subprocess.run(argv, cwd=wt, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL, env=env)
            rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
        except subprocess.TimeoutExpired:
            rc, out = 124, f"timeout after {timeout}s"
        shutil.rmtree(tmp, ignore_errors=True)
        return rc, out, f"codex sandbox workspace-write, /tmp excluded, writable: {writable or 'worktree only'}"
    if not unsandboxed:
        return 126, "codex binary not found; refusing to run VERIFY unsandboxed (pass --unsandboxed-verify to override)", "not run"
    rc, out = sh(cmd, wt, timeout, shell=True)
    return rc, out, "UNSANDBOXED (architect accepted the risk)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worktree", required=True, help="path the lane ran against")
    ap.add_argument("--lane", required=True, help='as executed, e.g. "gpt-5.6-luna @ high" or "gemini-3.8-flash-high"')
    ap.add_argument("--objective", default="", help="one-line objective from the spec")
    ap.add_argument("--files", action="append", default=[], help="paths the spec allows the lane to touch (repeatable; dirs allowed)")
    ap.add_argument("--verify", action="append", default=[], help="VERIFY command to re-run (repeatable)")
    ap.add_argument("--verify-timeout", type=int, default=600, help="seconds per verify command (default 600)")
    ap.add_argument("--unsandboxed-verify", action="store_true", help="run VERIFY outside codex sandbox; only after the diff has been read")
    ap.add_argument("--writable", action="append", default=[], help="extra directory the sandboxed VERIFY may write (repeatable). Toolchain caches (~/.gradle, ~/.npm, ...) are added automatically")
    ap.add_argument("--no-toolchain-caches", action="store_true", help="do not auto-add detected toolchain caches as writable roots")
    ap.add_argument("--final", help="file holding the lane's final message")
    ap.add_argument("--base", help="ref the lane branched from (e.g. main, dev, or a SHA). Diff is measured against it, so committed lane work counts. Default HEAD = uncommitted only")
    ap.add_argument("--status-hint", choices=["timeout", "unavailable"], help="the wrapper already knows the lane hit its cap or was unavailable. A timeout with a non-empty diff is still evaluated; the overrun is recorded in GAPS")
    ap.add_argument("--tail", type=int, default=40, help="lines of verify output to keep (default 40)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of the text contract")
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

    lane_said = ""
    if args.final and Path(args.final).exists():
        lane_said = tail(Path(args.final).read_text(errors="ignore"), 3).strip()

    verified: list[dict] = []
    out_of_scope = [p for p in touched if args.files and not in_scope(p, args.files)]
    exec_cfg = [p for p in touched if is_exec_config(p)]

    if args.status_hint == "unavailable" or (args.status_hint == "timeout" and not changed):
        status = args.status_hint
        gaps.append(f"wrapper reported {status}")
    elif not changed:
        status = "refused"
        gaps.append("empty diff with clean exit: treat as refusal, not success; check AGENTS.md pins and the spec preamble")
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
            vrc, out, how = run_verify(cmd, wt, args.verify_timeout, args.unsandboxed_verify, writable)
            verified.append({"command": cmd, "exit": vrc, "how": how, "output_tail": tail(out, args.tail)})
            if vrc != 0:
                status = "partial"
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
        "GAPS": gaps,
    }
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
        print("GAPS       " + ("; ".join(gaps) if gaps else "none"))
    return {"complete": 0, "partial": 2, "refused": 3}.get(status, 4)


if __name__ == "__main__":
    sys.exit(main())
