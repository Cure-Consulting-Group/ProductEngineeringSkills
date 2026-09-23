---
description: 'Routing (T53): natural phrasing must reach rag-architect from its description alone.'
tags: [rag-architect, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

Our docs chatbot keeps answering from the wrong product version. We chunk PDFs into 1,000-token pieces and take the top 5 by cosine similarity. How do we fix retrieval?
