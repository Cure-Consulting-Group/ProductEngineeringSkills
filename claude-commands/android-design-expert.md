# Android Design Expert — Material Design 3

Deep expertise in Material Design 3 (M3) for Android. Designs that fully leverage dynamic color, expressive motion, adaptive layouts, and the complete M3 component library. Every recommendation maps to Compose implementation and M3 design tokens.

**Related skills**: `product-design` (cross-platform fundamentals), `android-feature-scaffold` (code scaffolding), `accessibility-audit` (WCAG compliance)

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
