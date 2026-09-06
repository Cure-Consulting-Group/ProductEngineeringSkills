# Web: responsive product and marketing surfaces

Judgment layer. For CSS architecture, container queries, Tailwind, and dark mode implementation, invoke `web-design-expert`; for scaffolding, `nextjs-feature-scaffold`. The web is its own platform with pointer, touch, and keyboard users on the same page.

## Breakpoints and grids

State the breakpoints and the transformation at each; never only the widths.

| Range | Typical | Transformation to specify |
|---|---|---|
| < 640 | phone | single column; navigation becomes tabs (product) or a menu (marketing); tables become rows or cards |
| 640 to 1023 | tablet, small laptop | two columns; sidebar collapses to rail or drawer; secondary panels become sheets |
| 1024 to 1439 | laptop, desktop | full layout; persistent sidebar; multi-column tables |
| >= 1440 | large desktop | max content width (1200 to 1440) with margins; do not stretch text; optional third column |
| >= 1920 | ultrawide | centred content; use the width for panels and data, never for longer lines |

Fluid grids (12 columns product, 6 to 8 editorial) with a stated gutter; fluid type with `clamp()` between named minimum and maximum sizes; container queries for components that live in more than one column width; high-density displays get 2x raster or vector.

## Navigation and structure

Top navigation for marketing and products with up to 5 sections; sidebar for products with more; mega menus only for catalogues with more than 20 destinations, and then with visible grouping; breadcrumbs when depth exceeds two; command palette (Cmd/Ctrl+K) for power tools with more than 20 actions, never as the only route.

Sticky and fixed elements earn their place: a fixed header costs 64 px of every viewport; justify it. Sticky table headers and sticky column for wide tables. Sticky call to action only in checkout, long forms, and editors.

## Components and states

Tables with sort, filter, column visibility, row selection and bulk bar, sticky header, responsive collapse rule; forms with visible labels (no placeholder-as-label), inline validation on blur, error summary at the top on submit, autofill-friendly names; modals for blocking decisions, drawers for editing alongside context; cards only for objects with imagery or heterogeneous shapes; skeletons matching the final layout's silhouette; empty states with the next action; loading states that never shift layout (reserve space).

Pointer states: hover reveals, never hides essential controls (touch users get nothing from hover). Focus visible at 3:1 against the surface, on every interactive element, in the DOM order the eye expects.

## Type and colour

Responsive type scale with 5 to 7 steps; body 16 to 18 px; measure 45 to 75 characters; `text-wrap: balance` on headings; tabular numerals in tables. Colour tokens in three tiers (see `design-system-spec.md`); dark mode designed from the same ramps, not inverted; `color-scheme` set so native controls match.

## Motion

CSS transitions 150 to 250 ms for state; view transitions for route changes where continuity helps; scroll-linked animation only in the expressive register; `prefers-reduced-motion` honoured with cross-fade or nothing. Anything needing WebGL, shaders, or canvas gets an explicit flag and a fallback.

## Accessibility (WCAG 2.2 AA unless the project says otherwise)

Contrast 4.5:1 text, 3:1 large text and UI; 24 x 24 CSS px minimum target (44 preferred); keyboard for everything; focus not obscured by sticky bars; landmarks and heading order; labels and names; error identification in text; 200 percent zoom and 320 px reflow without horizontal scrolling; no motion or autoplay that cannot be paused. `contrast_check.py` verifies the palette pairs.

## Assets

Favicons (16, 32, 48, `.ico`, SVG), apple-touch-icon 180, web app manifest icons 192 and 512 (maskable variant with safe zone), OpenGraph 1200 x 630, Twitter/X header 1500 x 500, avatar 400. `export_asset_matrix.py` produces them.

## Implementation mapping

React or Next.js App Router components, CSS grid and flexbox with logical properties, container queries, CSS custom properties from the tokens. Flag WebGL, shader, or heavy animation dependencies with cost and fallback.
