---
description: 'Ported golden task (design-studio skill (Illustrator Automation)). Result gate mirrors evals/tasks/t18-illustrator-production/score.sh.'
tags: [design-studio, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Write an Adobe Illustrator ExtendScript 'build_logo.jsx' for a luxury hospitality brand named 'Vespera'.
The script must:
1. Initialize a print document using DocumentColorMode.CMYK.
2. Create 4 named artboards: '01_Primary_Horizontal', '02_Stacked_Vertical', '03_Submark_Icon', and '04_Monochrome_1Bit'.
3. Establish an organized layer hierarchy with: '[Guides]', '[Artwork]', '[Typography]', and '[Background]'.
4. Register at least two Spot Color swatches using doc.spots.add() with CMYK color values.
5. Save the resulting document as a native .ai file.
