---
description: 'Ported golden task (testing-strategy skill). Result gate mirrors evals/tasks/t08-test-strategy/score.sh.'
tags: [ported, testing-strategy]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Our Next.js 14 + Firebase app has basically no tests. Write TESTING.md: the test pyramid with actual ratios, which framework we use at each layer (unit, integration, e2e), and numeric coverage targets.
