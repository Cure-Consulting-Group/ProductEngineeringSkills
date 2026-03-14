---
name: design-system
description: "Build cross-platform design systems — design tokens, component libraries, Storybook/Catalog setup, theme architecture, and platform consistency"
argument-hint: "[project-or-platform]"
---

# Design System

Build and maintain cross-platform design systems with design tokens as the single source of truth. Covers token architecture, component libraries for Android (Compose), iOS (SwiftUI), and Web (React/Tailwind), documentation and playground setup, governance processes, and cross-platform consistency rules. A design system is not a component library -- it is the shared language between design and engineering.

## Step 1: Classify the Design System Need

| Need | Scope | Typical Trigger |
|------|-------|-----------------|
| Greenfield | Build a design system from scratch for a new product or org | New product launch, rebrand, first multi-platform effort |
| Unify Existing | Consolidate inconsistent UI across platforms into a single system | Visual inconsistencies, designer/engineer friction, scaling team |
| Add Platform | Extend an existing design system to a new platform (e.g., add iOS to existing web system) | Launching on a new platform, cross-platform product expansion |
| Token Migration | Move from hardcoded values to design tokens without changing the visual output | Tech debt cleanup, theme support, dark mode initiative |

## Step 2: Gather Context

1. **Platforms** -- which platforms need to be supported (Android, iOS, Web, all three)? Which is the primary platform?
2. **Existing components** -- is there an existing component library, even informal? What framework (Compose, SwiftUI, React, Vue)?
3. **Brand guidelines** -- does a brand guide exist with colors, typography, spacing rules? Or are we defining this from scratch?
4. **Design tool** -- what does the design team use (Figma, Sketch, Adobe XD)? Are there existing Figma components?
5. **Team size** -- how many designers and engineers will use and contribute to the system? Is there a dedicated design systems team?
6. **Accessibility requirements** -- what WCAG level is required (AA minimum, AAA target)? Any platform-specific requirements?
7. **Theme requirements** -- light/dark mode? Multiple brand themes? White-label support?

## Step 3: Design Token Architecture

### Token Hierarchy

```
Tokens follow a three-level hierarchy. Never skip levels.

Level 1 — Global tokens (raw values)
  The complete palette of available values. Not used directly in components.
  Examples:
    color.blue.500:     #3B82F6
    color.gray.100:     #F3F4F6
    font.size.16:       16
    spacing.4:          4
    radius.8:           8

Level 2 — Alias tokens (semantic meaning)
  Map global tokens to semantic purpose. These change between themes.
  Examples:
    color.primary:          {color.blue.500}
    color.surface:          {color.gray.100}       // light theme
    color.surface:          {color.gray.900}       // dark theme
    color.text.primary:     {color.gray.900}       // light theme
    color.text.primary:     {color.gray.50}        // dark theme
    font.size.body:         {font.size.16}
    spacing.component.gap:  {spacing.4}

Level 3 — Component tokens (component-specific)
  Map alias tokens to specific component properties. Optional but powerful.
  Examples:
    button.primary.background:    {color.primary}
    button.primary.text:          {color.text.on-primary}
    button.border-radius:         {radius.8}
    card.padding:                 {spacing.component.gap}
    input.border.color:           {color.border.default}
```

### Token Categories

```
Category        Token Examples                          Notes
──────────────────────────────────────────────────────────────────
Color           primary, secondary, surface, error,     Must pass WCAG AA contrast
                text.primary, text.secondary,           ratios for text/background
                border, divider, overlay                combinations

Typography      font.family (sans, serif, mono)         Use system fonts where
                font.size (xs through 3xl)              possible for performance.
                font.weight (regular, medium, bold)     Define type scale with
                line-height (tight, normal, relaxed)    consistent ratios.
                letter-spacing (tight, normal, wide)

Spacing         4, 8, 12, 16, 20, 24, 32, 40, 48,     8pt grid system.
                56, 64, 80, 96                          All spacing values are
                                                        multiples of 4.

Elevation       shadow.sm, shadow.md, shadow.lg,        Platform-specific
                shadow.xl                               implementation (Android
                                                        elevation, CSS box-shadow)

Motion          duration.fast (150ms)                   Respect prefers-reduced-
                duration.normal (300ms)                 motion on web. Follow
                duration.slow (500ms)                   platform conventions
                easing.standard, easing.decelerate      (Material Motion, UIKit
                easing.accelerate                       spring animations).

Breakpoints     sm (640px), md (768px), lg (1024px),    Web only. Mobile uses
                xl (1280px), 2xl (1536px)               adaptive layout breakpoints
                                                        built into platform.

Border Radius   none (0), sm (4), md (8), lg (12),     Use consistently. Do not
                xl (16), full (9999)                    mix rounded and sharp
                                                        corners in the same context.
```

