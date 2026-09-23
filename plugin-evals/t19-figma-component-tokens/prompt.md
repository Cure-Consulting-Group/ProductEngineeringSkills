---
description: 'Ported golden task (design-studio skill (Figma Architecture)). Result gate mirrors evals/tasks/t19-figma-component-tokens/score.sh.'
tags: [design-studio, ported]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Create a production-grade Figma design system specification and W3C design tokens for a fintech application named 'Vaultix'.
You must output:
1. 'tokens.json': W3C DTCG-compliant tokens with color definitions for both light and dark themes (background, surface, text, primary) plus a spacing scale (4px, 8px, 16px, 24px, 32px).
2. 'FIGMA_SPEC.md': Detailed Figma component specification detailing Auto-Layout frame hierarchy, component variants (Type: Primary/Stacked/Icon; Theme: Light/Dark), and instructions for syncing to Figma Variables via REST API.
