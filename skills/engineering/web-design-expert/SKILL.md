---
name: web-design-expert
description: "Expert web design guidance — responsive design, CSS architecture, design tokens, container queries, accessibility-first patterns, dark mode, and Tailwind/CSS implementation"
when_to_use: "Use for responsive design, CSS architecture, design tokens, container queries, dark mode, and Tailwind patterns. NOT for scaffolding code (use nextjs-feature-scaffold)."
argument-hint: "[page-or-component-name]"
paths: "*.ts,*.tsx,*.css,*.html"
---

# Web Design Expert — Modern Web Design Systems

Deep expertise in modern web design: responsive layouts, CSS architecture, design tokens, component patterns, accessibility-first design, and performance-conscious UI. Every recommendation maps to production CSS/Tailwind implementation and follows WCAG 2.2 AA standards.

**Related skills**: `product-design` (cross-platform fundamentals), `nextjs-feature-scaffold` (code scaffolding), `accessibility-audit` (WCAG compliance)

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

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

See [reference/details.md](reference/details.md) (section “Step 3: Web Design Foundations (Always Apply)”) for full detail.

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

## Code Generation (Required)

When designing for web, generate actual files using Write:

1. **Tailwind config**: `tailwind.config.ts` — brand colors, fonts, spacing, breakpoints as design tokens
2. **CSS variables**: `styles/tokens.css` — CSS custom properties for all tokens
3. **Component**: `components/ui/{Component}.tsx` — accessible component with variants (using cva or class-variance-authority)
4. **cn utility**: `lib/cn.ts` — className merge utility (clsx + tailwind-merge)
5. **Responsive test matrix**: `docs/responsive-test-matrix.md` — viewport checklist for QA

Before generating, Read existing `tailwind.config.ts` and Glob for `components/ui/**` to understand current design system.

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
