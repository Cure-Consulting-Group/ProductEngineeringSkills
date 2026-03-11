---
name: web-design-expert
description: "Expert web design guidance — responsive design, CSS architecture, design tokens, container queries, accessibility-first patterns, dark mode, and Tailwind/CSS implementation"
argument-hint: "[page-or-component-name]"
---

# Web Design Expert — Modern Web Design Systems

Deep expertise in modern web design: responsive layouts, CSS architecture, design tokens, component patterns, accessibility-first design, and performance-conscious UI. Every recommendation maps to production CSS/Tailwind implementation and follows WCAG 2.2 AA standards.

**Related skills**: `product-design` (cross-platform fundamentals), `nextjs-feature-scaffold` (code scaffolding), `accessibility-audit` (WCAG compliance)

## Step 1: Classify the Request

| Request | Action |
|---------|--------|
| Page design / layout | Design responsive page with breakpoint strategy |
| Component design | Spec component with all states, variants, and responsive behavior |
| Design system / tokens | Build token architecture with CSS custom properties |
| Navigation pattern | Design responsive nav (mobile menu, desktop nav, sidebar) |
| Typography system | Spec fluid type scale with responsive behavior |
| Color system / dark mode | Design semantic color scheme with dark mode |
| Spacing / grid system | Define spacing scale and responsive grid |
| Form design | Design accessible form patterns with validation |
| Animation / motion | Design performant CSS animations and transitions |
| Design-to-code handoff | Generate Tailwind/CSS implementation specs |
| Landing page / marketing | Design conversion-optimized page layouts |
| Dashboard / app UI | Design data-dense application interface |

## Step 2: Gather Context

1. **Project type** — Marketing site? SaaS app? E-commerce? Blog? Dashboard?
2. **Framework** — Next.js, React, Vue, Svelte, or static HTML?
3. **CSS approach** — Tailwind CSS (preferred), CSS Modules, vanilla CSS, styled-components?
4. **Responsive targets** — Mobile-first? Desktop-first? Specific breakpoints?
5. **Design system** — Building new? Extending existing? Using a library (shadcn/ui, Radix)?
6. **Brand constraints** — Colors, fonts, imagery style?
7. **Accessibility level** — WCAG AA (standard) or AAA (enhanced)?
8. **Performance budget** — Critical rendering path constraints, LCP targets?

## Step 3: Web Design Foundations (Always Apply)

### 3.1 Design Principles

```
Content First        — Design serves the content, not the other way around
Progressive Enhancement — Core functionality works without JS; enhanced with JS
Mobile First         — Design for the smallest viewport first, enhance upward
Accessible by Default — Semantic HTML, keyboard navigation, screen reader support
Performance Conscious — Every design decision impacts load time and interactivity
Consistent           — Systematic design tokens, not one-off values
```

### 3.2 Responsive Breakpoint System

#### Breakpoints
```
┌─────────────────┬──────────────┬───────────────────────────────────────┐
│ Name            │ Min Width    │ Devices / Context                     │
├─────────────────┼──────────────┼───────────────────────────────────────┤
│ (default)       │ 0            │ Small phones (portrait)               │
│ sm              │ 640px        │ Large phones (landscape)              │
│ md              │ 768px        │ Tablets (portrait)                    │
│ lg              │ 1024px       │ Tablets (landscape), small desktops   │
│ xl              │ 1280px       │ Standard desktops                     │
│ 2xl             │ 1536px       │ Large desktops                        │
└─────────────────┴──────────────┴───────────────────────────────────────┘

Tailwind: mobile-first → sm: md: lg: xl: 2xl: prefixes
CSS: @media (min-width: 768px) { }

Rules:
- Design mobile layout FIRST — this is the base, not the exception
- Use min-width media queries (mobile-first), never max-width
- Container queries (@container) for component-level responsiveness
- Content dictates breakpoints — if layout breaks, add a breakpoint
- Test at common widths: 375, 390, 428, 768, 1024, 1280, 1440, 1920
```

#### Container Queries
```css
/* Define containment context */
.card-grid {
  container-type: inline-size;
  container-name: card-grid;
}

/* Respond to container width, not viewport */
@container card-grid (min-width: 400px) {
  .card { flex-direction: row; }
}
@container card-grid (min-width: 700px) {
  .card { grid-template-columns: 1fr 1fr; }
}

/* Tailwind (v3.3+): @container and @[min-width] */
/* <div class="@container"> */
/* <div class="@md:flex-row @lg:grid-cols-2"> */

Use container queries when:
- Component is reused at different sizes in different layouts
- Sidebar/main content changes component layout
- Card grids need to adapt to available space, not viewport
```

