# Web Design Expert — Modern Web Design Systems

**Outcome:** a page, component, or token spec (or a design review) that an engineer can implement directly in Tailwind v4 / CSS, WCAG 2.2 AA by construction, with every state and breakpoint defined. Done when the spec meets the Step 4 contract for its type; files are written only when Step 1 says so.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Styling deps: `grep -oE '"(tailwindcss|@tailwindcss/[a-z-]+|next|react|class-variance-authority|tailwind-merge|tw-animate-css|tailwindcss-animate)": *"[^"]+"' package.json 2>/dev/null | head -10 || echo "(no package.json)"`
- Tailwind v3 config present: `ls tailwind.config.* 2>/dev/null || echo "(none — v4 CSS-first or no Tailwind)"`
- Theme CSS: `grep -rlE "@theme|@import \"tailwindcss\"|@tailwind base" --include=*.css . 2>/dev/null | grep -v node_modules | head -3`
- UI components: `ls components/ui src/components/ui 2>/dev/null | head -15`

## Step 1: Classify the Request

| Request | Output |
|---|---|
| Page layout / landing / dashboard | Page spec |
| Component design | Component spec with all states and variants |
| Tokens / theming / dark mode | Token spec (primitive → semantic → component) |
| Typography, spacing, motion system | Focused scale spec |
| Design review of existing UI | Findings — every issue with severity, no code |
| Tailwind v3 → v4 migration of a theme | Migration plan + changed CSS |
| "Build it" / design-to-code handoff | Spec, then Code/Artifact Generation |

## Step 2: Gather Context

Ask only what auto-context didn't answer: project type (marketing, SaaS app, dashboard, e-commerce), framework, existing design system or component library (shadcn/ui, Radix), brand constraints, and performance targets. Cure default stack: Next.js App Router + Tailwind v4 + shadcn/ui; WCAG 2.2 AA.

## Step 3: Cure Defaults (always apply)

**Tailwind v4 is CSS-first.** Tokens live in CSS under `@theme { --color-*, --font-*, --text-*, --spacing, --radius-*, --shadow-*, --breakpoint-* }`, which also generates the utilities. There is no `tailwind.config.ts` by default (a legacy JS config needs an explicit `@config`). Runtime-switchable values (theme colors) are plain CSS variables on `:root`/`.dark`, mapped into utilities with `@theme inline`. Class-based dark mode: `@custom-variant dark (&:where(.dark, .dark *));`. shadcn/ui on v4 uses OKLCH colors and `tw-animate-css` (replacing `tailwindcss-animate`). When a v3 config exists, say so and propose the migration (`npx @tailwindcss/upgrade`) rather than extending it.

**Token layers.** Primitive (`--color-blue-600`) → semantic (`--color-primary`, `--color-surface`, `--color-text-secondary`, `--color-border-focus`) → component (`--button-primary-bg`). Components reference semantic tokens only; dark mode swaps semantic values, never primitives. Token file format for cross-platform export is owned by `design-studio` (W3C DTCG `$value`).

**Layout.** Mobile-first `min-width` queries; Tailwind default breakpoints (sm 640, md 768, lg 1024, xl 1280, 2xl 1536). Container queries (`@container`, `@md:`) for components reused at different widths. Everything usable at 320 CSS px with no horizontal scroll. Body measure 65–75ch. Grid for page layout, flex for components, `gap` instead of child margins.

**Type.** Root 16px, never changed; `rem` sizes; fluid `clamp()` only for display sizes; body line-height 1.5–1.6, headings 1.1–1.3; ≤2 font families; `font-display: swap` plus a metric-matched fallback (`size-adjust`, or `next/font`, which does this automatically) to avoid CLS.

**Color and dark mode.** Contrast ≥4.5:1 body, ≥3:1 large text and UI boundaries, checked in both themes. Dark mode redesigns surfaces (dark grays, elevation by lightness, borders instead of shadows) — not inversion. Respect `prefers-color-scheme` by default, offer a toggle, persist it, and set the class before paint to avoid a flash.

**Interaction.** Visible `:focus-visible` ring (never bare `outline: none`); 24×24px minimum target (WCAG 2.5.8), 44×44px for primary touch controls; visible labels on inputs; one primary action per view; native `<dialog>` for modals with focus return; skip link as the first focusable element.

**Motion.** Animate `transform`/`opacity` only; 100–200ms micro, 200–300ms standard; honor `prefers-reduced-motion`; View Transitions API as progressive enhancement.

**Performance.** Design for LCP < 2.5s, INP < 200ms, CLS < 0.1 (p75). Explicit image dimensions or `aspect-ratio`; `loading="eager"` + `fetchpriority="high"` on the LCP image only; skeletons over spinners; virtualize lists over ~100 rows.

Read [reference/details.md](reference/details.md) when a spec needs the exact scales: fluid type table, spacing scale, shadow/radius scale, semantic color token set, component size tables (buttons, inputs, modals), and the Tailwind v4 `@theme` starter.

## Step 4: Output Contract

- **Page spec:** purpose and user goal; layout (grid/flex) per breakpoint; content hierarchy; states — loading, empty, content, error, offline; token assignments for text and color; dark-mode appearance; landmarks, heading levels, focus order; LCP element and loading strategy; Tailwind class skeleton.
- **Component spec:** anatomy; states (default, hover, focus-visible, active, disabled, loading, error, selected); size variants; tokens per state; transition (property, duration, easing); responsive or container-query behavior; ARIA role/attributes and keyboard behavior; class list (cva variants if the project uses cva).
- **Token spec:** the three layers, light/dark mappings, type/spacing/radius/shadow/motion scales, and the `@theme` CSS.
- **Review:** every finding with severity (blocker / major / minor), the rule or WCAG criterion it breaks, and the fix. Don't filter to "top issues".

Match length to the need; no filler sections or restated summaries.

## Code/Artifact Generation

Applies only when Step 1 classified the request as build/handoff or the user asked for files. Extend what auto-context found; don't create a parallel system. Typical files: the global CSS with `@theme` / `@theme inline` tokens (e.g. `app/globals.css`), `components/ui/<Component>.tsx` using `class-variance-authority` for variants, and `lib/utils.ts` `cn()` (clsx + tailwind-merge) if absent. Write only what was asked; don't restyle adjacent components.

## Step 5: Anti-Patterns

- Model fallback styles when no direction is given (Anthropic, Opus 5.5 guide): cream/off-white backgrounds, italic
  accent words in headlines, numbered "01/02/03" section labels, monospace labels, pill-shaped buttons. Name
  them as exclusions in the spec; "avoid a generic look" only swaps one default for another.
- Placeholder-only labels; `outline: none` without replacement; hover-only interactions; disabled buttons with no explanation.
- Pixel font sizes; horizontal scroll at 320px; images without dimensions (CLS).
- Arbitrary values instead of tokens; z-index wars (use a token scale); `!important` outside reduced-motion overrides.
- Animating width/height/top/left; autoplay with sound; carousels as the only path to content; infinite scroll without a load-more fallback.
- Text over images without a contrast overlay; light gray text under 4.5:1.
- Hamburger menus on desktop; modals on page load or stacked modals.
- New `tailwind.config.ts` in a v4 project; HSL-triplet shadcn tokens copied from v3 examples.

## Related

`nextjs-feature-scaffold` (feature code) · `design-studio` (brand, full design systems, DTCG tokens) · `design-system` (Storybook and governance) · `accessibility-audit` (WCAG verification) · `performance-review` (measured Core Web Vitals)
