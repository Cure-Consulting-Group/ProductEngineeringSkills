---
description: 'Ported golden task (firebase-architect skill; firebase-security-auditor standards). Result gate mirrors evals/tasks/t06-firestore-rules/score.sh.'
tags: [firebase-architect, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Write firestore.rules for our users collection: a signed-in user can read and write only their own document (the doc id is their uid), and everything else is denied by default.