#### Layout Patterns
```
Max content width:     1280px (standard), 1440px (wide), 960px (reading)
Content measure:       65-75ch for body text (optimal readability)
Minimum viewport:      320px — all content must be usable at 320px CSS width
Page margin (mobile):  16px (1rem)
Page margin (desktop): 24-32px (1.5-2rem) or auto-centered with max-width

Layout strategies:
  CSS Grid:    Page-level layout, complex 2D arrangements
  Flexbox:     Component-level layout, 1D alignment
  Auto layout: gap + flex-wrap for fluid component grids
  Subgrid:     Aligning child elements to parent grid tracks

Grid patterns:
  12-column grid (desktop) → 4-column (tablet) → stack (mobile)
  Use grid-template-columns: repeat(auto-fit, minmax(min, 1fr)) for fluid grids
  Named grid areas for semantic layout: grid-template-areas
```

### 3.3 Typography System

#### Fluid Type Scale
```
Modular scale with fluid sizing using clamp():

┌──────────────────┬──────────────┬──────────────────────────────────────┐
│ Token            │ Size Range   │ Usage                                │
├──────────────────┼──────────────┼──────────────────────────────────────┤
│ --text-xs        │ 12px         │ Badges, fine print, legal text       │
│ --text-sm        │ 14px         │ Captions, metadata, helper text      │
│ --text-base      │ 16px         │ Body text (base)                     │
│ --text-lg        │ 18px         │ Lead paragraphs, emphasized body     │
│ --text-xl        │ 20px         │ Card titles, section labels          │
│ --text-2xl       │ 24px         │ Section headings                     │
│ --text-3xl       │ clamp(28px, 2vw + 20px, 36px) │ Page headings       │
│ --text-4xl       │ clamp(32px, 3vw + 20px, 48px) │ Hero headings       │
│ --text-5xl       │ clamp(40px, 4vw + 20px, 64px) │ Display text        │
│ --text-6xl       │ clamp(48px, 5vw + 20px, 80px) │ Large display       │
└──────────────────┴──────────────┴──────────────────────────────────────┘

Rules:
- Base font size: 16px (1rem) — never change the root font size
- Body text: 16-18px, line-height 1.5-1.6
- Headings: line-height 1.1-1.3
- Measure (line length): max-width: 65ch for body text containers
- Use rem for font sizes, em for spacing relative to text size
- Font loading: font-display: swap for body, optional for display fonts
- System font stack fallback:
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
               Roboto, "Helvetica Neue", Arial, sans-serif;
- Variable fonts: use font-variation-settings for fine weight/width control
- Never use font sizes below 12px (unreadable on mobile)
- Truncation: text-overflow: ellipsis + overflow: hidden + white-space: nowrap
  (single line) or -webkit-line-clamp for multi-line
```

#### Font Loading Strategy
```css
/* Preload critical fonts */
<link rel="preload" href="/fonts/brand.woff2" as="font" type="font/woff2" crossorigin>

/* Font face with subsetting */
@font-face {
  font-family: 'Brand';
  src: url('/fonts/brand.woff2') format('woff2');
  font-weight: 100 900;  /* Variable font range */
  font-display: swap;    /* Show fallback immediately, swap when loaded */
  unicode-range: U+0000-00FF; /* Latin subset */
}

/* Size-adjust for reduced layout shift */
@font-face {
  font-family: 'Brand Fallback';
  src: local('Arial');
  size-adjust: 105%;
  ascent-override: 95%;
  descent-override: 22%;
  line-gap-override: 0%;
}
```

### 3.4 Color System

