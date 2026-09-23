---
description: 'Ported golden task (accessibility-audit skill (WCAG 2.2)). Result gate mirrors evals/tasks/t13-a11y-fixture/score.sh.'
tags: [accessibility-audit, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Check index.html against WCAG 2.2 and write A11Y.md listing each violation, the success criterion it breaks, and how to fix it.
