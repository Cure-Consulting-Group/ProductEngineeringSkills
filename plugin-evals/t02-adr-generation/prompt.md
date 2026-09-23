---
description: 'Ported golden task (statledger docs/adr practice; sdlc skill Step 4). Result gate mirrors evals/tasks/t02-adr-generation/score.sh.'
tags: [ported, sdlc]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

We picked Firestore over Postgres for our real-time basketball stats app and I want that decision on record. Write it up at docs/adr/001-firestore-vs-postgres.md in the usual ADR shape.