#### Design Token Architecture
```
Layer 1 — Primitive tokens (raw values):
  --color-blue-50: #eff6ff;
  --color-blue-100: #dbeafe;
  ...
  --color-blue-900: #1e3a5f;
  --color-blue-950: #0f172a;

Layer 2 — Semantic tokens (purpose-mapped):
  --color-primary: var(--color-blue-600);
  --color-primary-hover: var(--color-blue-700);
  --color-primary-active: var(--color-blue-800);
  --color-on-primary: var(--color-white);

  --color-surface: var(--color-white);
  --color-surface-raised: var(--color-gray-50);
  --color-surface-overlay: var(--color-gray-100);

  --color-text-primary: var(--color-gray-900);
  --color-text-secondary: var(--color-gray-600);
  --color-text-tertiary: var(--color-gray-400);
  --color-text-disabled: var(--color-gray-300);
  --color-text-inverse: var(--color-white);

  --color-border-default: var(--color-gray-200);
  --color-border-strong: var(--color-gray-300);
  --color-border-focus: var(--color-blue-500);

  --color-success: var(--color-green-600);
  --color-warning: var(--color-amber-500);
  --color-error: var(--color-red-600);
  --color-info: var(--color-blue-600);

Layer 3 — Component tokens (component-specific):
  --button-primary-bg: var(--color-primary);
  --button-primary-text: var(--color-on-primary);
  --button-primary-hover-bg: var(--color-primary-hover);
  --card-bg: var(--color-surface-raised);
  --card-border: var(--color-border-default);
  --input-border: var(--color-border-default);
  --input-border-focus: var(--color-border-focus);
```

#### Dark Mode
```css
/* System preference detection */
@media (prefers-color-scheme: dark) {
  :root {
    --color-surface: var(--color-gray-950);
    --color-surface-raised: var(--color-gray-900);
    --color-surface-overlay: var(--color-gray-800);
    --color-text-primary: var(--color-gray-50);
    --color-text-secondary: var(--color-gray-400);
    --color-text-tertiary: var(--color-gray-500);
    --color-border-default: var(--color-gray-800);
    --color-border-strong: var(--color-gray-700);
    --color-primary: var(--color-blue-400);
    --color-primary-hover: var(--color-blue-300);
    --color-on-primary: var(--color-gray-950);
  }
}

/* Manual toggle with class */
[data-theme="dark"] { /* same overrides */ }

/* Tailwind: dark: prefix with class strategy */
/* tailwind.config: darkMode: 'class' */

Rules:
- Dark mode is NOT color inversion — redesign surface hierarchy
- Light mode: white/light gray surfaces, dark text
- Dark mode: dark gray surfaces (NOT pure black for most elements), light text
- Pure black (#000) only for OLED-optimized backgrounds (user preference)
- Reduce image brightness in dark mode: filter: brightness(0.9)
- Shadows: increase opacity in dark mode or replace with border/outline
- Charts/graphs: adjust colors for dark backgrounds, increase line weight
- Test contrast ratios in BOTH modes
- Provide a toggle — never only auto-detect
- Persist user preference in localStorage, respect system preference as default
```

### 3.5 Spacing System

```
4px base unit, 8px macro grid:

┌─────────────┬──────────┬──────────────────────────────────────────┐
│ Token        │ Value    │ Usage                                    │
├─────────────┼──────────┼──────────────────────────────────────────┤
│ --space-0.5  │ 2px      │ Hairline gaps, optical adjustments       │
│ --space-1    │ 4px      │ Tight spacing, icon-to-text gap          │
│ --space-1.5  │ 6px      │ Compact component padding                │
│ --space-2    │ 8px      │ Default component gap                    │
│ --space-3    │ 12px     │ Component internal padding               │
│ --space-4    │ 16px     │ Section padding, card padding            │
│ --space-5    │ 20px     │ Comfortable component padding            │
│ --space-6    │ 24px     │ Section gaps, generous padding           │
│ --space-8    │ 32px     │ Large section spacing                    │
│ --space-10   │ 40px     │ Section separation                       │
│ --space-12   │ 48px     │ Large section separation                 │
│ --space-16   │ 64px     │ Page section spacing                     │
│ --space-20   │ 80px     │ Major page divisions                     │
│ --space-24   │ 96px     │ Hero spacing                             │
└─────────────┴──────────┴──────────────────────────────────────────┘

Rules:
- Use spacing tokens — never arbitrary pixel values
- gap property for flex/grid spacing (not margin on children)
- Consistent vertical rhythm: section spacing > component spacing > element spacing
- Padding: use the same token for all sides unless layout demands asymmetry
- Mobile padding: 16px page margin minimum
- Desktop padding: 24-32px page margin, or centered with max-width
```

### 3.6 Component Patterns

