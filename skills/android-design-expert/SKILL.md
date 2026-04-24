---
name: android-design-expert
version: "1.0.0"
description: "Expert Android design guidance following Material Design 3 — dynamic color, component tokens, adaptive layouts, motion system, and Jetpack Compose implementation patterns"
when_to_use: "Use for Material Design 3 guidance on Android screens — dynamic color, Compose components, adaptive layouts. NOT for scaffolding code (use android-feature-scaffold)."
argument-hint: "[screen-or-component-name]"
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

### 3.1 Design Principles

```
Elevated & Personal  — Dynamic color makes every device feel personal
Expressive           — Motion, type, and color convey meaning and delight
Adaptive             — Layouts transform gracefully across screen sizes
Accessible           — Meets WCAG AA by default with sufficient color contrast
```

### 3.2 Color System — Tonal Palettes and Color Roles

#### Tonal Palette Generation
```
M3 color is built from tonal palettes — 13 tones per hue:
  Tones: 0, 10, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 95, 98, 99, 100

Source color → Algorithm generates 5 key colors:
  Primary        — Brand identity, prominent buttons, active states
  Secondary      — Supporting UI, less prominent components
  Tertiary       — Contrasting accent, complementary color
  Neutral        — Surfaces, backgrounds, text
  Neutral Variant — Surface variants, outlines, subtle differentiators
  Error          — System-defined red palette for error states

Each key color generates a full tonal palette.
Color roles are mapped from specific tones in light and dark schemes.
```

#### Color Roles (Light / Dark)
```
┌───────────────────────────┬─────────────┬─────────────┐
│ Role                      │ Light Mode  │ Dark Mode   │
├───────────────────────────┼─────────────┼─────────────┤
│ primary                   │ tone 40     │ tone 80     │
│ onPrimary                 │ tone 100    │ tone 20     │
│ primaryContainer          │ tone 90     │ tone 30     │
│ onPrimaryContainer        │ tone 10     │ tone 90     │
│ secondary                 │ tone 40     │ tone 80     │
│ onSecondary               │ tone 100    │ tone 20     │
│ secondaryContainer        │ tone 90     │ tone 30     │
│ onSecondaryContainer      │ tone 10     │ tone 90     │
│ tertiary                  │ tone 40     │ tone 80     │
│ onTertiary                │ tone 100    │ tone 20     │
│ tertiaryContainer         │ tone 90     │ tone 30     │
│ onTertiaryContainer       │ tone 10     │ tone 90     │
│ error                     │ tone 40     │ tone 80     │
│ onError                   │ tone 100    │ tone 20     │
│ errorContainer            │ tone 90     │ tone 30     │
│ onErrorContainer          │ tone 10     │ tone 90     │
│ surface                   │ tone 98     │ tone 6      │
│ onSurface                 │ tone 10     │ tone 90     │
│ surfaceVariant            │ tone 90     │ tone 30     │
│ onSurfaceVariant          │ tone 30     │ tone 80     │
│ surfaceContainerLowest    │ tone 100    │ tone 4      │
│ surfaceContainerLow       │ tone 96     │ tone 10     │
│ surfaceContainer          │ tone 94     │ tone 12     │
│ surfaceContainerHigh      │ tone 92     │ tone 17     │
│ surfaceContainerHighest   │ tone 90     │ tone 22     │
│ outline                   │ tone 50     │ tone 60     │
│ outlineVariant            │ tone 80     │ tone 30     │
│ inverseSurface            │ tone 20     │ tone 90     │
│ inverseOnSurface          │ tone 95     │ tone 20     │
│ inversePrimary            │ tone 80     │ tone 40     │
│ scrim                     │ tone 0      │ tone 0      │
│ shadow                    │ tone 0      │ tone 0      │
└───────────────────────────┴─────────────┴─────────────┘
```

