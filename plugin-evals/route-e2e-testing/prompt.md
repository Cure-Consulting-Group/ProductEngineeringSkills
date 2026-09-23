---
description: 'Routing (T53): natural phrasing must reach e2e-testing from its description alone.'
tags: [e2e-testing, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

Write end-to-end tests for our Next.js signup -> onboarding -> first project flow. The ones we had kept flaking in CI so we deleted them.