#### Buttons
```
Hierarchy (ONE primary per view):
  Primary:    Filled background, high contrast text. Main CTA
  Secondary:  Outlined or subtle fill. Supporting action
  Tertiary:   Text-only or ghost. Low emphasis action
  Destructive: Red/error variant. Requires confirmation for irreversible actions
  Icon-only:  Square, with tooltip + aria-label. Toolbar actions

Sizes:
  Small:   h-8 (32px), text-sm, px-3
  Default: h-10 (40px), text-sm, px-4
  Large:   h-12 (48px), text-base, px-6

States: default, hover, focus-visible, active, disabled, loading
  Focus: 2px ring with 2px offset, --color-border-focus
  Disabled: opacity-50, cursor-not-allowed, pointer-events-none
  Loading: spinner replaces text, same dimensions, disabled

Rules:
  - Minimum touch target: 44×44px on mobile (can have smaller visual size with padding)
  - Button labels: use verbs ("Save changes", "Create account")
  - Icon + label: icon leading, 8px gap
  - Full-width buttons: mobile only, at bottom of forms
  - Never use color alone — pair with text labels
  - Focus indicator: MUST be visible (no outline: none without replacement)
```

#### Cards
```
Anatomy:
  Media (optional)  → Image, video, or illustration at top
  Header            → Title + subtitle + optional action
  Body              → Content text, data, or nested components
  Footer (optional) → Actions or metadata

Variants:
  Default:    border + subtle background
  Elevated:   box-shadow, no border
  Interactive: clickable with hover state + cursor: pointer
  Selected:   primary border or background tint

Rules:
  - Clickable cards: entire card is the link (wrap in <a> or use onClick)
  - Do NOT nest links inside clickable cards (nested interactive elements)
  - Padding: 16-24px internal
  - Border radius: 8-12px (--radius-md to --radius-lg)
  - Card grids: use CSS Grid with auto-fit/auto-fill for responsive layouts
  - Loading: skeleton placeholders matching content shape
```

#### Forms
```
Layout:
  - Single column for most forms — never side-by-side inputs on mobile
  - Group related fields with <fieldset> and <legend>
  - Labels ABOVE inputs (not beside, not placeholder-only)
  - Required indicator: asterisk (*) after label, explain convention at top of form
  - Helper text: below input, before error message position
  - Error messages: below input, red text with error icon, associated via aria-describedby

Input sizing:
  Default:  h-10 (40px), px-3, text-base
  Large:    h-12 (48px), px-4, text-lg

Validation:
  - Validate on blur (field level) + on submit (form level)
  - Show inline errors immediately after blur validation fails
  - Show success checkmark for validated fields (optional)
  - Error state: red border, red error icon, descriptive error message
  - Disable submit until required fields are valid (or show all errors on submit)
  - Use native input types: type="email", type="tel", type="url", inputmode="numeric"
  - Autocomplete: always specify autocomplete attribute for known fields

Accessibility:
  - <label for="id"> on every input — NEVER placeholder-only
  - aria-describedby pointing to helper text and error message elements
  - aria-invalid="true" on fields with validation errors
  - aria-required="true" on required fields
  - Fieldset + legend for radio/checkbox groups
  - Error summary at top of form for screen readers (role="alert")
```

#### Navigation
```
Mobile (< 768px):
  - Hamburger menu → slide-out drawer or full-screen overlay
  - Bottom navigation bar for apps (3-5 items max)
  - Hamburger icon: 44×44px touch target, aria-label="Open menu"
  - Menu: focus trap, close on Escape, return focus to trigger

Desktop (>= 768px):
  - Horizontal navigation bar (persistent)
  - Mega menu for complex site structures (hover + click accessible)
  - Sidebar navigation for dashboards and admin panels

Breadcrumbs:
  - Use <nav aria-label="Breadcrumb"> with <ol>
  - Current page: aria-current="page"
  - Separator: CSS pseudo-element (not a link)

Skip link:
  - FIRST focusable element on every page
  - "Skip to main content" → links to <main id="main-content">
  - Visually hidden until focused: sr-only + focus:not-sr-only
  - Required for WCAG 2.4.1

Tab navigation:
  - role="tablist", role="tab", role="tabpanel"
  - Arrow keys to move between tabs (not Tab key)
  - Active tab: aria-selected="true"
  - Tab panel: aria-labelledby pointing to its tab
```

