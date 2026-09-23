---
description: 'Ported golden task (git-worktree-manager skill, hotfix scenario). Result gate mirrors evals/tasks/t07-hotfix-worktree/score.sh.'
tags: [git-worktree-manager, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

I'm halfway through feat/big-refactor with a dirty working tree and production just broke — I need to hotfix off main right now. Write HOTFIX.md with the exact git commands to do it without stashing or switching my current branch, and how to clean up once the fix ships.
