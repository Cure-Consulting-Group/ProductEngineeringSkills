#!/usr/bin/env python3
"""Report worktrees that are merged or stale, and release port slots of removed worktrees.

Usage:
  python3 worktree_report.py
  python3 worktree_report.py --base origin/main --stale-days 30 --json
  python3 worktree_report.py --release-missing   # drop registry entries whose directory is gone
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REGISTRY = "worktree-ports.json"


def git(*args, cwd=None):
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip()


def worktrees():
    code, out = git("worktree", "list", "--porcelain")
    if code != 0:
        raise RuntimeError("not inside a git repository")
    items, cur = [], {}
    for line in out.splitlines() + [""]:
        if not line:
            if cur:
                items.append(cur)
            cur = {}
        elif line.startswith("worktree "):
            cur["path"] = line[len("worktree "):]
        elif line.startswith("branch "):
            cur["branch"] = line[len("branch "):].replace("refs/heads/", "", 1)
        elif line == "detached":
            cur["branch"] = None
    return items


def main():
    p = argparse.ArgumentParser(description="List merged/stale worktrees and manage the port registry.")
    p.add_argument("--base", default="origin/main", help="branch merged work lands on (default: origin/main)")
    p.add_argument("--stale-days", type=int, default=30, help="flag worktrees with no commit in N days (default: 30)")
    p.add_argument("--release-missing", action="store_true", help="remove registry slots for directories that no longer exist")
    p.add_argument("--json", action="store_true", help="emit JSON")
    a = p.parse_args()

    try:
        items = worktrees()
        _, common = git("rev-parse", "--path-format=absolute", "--git-common-dir")
        reg_path = Path(common) / REGISTRY
        try:
            registry = json.loads(reg_path.read_text())
        except (OSError, ValueError):
            registry = {}

        now = time.time()
        rows = []
        for i, wt in enumerate(items):
            path, branch = wt["path"], wt.get("branch")
            _, ts = git("-C", path, "log", "-1", "--format=%ct", "HEAD")
            age = int((now - int(ts)) // 86400) if ts.isdigit() else None
            merged = False
            if branch and i > 0:
                merged = git("merge-base", "--is-ancestor", branch, a.base)[0] == 0
            rows.append({"path": path, "branch": branch, "main": i == 0, "slot": registry.get(path, 0 if i == 0 else None),
                         "days_since_commit": age, "merged": merged,
                         "stale": age is not None and age > a.stale_days and i > 0})

        released = []
        if a.release_missing:
            for path in list(registry):
                if not Path(path).exists():
                    released.append(path)
                    del registry[path]
            reg_path.write_text(json.dumps(registry, indent=2) + "\n")
    except (RuntimeError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    flagged = [r for r in rows if r["merged"] or r["stale"]]
    if a.json:
        print(json.dumps({"worktrees": rows, "released_slots": released}, indent=2))
    else:
        for r in rows:
            tags = [t for t, on in (("MERGED", r["merged"]), ("STALE", r["stale"]), ("main", r["main"])) if on]
            print(f"{r['path']}  [{r['branch'] or 'detached'}]  slot={r['slot']}  "
                  f"{r['days_since_commit']}d  {' '.join(tags)}")
        for path in released:
            print(f"released slot for missing {path}")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
