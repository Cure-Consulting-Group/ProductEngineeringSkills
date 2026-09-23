---
description: 'Routing (T53): natural phrasing must reach llmops from its description alone.'
tags: [llmops, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

Our support-reply summarizer is live in production on Claude and people keep tweaking the prompt. How do I set things up so a prompt change can't ship if quality drops, and so I can see what each request costs?
