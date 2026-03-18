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

## Step 3: Apply M3 Expertise

Cover all applicable areas: tonal palette generation (5 key colors, 13 tones), color roles (40+ role assignments for light/dark), dynamic color (API 31+), M3 type scale (15 roles from displayLarge to labelSmall), window size classes and canonical layouts (list-detail, feed, supporting pane), adaptive navigation (bar/rail/drawer), M3 component patterns (buttons, cards, text fields, bottom sheets), motion system (easing curves and duration tokens), Material Symbols (style, fill, weight, grade, optical size), widgets, and dark theme with tonal elevation.

## Step 4: Output Format

For screen specs: purpose, canonical layout pattern, layout anatomy with dp values, all states, window size class adaptations, color role assignments, typography roles, dark theme, TalkBack reading order, motion specs, Compose hierarchy.

For component specs: anatomy with M3 token names, all states with color roles per state, typography roles, shape (corner radius), elevation, spacing in dp, Material Symbol config, motion spec (easing + duration), ripple spec, accessibility (role, contentDescription, stateDescription), Compose skeleton.

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
