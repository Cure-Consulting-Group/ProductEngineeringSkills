# web-design-expert: scales and starter tokens

Exact values for `web-design-expert`. The rules that always apply are in SKILL.md; read this file when a spec needs a number, a token name, or the `@theme` starter. Tailwind v4 syntax (verified against tailwindcss.com docs, v4.3, 2026-09-23).

## Tailwind v4 `@theme` starter

```css
/* app/globals.css */
@import "tailwindcss";
@import "tw-animate-css";                          /* shadcn v4 default; replaces tailwindcss-animate */
@custom-variant dark (&:where(.dark, .dark *));    /* class-based dark mode */

/* Static design tokens → generate utilities (bg-brand-600, font-display, text-display-lg …) */
@theme {
  --font-sans: "Inter", system-ui, sans-serif;
  --font-display: "Cal Sans", "Inter", sans-serif;
  --color-brand-50:  oklch(0.97 0.02 250);
  --color-brand-600: oklch(0.55 0.20 255);
  --color-brand-700: oklch(0.48 0.19 257);
  --text-display-lg: clamp(2.5rem, 4vw + 1.25rem, 4rem);
  --text-display-lg--line-height: 1.1;
  --radius-card: 0.75rem;
  --ease-emphasized: cubic-bezier(0.2, 0, 0, 1);
}

/* Runtime-switchable semantic tokens (light/dark) */
:root {
  --surface: oklch(1 0 0);
  --surface-raised: oklch(0.985 0 0);
  --text-primary: oklch(0.21 0.02 265);
  --text-secondary: oklch(0.45 0.02 265);
  --border-default: oklch(0.92 0.01 265);
  --primary: var(--color-brand-600);
  --on-primary: oklch(1 0 0);
  --focus-ring: var(--color-brand-600);
}
.dark {
  --surface: oklch(0.15 0.01 265);
  --surface-raised: oklch(0.21 0.01 265);
  --text-primary: oklch(0.97 0 0);
  --text-secondary: oklch(0.72 0.01 265);
  --border-default: oklch(0.30 0.01 265);
  --primary: oklch(0.70 0.15 255);
  --on-primary: oklch(0.15 0.01 265);
}

/* Map semantic variables into utilities (bg-surface, text-text-primary, ring-focus …) */
@theme inline {
  --color-surface: var(--surface);
  --color-surface-raised: var(--surface-raised);
  --color-text-primary: var(--text-primary);
  --color-text-secondary: var(--text-secondary);
  --color-border-default: var(--border-default);
  --color-primary: var(--primary);
  --color-on-primary: var(--on-primary);
  --color-focus: var(--focus-ring);
}
```

The OKLCH values are illustrative — derive real ones from the brand palette and check contrast in both themes.

## Semantic color token set

| Group | Tokens |
|---|---|
| Surface | `surface`, `surface-raised`, `surface-overlay` |
| Text | `text-primary`, `text-secondary`, `text-tertiary`, `text-disabled`, `text-inverse` |
| Border | `border-default`, `border-strong`, `border-focus` |
| Action | `primary`, `primary-hover`, `primary-active`, `on-primary` |
| Status | `success`, `warning`, `error`, `info` (+ `on-*` for each) |

Component tokens reference these: `--button-primary-bg: var(--primary)`, `--card-bg: var(--surface-raised)`, `--input-border-focus: var(--border-focus)`.

## Breakpoints and layout

| Name | Min width | Context |
|---|---|---|
| (base) | 0 | Phones, portrait |
| sm | 640px | Large phones, landscape |
| md | 768px | Tablets, portrait |
| lg | 1024px | Tablets landscape, small laptops |
| xl | 1280px | Desktops |
| 2xl | 1536px | Large desktops |

Test widths: 320, 375, 390, 430, 768, 1024, 1280, 1440, 1920. Max content width 1280px (standard), 1440px (wide), 960px or 65–75ch (reading). Page gutter 16px mobile, 24–32px desktop. Fluid card grids: `grid-template-columns: repeat(auto-fit, minmax(<min>, 1fr))`.

## Type scale

| Token | Size | Usage |
|---|---|---|
| `text-xs` | 12px | Badges, fine print (minimum size) |
| `text-sm` | 14px | Captions, helper text |
| `text-base` | 16px | Body |
| `text-lg` | 18px | Lead paragraphs |
| `text-xl` | 20px | Card titles |
| `text-2xl` | 24px | Section headings |
| `text-3xl` | clamp(28px, 2vw + 20px, 36px) | Page headings |
| `text-4xl` | clamp(32px, 3vw + 20px, 48px) | Hero headings |
| `text-5xl` | clamp(40px, 4vw + 20px, 64px) | Display |
| `text-6xl` | clamp(48px, 5vw + 20px, 80px) | Large display |

Fluid `clamp()` values must include a `rem`/`px` term (as above) so browser zoom still scales them (WCAG 1.4.4).

## Spacing scale (4px base)

`0.5`=2 · `1`=4 · `1.5`=6 · `2`=8 · `3`=12 · `4`=16 · `5`=20 · `6`=24 · `8`=32 · `10`=40 · `12`=48 · `16`=64 · `20`=80 · `24`=96 (px). In v4 these come from the single `--spacing` base (0.25rem) multiplied by the utility number. Rhythm: section spacing > component spacing > element spacing.

## Radius, shadow, z-index

- Radius: `sm` 4 · `md` 8 · `lg` 12 · `xl` 16 · `2xl` 24 · `full` 9999 (px). Cards 8–12px.
- Shadows (light): `xs` 0 1px 2px rgb(0 0 0/.05) · `sm` 0 1px 3px rgb(0 0 0/.1) · `md` 0 4px 6px -1px rgb(0 0 0/.1) · `lg` 0 10px 15px -3px rgb(0 0 0/.1) · `xl` 0 20px 25px -5px rgb(0 0 0/.1). Elevation: page 0 → cards `sm` → dropdowns/tooltips `md` → modals/popovers `lg` → toasts `xl`. Dark mode: lighter surface + 1px border instead of shadow.
- z-index tokens: dropdown 10 · sticky 20 · overlay 40 · modal 50 · popover 60 · toast 70.

## Component sizes

| Component | Small | Default | Large |
|---|---|---|---|
| Button | h-8 (32px), text-sm, px-3 | h-10 (40px), text-sm, px-4 | h-12 (48px), text-base, px-6 |
| Input | — | h-10, px-3, text-base | h-12, px-4, text-lg |
| Modal max-width | 400px (confirm) | 560px (forms) | 768px (complex); full-screen on mobile |

Inputs use `text-base` (16px) on mobile — smaller sizes trigger iOS Safari zoom on focus.

## Motion tokens

Micro 100–200ms · standard 200–300ms · page 300–500ms. Easing: `ease-out` enter, `ease-in` exit, `cubic-bezier(0.2, 0, 0, 1)` emphasized enter. Reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