### Token Format and Tooling

```
Source of truth: tokens.json (or tokens.yaml)
  Store in dedicated design-system repo or monorepo package.
  Versioned, reviewed, and released like code.

Example tokens.json:
{
  "color": {
    "global": {
      "blue": {
        "50":  { "value": "#EFF6FF" },
        "500": { "value": "#3B82F6" },
        "900": { "value": "#1E3A8A" }
      }
    },
    "alias": {
      "primary":    { "value": "{color.global.blue.500}" },
      "on-primary": { "value": "{color.global.white}" }
    }
  },
  "spacing": {
    "1": { "value": "4px" },
    "2": { "value": "8px" },
    "3": { "value": "12px" },
    "4": { "value": "16px" }
  }
}

Platform transforms (Style Dictionary):
  - Web:     CSS custom properties (--color-primary: #3B82F6)
  - Android: Kotlin object / XML resource (ColorPrimary = Color(0xFF3B82F6))
  - iOS:     Swift Color extension (Color.primary = Color(hex: 0x3B82F6))

Build pipeline:
  tokens.json → Style Dictionary → platform-specific output files
  Run on CI: tokens change → rebuild → publish platform packages
```

### Dark Mode and Theme Variants

```
Theme architecture:
  Each theme is a complete set of alias tokens.
  Global tokens do NOT change between themes.
  Only alias tokens (Level 2) swap values.

  themes/
    light.json    — alias token values for light mode
    dark.json     — alias token values for dark mode
    brand-a.json  — alias token values for white-label brand A (if applicable)

Implementation per platform:
  Web:     CSS custom properties on :root and [data-theme="dark"]
           Or Tailwind dark: variant with class strategy
  Android: MaterialTheme with dynamicColorScheme / custom ColorScheme
           isSystemInDarkTheme() for automatic switching
  iOS:     Color assets with light/dark variants in Asset Catalog
           Or @Environment(\.colorScheme) for programmatic switching

Rule: Never hardcode color values in components. Always reference tokens.
      A component that works in light mode must work in dark mode without
      code changes — only token values change.
```

## Step 4: Component Library Per Platform

### Android — Jetpack Compose

```kotlin
// design-system/src/main/kotlin/com/example/ds/theme/Theme.kt
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        shapes = AppShapes,
        content = content
    )
}

// design-system/src/main/kotlin/com/example/ds/components/Button.kt
@Composable
fun PrimaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    loading: Boolean = false,
) {
    Button(
        onClick = onClick,
        modifier = modifier.height(48.dp),  // minimum touch target
        enabled = enabled && !loading,
        shape = MaterialTheme.shapes.medium,
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.primary,
            contentColor = MaterialTheme.colorScheme.onPrimary,
        ),
    ) {
        if (loading) {
            CircularProgressIndicator(
                modifier = Modifier.size(20.dp),
                color = MaterialTheme.colorScheme.onPrimary,
                strokeWidth = 2.dp,
            )
        } else {
            Text(text = text, style = MaterialTheme.typography.labelLarge)
        }
    }
}

// Component structure:
// design-system/
//   src/main/kotlin/com/example/ds/
//     theme/        — Theme.kt, Color.kt, Typography.kt, Shape.kt
//     tokens/       — Generated token values from Style Dictionary
//     components/   — Button, Card, TextField, Dialog, etc.
//     icons/        — Icon set (Material Icons extended or custom)
```

### iOS — SwiftUI

