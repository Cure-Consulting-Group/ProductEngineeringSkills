---
description: 'Ported golden task (design-studio skill). Result gate mirrors evals/tasks/t17-brand-vector-engineering/score.sh.'
tags: [design-studio, ported]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Create a complete brand identity and vector logo for 'ApexOrbit', an aerospace startup building autonomous satellite telemetry systems.
You must output:
1. 'logo.svg': A pure, semantic SVG logomark and wordmark. It must define viewBox="0 0 512 512", contain NO embedded raster images (<image> or data:image), and convert wordmark typography to vector paths.
2. 'tokens.json': W3C DTCG-compliant design tokens containing brand colors (primary, secondary, accent, neutral dark, neutral light), spacing scale (xs to 2xl), and border radii.
3. 'BRAND.md': Brand strategy document specifying the core brand archetype, visual rationale, clearspace rules, and mathematical contrast ratio calculations verifying WCAG compliance.
