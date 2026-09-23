#!/usr/bin/env python3
"""Create a sibling git worktree with a stable port block and per-worktree env files.

Ports come from a registry in the repo's shared git dir (worktree-ports.json), so a
worktree keeps its block for life and removing another worktree never shifts it.

Usage:
  python3 worktree_create.py payments --branch feature/payments
  python3 worktree_create.py pr-1234 --pr 1234
  python3 worktree_create.py bisect --detach HEAD~50 --no-env
  python3 worktree_create.py payments --branch feature/payments --db --dry-run --json
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REGISTRY = "worktree-ports.json"


def git(*args, cwd=None, check=True):
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {res.stderr.strip()}")
    return res.stdout.strip()


def load_registry(common_dir):
    path = Path(common_dir) / REGISTRY
    try:
        return path, json.loads(path.read_text())
    except (OSError, ValueError):
        return path, {}


def allocate_slot(registry, target):
    """Main checkout is slot 0; reuse this path's slot or take the lowest free one."""
    if target in registry:
        return registry[target]
    used = set(registry.values())
    slot = 1
    while slot in used:
        slot += 1
    return slot


def set_var(text, key, value):
    line = f"{key}={value}"
    pattern = re.compile(rf"^{re.escape(key)}=.*$", re.M)
    return pattern.sub(line, text) if pattern.search(text) else text.rstrip("\n") + ("\n" if text else "") + line + "\n"


def main():
    p = argparse.ArgumentParser(description="Create a sibling worktree with an isolated port block and env files.")
    p.add_argument("name", help="short purpose id; directory becomes <repo>-<name> next to the main checkout")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--branch", help="branch to create (from --base) or check out if it already exists")
    mode.add_argument("--pr", type=int, help="GitHub PR number; fetched as pr-<N> without touching the current checkout")
    mode.add_argument("--detach", metavar="REF", help="detached HEAD at REF (review/bisect)")
    p.add_argument("--base", default="origin/main", help="start point for a new branch (default: origin/main)")
    p.add_argument("--remote", default="origin", help="remote for --pr fetches (default: origin)")
    p.add_argument("--base-port", type=int, default=3000, help="port of the main checkout (default: 3000)")
    p.add_argument("--step", type=int, default=10, help="ports per worktree block (default: 10)")
    p.add_argument("--no-env", action="store_true", help="skip env-file setup")
    p.add_argument("--db", action="store_true", help="write a per-worktree Postgres DATABASE_URL into .env.local")
    p.add_argument("--dry-run", action="store_true", help="print the plan, change nothing")
    p.add_argument("--json", action="store_true", help="emit JSON")
    a = p.parse_args()

    try:
        top = Path(git("rev-parse", "--show-toplevel"))
        common = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir"))
        main_root = common.parent if common.name == ".git" else top
        target = main_root.parent / f"{main_root.name}-{a.name}"
        if target.exists():
            print(f"error: {target} already exists; worktree names are never reused", file=sys.stderr)
            return 2

        if not a.no_env:
            ignored = subprocess.run(["git", "check-ignore", "-q", ".env.local"], cwd=main_root).returncode == 0
            if not ignored:
                print("error: .env.local is not gitignored; add .env* to .gitignore before creating worktrees", file=sys.stderr)
                return 2

        reg_path, registry = load_registry(common)
        slot = allocate_slot(registry, str(target))
        port = a.base_port + slot * a.step
        branch = a.branch or (f"pr-{a.pr}" if a.pr else None)

        cmds = []
        if a.pr:
            cmds.append(["git", "fetch", a.remote, f"pull/{a.pr}/head:pr-{a.pr}"])
            cmds.append(["git", "worktree", "add", str(target), f"pr-{a.pr}"])
        elif a.detach:
            cmds.append(["git", "worktree", "add", "--detach", str(target), a.detach])
        elif a.branch:
            exists = subprocess.run(["git", "rev-parse", "--verify", "--quiet", a.branch], cwd=main_root,
                                    capture_output=True).returncode == 0
            cmds.append(["git", "worktree", "add", str(target), a.branch] if exists
                        else ["git", "worktree", "add", "-b", a.branch, str(target), a.base])
        else:
            cmds.append(["git", "worktree", "add", "-b", a.name, str(target), a.base])
            branch = a.name

        db_name = re.sub(r"[^a-z0-9_]", "_", target.name.lower())
        plan = {"target": str(target), "branch": branch, "slot": slot, "port_base": port,
                "commands": [" ".join(c) for c in cmds], "database": db_name if a.db else None,
                "dry_run": a.dry_run}

        if not a.dry_run:
            for c in cmds:
                subprocess.run(c, cwd=main_root, check=True, capture_output=True, text=True)
            registry[str(target)] = slot
            reg_path.write_text(json.dumps(registry, indent=2) + "\n")
            if not a.no_env:
                for shared in (".env.development", ".env.test"):
                    src = main_root / shared
                    if src.exists():
                        os.symlink(src, target / shared)
                local = main_root / ".env.local"
                text = local.read_text() if local.exists() else ""
                text = set_var(text, "PORT", port)
                text = set_var(text, "PORT_BASE", port)
                if a.db:
                    text = set_var(text, "DATABASE_URL", f"postgresql://localhost:5432/{db_name}")
                (target / ".env.local").write_text(text)
    except (RuntimeError, OSError, subprocess.CalledProcessError) as e:
        msg = getattr(e, "stderr", None) or str(e)
        print(f"error: {msg.strip()}", file=sys.stderr)
        return 1

    if a.json:
        print(json.dumps(plan, indent=2))
    else:
        verb = "Would create" if a.dry_run else "Created"
        print(f"{verb} {plan['target']} on {branch or 'detached HEAD'}; ports {port}-{port + a.step - 1} (slot {slot})")
        for c in plan["commands"]:
            print(f"  $ {c}")
        if a.db:
            print(f"  create the database: createdb {db_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
