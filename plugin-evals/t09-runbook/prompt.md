---
description: 'Ported golden task (incident-response skill; runbook output style). Result gate mirrors evals/tasks/t09-runbook/score.sh.'
tags: [incident-response, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Firestore reads spiked 10x overnight and it's burning our budget. Write RUNBOOK.md for this situation: numbered diagnostic steps with the exact commands, a decision tree for mitigation, and who to escalate to at what time thresholds.