```swift
// DesignSystem/Sources/Theme/AppTheme.swift
public struct AppTheme {
    public let colors: AppColors
    public let typography: AppTypography
    public let spacing: AppSpacing

    public static let light = AppTheme(
        colors: .light,
        typography: .default,
        spacing: .default
    )

    public static let dark = AppTheme(
        colors: .dark,
        typography: .default,
        spacing: .default
    )
}

// DesignSystem/Sources/Components/PrimaryButton.swift
public struct PrimaryButton: View {
    let title: String
    let action: () -> Void
    var isLoading: Bool = false
    var isEnabled: Bool = true

    @Environment(\.appTheme) private var theme

    public var body: some View {
        Button(action: action) {
            Group {
                if isLoading {
                    ProgressView()
                        .tint(theme.colors.onPrimary)
                } else {
                    Text(title)
                        .font(theme.typography.labelLarge)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 48)  // minimum touch target
        }
        .buttonStyle(.borderedProminent)
        .tint(theme.colors.primary)
        .disabled(!isEnabled || isLoading)
        .accessibilityLabel(title)
        .accessibilityHint(isLoading ? "Loading" : "")
    }
}

// Package structure:
// DesignSystem/
//   Sources/
//     Theme/        — AppTheme, AppColors, AppTypography, AppSpacing
//     Tokens/       — Generated token values from Style Dictionary
//     Components/   — Button, Card, TextField, etc.
//     Modifiers/    — Custom ViewModifiers (shadow, shimmer, etc.)
//   Tests/          — Snapshot tests for components
```

### Web — React + Tailwind

```typescript
// design-system/src/theme/tailwind-tokens.ts
// Generated from Style Dictionary — do not edit manually
export const tokens = {
  colors: {
    primary: {
      DEFAULT: 'var(--color-primary)',
      foreground: 'var(--color-on-primary)',
    },
    secondary: {
      DEFAULT: 'var(--color-secondary)',
      foreground: 'var(--color-on-secondary)',
    },
    surface: {
      DEFAULT: 'var(--color-surface)',
      foreground: 'var(--color-on-surface)',
    },
    destructive: {
      DEFAULT: 'var(--color-error)',
      foreground: 'var(--color-on-error)',
    },
  },
} as const;

// design-system/src/components/button.tsx
// Following shadcn/Radix patterns — composable, accessible by default
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "../utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium " +
  "ring-offset-background transition-colors focus-visible:outline-none " +
  "focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none " +
  "disabled:opacity-50",
  {
    variants: {
      variant: {
        primary:     "bg-primary text-primary-foreground hover:bg-primary/90",
        secondary:   "bg-secondary text-secondary-foreground hover:bg-secondary/90",
        outline:     "border border-input bg-background hover:bg-accent",
        ghost:       "hover:bg-accent hover:text-accent-foreground",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      },
      size: {
        sm: "h-9 px-3",
        md: "h-10 px-4 py-2",
        lg: "h-12 px-8 text-base",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

export function Button({
  className, variant, size, asChild, loading, children, disabled, ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <Spinner className="mr-2 h-4 w-4" /> : null}
      {children}
    </Comp>
  );
}

// Package structure:
// design-system/
//   src/
//     theme/        — tokens, CSS custom properties, Tailwind config
//     components/   — Button, Card, Input, Dialog, etc. (Radix primitives)
//     utils/        — cn(), token helpers
//   stories/        — Storybook stories for each component
```

## Step 5: Documentation and Playground

### Web — Storybook

```
Setup:
  npx storybook@latest init
  Configure for React + Tailwind
  Deploy to Chromatic or Vercel for team access

Story structure per component:
  ComponentName.stories.tsx:
    - Default (primary variant, no props)
    - All Variants (visual grid of all variant + size combinations)
    - Interactive (with args/controls for live editing)
    - Accessibility (with a11y addon checks visible)
    - Dark Mode (wrapped in dark theme provider)

Required Storybook addons:
  @storybook/addon-a11y          — automated accessibility checks
  @storybook/addon-designs       — embed Figma frames
  @storybook/addon-interactions  — test user flows
  storybook-dark-mode            — theme toggle
```

