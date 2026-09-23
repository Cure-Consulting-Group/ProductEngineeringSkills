# Android Design Expert — Material Design 3

**Outcome:** an M3 spec (or a review of existing UI) precise enough to build in Compose without guessing:
every element has a color role, type role, shape token, spacing in dp, all states, and window-size
behaviour. Done when each item in the Step 4 output contract is filled or explicitly marked N/A.
Match length to the need; no filler sections or restated summaries.

Related: `product-design` (cross-platform specs), `android-feature-scaffold` (feature code),
`accessibility-audit` (WCAG), `design-studio` (brand and token system; owns the DTCG token format).

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Build config: !`grep -hE "compileSdk|targetSdk|minSdk|compose-bom|material3" app/build.gradle.kts gradle/libs.versions.toml 2>/dev/null | head -12 || echo "(no Gradle config found)"`
- Existing theme: !`find . -path ./node_modules -prune -o -path "*/ui/theme/*.kt" -print 2>/dev/null | head -6`

## Step 1: Classify the Request

| Request | Output |
|---|---|
| Screen design / layout | Screen spec (Step 4) |
| Component design | Component spec (Step 4) |
| Navigation architecture | Navigation spec (Step 4) |
| Color / dynamic color / typography / icons | Role and token mapping, with a Compose snippet |
| Motion | Motion spec using M3 motion tokens |
| Adaptive layout | Layout per width class, compact → extra-large |
| Widget (Glance) | Widget spec |
| Design review of existing UI | Findings, each with severity and the M3 rule it breaks; report everything found |
| Theme / design-system code for Android | Compose theme files (see Code Generation) |

## Step 2: Gather Context

Ask only what the build config above doesn't answer:
1. Device targets: phone, tablet, foldable, ChromeOS/desktop, Wear OS?
2. `minSdk` / `targetSdk` (drives dynamic color, edge-to-edge, predictive back — see Step 3).
3. Brand level: M3 defaults, custom color, custom type, or full brand override? Existing tokens?
4. Expressive or baseline M3 (see Step 3)?
5. Accessibility target: WCAG AA (default) or AAA.
6. Compose (default) or legacy Views.

## Step 3: Cure M3 Decisions and Gotchas (always apply)

**Platform behaviour that changes the design (verified 2026-09-23, developer.android.com):**
- **Edge-to-edge is enforced** on Android 15+ once `targetSdk ≥ 35`. Every screen spec states how
  it handles system-bar and display-cutout insets (`Scaffold` content padding, `WindowInsets`,
  `enableEdgeToEdge()`). Status/nav bars are transparent; never "primary-colored system bars".
- **Predictive back:** system back-to-home / cross-activity animations show on Android 15+ for apps
  that opt in; at `targetSdk ≥ 36` on Android 16+ they are on by default and `onBackPressed()` /
  `KEYCODE_BACK` are no longer dispatched. Specify back behaviour with `BackHandler` /
  `PredictiveBackHandler` (Compose) or `OnBackPressedCallback`, and design the in-progress back preview
  for sheets, drawers, and search.
- **Dynamic color** needs API 31+. Always ship a static brand fallback scheme; keep logos, brand
  illustrations, and content imagery out of dynamic tinting.
- **M3 Expressive** (expressive motion springs, shape morphing, new components such as button groups
  and loading indicators): APIs are still `@ExperimentalMaterial3ExpressiveApi` in the stable
  `material3` 1.4.0; `MaterialExpressiveTheme` is non-experimental only in 1.5.0 alphas. Cure default:
  baseline M3 for client production apps; Expressive only when the client accepts an experimental
  API opt-in (confirm before use — re-check the Compose Material 3 release notes).

**Adaptive layout.** Width classes (dp): Compact < 600 · Medium 600–839 · Expanded 840–1199 ·
Large 1200–1599 · Extra-large ≥ 1600. Height: Compact < 480 · Medium 480–899 · Expanded ≥ 900.
Use `currentWindowAdaptiveInfo(supportLargeAndXLargeWidth = true).windowSizeClass` and
`isWidthAtLeastBreakpoint(WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND)`; the
`windowWidthSizeClass` enum API is deprecated. Classes describe the window, not the device — a
tablet in split-screen is Compact. Navigation: bar (Compact) → rail (Medium/Expanded) → rail or
permanent drawer (Large+), via `NavigationSuiteScaffold`. Canonical layouts: list-detail
(`ListDetailPaneScaffold`), supporting pane (`SupportingPaneScaffold`), feed.

**Color.** Reference only color roles (`MaterialTheme.colorScheme.*`), never hex. Every `on*` role
pairs with its container. Surfaces use the `surfaceContainer*` roles; tonal elevation, not shadows,
in dark theme. Primary never fills large areas. Dark theme is required.

**Type.** Text in `sp`, never `dp`; map every text element to one of the 15 M3 type roles; test at
200% font scale and with non-linear font scaling (Android 14+).

**Components.** One Filled button per screen. Touch targets ≥ 48×48dp. Sentence-case labels. Never
remove ripple/indication from clickables. Bottom bar holds 3–5 destinations; don't combine an
implicit card tap with explicit card buttons; no critical actions in dismissible bottom sheets.

**Motion.** Use M3 easing/duration tokens (or Expressive spring tokens) — never ad-hoc millisecond
values. Respect "Remove animations". Shared-element list→detail via `SharedTransitionLayout`.

Read `reference/details.md` when you need exact token values: the color-role → tone table, the type
scale sizes, shape scale, motion easing/duration tokens, spacing grid, or widget sizing.

## Step 4: Output Contract

**Screen spec:** purpose and user goal · canonical layout · anatomy with dp spacing · states
(loading, empty, content, error, partial) · behaviour per width class · color role and type role per
element · inset handling (edge-to-edge) · back behaviour (predictive back) · dark theme · TalkBack
order and semantics · motion tokens · Compose component hierarchy.

**Component spec:** anatomy with M3 token names · all states (enabled, disabled, hovered, focused,
pressed, dragged, selected, error) with color roles · type roles · shape token · elevation · padding
in dp · Material Symbol name/fill/weight/optical size · motion · indication · accessibility (role,
`contentDescription`, `stateDescription`, custom actions) · Compose skeleton.

**Navigation spec:** `NavigationSuiteScaffold` config · component per width class · destinations
with filled/outlined icons · top app bar per destination · transitions · deep-link URIs · back stack.

## Code/Artifact Generation

Applies only when Step 1 is "theme / design-system code" or the user asks for code; a spec or review
gets the Step 4 output, not files. Extend the existing theme files found above rather than replacing
them. Typical set: `ui/theme/Theme.kt` (ColorScheme with dynamic + static fallback, Typography,
Shapes), `Color.kt`, `Type.kt`, requested components, and `@Preview`s for light/dark and key states.
Deliver what was asked; don't refactor adjacent code.

## Anti-Patterns (flag in reviews)

- iOS idioms: text-only tab bars, custom back-swipe, action sheets, segmented controls (use M3 bar with
  icons, system/predictive back, `ModalBottomSheet`/`AlertDialog`, `SegmentedButton`/Tabs).
- Hard-coded colors or dp text sizes; primary as a large background; shadow elevation in dark theme.
- Content drawn under system bars with no inset handling; `onBackPressed()` overrides.
- One layout for all window sizes; hamburger as primary phone navigation; > 5 bottom destinations.
- FAB overlapping the navigation bar; dialogs without explicit action labels; missing
  loading/empty/error states.