#### Modals / Dialogs
```
Implementation:
  - Use <dialog> element (native) or aria-modal="true" + role="dialog"
  - Focus trap: tab cycles within modal only
  - Close: Escape key, close button, click backdrop (non-critical modals)
  - On open: focus first focusable element (or heading)
  - On close: return focus to trigger element
  - Backdrop: semi-transparent overlay, pointer-events to dismiss or block

Sizing:
  Small:    max-width: 400px (confirmations)
  Medium:   max-width: 560px (forms, content)
  Large:    max-width: 768px (complex content)
  Full:     100vw/100vh minus margins (mobile)

Rules:
  - Confirm destructive actions with explicit modal ("Delete this item?")
  - Modal title: aria-labelledby pointing to heading
  - Description: aria-describedby pointing to body text
  - Never stack modals (modal opening another modal)
  - Prevent body scroll when modal is open (overflow: hidden on body)
```

### 3.7 Animation and Motion

#### Performance-First Animation
```
Animatable properties (GPU-accelerated, 60fps):
  ✓ transform (translate, scale, rotate)
  ✓ opacity
  ✓ filter (blur, brightness — use sparingly)

Avoid animating (triggers layout/paint):
  ✗ width, height
  ✗ top, left, right, bottom
  ✗ margin, padding
  ✗ border-width
  ✗ font-size

Timing:
  Micro interactions:  100-200ms (hover, focus, toggle)
  Standard transitions: 200-300ms (expand, collapse, slide)
  Page transitions:    300-500ms (route changes, major state changes)
  Complex animations:  500-1000ms (onboarding, illustrations)

Easing:
  ease-out:     Enter animations (element appearing)
  ease-in:      Exit animations (element leaving)
  ease-in-out:  State changes, size transitions
  spring:       User-gesture-driven (drag, swipe) — use CSS spring() or JS

  Custom cubic-bezier:
    Subtle:     cubic-bezier(0.4, 0, 0.2, 1)     — Material standard
    Expressive: cubic-bezier(0.2, 0, 0, 1)        — Emphasized entrance
    Bounce:     cubic-bezier(0.34, 1.56, 0.64, 1) — Playful overshoot
```

#### Motion Rules
```css
/* ALWAYS respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Progressive enhancement: add motion, don't remove it */
@media (prefers-reduced-motion: no-preference) {
  .card {
    transition: transform 200ms ease-out, box-shadow 200ms ease-out;
  }
  .card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
}
```

#### View Transitions API
```css
/* Page transitions (supported browsers) */
@view-transition {
  navigation: auto;
}

::view-transition-old(root) {
  animation: fade-out 200ms ease-in;
}
::view-transition-new(root) {
  animation: fade-in 200ms ease-out;
}

/* Element transitions */
.card { view-transition-name: card-hero; }
```

### 3.8 Shadows and Elevation

```
Shadow scale (light mode):
  --shadow-xs:  0 1px 2px 0 rgb(0 0 0 / 0.05)
  --shadow-sm:  0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)
  --shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)
  --shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)
  --shadow-xl:  0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25)

Elevation hierarchy:
  Level 0: Page background (no shadow)
  Level 1: Cards, raised sections (shadow-sm)
  Level 2: Dropdowns, tooltips (shadow-md)
  Level 3: Modals, popovers (shadow-lg)
  Level 4: Notifications, toasts (shadow-xl)

Border radius scale:
  --radius-none: 0
  --radius-sm:   4px
  --radius-md:   8px
  --radius-lg:   12px
  --radius-xl:   16px
  --radius-2xl:  24px
  --radius-full: 9999px (pill shape, circles)

Dark mode shadows:
  - Reduce shadow opacity or replace with borders
  - Use subtle borders (1px solid var(--color-border-default)) instead of shadows
  - Or increase shadow opacity significantly for visibility
```

### 3.9 Images and Media

```
Responsive images:
  <img
    srcset="image-400.webp 400w, image-800.webp 800w, image-1200.webp 1200w"
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
    src="image-800.webp"
    alt="Descriptive alt text"
    loading="lazy"
    decoding="async"
    width="800" height="600"
  >

Rules:
  - Use WebP/AVIF with JPEG/PNG fallback
  - Explicit width and height attributes to prevent layout shift (CLS)
  - loading="lazy" on below-the-fold images
  - loading="eager" on hero/LCP images
  - Aspect ratio: use aspect-ratio CSS property for responsive containers
  - Object-fit: object-fit: cover for thumbnail crops, contain for full images
  - Art direction: <picture> with <source media="..."> for different crops per breakpoint
  - Next.js: use <Image> component with fill prop or explicit dimensions
  - Decorative images: alt="" (empty string, not missing)
  - Meaningful images: descriptive alt text focused on function/content
```