#### Dynamic Color (API 31+)
```
- System extracts wallpaper colors and generates M3 tonal palettes automatically
- App receives dynamicDarkColorScheme() / dynamicLightColorScheme()
- ALWAYS provide a fallback static color scheme for devices without dynamic color
- Brand-critical elements (logo, brand illustrations) should NOT use dynamic color
- Content colors (photos, album art) should NOT be tinted by dynamic color

Compose implementation:
  val colorScheme = when {
      dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
          if (darkTheme) dynamicDarkColorScheme(context)
          else dynamicLightColorScheme(context)
      }
      darkTheme -> darkColorScheme(...)
      else -> lightColorScheme(...)
  }
```

#### Color Rules
```
- ALWAYS use M3 color roles (MaterialTheme.colorScheme.primary) — never hardcode hex
- on* colors are MANDATORY for text/icons on their corresponding container
  (e.g., onPrimaryContainer text on primaryContainer background)
- Minimum contrast: 4.5:1 for normal text, 3:1 for large text (M3 ensures this by design)
- Surface elevation: use surfaceColorAtElevation() for tonal elevation (no shadows in M3)
- Dark mode: MANDATORY — M3 generates dark scheme automatically from the same source color
- Never use primary color for large background areas — use surface variants instead
```

### 3.3 Typography — M3 Type Scale

#### Type Scale
```
┌──────────────────┬──────────────┬──────────────┬──────────────────────────────┐
│ Role             │ Default Size │ Line Height  │ Usage                        │
├──────────────────┼──────────────┼──────────────┼──────────────────────────────┤
│ displayLarge     │ 57sp         │ 64sp         │ Hero text, major numbers     │
│ displayMedium    │ 45sp         │ 52sp         │ Large display text           │
│ displaySmall     │ 36sp         │ 44sp         │ Smaller display text         │
│ headlineLarge    │ 32sp         │ 40sp         │ Screen titles                │
│ headlineMedium   │ 28sp         │ 36sp         │ Section headers              │
│ headlineSmall    │ 24sp         │ 32sp         │ Sub-section headers          │
│ titleLarge       │ 22sp         │ 28sp         │ Top app bar title            │
│ titleMedium      │ 16sp / 500   │ 24sp         │ Card titles, nav labels      │
│ titleSmall       │ 14sp / 500   │ 20sp         │ Tab labels                   │
│ bodyLarge        │ 16sp         │ 24sp         │ Primary body text            │
│ bodyMedium       │ 14sp         │ 20sp         │ Secondary body text          │
│ bodySmall        │ 12sp         │ 16sp         │ Captions, metadata           │
│ labelLarge       │ 14sp / 500   │ 20sp         │ Buttons, prominent labels    │
│ labelMedium      │ 12sp / 500   │ 16sp         │ Navigation labels            │
│ labelSmall       │ 11sp / 500   │ 16sp         │ Smallest labels              │
└──────────────────┴──────────────┴──────────────┴──────────────────────────────┘

Rules:
- ALWAYS use sp units for text — enables system font scaling
- NEVER use dp or px for text sizes
- Use MaterialTheme.typography.bodyLarge, etc. in Compose
- Custom fonts: define via Typography() in your theme, mapped to M3 roles
- Test at 200% font scale (Settings → Accessibility → Font size → Largest)
- Line height included in the type scale — do not override
```

### 3.4 Layout System — Adaptive Design

#### Window Size Classes
```
┌─────────────────────┬──────────────────┬──────────────────────────────────┐
│ Width Class         │ Breakpoint       │ Devices                          │
├─────────────────────┼──────────────────┼──────────────────────────────────┤
│ Compact             │ < 600dp          │ Phone portrait, small foldable   │
│ Medium              │ 600dp - 839dp    │ Tablet portrait, foldable open   │
│ Expanded            │ >= 840dp         │ Tablet landscape, desktop        │
├─────────────────────┼──────────────────┼──────────────────────────────────┤
│ Height Class        │ Breakpoint       │ Context                          │
├─────────────────────┼──────────────────┼──────────────────────────────────┤
│ Compact             │ < 480dp          │ Phone landscape                  │
│ Medium              │ 480dp - 899dp    │ Phone portrait, tablet landscape │
│ Expanded            │ >= 900dp         │ Tablet portrait                  │
└─────────────────────┴──────────────────┴──────────────────────────────────┘
```

