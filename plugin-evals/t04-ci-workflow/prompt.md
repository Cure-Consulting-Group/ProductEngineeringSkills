---
description: 'Ported golden task (ci-cd-pipeline skill; rules/cicd.md). Result gate mirrors evals/tasks/t04-ci-workflow/score.sh.'
tags: [ci-cd-pipeline, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Set up CI for this Node 20 project: .github/workflows/test.yml should run npm test on every pull request and cache dependencies. Lock it down the way a security reviewer would want.
