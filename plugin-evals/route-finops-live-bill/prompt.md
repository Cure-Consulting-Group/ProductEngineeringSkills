---
description: 'Routing (T81 single owner): budgets and alerts on a live cloud bill belong to finops, not infrastructure-scaffold or burn-rate-tracker.'
tags: [finops, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

Our GCP bill went from about $1,800 last month to $6,400 this month, mostly Cloud Run and Vertex AI calls. Set us up with budgets and alerts so this can't sneak up on us again, and tell me where to cut.
