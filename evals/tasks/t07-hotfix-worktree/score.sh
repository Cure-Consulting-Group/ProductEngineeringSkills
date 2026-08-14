#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f HOTFIX.md ] && grep -q "git worktree add" HOTFIX.md && grep -qE "git worktree (remove|prune)" HOTFIX.md && ! grep -q "git stash" HOTFIX.md