### Android — Showkase

```kotlin
// Add Showkase for component catalog
// build.gradle.kts
dependencies {
    implementation("com.airbnb.android:showkase:1.0.3")
    ksp("com.airbnb.android:showkase-processor:1.0.3")
}

// Annotate components
@ShowkaseComposable(name = "Primary Button", group = "Buttons")
@Composable
fun PrimaryButtonPreview() {
    AppTheme {
        PrimaryButton(text = "Click me", onClick = {})
    }
}

// Showkase browser activity is auto-generated
// Launch in debug builds for component browsing
```

### iOS — SwiftUI Previews Catalog

```swift
// Create a dedicated preview catalog target
// DesignSystemCatalog/CatalogApp.swift
@main
struct CatalogApp: App {
    var body: some Scene {
        WindowGroup {
            NavigationStack {
                List {
                    Section("Buttons") {
                        NavigationLink("Primary Button") { ButtonCatalog() }
                    }
                    Section("Cards") {
                        NavigationLink("Content Card") { CardCatalog() }
                    }
                    // ... all components
                }
                .navigationTitle("Design System")
            }
        }
    }
}

// DesignSystemCatalog/ButtonCatalog.swift
struct ButtonCatalog: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Text("Primary Button").font(.headline)
                PrimaryButton(title: "Default", action: {})
                PrimaryButton(title: "Loading", action: {}, isLoading: true)
                PrimaryButton(title: "Disabled", action: {}, isEnabled: false)
            }
            .padding()
        }
    }
}
```

### Component Documentation Requirements

```
Every component must document:
  1. Name and description
  2. Props/parameters with types and defaults
  3. Variants (visual examples of each)
  4. Accessibility notes:
     - Minimum touch target (48x48dp Android, 44x44pt iOS)
     - Screen reader behavior (what is announced)
     - Keyboard navigation (web)
     - Color contrast compliance
  5. Usage examples (code snippets)
  6. Do/Don't examples:
     DO: Use PrimaryButton for the main action on a screen
     DON'T: Use more than one PrimaryButton per screen section
     DO: Provide loading state for async actions
     DON'T: Disable the button without explaining why (use helper text)
```

## Step 6: Governance

### Contribution Process

```
1. Propose: Open an issue/RFC describing the new component or token change
   - What problem does it solve?
   - Which platforms need it?
   - Figma design attached (required)

2. Design review: Design lead approves visual design and token usage
   - Follows token hierarchy (no hardcoded values)
   - Meets accessibility requirements (WCAG AA minimum)
   - Consistent with existing component patterns

3. Implementation: Build on all required platforms
   - Must include: component code, tests, documentation, stories/previews
   - Must pass: accessibility checks, visual regression tests

4. Code review: Design system team reviews
   - API consistency across platforms (same props/behavior)
   - Token usage (no magic numbers)
   - Accessibility (screen reader, touch targets, contrast)

5. Release: Merge and publish new version
   - Update changelog
   - Bump version (semver)
   - Notify consuming teams
```

### Versioning and Breaking Changes

```
Semantic versioning (MAJOR.MINOR.PATCH):
  PATCH: bug fix, accessibility improvement, internal refactor
  MINOR: new component, new variant, new token (backward compatible)
  MAJOR: removed component, changed API, renamed token

Breaking change policy:
  - Deprecate first, remove in next major version
  - Minimum 1 release cycle deprecation notice
  - Provide migration guide for all breaking changes
  - Never break dark mode or accessibility in any release
```

## Step 7: Cross-Platform Consistency Rules

### Shared Naming Conventions

```
Components use the SAME name across all platforms:
  PrimaryButton   (not CTA, ActionButton, MainButton)
  ContentCard     (not InfoCard, DataCard, ItemCard)
  TextInput       (not TextField, InputField, EditText)
  BottomSheet     (not Modal, Drawer, ActionSheet)

Tokens use the SAME name across all platforms:
  color.primary   (not brandColor, accentColor, mainColor)
  spacing.md      (not spacing.medium, spacing.3, gap.16)
  font.size.body  (not font.size.16, fontSize.regular, textSize.normal)

Exceptions (platform-appropriate deviations):
  Navigation: Tabs (Android/iOS) vs Sidebar (Web desktop) — OK
  Selection: Switch (Android) vs Toggle (iOS) — use platform name
  System UI: follows platform conventions (Android nav bar, iOS home indicator)
```

