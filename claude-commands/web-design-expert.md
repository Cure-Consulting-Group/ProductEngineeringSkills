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

## Step 3: Apply Web Design Expertise

Cover all applicable areas: responsive breakpoint system (mobile-first, 6 breakpoints), container queries for component-level responsiveness, layout patterns (CSS Grid, Flexbox, auto-fit/auto-fill), fluid typography (clamp()), design token architecture (primitives → semantic → component), color system with dark mode (system preference + manual toggle), spacing system (4px base, token scale), component patterns (buttons, cards, forms, navigation, modals), performant animation (GPU-accelerated properties, reduced motion), image optimization (srcset, WebP/AVIF, lazy loading), and Core Web Vitals awareness.

## Step 4: Output Format

For page specs: purpose, layout strategy, content hierarchy, all states, responsive behavior at each breakpoint, typography tokens, color tokens, dark mode, SEO (heading hierarchy, meta, structured data), accessibility (landmarks, headings, skip links, focus order), performance (LCP, critical CSS, lazy loading), CSS/Tailwind skeleton.

For component specs: anatomy, all states (default, hover, focus-visible, active, disabled, loading, error, selected), size variants, color tokens per state, typography tokens, spacing tokens, border radius and shadow tokens, animation spec, responsive behavior, accessibility (role, aria attributes, keyboard behavior), dark mode, CSS/Tailwind classes.

## Code Generation (Required)

When designing for web, generate actual files using Write:

1. **Tailwind config**: `tailwind.config.ts` — brand colors, fonts, spacing, breakpoints as design tokens
2. **CSS variables**: `styles/tokens.css` — CSS custom properties for all tokens
3. **Component**: `components/ui/{Component}.tsx` — accessible component with variants (using cva or class-variance-authority)
4. **cn utility**: `lib/cn.ts` — className merge utility (clsx + tailwind-merge)
5. **Responsive test matrix**: `docs/responsive-test-matrix.md` — viewport checklist for QA

Before generating, Read existing `tailwind.config.ts` and Glob for `components/ui/**` to understand current design system.
