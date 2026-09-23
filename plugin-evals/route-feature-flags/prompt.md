---
description: 'Routing (T53): natural phrasing must reach feature-flags from its description alone.'
tags: [feature-flags, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

I want to roll the new checkout flow out to 5% of users, then 25%, then everyone, and be able to kill it instantly if conversion drops. We're on Firebase.