#### Canonical Layouts
```
M3 defines four canonical layouts that adapt across window sizes:

1. LIST-DETAIL
   Compact:  Full-screen list → full-screen detail (navigation push)
   Medium:   Side-by-side list (1/3) + detail (2/3)
   Expanded: Side-by-side list (1/3) + detail (2/3) with nav rail

2. FEED
   Compact:  Single-column scrolling feed
   Medium:   Two-column masonry/grid feed
   Expanded: Three-column grid feed with nav rail

3. SUPPORTING PANE
   Compact:  Stacked — main content above, supporting below (or bottom sheet)
   Medium:   Side-by-side with 60/40 split
   Expanded: Side-by-side with 60/40 split + nav rail

4. FULL-SCREEN / FOCUS
   Compact:  Full-bleed content (media player, camera, map)
   Medium:   Full-bleed with optional side controls
   Expanded: Full-bleed with persistent side panel

Implementation:
  Use WindowSizeClass from Compose Material 3:
    val windowSizeClass = currentWindowAdaptiveInfo().windowSizeClass
    when (windowSizeClass.windowWidthSizeClass) {
        WindowWidthSizeClass.COMPACT -> CompactLayout()
        WindowWidthSizeClass.MEDIUM -> MediumLayout()
        WindowWidthSizeClass.EXPANDED -> ExpandedLayout()
    }
```

#### Grid and Spacing
```
Margins and gutters:
  Compact:   16dp margins, 8dp gutters
  Medium:    24dp margins, 16dp gutters
  Expanded:  24dp margins, 24dp gutters

Column grid:
  Compact:   4 columns
  Medium:    8 columns (12 on some layouts)
  Expanded:  12 columns

Spacing scale (multiples of 4dp):
  4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96

Component padding:
  Cards:        16dp internal padding
  List items:   16dp horizontal, 8-12dp vertical
  Dialogs:      24dp padding
  Bottom sheets: 16dp horizontal, varies vertical

Corner radius (M3 shape scale):
  None:         0dp     — Full-bleed elements
  Extra Small:  4dp     — Chips, small badges
  Small:        8dp     — Cards in dense layouts
  Medium:       12dp    — Cards, dialogs, text fields
  Large:        16dp    — FAB, bottom sheets
  Extra Large:  28dp    — Large FAB, navigation drawer
  Full:         50%     — Circular elements (avatar, icon button)
```

### 3.5 Navigation Patterns

#### Navigation Component Selection
```
┌────────────────────────┬──────────────────────────────────────────────┐
│ Window Width           │ Navigation Component                         │
├────────────────────────┼──────────────────────────────────────────────┤
│ Compact (< 600dp)      │ Bottom Navigation Bar (3-5 destinations)     │
│ Medium (600-839dp)     │ Navigation Rail (vertical, side)             │
│ Expanded (>= 840dp)   │ Navigation Drawer (persistent, side)         │
└────────────────────────┴──────────────────────────────────────────────┘

NavigationSuiteScaffold (Compose):
  Automatically switches between bar/rail/drawer based on window size.

Rules:
  - Bottom nav: 3-5 destinations. Use Material Symbols. Active = filled, inactive = outlined
  - Nav rail: can include FAB at top. Labels optional but recommended
  - Nav drawer: full labels always visible. Group destinations with dividers
  - Top app bar: small (default), medium (two-line), large (prominent headline)
  - Top app bar scrolling: .pinnedScroll, .enterAlwaysScroll, .exitUntilCollapsedScroll
```

#### Navigation Architecture
```
Top-level destinations:
  → NavigationSuiteScaffold with NavHost per destination

Sub-navigation within a destination:
  → Tabs (scrollable or fixed) at the top of content

Detail from list:
  → NavHost navigation with slide transition
  → On expanded: List-Detail canonical layout (no navigation, side-by-side)

Modal tasks (create, edit):
  → Full-screen dialog (ModalBottomSheet or full-screen activity)
  → Save/close in top app bar

Contextual actions:
  → DropdownMenu (3+ actions)
  → BottomSheet (complex selection or confirmation)
  → AlertDialog (confirmation, destructive actions)
```

