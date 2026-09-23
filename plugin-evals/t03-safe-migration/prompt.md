---
description: 'Ported golden task (rules/sql.md; migration-validator agent standards). Result gate mirrors evals/tasks/t03-safe-migration/score.sh.'
tags: [database-architect, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

I need a Postgres migration at migrations/001_add_email_verified.sql that adds an email_verified boolean (default false) to our users table, plus an index on it. The table has about 10M rows and this has to run on production during business hours without taking the app down.
