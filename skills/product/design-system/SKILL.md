---
name: design-system
description: "Builds and governs component libraries from design-studio tokens. Use when setting up Storybook, Showkase, a SwiftUI catalog, token builds, or DS contribution rules."
when_to_use: "NOT for defining tokens, visual language, or screens (design-studio owns the DTCG token format) or platform UI guidance."
argument-hint: "[project-or-platform]"
metadata:
  verified: 2026-09-23
---

# Design System

**Outcome:** a working component library pipeline — design-studio's tokens compiled to every platform,
components cataloged (Storybook / Showkase / SwiftUI catalog), and a governance process consuming
teams can follow. Done when tokens build from one source on CI, every component has a catalog entry
with its states, and the contribution/versioning rules are written down. Match length to the need;
no filler sections or restated summaries.

**Boundary.** design-studio owns token *content*, tiers (primitive → semantic → component), and the
format: W3C Design Tokens (DTCG) JSON with `$value`/`$type` (design-studio ships the starter schema, w3c_token_schema.json).
This skill consumes that file; it never introduces a second token format. If no tokens exist yet,
run design-studio first (Step 6 "Systemise") or ask the user to.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Token files: !`ls design/tokens.json tokens.json tokens/*.json 2>/dev/null | head -4 | grep . || echo "(no token file)"`
- Catalog tooling: !`grep -m3 -oE '"(storybook|@storybook/[a-z-]+|style-dictionary)": *"[^"]+"' package.json 2>/dev/null | grep . || echo "(no Storybook/Style Dictionary in package.json)"`
- Platforms present: !`ls package.json build.gradle.kts Podfile Package.swift 2>/dev/null | head -4 | grep . || echo "(none detected)"`

## Step 1: Classify

| Need | Deliver |
|---|---|
| Greenfield library | Token pipeline + catalog per platform + governance doc |
| Unify existing UI | Inventory of divergent components, mapping to canonical names, migration order |
| Add a platform | Token transform + catalog + parity table for the new platform |
| Token migration (hard-coded → tokens) | Codemod/grep plan, no visual change, before/after screenshots |
| Governance only | Contribution, review, versioning, deprecation rules |
| Question / review | An answer or findings; no files |

## Step 2: Gather Context

Ask only for what is missing: platforms and the primary one, existing components (and framework),
where tokens live, who contributes (dedicated DS team or federated), theme needs (light/dark,
white-label), distribution (npm, Maven, SPM), and the design tool (Figma library?).

## Step 3: Token Build Pipeline (Cure defaults)

- Source: design-studio's DTCG `tokens.json`, versioned in the design-system package, reviewed like code.
- Build with **Style Dictionary v4+** (reads DTCG `$value` natively; don't mix DTCG and legacy `value` files in one instance). Newer DTCG 2025.10 features are partially supported — confirm the current release before relying on them.
- Outputs: Web → CSS custom properties, mapped into Tailwind v4 with `@theme` in CSS (there is no `tailwind.config.ts` in v4); Android → Kotlin `ColorScheme`/typography objects; iOS → Swift `Color`/`Font` extensions or asset catalog colors.
- Themes swap **semantic** tokens only; primitives never change per theme. A component that works in light mode must work in dark without code changes.
- Android: `dynamicLightColorScheme(context)` / `dynamicDarkColorScheme(context)` (API 31+) only if the brand allows dynamic color; otherwise the generated scheme.
- CI: token change → rebuild → contrast + lint (design-studio's `tokens_lint.py`, `contrast_check.py`) → publish platform packages.

## Step 4: Component Library per Platform

Canonical names are identical on every platform (`PrimaryButton`, `TextInput`, `ContentCard`,
`BottomSheet`); only interaction feel is native (ripple / highlight / hover). Read
`reference/details.md` when scaffolding the Compose, SwiftUI, or React (shadcn/Radix + cva) library
code — it holds the theme wrapper, a reference button, and package layout per platform.

| Component | Compose | SwiftUI | React |
|---|---|---|---|
| PrimaryButton | `Button` (M3) | `Button` + style | `<Button>` (cva) |
| TextInput | `OutlinedTextField` | `TextField` | `<Input>` |
| BottomSheet | `ModalBottomSheet` | `.sheet()` | `<Sheet>` (Radix Dialog) |
| Dialog | `AlertDialog` | `.alert()` | `<Dialog>` (Radix) |
| Toast | `Snackbar` | custom overlay | `<Toast>` (Sonner) |

Parity bugs (fix, don't document): different color for the same semantic token, different
spacing/radius for the same component, dark mode missing on one platform, accessibility working
on one platform only. Expected differences: system fonts, navigation pattern, haptics, gestures.

## Step 5: Catalogs

- **Web — Storybook 10** (requires Node 20.19+ or 22.12+; verified 2026-09-23 against the Storybook migration guide). `npx storybook@latest init`. Controls, actions, viewport, backgrounds, and interactions are in core since Storybook 9 — don't install `@storybook/addon-interactions` or `addon-essentials`. Add `@storybook/addon-a11y` and `@storybook/addon-themes` (the maintained light/dark switcher; the old `storybook-dark-mode` package doesn't support 9+). `@storybook/addon-designs` for Figma embeds. Deploy to Chromatic or a Vercel preview.
- Stories per component: default, all variants × sizes, interactive (args), every state (loading, disabled, error), dark theme.
- **Android — Showkase** (`com.airbnb.android:showkase` + `showkase-processor` via KSP; 1.0.5 is the latest seen, Aug 2025 — confirm before pinning). Annotate previews with `@ShowkaseComposable`; debug builds only.
- **iOS — catalog app target** listing each component's states, plus `#Preview` blocks per component; snapshot-test the catalog.
- Each component documents: API with defaults, variants, a11y notes (touch target 48dp Android / 44pt iOS / 24px web AA minimum; what the screen reader announces; keyboard behavior), and one do/don't pair.

## Step 6: Governance

- Contribution: RFC issue (problem, platforms, Figma frame) → design review against tokens and WCAG AA → implementation on every required platform with stories/previews and tests → DS-owner code review for cross-platform API parity → release.
- Versioning is semver: PATCH fix/a11y, MINOR new component/variant/token, MAJOR removed or renamed component, token, or prop.
- Deprecate before removing: mark deprecated for at least one minor release with a migration note; remove only in the next major. Never ship a release that breaks dark mode or accessibility.
- Federated teams (no dedicated DS team): one named owner per platform; nothing merges without an owner review.

## Step 7: Code/Artifact Generation

Applies when Step 1 calls for building (greenfield, add platform, token migration). First read
existing theme/token code (paths like `**/theme/**`, `**/tokens/**`, `**/designsystem/**`) and extend
rather than replace. Write only what the classification needs:

1. Style Dictionary config reading the DTCG token file, with the platform targets in use.
2. Web: generated `tokens.css` + a `theme.css` with `@theme inline`.
3. Android: generated theme object + `AppTheme` wrapper; iOS: generated `DesignTokens.swift`.
4. Catalog setup for each platform in scope, with one fully-worked component as the pattern.
5. `CONTRIBUTING.md` (or a DS section) with the Step 6 rules.

Deliver the requested artifacts; don't restyle adjacent screens.

## Step 8: Output Summary

Close with a short table: classification, platforms, token source and build command, catalog per
platform and where it's deployed, distribution channel per platform, open parity gaps, and what was
not done. Related skills: accessibility-audit (contrast and screen-reader verification),
android-feature-scaffold / ios-architect / nextjs-feature-scaffold (feature code that consumes the library).
