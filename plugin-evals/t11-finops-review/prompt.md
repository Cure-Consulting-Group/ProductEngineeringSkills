---
description: 'Ported golden task (finops skill — the post-T34-repair skill under test). Result gate mirrors evals/tasks/t11-finops-review/score.sh.'
tags: [finops, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Our Cloud Functions bill is way higher than it should be for what this does. Look at functions/index.js and write COSTS.md: what's overprovisioned, and the concrete values you'd change it to and why.