### Equivalent Components Across Platforms

```
┌──────────────────┬─────────────────────┬──────────────────┬──────────────────┐
│ Component        │ Android (Compose)   │ iOS (SwiftUI)    │ Web (React)      │
├──────────────────┼─────────────────────┼──────────────────┼──────────────────┤
│ PrimaryButton    │ Button + Material3  │ Button bordered  │ <Button>         │
│ TextInput        │ OutlinedTextField   │ TextField        │ <Input>          │
│ ContentCard      │ Card + Material3    │ Custom View      │ <Card>           │
│ BottomSheet      │ ModalBottomSheet    │ .sheet()         │ <Sheet> (Radix)  │
│ Dialog           │ AlertDialog         │ .alert()         │ <Dialog> (Radix) │
│ TopBar           │ TopAppBar           │ .navigationTitle │ <Header>         │
│ LoadingSpinner   │ CircularProgress    │ ProgressView     │ <Spinner>        │
│ Avatar           │ Custom Composable   │ Custom View      │ <Avatar>         │
│ Badge            │ Badge + Material3   │ Custom View      │ <Badge>          │
│ Toast            │ Snackbar            │ Custom overlay   │ <Toast> (Sonner) │
└──────────────────┴─────────────────────┴──────────────────┴──────────────────┘

Rule: Same visual weight, same semantic meaning, platform-native interaction patterns.
      A PrimaryButton should LOOK the same across platforms (same color, same radius)
      but FEEL native (Material ripple on Android, highlight on iOS, hover on Web).
```

### Platform-Appropriate Deviations

```
These differences are EXPECTED and CORRECT:
  - Typography: SF Pro (iOS), Roboto (Android), Inter/system (Web)
  - Navigation: Bottom tabs (mobile) vs sidebar (web desktop)
  - Interactions: ripple (Android), highlight (iOS), hover (Web)
  - System UI: status bar, navigation bar, safe areas — follow platform
  - Haptics: available on mobile, not on web
  - Gestures: swipe-to-dismiss, pull-to-refresh — platform patterns

These differences are BUGS and must be fixed:
  - Different colors for the same semantic token across platforms
  - Different spacing/padding for equivalent components
  - Different border radius for the same component type
  - Missing dark mode support on any platform
  - Accessibility works on one platform but not others
```

## Step 8: Output

```
DESIGN SYSTEM PLAN
Project: [NAME]
Date: [TODAY]
Prepared by: [NAME]
Platforms: [Android / iOS / Web]

SYSTEM SUMMARY
┌──────────────────────┬────────────────────────────────────┐
│ Field                │ Value                              │
├──────────────────────┼────────────────────────────────────┤
│ Design System Need   │ [From Step 1 classification]       │
│ Platforms            │ [List]                             │
│ Token Count          │ [Global / Alias / Component]       │
│ Component Count      │ [Number per platform]              │
│ Theme Support        │ [Light / Dark / Custom]            │
│ Accessibility Level  │ [WCAG AA / AAA]                    │
│ Documentation        │ [Storybook / Showkase / Catalog]   │
│ Distribution         │ [npm / Maven / SPM]                │
└──────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Design token architecture (global, alias, component levels)
  - [ ] Token source file (tokens.json) with Style Dictionary config
  - [ ] Component library scaffold per platform
  - [ ] Theme support (light + dark mode minimum)
  - [ ] Documentation/playground setup
  - [ ] Governance process and contribution guide
  - [ ] Cross-platform consistency rules

CROSS-REFERENCES:
  - /product-design — for design principles and platform guidelines
  - /android-design-expert — for Android-specific Material Design 3 patterns
  - /ios-design-expert — for iOS-specific Human Interface Guidelines
  - /web-design-expert — for web-specific design patterns
  - /accessibility-audit — for WCAG compliance verification
```
