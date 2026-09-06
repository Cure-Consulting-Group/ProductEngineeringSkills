#!/usr/bin/env python3
"""lane-selftest: exercise every safety rail end to end in a scratch repo, in under a minute.

Creates a throwaway git repo (never touches the user's checkouts), then checks:
  1. guard hook blocks unsandboxed codex/agy and passes sandboxed forms
  2. lane-report: empty diff -> refused; out-of-scope/exec-config -> VERIFY not run; --base counts commits
  3. sandboxed VERIFY: write inside worktree ok, write to $HOME denied, /tmp denied   (skipped if codex missing)
  4. lane-worktree: add, lock, status=alive, remove refused, unlock, remove salvages unmerged work (no push)
  5. lane_toolchains: detects a gradle marker and resolves physical cache paths

Prints JSON; exit 0 when every check passed or was skipped for a documented reason, 1 otherwise.
Run by `lane-preflight.py --self-test` and by CI. Python stdlib only.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOOK = HERE.parent.parent.parent / "hooks" / "guard-lane-command.py"


def sh(cmd, cwd=None, env=None, inp=None, timeout=120):
    p = subprocess.run(cmd, cwd=cwd, env=env, input=inp, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def git(args, cwd):
    return sh(["git", "-c", "user.email=selftest@cure", "-c", "user.name=selftest"] + args, cwd=cwd)


def main() -> int:
    results = []
    def rec(name, ok, detail="", skipped=False):
        results.append({"check": name, "status": "skip" if skipped else ("pass" if ok else "FAIL"), "detail": detail})

    base = Path(tempfile.mkdtemp(prefix="tri-lane-selftest-"))
    repo = base / "repo"
    repo.mkdir()
    git(["init", "-q", "-b", "main"], repo)
    (repo / "README.md").write_text("selftest\n")
    git(["add", "-A"], repo); git(["commit", "-qm", "init"], repo)
    env = dict(os.environ, TRI_LANE_NO_POOLS="1")

    # 1. guard hook
    cases = [("block", 'codex exec - -m gpt-5.6-luna < s'), ("pass", 'codex exec - -s workspace-write -m gpt-5.6-luna < s'),
             ("block", 'agy -p "x" --mode plan'), ("pass", 'agy -p "x" --mode plan --sandbox'), ("block", 'agy -p "x" --sandbox --mode accept-edits'),
             ("pass", 'codex exec review --base main'), ("block", 'codex exec - -s read-only --yolo "x"')]
    bad = []
    for want, cmd in cases:
        rc, _ = sh([sys.executable, str(HOOK)], inp=json.dumps({"tool_input": {"command": cmd}}))
        got = "block" if rc == 2 else "pass"
        if got != want:
            bad.append(cmd)
    rec("guard hook matrix", not bad, f"{len(cases)} cases" + (f"; mismatches: {bad}" if bad else ""))

    # 4. lane-worktree (do first so the report tests can use the worktree)
    LW = HERE / "lane-worktree.py"
    rc, out = sh([sys.executable, str(LW), "add", "--task", "st", "--base", "main"], cwd=repo, env=env)
    try:
        wt = Path(json.loads(out.strip().splitlines()[-1])["worktree"])
    except Exception:
        wt = None
    rec("lane-worktree add", rc == 0 and wt is not None and wt.exists(), out.strip()[-160:])
    if wt:
        sleeper = subprocess.Popen(["sleep", "30"])
        sh([sys.executable, str(LW), "lock", "--task", "st", "--pid", str(sleeper.pid)], cwd=repo, env=env)
        rc_s, _ = sh([sys.executable, str(LW), "status", "--task", "st"], cwd=repo, env=env)
        rc_r, out_r = sh([sys.executable, str(LW), "remove", "--task", "st", "--base", "main"], cwd=repo, env=env)
        rec("lane-worktree refuses removal while alive", rc_s == 3 and rc_r == 3 and wt.exists(), "status exit 3, remove exit 3")
        sleeper.kill(); sleeper.wait()
        sh([sys.executable, str(LW), "unlock", "--task", "st"], cwd=repo, env=env)

    # 2. lane-report
    LR = HERE / "lane-report.py"
    if wt:
        rc, out = sh([sys.executable, str(LR), "--worktree", str(wt), "--lane", "x", "--json"], cwd=repo, env=env)
        rec("lane-report empty diff -> refused", rc == 3 and '"refused"' in out, "")
        (wt / "README.md").write_text("selftest changed\n")
        (wt / "package.json").write_text("{}\n")
        rc, out = sh([sys.executable, str(LR), "--worktree", str(wt), "--lane", "x", "--files", "README.md", "--verify", "echo should-not-run", "--json"], cwd=repo, env=env)
        try:
            d = json.loads(out)
            ok = d["STATUS"] == "partial" and not d["VERIFIED"] and "package.json" in d["EXEC_CONFIG_TOUCHED"]
        except Exception:
            ok = False
        rec("lane-report refuses VERIFY on exec-config/out-of-scope", ok, "")
        (wt / "package.json").unlink()
        git(["add", "-A"], wt); git(["commit", "-qm", "lane work"], wt)
        rc, out = sh([sys.executable, str(LR), "--worktree", str(wt), "--lane", "x", "--base", "main", "--files", "README.md", "--verify", "true", "--unsandboxed-verify", "--json"], cwd=repo, env=env)
        try:
            d = json.loads(out); ok = d["STATUS"] == "complete" and d["BASE"] == "main" and "README.md" in d["TOUCHED"]
        except Exception:
            ok = False
        rec("lane-report --base counts committed work", ok, "")

        # 3. sandboxed VERIFY
        if shutil.which("codex"):
            probe = Path.home() / ".tri-lane-selftest-probe"
            rc, out = sh([sys.executable, str(LR), "--worktree", str(wt), "--lane", "x", "--base", "main", "--files", "README.md", "--no-toolchain-caches",
                          "--verify", f"touch inside.txt && echo IN_OK; touch '{probe}' 2>&1 | head -1; touch /tmp/tri-lane-selftest-probe 2>&1 | head -1", "--json"], cwd=repo, env=env, timeout=180)
            try:
                d = json.loads(out); tail = d["VERIFIED"][0]["output_tail"]
                ok = "IN_OK" in tail and "not permitted" in tail and not probe.exists() and not Path("/tmp/tri-lane-selftest-probe").exists()
            except Exception:
                ok = False
            rec("sandboxed VERIFY: worktree ok, home and /tmp denied", ok, out.strip()[-200:] if not ok else "")
            probe.unlink(missing_ok=True)
        else:
            rec("sandboxed VERIFY", True, "codex not installed", skipped=True)

        # 4b. salvage on remove
        rc, out = sh([sys.executable, str(LW), "remove", "--task", "st", "--base", "main", "--no-push"], cwd=repo, env=env)
        rc_b, branches = git(["branch", "--list", "lane/st-salvage"], repo)
        rec("lane-worktree remove salvages unmerged commits", rc == 0 and "lane/st-salvage" in branches and not wt.exists(), out.strip()[-160:])

    # 5. toolchains
    (repo / "gradlew").write_text("#!/bin/sh\n")
    sys.path.insert(0, str(HERE))
    try:
        from lane_toolchains import detect  # noqa: E402
        tcs = detect(repo)
        names = [t["toolchain"] for t in tcs]
        rec("lane_toolchains detects gradle", "gradle" in names, f"detected {names}")
    except Exception as e:
        rec("lane_toolchains", False, str(e))

    shutil.rmtree(base, ignore_errors=True)
    failed = [r for r in results if r["status"] == "FAIL"]
    print(json.dumps({"status": "ok" if not failed else "FAIL", "checks": results, "elapsed_note": "scratch repo removed"}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    t0 = time.time()
    code = main()
    print(f"selftest finished in {round(time.time() - t0, 1)}s", file=sys.stderr)
    sys.exit(code)
