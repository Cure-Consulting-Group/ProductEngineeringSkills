---
description: 'Ported golden task (T34 / commit 845c62a — real defect shipped for a month). Result gate mirrors evals/tasks/t01-fix-dangling-gather/score.sh.'
tags: [ported, sdlc]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

BROKEN_SKILL.md got mangled by a bad migration: the 'Additionally gather (domain-specific):' header has no bullet list under it, and a line of body prose got spliced in where the bullets should be. Fix it in place: add 2-4 sensible domain-specific context-gathering bullets directly after that header, and don't lose any of the existing text.
