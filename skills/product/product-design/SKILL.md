---
name: product-design
version: "1.0.0"
description: "Create design specs following Apple HIG, Material Design 3, design tokens, and accessibility standards"
when_to_use: "Use for cross-platform design specs combining Apple HIG and Material Design 3. For deep platform-specific guidance, use android-design-expert, ios-design-expert, or web-design-expert instead."
argument-hint: "[feature-or-screen-name]"
---

# Product Design

Expert design across Apple HIG, Material Design 3, and Web. Platform-native first. Accessibility is a requirement, not a feature.

**For deep platform-specific expertise, use the dedicated design expert skills:**
- `ios-design-expert` — Apple HIG, SF Symbols, Dynamic Type, SwiftUI components, haptics
- `android-design-expert` — Material Design 3, dynamic color, tonal palettes, adaptive layouts, Compose
- `web-design-expert` — Responsive design, CSS architecture, design tokens, container queries, Tailwind

## Design System Hierarchy

```
Brand Foundation
  ├── Design Tokens (primitive values — color hex, spacing px, font names)
  │     └── Semantic Tokens (purpose-mapped — color.surface.primary, spacing.component.gap)
  ├── Component Library (atoms → molecules → organisms)
  ├── Pattern Library (flows, layouts, navigation patterns)
  └── Platform Adaptations
        ├── iOS (HIG-compliant — SwiftUI components)
        ├── Android (MD3-compliant — Compose components)
        └── Web (CSS custom properties + component library)
```

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Request

| Request | Platform | Action |
|---------|---------|--------|
| iOS screen / component | Apple HIG | Design per HIG guidelines |
| Android screen / component | Material Design 3 | Design per MD3 spec |
| Web screen / component | Web design system | Design with modern web standards |
| Cross-platform design system | All three | Generate platform-adaptive specs |
| Design tokens | All | Define token system |
| Accessibility spec | All | Generate a11y requirements |
| Motion / animation spec | Platform-specific | Define animations |
| Figma architecture | All | Structure Figma file |
| Design review / audit | Platform-specific | Audit against guidelines |

## Step 2: Gather Context

1. **Platform(s)** — iOS / Android / Web / cross-platform?
2. **Feature/screen** — what is being designed?
3. **Existing design system** — token names, component names, Figma file structure?
4. **Brand constraints** — colors, typefaces, logo usage rules?
5. **User context** — consumer / enterprise / specialized (e.g., sports, fintech)?
6. **Accessibility level** — WCAG AA (standard) or AAA (enhanced)?
7. **Design handoff target** — Figma specs → SwiftUI / Compose / CSS?

## Platform Detection and Routing

After classifying the request, detect which platforms are in scope:
- If Android (Kotlin/Compose detected): reference `/android-design-expert` for M3-specific guidance
- If iOS (Swift/SwiftUI detected): reference `/ios-design-expert` for HIG-specific guidance
- If Web (TypeScript/React detected): reference `/web-design-expert` for web-specific guidance
- If cross-platform: generate design tokens that map to all platforms

## Artifact Generation (Required)

Generate using Write:
1. **Design brief**: `docs/design-brief.md` — problem, user flows, wireframes (ASCII), component list
2. **Token specification**: `docs/design-tokens.md` — color, type, spacing, elevation values
3. **Component inventory**: `docs/component-inventory.md` — all components needed with states and variants
4. **Accessibility checklist**: `docs/accessibility-requirements.md` — WCAG AA requirements for this feature

## Step 3: Universal Design Principles (Always Apply)

### Accessibility First (Non-Negotiable)
```
Color contrast:     Text on background >= 4.5:1 (AA) | >= 7:1 (AAA)
                    Large text (18pt+) >= 3:1
Touch targets:      iOS minimum 44x44pt | Android minimum 48x48dp | Web minimum 44x44px
Focus indicators:   Visible, 3:1 contrast against adjacent colors
Motion:             Respect prefers-reduced-motion — all animations have no-motion fallback
Screen readers:     Every interactive element has accessible name
Color alone:        Never the sole means of conveying information
```

### Spacing System (8pt/8dp grid)
```
Base unit: 8pt (iOS) / 8dp (Android) / 8px (Web)
Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96
Component padding: multiples of 8
Text line height: nearest 4pt multiple
Never use odd numbers except for border widths (1pt/1dp/1px)
```

### Typography Rules
```
Never use fewer than 2 type sizes in a screen (creates visual hierarchy)
Never use more than 3 type sizes in a single component
Line length: 45-75 characters optimal for body text
Line height: 1.4-1.6x for body, 1.1-1.3x for display/heading
```

## Step 4: Output Format

For component specs, always output:
1. **Component anatomy** — named parts diagram (text)
2. **States** — default, hover/pressed, focused, disabled, loading, error
3. **Variants** — size variants, style variants
4. **Spacing spec** — internal padding, margins, gap
5. **Accessibility requirements** — role, label, keyboard behavior
6. **Motion spec** — entry, exit, state change animations
7. **Figma structure** — frame naming, variant property names
8. **Code tokens** — token names for handoff

For screen specs, always output:
1. **Screen anatomy** — regions and components
2. **All states** (Loading/Skeleton, Empty, Success, Error, Partial)
3. **Navigation pattern** — entry, exit, back behavior
4. **Responsive behavior** — how layout adapts
5. **Accessibility flow** — TalkBack/VoiceOver reading order

## Platform Selection Guide

| Context | Use |
|---------|-----|
| Native iOS app | Apple HIG exclusively — no Material components |
| Native Android app | Material Design 3 exclusively — no HIG components |
| Cross-platform (React Native, Flutter) | Platform-adaptive: HIG on iOS, MD3 on Android |
| Web app (any user) | Web design system with Material influence acceptable |
| PWA | Web design system — do not use native platform patterns |
| Hybrid (Capacitor/Ionic) | Web patterns — avoid platform-native illusions |
