# android-design-expert: M3 token lookup tables

> Exact values for the `android-design-expert` skill. Read when a spec needs a specific tone,
> type size, shape, spacing, motion token, or widget size. The rules and decisions live in SKILL.md.
> Baseline M3 values; Expressive adds spring motion and extra shapes — take those from the
> current Compose Material 3 API, not from this file.

## Color: key colors and tone mapping

A source color generates **five key colors** — primary, secondary, tertiary, neutral, neutral
variant — each expanded into a tonal palette (tones 0–100). **Error** is a sixth, system-defined
palette, not derived from the source.

| Role | Light tone | Dark tone |
|---|---|---|
| primary / secondary / tertiary / error | 40 | 80 |
| on-primary (etc.) | 100 | 20 |
| primaryContainer (etc.) | 90 | 30 |
| onPrimaryContainer (etc.) | 10 | 90 |
| surface | 98 | 6 |
| onSurface | 10 | 90 |
| onSurfaceVariant | 30 | 80 |
| surfaceContainerLowest | 100 | 4 |
| surfaceContainerLow | 96 | 10 |
| surfaceContainer | 94 | 12 |
| surfaceContainerHigh | 92 | 17 |
| surfaceContainerHighest | 90 | 22 |
| outline | 50 | 60 |
| outlineVariant | 80 | 30 |
| inverseSurface | 20 | 90 |
| inverseOnSurface | 95 | 20 |
| inversePrimary | 80 | 40 |
| scrim / shadow | 0 | 0 |

Card fills: Filled → `surfaceContainerHighest`; Elevated → `surfaceContainerLow` + level 1;
Outlined → `surface` + `outlineVariant` border. Filled text field container → `surfaceContainerHighest`.

## Type scale (sp; weight 400 unless noted)

| Role | Size / line height | Typical use |
|---|---|---|
| displayLarge | 57 / 64 | Hero numbers |
| displayMedium | 45 / 52 | |
| displaySmall | 36 / 44 | |
| headlineLarge | 32 / 40 | Screen titles |
| headlineMedium | 28 / 36 | Section headers |
| headlineSmall | 24 / 32 | |
| titleLarge | 22 / 28 | Top app bar title |
| titleMedium | 16 / 24, 500 | Card titles |
| titleSmall | 14 / 20, 500 | Tab labels |
| bodyLarge | 16 / 24 | Body |
| bodyMedium | 14 / 20 | Secondary body |
| bodySmall | 12 / 16 | Captions |
| labelLarge | 14 / 20, 500 | Buttons |
| labelMedium | 12 / 16, 500 | Nav labels |
| labelSmall | 11 / 16, 500 | Smallest labels |

## Shape scale

None 0dp · Extra small 4dp (chips) · Small 8dp · Medium 12dp (cards) ·
Large 16dp (FAB, navigation drawer) · Extra large 28dp (dialogs, bottom-sheet top corners,
large FAB) · Full (pill/circle).

## Spacing and grid

4dp base: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96.
Margins: Compact 16dp · Medium 24dp · Expanded+ 24dp. Columns: Compact 4 · Medium 8 · Expanded+ 12.
Padding: cards 16dp · list items 16dp horizontal, 8–12dp vertical · dialogs 24dp.
Touch target ≥ 48×48dp. Drag handle 4×32dp, `onSurfaceVariant`.
FAB sizes: small 40dp · FAB 56dp · large 96dp.

## Motion tokens (baseline M3)

| Easing | Cubic bezier | Use |
|---|---|---|
| emphasized | (0.2, 0, 0, 1) | Primary transitions |
| emphasizedDecelerate | (0.05, 0.7, 0.1, 1) | Enter |
| emphasizedAccelerate | (0.3, 0, 0.8, 0.15) | Exit |
| standard | (0.2, 0, 0, 1) | Small state changes |
| standardDecelerate | (0, 0, 0, 1) | Enter |
| standardAccelerate | (0.3, 0, 1, 1) | Exit |

Durations: Short 1–4 = 50/100/150/200ms · Medium 1–4 = 250/300/350/400ms ·
Long 1–4 = 450/500/550/600ms · Extra long 1–4 = 700/800/900/1000ms.
Transition patterns: container transform (list→detail), shared axis (spatial), fade through (tab
switch), fade (dialogs, menus). Gesture-driven motion uses `spring()`.

## Material Symbols

Styles: Outlined (default), Rounded, Sharp. Optical size 20/24/40/48dp. Weight 100–700 (default 400).
Fill 0 = inactive, 1 = active/selected. Grade −25 / 0 / 200. Decorative icons get no content
description; meaningful icons get one.

## Widgets (Glance)

Sizes in cells: small 2×1–3×1 · medium 2×2–4×2 · large 3×3–5×3. Corner radius is system-managed;
inner radius = system radius − padding. Padding 16dp. Periodic refresh via WorkManager (≥ 15 min).
Taps deep-link into the matching screen.
