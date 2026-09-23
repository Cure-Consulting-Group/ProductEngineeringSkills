---
description: 'Ported golden task (design-studio skill (UX architecture)). Result gate mirrors evals/tasks/t20-product-ux-architecture/score.sh.'
tags: [design-studio, ported]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Design the iOS app 'Pipeline' for recruiters who review candidates between meetings. Deliver, in the working directory: design/spec.json (a wireframe.py spec with at least 3 screens, each with fixed/sticky regions and notes covering empty, error, and long-content states, plus flows between them), design/wireframes/ rendered from it (screens/*.svg, flow.svg, inventory.md), design/decisions.md with at least three 'Decision:' / 'Reason:' pairs covering navigation model and scrolling, and design/states.md with a state matrix that covers empty, loading, error, offline, and long content for the candidate list. Utility register; no marketing hero.