### 3.10 Performance-Conscious Design

```
Core Web Vitals targets:
  LCP (Largest Contentful Paint):  < 2.5s
  INP (Interaction to Next Paint): < 200ms
  CLS (Cumulative Layout Shift):   < 0.1

Design decisions that impact performance:
  Fonts:     Max 2 font families, subset to used characters, preload critical
  Images:    Responsive srcset, lazy load below fold, WebP/AVIF format
  Animation: GPU-only properties (transform, opacity), respect reduced motion
  Layout:    Minimize DOM depth, avoid deep nesting (< 32 levels)
  Icons:     SVG sprites or icon font (single request) over individual SVGs
  CSS:       Purge unused styles (Tailwind does this automatically)
  Above fold: Inline critical CSS, defer non-critical

Loading patterns:
  Skeleton screens:  Gray shapes matching content layout (preferred over spinners)
  Progressive:       Low-quality image placeholder → full image
  Optimistic UI:     Update UI immediately, rollback on error
  Infinite scroll:   Load more on intersection observer (vs. pagination buttons)
  Virtual scrolling: For lists > 100 items (react-virtual, tanstack-virtual)
```

## Step 4: Output Format

### For Page Specs
```
1. Page purpose and user goals
2. Layout strategy (Grid/Flexbox) with responsive breakdowns
3. Content hierarchy and visual weight distribution
4. All page states: Loading (skeleton), Empty, Content, Error, Offline
5. Responsive behavior at each breakpoint (320, 640, 768, 1024, 1280, 1536)
6. Typography assignments (token names for every text element)
7. Color token assignments for every element
8. Dark mode appearance
9. SEO: heading hierarchy, meta description, structured data
10. Accessibility: landmark regions, heading levels, skip links, focus order
11. Performance: LCP element, critical rendering path, lazy loading strategy
12. CSS/Tailwind implementation skeleton
```

### For Component Specs
```
1. Component anatomy (named parts)
2. All states: default, hover, focus-visible, active, disabled, loading, error, selected
3. Size variants with exact dimensions
4. Color tokens per state
5. Typography tokens
6. Spacing (padding, margin, gap — in px/rem using token names)
7. Border radius and shadow tokens
8. Animation/transition spec (property, duration, easing)
9. Responsive behavior (breakpoints or container queries)
10. Accessibility: role, aria attributes, keyboard behavior, screen reader announcements
11. Dark mode appearance
12. CSS/Tailwind class list
```

### For Design System Specs
```
1. Token architecture (primitives → semantic → component)
2. Color palette with light/dark mode mappings
3. Typography scale with font loading strategy
4. Spacing scale
5. Shadow/elevation scale
6. Border radius scale
7. Breakpoint system
8. Component inventory with state matrix
9. Animation/motion tokens
10. Icon system (source, sizing, coloring)
11. CSS custom properties file
12. Tailwind theme extension config
```

## Step 5: Anti-Patterns (Never Do These)

```
✗ Placeholder-only labels on form inputs (must have visible <label>)
✗ outline: none without a replacement focus indicator
✗ Fixed-width layouts that break on small screens
✗ Pixel font sizes (use rem/em for scalability)
✗ z-index wars (use a managed z-index scale: --z-dropdown: 10, --z-modal: 50, etc.)
✗ !important for styling (only for utility overrides and reduced motion)
✗ Layout animation (animating width/height/top/left — use transform instead)
✗ Auto-playing video with sound (autoplay is muted-only)
✗ Infinite scroll without a "load more" fallback and visible item count
✗ Carousel as the only way to see content (all items must be reachable)
✗ Text over images without sufficient contrast overlay
✗ Custom scrollbars that break keyboard scrolling
✗ Hover-only interactions with no touch/keyboard alternative
✗ Light gray text on white backgrounds (contrast ratio < 4.5:1)
✗ Hamburger menu on desktop (only mobile/tablet)
✗ Modal overload — popups on page load, stacked modals, modals for simple messages
✗ Disabled buttons without explanation of why (use tooltip or helper text)
✗ Content that requires horizontal scrolling at 320px viewport width
✗ Images without width/height causing layout shift (CLS)
```