### 3.6 Component Patterns

#### Buttons
```
M3 Button hierarchy (choose ONE primary per screen):
  Filled Button         → Highest emphasis. Primary CTA. containerColor = primary
  Filled Tonal Button   → Medium emphasis. secondary container color
  Outlined Button       → Low emphasis. Outlined, transparent fill
  Text Button           → Lowest emphasis. Dialogs, inline actions
  Elevated Button       → Medium emphasis with shadow. Use sparingly

FAB (Floating Action Button):
  FAB              → 56dp, primary action for the screen
  Small FAB        → 40dp, secondary floating action
  Large FAB        → 96dp, rare — only for the single most important action
  Extended FAB     → Icon + label, scrolls to collapse to regular FAB

Icon Buttons:
  Standard         → No container. Toolbar actions
  Filled           → Primary container fill
  Filled Tonal     → Secondary container fill
  Outlined         → Outlined, transparent fill

Rules:
  - ONE primary (Filled) button per screen maximum
  - Minimum touch target: 48x48dp — always
  - Button labels: sentence case ("Create account" not "CREATE ACCOUNT")
  - Icon + label: icon on the leading side
  - Loading: CircularProgressIndicator replacing content, button disabled
  - Destructive: use error color role
```

#### Cards
```
Card types:
  Filled Card      → surfaceContainerHighest fill, no elevation (default)
  Elevated Card    → surfaceContainerLow fill, level 1 elevation
  Outlined Card    → surface fill, outlineVariant border

Card rules:
  - Implicit action: entire card is tappable (single action)
  - Explicit actions: action buttons at bottom of card
  - Do NOT combine implicit tap + explicit buttons on the same card
  - Internal padding: 16dp
  - Corner radius: Medium (12dp)
  - Content order: media → header → supporting text → actions
  - Ripple effect on tap (Compose: Modifier.clickable with default indication)
```

#### Text Fields
```
Filled TextField (default):
  - Container with surfaceContainerHighest background
  - Active indicator (bottom line) changes color on focus
  - Recommended for most forms

Outlined TextField:
  - Transparent with outline border
  - Label moves to border on focus
  - Use in sparse layouts or when multiple fields are adjacent

Rules:
  - Label: always visible — floats above input on focus
  - Placeholder: optional hint text — disappears on input (secondary to label)
  - Helper text: below the field for format guidance
  - Error text: replaces helper text in error color with error icon
  - Character counter: below field, trailing side
  - Leading icon: optional, for input context (search, email)
  - Trailing icon: clear button, visibility toggle, dropdown arrow
  - Minimum height: 56dp
```

#### Bottom Sheets
```
Standard:    Scrollable content, partially covers screen. Drag handle at top.
Modal:       Scrim overlay, blocks interaction with content behind.

Rules:
  - Drag handle: always visible (4dp × 32dp, rounded, onSurfaceVariant)
  - Initial height: content-dependent, not arbitrary
  - Expandable: half → full with drag gesture
  - Dismissible: drag down or tap scrim (modal)
  - Corner radius: Extra Large (28dp) top corners only
  - Do not put critical actions in bottom sheets — users may dismiss accidentally
```

### 3.7 Motion System

