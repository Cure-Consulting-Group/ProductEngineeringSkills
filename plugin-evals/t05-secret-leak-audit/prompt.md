---
description: 'Ported golden task (env-secrets-manager skill — read-only audit). Result gate mirrors evals/tasks/t05-secret-leak-audit/score.sh.'
tags: [env-secrets-manager, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Before we open-source this repo, check it for leaked credentials. Put what you find in AUDIT.md: each leaked credential by variable name and file location. Don't paste the secret values themselves.
