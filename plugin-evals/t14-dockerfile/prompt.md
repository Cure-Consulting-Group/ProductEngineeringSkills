---
description: 'Ported golden task (rules/docker.md standards). Result gate mirrors evals/tasks/t14-dockerfile/score.sh.'
tags: [infrastructure-scaffold, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Write a Dockerfile for this Node 20 Express API. I want a multi-stage build, the app running as a non-root user, and only production dependencies in the final image.
