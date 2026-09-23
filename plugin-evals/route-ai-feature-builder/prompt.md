---
description: 'Routing (T53): natural phrasing must reach ai-feature-builder from its description alone.'
tags: [ai-feature-builder, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

Add a 'summarize this thread' button to our Next.js app. It should stream the summary from an LLM, fall back gracefully when the model call fails, and we need to be able to switch it off in production without a deploy.
