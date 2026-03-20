# Platform Token Translation Tables

Maps DESIGN.md tokens to platform-specific implementations for Android Compose, React/Web (Tailwind + shadcn), and raw CSS.

## Color Tokens — Core

| DESIGN.md Token | Material 3 (Compose) | Tailwind/shadcn | CSS Custom Property | HIG (SwiftUI) |
|---|---|---|---|---|
| `primary` | `colorScheme.primary` | `bg-primary` | `var(--color-primary)` | `.tint` (app accent) |
| `on-primary` | `colorScheme.onPrimary` | `text-primary-foreground` | `var(--color-on-primary)` | `.white` on tint |
| `secondary` | `colorScheme.secondary` | `bg-secondary` | `var(--color-secondary)` | `.secondary` (system) |
| `on-secondary` | `colorScheme.onSecondary` | `text-secondary-foreground` | `var(--color-on-secondary)` | `.white` on secondary |
| `surface` | `colorScheme.surface` | `bg-background` | `var(--color-surface)` | `.systemBackground` |
| `on-surface` | `colorScheme.onSurface` | `text-foreground` | `var(--color-on-surface)` | `.label` |
| `surface-variant` | `colorScheme.surfaceVariant` | `bg-muted` | `var(--color-surface-variant)` | `.secondarySystemBackground` |
| `error` | `colorScheme.error` | `bg-destructive` | `var(--color-error)` | `.systemRed` |
| `on-error` | `colorScheme.onError` | `text-destructive-foreground` | `var(--color-on-error)` | `.white` on red |
| `outline` | `colorScheme.outline` | `border-border` | `var(--color-outline)` | `.separator` |

## Color Tokens — M3 Extended (Container System)

| DESIGN.md Token | Material 3 (Compose) | Tailwind/shadcn | CSS Custom Property |
|---|---|---|---|
| `primary-container` | `colorScheme.primaryContainer` | `bg-primary/10` | `var(--color-primary-container)` |
| `on-primary-container` | `colorScheme.onPrimaryContainer` | `text-primary` | `var(--color-on-primary-container)` |
| `secondary-container` | `colorScheme.secondaryContainer` | `bg-secondary/10` | `var(--color-secondary-container)` |
| `on-secondary-container` | `colorScheme.onSecondaryContainer` | `text-secondary` | `var(--color-on-secondary-container)` |
| `tertiary` | `colorScheme.tertiary` | `bg-accent` | `var(--color-tertiary)` |
| `tertiary-container` | `colorScheme.tertiaryContainer` | `bg-accent/10` | `var(--color-tertiary-container)` |
| `surface-container` | `colorScheme.surfaceContainer` | `bg-muted` | `var(--color-surface-container)` |
| `surface-container-high` | `colorScheme.surfaceContainerHigh` | `bg-muted/80` | `var(--color-surface-container-high)` |
| `surface-container-highest` | `colorScheme.surfaceContainerHighest` | `bg-card` | `var(--color-surface-container-highest)` |
| `surface-container-low` | `colorScheme.surfaceContainerLow` | `bg-background/95` | `var(--color-surface-container-low)` |
| `surface-dim` | `colorScheme.surfaceDim` | `bg-muted/60` | `var(--color-surface-dim)` |
| `surface-bright` | `colorScheme.surfaceBright` | `bg-background` | `var(--color-surface-bright)` |
| `inverse-surface` | `colorScheme.inverseSurface` | `bg-foreground` | `var(--color-inverse-surface)` |
| `inverse-on-surface` | `colorScheme.inverseOnSurface` | `text-background` | `var(--color-inverse-on-surface)` |
| `inverse-primary` | `colorScheme.inversePrimary` | `text-primary-foreground` | `var(--color-inverse-primary)` |
| `outline-variant` | `colorScheme.outlineVariant` | `border-border/50` | `var(--color-outline-variant)` |
| `scrim` | `colorScheme.scrim` | `bg-black/50` | `var(--color-scrim)` |

## Color Tokens — HIG System Colors