#### M3 Easing and Duration
```
Easing curves:
  emphasized         → CubicBezier(0.2, 0.0, 0.0, 1.0) — Primary transitions, enter/exit
  emphasizedDecelerate → CubicBezier(0.05, 0.7, 0.1, 1.0) — Enter only
  emphasizedAccelerate → CubicBezier(0.3, 0.0, 0.8, 0.15) — Exit only
  standard           → CubicBezier(0.2, 0.0, 0.0, 1.0) — Small components, state changes
  standardDecelerate → CubicBezier(0.0, 0.0, 0.0, 1.0) — Enter only
  standardAccelerate → CubicBezier(0.3, 0.0, 1.0, 1.0) — Exit only

Duration tokens:
  Short 1:   50ms    — Micro-interactions (ripple, icon change)
  Short 2:   100ms   — Small component state changes
  Short 3:   150ms   — Selection, toggles
  Short 4:   200ms   — Standard component animations
  Medium 1:  250ms   — Card expand, menu open
  Medium 2:  300ms   — Navigation transitions
  Medium 3:  350ms   — Sheet expand
  Medium 4:  400ms   — Larger element transitions
  Long 1:    450ms   — Complex transitions
  Long 2:    500ms   — Full-screen transitions
  Long 3:    550ms   — Large layout changes
  Long 4:    600ms   — Staggered animations
  Extra Long 1-4: 700-1000ms — Page-level transitions

Transition patterns:
  Container transform   — Element morphs into new screen (shared element)
  Shared axis           — Spatial relationship (forward/backward, up/down)
  Fade through          — No strong spatial relationship (tab switch)
  Fade                  — Simple appear/disappear (dialogs, menus)
```

#### Motion Rules
```
- Respect "Remove animations" system setting (Settings → Accessibility)
- AnimatedVisibility for enter/exit with appropriate transition
- Container transform for list → detail transitions (SharedTransitionLayout in Compose)
- Ripple is mandatory on all clickable surfaces — never remove default indication
- Stagger: delay each item by Short1 (50ms) for sequential animations
- Physics-based: use spring() for user-gesture-driven animations
```

### 3.8 Material Symbols

```
Symbol styles:
  Outlined (default)  — Standard weight, clean lines. Use for inactive states
  Rounded            — Softer, rounded terminals
  Sharp              — Angular terminals

Optical size: match to context
  20dp — Dense UI, chips, badges
  24dp — Standard UI, buttons, lists (default)
  40dp — Prominent placement
  48dp — Hero/feature display

Weight: 100-700 (match to adjacent text weight)
  Default: 400 (Regular)

Fill:
  0 (outlined) → inactive, unselected states
  1 (filled) → active, selected states (e.g., nav bar selected)

Grade: fine-tune weight without changing size
  -25: reduce emphasis
  0: default
  200: increase emphasis

Rules:
  - Active nav destination: filled (fill=1). Inactive: outlined (fill=0)
  - Icon + text label: 24dp icon with 4dp gap
  - Icon buttons: 24dp icon in 48dp touch target (40dp visual container)
  - Decorative icons: set importantForAccessibility="no"
  - Meaningful icons: set contentDescription
```

### 3.9 Widgets (Glance/App Widgets)

```
Widget sizes (cells):
  Small:        2×1, 3×1        — Single action or key metric
  Medium:       2×2, 3×2, 4×2   — Summary with a few actions
  Large:        3×3, 4×3, 5×3   — Rich information display

Design rules:
  - Use M3 color roles from the widget theme
  - Corner radius: system-managed (matches launcher)
  - Internal padding: 16dp
  - Touch targets: 48dp minimum
  - No scrolling within widgets (except on API 31+)
  - Use Glance (Jetpack Glance) for Compose-based widget development
  - Deep link taps into the relevant app screen
  - Configuration: use widget picker or reconfigurable activity
  - Dynamic content: use WorkManager for periodic updates (min 15 min)
  - Rounded inner corners: system radius minus internal padding (r - 16dp)
```

### 3.10 Dark Theme

```
M3 Dark Theme rules:
  - Surface colors shift to darker tones automatically from the tonal palette
  - Elevation in dark theme: tonal elevation (surface tint overlay), NOT shadow
  - Primary colors shift to lighter tones (tone 80 instead of 40)
  - Large filled surfaces use surface roles, NEVER primary color
  - Images and illustrations: slightly reduce brightness/saturation if needed
  - System bars (status, nav): transparent or surface color — never primary
  - Text: onSurface (tone 90) — high contrast against dark surfaces

  surfaceColorAtElevation() replaces shadow elevation:
    Level 0:  surface tone (6 in dark)
    Level 1:  +5% primary overlay
    Level 2:  +8% primary overlay
    Level 3:  +11% primary overlay
    Level 4:  +12% primary overlay
    Level 5:  +14% primary overlay
```

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
