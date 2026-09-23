---
description: 'Routing (T53): natural phrasing must reach test-accounts from its description alone.'
tags: [routing, test-accounts]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

QA keeps making random Gmail accounts to test signup and password reset on staging. Set us up with a proper set of test users we can reset between runs, and make sure none of it can ever touch prod.
