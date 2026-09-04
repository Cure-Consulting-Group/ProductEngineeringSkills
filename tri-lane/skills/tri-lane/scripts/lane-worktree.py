#!/usr/bin/env python3
"""lane-worktree: create and remove lane worktrees safely, so a live lane is never orphaned.

  add     git worktree add ../wt/<task> (branch lane/<task> from --base), or a detached read-only twin with --ro;
          creates the run dir $(git rev-parse --git-common-dir)/tri-lane/run/<task>/ and prints paths as JSON
  lock    write run/<task>/lane.lock with the lane's pid and start time (wrappers call this before dispatch)
  unlock  remove the lock (wrappers call this after the report is produced)
  status  is the lane alive? lock present, pid alive, any codex/agy process with the worktree path in its args
  remove  refuses while a lock is present and its pid is alive, or while a codex/agy process references the
          worktree; otherwise pushes the branch as lane/<task>-salvage if it has unmerged commits, then removes.
          --force skips the liveness check but never the salvage push.

Orphaning a live lane cost two runs in one session (HoopTrace, 3 Sep 2026). Python stdlib only.

Examples:
  python3 lane-worktree.py add --task a4 --base main
  python3 lane-worktree.py add --task a4 --ro
  python3 lane-worktree.py lock --task a4 --pid $!
  python3 lane-worktree.py status --task a4
  python3 lane-worktree.py remove --task a4
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def sh(cmd, cwd=None, timeout=120):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return 1, str(e)


def repo_root() -> Path:
    rc, out = sh(["git", "rev-parse", "--show-toplevel"])
    if rc != 0:
        sys.exit("not inside a git repository")
    return Path(out.strip())


def run_dir(task: str) -> Path:
    rc, out = sh(["git", "rev-parse", "--git-common-dir"])
    base = Path(out.strip()).resolve() if rc == 0 else Path.cwd()
    d = base / "tri-lane" / "run" / task
    (d / "tmp").mkdir(parents=True, exist_ok=True)
    return d


def wt_path(task: str, ro: bool) -> Path:
    return (repo_root().parent / "wt" / (task + ("-ro" if ro else ""))).resolve()


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def processes_referencing(path: Path) -> list:
    rc, out = sh(["ps", "-axo", "pid=,command="], timeout=30)
    hits = []
    needle = str(path)
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        pid, _, cmd = line.partition(" ")
        if needle in cmd and any(tok in cmd for tok in ("codex", "agy", "gradle", "node", "npm", "pytest", "vitest")):
            hits.append({"pid": int(pid), "command": cmd[:160]})
    return hits


def liveness(task: str, wt: Path) -> dict:
    lock = run_dir(task) / "lane.lock"
    info = {"worktree": str(wt), "exists": wt.exists(), "lock": None, "lock_pid_alive": False, "processes": []}
    if lock.exists():
        try:
            info["lock"] = json.loads(lock.read_text())
            info["lock_pid_alive"] = pid_alive(int(info["lock"].get("pid", 0)))
        except Exception:
            info["lock"] = {"raw": lock.read_text()[:200]}
    if wt.exists():
        info["processes"] = processes_referencing(wt)
    info["alive"] = bool(info["lock_pid_alive"] or info["processes"])
    return info


def cmd_add(a) -> int:
    root = repo_root()
    wt = wt_path(a.task, a.ro)
    rd = run_dir(a.task)
    if wt.exists():
        print(json.dumps({"worktree": str(wt), "run_dir": str(rd), "note": "already exists; reused"}))
        return 0
    wt.parent.mkdir(parents=True, exist_ok=True)
    if a.ro:
        ref = a.base or f"lane/{a.task}"
        rc, out = sh(["git", "worktree", "add", "--detach", str(wt), ref], cwd=str(root))
        if rc == 0:
            sh(["chmod", "-R", "a-w", str(wt)], timeout=300)
    else:
        rc, out = sh(["git", "worktree", "add", str(wt), "-b", f"lane/{a.task}", a.base or "HEAD"], cwd=str(root))
        if rc != 0 and "already exists" in out:
            rc, out = sh(["git", "worktree", "add", str(wt), f"lane/{a.task}"], cwd=str(root))
    if rc != 0:
        print(out.strip(), file=sys.stderr)
        return 1
    print(json.dumps({"worktree": str(wt), "worktree_physical": str(wt.resolve()), "branch": None if a.ro else f"lane/{a.task}", "run_dir": str(rd), "tmpdir": str(rd / "tmp")}))
    return 0


def cmd_lock(a) -> int:
    lock = run_dir(a.task) / "lane.lock"
    lock.write_text(json.dumps({"pid": a.pid, "lane": a.lane, "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}))
    print(json.dumps({"locked": a.task, "pid": a.pid}))
    return 0


def cmd_unlock(a) -> int:
    lock = run_dir(a.task) / "lane.lock"
    if lock.exists():
        lock.unlink()
    print(json.dumps({"unlocked": a.task}))
    return 0


def cmd_status(a) -> int:
    info = liveness(a.task, wt_path(a.task, a.ro))
    print(json.dumps(info, indent=2))
    return 0 if not info["alive"] else 3


def cmd_remove(a) -> int:
    root = repo_root()
    wt = wt_path(a.task, a.ro)
    info = liveness(a.task, wt)
    if info["alive"] and not a.force:
        print(json.dumps({"refused": str(wt), "reason": "lane appears to be running", "lock": info["lock"], "processes": info["processes"],
                          "hint": "wait for the lane report, or `lane-worktree.py status`; --force only if you have confirmed the process is dead"}, indent=2), file=sys.stderr)
        return 3
    salvage = None
    if not a.ro and wt.exists():
        branch = f"lane/{a.task}"
        rc, unmerged = sh(["git", "log", "--oneline", f"{a.base or 'HEAD'}..{branch}"], cwd=str(root))
        rc2, dirty = sh(["git", "status", "--porcelain"], cwd=str(wt))
        if dirty.strip():
            sh(["git", "add", "-A"], cwd=str(wt))
            sh(["git", "-c", "user.email=tri-lane@cure", "-c", "user.name=tri-lane", "commit", "-qm", f"salvage: uncommitted lane state for {a.task}"], cwd=str(wt))
        if (rc == 0 and unmerged.strip()) or dirty.strip():
            salvage = f"{branch}-salvage"
            sh(["git", "branch", "-f", salvage, branch], cwd=str(root))
            if not a.no_push:
                rc3, out3 = sh(["git", "push", "-q", "origin", f"{salvage}:{salvage}"], cwd=str(root), timeout=300)
                if rc3 != 0:
                    salvage += " (push failed: " + out3.strip()[:80] + ")"
    if wt.exists():
        rc, out = sh(["git", "worktree", "remove", "--force", str(wt)], cwd=str(root))
        if rc != 0:
            print(out.strip(), file=sys.stderr)
            return 1
    sh(["git", "worktree", "prune"], cwd=str(root))
    lock = run_dir(a.task) / "lane.lock"
    if lock.exists():
        lock.unlink()
    print(json.dumps({"removed": str(wt), "salvage_branch": salvage, "run_dir_kept": str(run_dir(a.task))}))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("add", cmd_add), ("lock", cmd_lock), ("unlock", cmd_unlock), ("status", cmd_status), ("remove", cmd_remove)):
        s = sub.add_parser(name)
        s.add_argument("--task", required=True)
        s.add_argument("--ro", action="store_true", help="the read-only twin worktree (<task>-ro)")
        if name in ("add", "remove"):
            s.add_argument("--base", help="base ref (add: branch point; remove: what counts as merged; default HEAD)")
        if name == "lock":
            s.add_argument("--pid", type=int, required=True)
            s.add_argument("--lane", default="")
        if name == "remove":
            s.add_argument("--force", action="store_true", help="skip the liveness check (never skips salvage)")
            s.add_argument("--no-push", action="store_true", help="create the salvage branch locally only")
        s.set_defaults(fn=fn)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
