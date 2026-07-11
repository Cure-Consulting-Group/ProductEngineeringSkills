---
name: android-design-expert
description: "Expert Android design guidance following Material Design 3 — dynamic color, component tokens, adaptive layouts, motion system, and Jetpack Compose implementation patterns"
when_to_use: "Use for Material Design 3 guidance on Android screens — dynamic color, Compose components, adaptive layouts. NOT for scaffolding code (use android-feature-scaffold)."
argument-hint: "[screen-or-component-name]"
paths: "*.kt,*.kts"
---

# Android Design Expert — Material Design 3

Deep expertise in Material Design 3 (M3) for Android. Designs that fully leverage dynamic color, expressive motion, adaptive layouts, and the complete M3 component library. Every recommendation maps to Compose implementation and M3 design tokens.

**Related skills**: `product-design` (cross-platform fundamentals), `android-feature-scaffold` (code scaffolding), `accessibility-audit` (WCAG compliance)

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
| Screen design / layout | Design per M3 layout and canonical patterns |
| Component design | Spec per M3 component guidelines with all states |
| Navigation architecture | Design per M3 navigation patterns (nav bar, rail, drawer) |
| Typography | Spec M3 type scale with custom font integration |
| Color scheme / dynamic color | Generate M3 tonal palette and color roles |
| Icon system | Spec Material Symbols usage and configuration |
| Animation / motion | Design per M3 motion system (easing, duration) |
| Adaptive layout | Design responsive layouts across phone/tablet/foldable/desktop |
| Widget / Glance | Design per Android widget guidelines |
| Design-to-Compose handoff | Generate Compose implementation specs |
| Design system for Android | Build M3-based token system with custom theme |

## Step 2: Gather Context

1. **Device targets** — Phone only? Phone + tablet? Foldable? Large screen? Wear OS?
2. **Min SDK** — API 24+ (standard) or higher? (Dynamic color requires API 31+)
3. **Feature/screen** — what is being designed?
4. **Brand customization level** — Full M3 defaults? Custom color? Custom type? Full brand override?
5. **Existing design system** — established tokens, component overrides?
6. **Accessibility level** — WCAG AA (standard) or AAA (enhanced)?
7. **Implementation** — Jetpack Compose (preferred) or XML Views?

## Step 3: M3 Design Foundations (Always Apply)

See [reference/details.md](reference/details.md) (section “Step 3: M3 Design Foundations (Always Apply)”) for full detail.

## Step 4: Output Format

### For Screen Specs
```
1. Screen purpose and user goal
2. Canonical layout pattern (list-detail, feed, supporting pane, or full-screen)
3. Layout anatomy with dp values for all spacing
4. All screen states: Loading (skeleton/shimmer), Empty, Content, Error, Partial
5. Window size class adaptations (compact → medium → expanded)
6. Color role assignments for every element
7. Typography role assignments for every text element
8. Dark theme appearance
9. TalkBack reading order and semantics tree
10. Motion specifications (transitions, easing, duration tokens)
11. Compose component hierarchy recommendation
```

### For Component Specs
```
1. Component anatomy (named parts with M3 component token names)
2. All states: enabled, disabled, hovered, focused, pressed, dragged, selected, error
3. Color role assignments per state
4. Typography roles used
5. Shape (corner radius from M3 shape scale)
6. Elevation level (tonal or shadow)
7. Spacing spec (internal padding, margins — in dp)
8. Material Symbol names, style, fill, and optical size
9. Motion spec (state transitions with easing and duration tokens)
10. Ripple/indication spec
11. Accessibility: role, contentDescription, stateDescription, custom actions
12. Compose implementation skeleton
```

### For Navigation Architecture
```
1. NavigationSuiteScaffold configuration
2. Navigation component per window size class
3. Destination list with icons (filled/outlined variants)
4. Top app bar style per destination
5. Transition type between destinations (fade through, shared axis)
6. Deep link URI patterns
7. Back stack behavior
```

## Code Generation (Required)

When designing for Android, generate actual Compose code using Write:

1. **Theme**: `ui/theme/Theme.kt` — MaterialTheme with custom ColorScheme, Typography, Shapes
2. **Colors**: `ui/theme/Color.kt` — brand colors mapped to M3 color roles
3. **Typography**: `ui/theme/Type.kt` — font families and text styles
4. **Component**: `ui/components/{Component}.kt` — custom components with M3 tokens
5. **Preview**: `ui/preview/{Screen}Preview.kt` — @Preview functions for all states

Before generating, Glob for existing theme files (`**/theme/**`, `**/ui/**`) and Read them to extend.

## Step 5: Anti-Patterns (Never Do These)

```
✗ iOS-style tab bar at the bottom with text-only labels (use M3 NavigationBar with icons)
✗ iOS-style back swipe gesture (Android uses system back — predictive back on API 34+)
✗ Custom ripple or removing ripple from clickable surfaces
✗ Using primary color for large background areas (use surface roles)
✗ Hardcoded colors instead of M3 color roles
✗ dp units for text (always sp)
✗ Circular corners instead of M3 shape tokens (rounded rectangles, not circles for cards)
✗ Hamburger menu as primary navigation on phone (use bottom nav bar)
✗ iOS-style action sheets (use M3 BottomSheet or AlertDialog)
✗ iOS-style segmented controls (use M3 Tabs or SegmentedButton)
✗ Alert dialogs without explicit action buttons ("OK" and "Cancel" with clear labels)
✗ Ignoring window size classes (one-size layout for all screen sizes)
✗ Bottom navigation with more than 5 destinations
✗ FAB overlapping bottom navigation (position with proper offset)
✗ Skipping loading/error/empty states
✗ Shadow elevation in dark theme (use tonal elevation instead)
```