| HIG Role | SwiftUI Color | Light | Dark | DESIGN.md Equivalent |
|---|---|---|---|---|
| Primary label | `.label` | `#000000` | `#FFFFFF` | `on-surface` |
| Secondary label | `.secondaryLabel` | `#3C3C43` (60%) | `#EBEBF5` (60%) | `on-surface` (secondary) |
| Tertiary label | `.tertiaryLabel` | `#3C3C43` (30%) | `#EBEBF5` (30%) | `on-surface` (tertiary) |
| System background | `.systemBackground` | `#FFFFFF` | `#000000` | `surface` |
| Secondary background | `.secondarySystemBackground` | `#F2F2F7` | `#1C1C1E` | `surface-variant` |
| Tertiary background | `.tertiarySystemBackground` | `#FFFFFF` | `#2C2C2E` | `surface-container` |
| Grouped background | `.systemGroupedBackground` | `#F2F2F7` | `#000000` | `surface` (grouped) |
| System blue | `.systemBlue` | `#007AFF` | `#0A84FF` | `info` |
| System green | `.systemGreen` | `#34C759` | `#30D158` | `success` |
| System red | `.systemRed` | `#FF3B30` | `#FF453A` | `error` |
| System yellow | `.systemYellow` | `#FFCC00` | `#FFD60A` | `warning` |
| System orange | `.systemOrange` | `#FF9500` | `#FF9F0A` | `warning` (alt) |
| Separator | `.separator` | `#3C3C43` (29%) | `#545458` (65%) | `outline` |
| Fill | `.systemFill` | `#787880` (20%) | `#787880` (36%) | `surface-variant` |

### Android Compose Example

```kotlin
// Color.kt — Generated from DESIGN.md
val VendlyPrimary = Color(0xFF00A859)
val VendlyOnPrimary = Color(0xFFFFFFFF)
val VendlySurface = Color(0xFFF8FAF9)
val VendlyOnSurface = Color(0xFF1A1A2E)

val VendlyLightColorScheme = lightColorScheme(
    primary = VendlyPrimary,
    onPrimary = VendlyOnPrimary,
    surface = VendlySurface,
    onSurface = VendlyOnSurface,
    // ...
)
```

### Tailwind/shadcn Example

```css
/* globals.css — Generated from DESIGN.md */
@layer base {
  :root {
    --primary: 153 100% 33%;        /* #00A859 in HSL */
    --primary-foreground: 0 0% 100%;
    --background: 150 20% 97%;      /* #F8FAF9 */
    --foreground: 240 25% 13%;      /* #1A1A2E */
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 100%;
    --border: 150 10% 85%;
    --ring: 153 100% 33%;
  }
}
```

### Raw CSS Example

```css
:root {
  --color-primary: #00A859;
  --color-on-primary: #FFFFFF;
  --color-surface: #F8FAF9;
  --color-on-surface: #1A1A2E;
  --color-error: #EF4444;
  --color-on-error: #FFFFFF;
  --color-outline: #D1D5DB;
}
```

---

## Typography Tokens

| DESIGN.md Token | Material 3 (Compose) | Tailwind Class | CSS |
|---|---|---|---|
| `display-large` | `MaterialTheme.typography.displayLarge` | `text-6xl font-bold` | `font-size: 3.75rem; font-weight: 700` |
| `display-medium` | `MaterialTheme.typography.displayMedium` | `text-5xl font-bold` | `font-size: 3rem; font-weight: 700` |
| `headline-large` | `MaterialTheme.typography.headlineLarge` | `text-3xl font-semibold` | `font-size: 1.875rem; font-weight: 600` |
| `headline-medium` | `MaterialTheme.typography.headlineMedium` | `text-2xl font-semibold` | `font-size: 1.5rem; font-weight: 600` |
| `body-large` | `MaterialTheme.typography.bodyLarge` | `text-base font-normal` | `font-size: 1rem; font-weight: 400` |
| `body-medium` | `MaterialTheme.typography.bodyMedium` | `text-sm font-normal` | `font-size: 0.875rem; font-weight: 400` |
| `label-large` | `MaterialTheme.typography.labelLarge` | `text-sm font-medium` | `font-size: 0.875rem; font-weight: 500` |
| `label-medium` | `MaterialTheme.typography.labelMedium` | `text-xs font-medium` | `font-size: 0.75rem; font-weight: 500` |

### Android Compose Example

```kotlin
// Typography.kt
val VendlyTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 57.sp,
        lineHeight = 64.sp,
    ),
    headlineLarge = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 32.sp,
        lineHeight = 40.sp,
    ),
    bodyLarge = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
    ),
    labelLarge = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
    ),
)
```

### Tailwind Config Example

```typescript
// tailwind.config.ts
export default {
  theme: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      display: ['Bebas Neue', 'Inter', 'sans-serif'], // The Initiated
    },
    fontSize: {
      'display-lg': ['3.75rem', { lineHeight: '1.1', fontWeight: '700' }],
      'display-md': ['3rem', { lineHeight: '1.15', fontWeight: '700' }],
      'headline-lg': ['1.875rem', { lineHeight: '1.3', fontWeight: '600' }],
      'headline-md': ['1.5rem', { lineHeight: '1.35', fontWeight: '600' }],
      'body-lg': ['1rem', { lineHeight: '1.5', fontWeight: '400' }],
      'body-md': ['0.875rem', { lineHeight: '1.5', fontWeight: '400' }],
      'label-lg': ['0.875rem', { lineHeight: '1.4', fontWeight: '500' }],
      'label-md': ['0.75rem', { lineHeight: '1.4', fontWeight: '500' }],
    },
  },
}
```

---

## Spacing Tokens

| DESIGN.md Token | Compose | Tailwind | CSS |
|---|---|---|---|
| `xs` (4px) | `4.dp` | `p-1` / `gap-1` | `var(--spacing-xs, 4px)` |
| `sm` (8px) | `8.dp` | `p-2` / `gap-2` | `var(--spacing-sm, 8px)` |
| `md` (16px) | `16.dp` | `p-4` / `gap-4` | `var(--spacing-md, 16px)` |
| `lg` (24px) | `24.dp` | `p-6` / `gap-6` | `var(--spacing-lg, 24px)` |
| `xl` (32px) | `32.dp` | `p-8` / `gap-8` | `var(--spacing-xl, 32px)` |
| `2xl` (48px) | `48.dp` | `p-12` / `gap-12` | `var(--spacing-2xl, 48px)` |

---

## Elevation Tokens

| DESIGN.md Level | Compose | Tailwind | CSS |
|---|---|---|---|
| `elevation-0` | `elevation = 0.dp` | `shadow-none` | `box-shadow: none` |
| `elevation-1` | `elevation = 1.dp` | `shadow-sm` | `box-shadow: 0 1px 2px rgba(0,0,0,0.05)` |
| `elevation-2` | `elevation = 3.dp` | `shadow` | `box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)` |
| `elevation-3` | `elevation = 6.dp` | `shadow-md` | `box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)` |
| `elevation-4` | `elevation = 8.dp` | `shadow-lg` | `box-shadow: 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)` |
| `elevation-5` | `elevation = 12.dp` | `shadow-xl` | `box-shadow: 0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04)` |

---

## Component Default Tokens

| DESIGN.md Token | Compose | Tailwind | CSS |
|---|---|---|---|
| `button-radius` | `RoundedCornerShape(8.dp)` | `rounded-lg` | `border-radius: 8px` |
| `input-height` | `Modifier.height(48.dp)` | `h-12` | `height: 48px` |
| `card-rounding` | `RoundedCornerShape(12.dp)` | `rounded-xl` | `border-radius: 12px` |
| `icon-size` | `24.dp` | `w-6 h-6` | `width: 24px; height: 24px` |
| `touch-target` | `Modifier.size(48.dp)` | `min-w-[48px] min-h-[48px]` | `min-width: 48px; min-height: 48px` |

---

## Motion Tokens

| DESIGN.md Token | Compose | CSS/Tailwind |
|---|---|---|
| `duration-fast` (150ms) | `tween(durationMillis = 150)` | `duration-150` / `transition-duration: 150ms` |
| `duration-medium` (300ms) | `tween(durationMillis = 300)` | `duration-300` / `transition-duration: 300ms` |
| `duration-slow` (500ms) | `tween(durationMillis = 500)` | `duration-500` / `transition-duration: 500ms` |
| `easing-standard` | `FastOutSlowInEasing` | `ease-in-out` / `cubic-bezier(0.4, 0, 0.2, 1)` |
| `easing-decelerate` | `LinearOutSlowInEasing` | `ease-out` / `cubic-bezier(0, 0, 0.2, 1)` |
| `easing-accelerate` | `FastOutLinearInEasing` | `ease-in` / `cubic-bezier(0.4, 0, 1, 1)` |
