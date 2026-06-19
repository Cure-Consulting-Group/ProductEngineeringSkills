# ios-design-expert: detailed reference

> Reference material for the `ios-design-expert` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 3: HIG Design Principles (Always Apply)

## Step 3: HIG Design Principles (Always Apply)

### 3.1 Platform Fundamentals

Apple design is built on six pillars. Every design decision must align:

```
Aesthetic Integrity — Visual design matches the app's purpose and personality
Consistency        — Follows platform conventions so users transfer existing knowledge
Direct Manipulation — Users feel they are directly interacting with on-screen content
Feedback           — Every action produces a perceivable response (visual, haptic, audio)
Metaphors          — Virtual objects and actions mirror familiar physical-world experiences
User Control       — The user initiates and controls actions; the app confirms destructive ones
```

### 3.2 Layout System

#### Safe Areas and Margins
```
Status bar:          Dynamic height (54pt on Dynamic Island devices, 44pt on notch, 20pt legacy)
Navigation bar:      44pt standard height (large title: 96pt expanded → 44pt collapsed)
Tab bar:             49pt standard (83pt on devices without home button due to home indicator)
Home indicator:      34pt bottom inset on Face ID devices
Layout margins:      16pt (compact width), 20pt (regular width)
Readable content:    System-managed readable width guide — max ~672pt on iPad
```

#### Size Classes and Adaptivity
```
┌─────────────────────────────────────────────────────────────────────┐
│ Device              │ Portrait          │ Landscape               │
├─────────────────────┼───────────────────┼──────────────────────────┤
│ iPhone SE/mini      │ compact W × regular H │ compact W × compact H │
│ iPhone standard     │ compact W × regular H │ compact W × compact H │
│ iPhone Pro Max      │ compact W × regular H │ regular W × compact H │
│ iPad                │ regular W × regular H │ regular W × regular H │
│ iPad Split (1/3)    │ compact W × regular H │ compact W × regular H │
│ iPad Split (1/2)    │ compact W × regular H │ regular W × regular H │
│ iPad Split (2/3)    │ regular W × regular H │ regular W × regular H │
└─────────────────────┴───────────────────┴──────────────────────────┘

Design rules:
- ALWAYS design for compact width first, then adapt for regular width
- Use ViewThatFits or AnyLayout for adaptive layouts
- Use NavigationSplitView for sidebar patterns on iPad
- Never assume a fixed screen size — always use geometry-relative layouts
```

#### Grid and Spacing
```
Base unit:           4pt (iOS uses a 4pt sub-grid within the 8pt macro grid)
Spacing scale:       4, 8, 12, 16, 20, 24, 32, 40, 48, 64
Component padding:   Standard system spacing — 16pt horizontal, 12pt vertical (cells)
Section spacing:     35pt between grouped sections in List/Form
Corner radius:       10pt (cards), 12pt (sheets), continuous corner curve (squircle, not circular)
                     Use .cornerRadius with .continuous style, not .circular
```

### 3.3 Typography — Dynamic Type

iOS uses the SF Pro type system with mandatory Dynamic Type support.

#### Type Styles (Default Sizes at Large — the system default)
```
┌──────────────────┬───────┬──────────┬─────────────────────────────────────┐
│ Style            │ Size  │ Weight   │ Usage                               │
├──────────────────┼───────┼──────────┼─────────────────────────────────────┤
│ .largeTitle      │ 34pt  │ Regular  │ Top-level screen titles             │
│ .title           │ 28pt  │ Regular  │ Section headers, key information    │
│ .title2          │ 22pt  │ Regular  │ Secondary section headers           │
│ .title3          │ 20pt  │ Regular  │ Tertiary headers                    │
│ .headline        │ 17pt  │ Semibold │ Emphasized body text, cell titles   │
│ .body            │ 17pt  │ Regular  │ Primary content text                │
│ .callout         │ 16pt  │ Regular  │ Secondary content, callouts         │
│ .subheadline     │ 15pt  │ Regular  │ Supporting text below headlines     │
│ .footnote        │ 13pt  │ Regular  │ Footnotes, timestamps, metadata    │
│ .caption         │ 12pt  │ Regular  │ Labels, tertiary information        │
│ .caption2        │ 11pt  │ Regular  │ Smallest readable text              │
├──────────────────┼───────┼──────────┼─────────────────────────────────────┤
│ Accessibility    │       │          │                                     │
│ sizes scale up   │       │          │ AX1: ~1.24x, AX2: ~1.47x,          │
│ from Large       │       │          │ AX3: ~1.71x, AX4: ~1.94x,          │
│                  │       │          │ AX5: ~2.35x                         │
└──────────────────┴───────┴──────────┴─────────────────────────────────────┘

Rules:
- ALWAYS use system text styles (.font(.body), .font(.headline)) — never hardcoded sizes
- Custom fonts MUST scale with Dynamic Type via UIFontMetrics or @ScaledMetric
- Test at EVERY Dynamic Type size, including AX5 (largest accessibility size)
- Line height is automatic with system styles — do not override unless brand-critical
- Truncation strategy: .lineLimit(nil) for primary content, truncate secondary content
- Use .minimumScaleFactor(0.75) sparingly and only for fixed-width containers
```

#### Custom Font Scaling
```swift
// SwiftUI
@ScaledMetric(relativeTo: .body) var customSize: CGFloat = 17

// UIKit
let metrics = UIFontMetrics(forTextStyle: .body)
let scaled = metrics.scaledFont(for: customFont)
```

### 3.4 Color System

#### System Colors
```
Primary semantic colors:
  .label              — Primary text (adapts light/dark)
  .secondaryLabel     — Secondary text
  .tertiaryLabel      — Tertiary/disabled text
  .quaternaryLabel    — Subtle separators, watermarks

Background hierarchy:
  .systemBackground           — Base (white/black)
  .secondarySystemBackground  — Grouped content background
  .tertiarySystemBackground   — Elevated content within groups

Grouped variant:
  .systemGroupedBackground            — Screen background for grouped content (like Settings)
  .secondarySystemGroupedBackground   — Card/cell background within groups
  .tertiarySystemGroupedBackground    — Nested content within cards

Fill hierarchy:
  .systemFill          — Thin overlay for filled controls
  .secondarySystemFill — Thicker overlay
  .tertiarySystemFill  — Even thicker
  .quaternarySystemFill — Thickest

System tint colors:
  .systemBlue, .systemGreen, .systemIndigo, .systemOrange,
  .systemPink, .systemPurple, .systemRed, .systemTeal,
  .systemYellow, .systemBrown, .systemCyan, .systemMint
```

#### Color Rules
```
- ALWAYS use semantic colors (.label, .systemBackground) — never hardcode hex values for system UI
- App accent color: defined in Asset Catalog, used via .tint() or .accentColor()
- Dark mode: MANDATORY — every custom color must have light and dark variants in Asset Catalog
- High contrast: provide increased contrast variants (Accessibility → Increase Contrast)
- Elevated appearances: on iPad sheets/popovers, backgrounds auto-elevate — account for this
- Never rely on color alone to convey meaning — pair with icons, text, or shape
- Transparency and materials: use .ultraThinMaterial, .thinMaterial, .regularMaterial, .thickMaterial
  for background blur effects (system bars, overlays, cards over content)
```

### 3.5 SF Symbols

#### Symbol Configuration
```
Rendering modes:
  .monochrome    — Single color (default). Use for toolbars, navigation, simple icons
  .hierarchical  — Single color with depth/opacity layers. Use for multi-layered symbols
  .palette       — 2-3 custom colors mapped to symbol layers. Use for branded/colorful icons
  .multicolor    — System-defined colors (e.g., weather). Use for symbols with inherent meaning

Symbol sizes: match text style they accompany
  .font(.body) symbol next to .font(.body) text
  Use .imageScale(.small/.medium/.large) for fine adjustment within text style

Weight: match or exceed the weight of adjacent text
  Text: .regular → Symbol: .regular or .medium
  Text: .semibold → Symbol: .semibold or .bold

Variable value (iOS 17+):
  Image(systemName: "speaker.wave.3", variableValue: 0.7)
  Use for progress indicators, volume levels, signal strength

Symbol effects (iOS 17+):
  .symbolEffect(.bounce)           — Attention, completion feedback
  .symbolEffect(.pulse)            — Ongoing activity
  .symbolEffect(.variableColor)    — Animated multi-phase (e.g., Wi-Fi scanning)
  .symbolEffect(.replace)          — State change transition
  .symbolEffect(.breathe)          — Subtle ambient animation
  .symbolEffect(.wiggle)           — Attention-drawing
  .symbolEffect(.rotate)           — Processing/loading

Custom symbols:
  Export from SF Symbols app as SVG template
  Maintain 3 weight variants minimum (Regular, Medium, Semibold)
  Include all rendering mode layers (primary, secondary, tertiary)
```

### 3.6 Navigation Patterns

#### Navigation Architecture Decision Tree
```
Single-level content list?
  → NavigationStack with NavigationLink

Multi-level content hierarchy?
  → NavigationStack with path-based navigation (NavigationPath)

Two primary sections?
  → TabView with 2 tabs

3-5 primary sections?
  → TabView with 3-5 tabs (5 maximum visible, more go to "More" tab)

Content browsing + detail (iPad/Mac)?
  → NavigationSplitView (two-column or three-column)

Modal task (create, edit, settings)?
  → .sheet() — dismissible, non-blocking

Blocking task (confirmation, alert)?
  → .alert() or .confirmationDialog()

Full-screen takeover (media, onboarding)?
  → .fullScreenCover()

Contextual actions on an item?
  → .contextMenu() or .swipeActions()

Inspector / supplementary info (iPad)?
  → .inspector()
```

#### Navigation Rules
```
- NEVER hide the back button — users must always be able to go back
- Large titles: use for top-level tabs (scrolls to inline). Use .navigationBarTitleDisplayMode(.large)
- Inline titles: use for pushed detail views. Use .navigationBarTitleDisplayMode(.inline)
- Tab bar: ALWAYS visible except during full-screen media or onboarding
- Tab bar icons: use SF Symbols. Selected state uses .fill variant automatically
- Toolbar items: use .toolbar {} with .topBarTrailing, .bottomBar, .keyboard placements
- Search: use .searchable() — placed in navigation bar automatically
- Pull-to-refresh: use .refreshable {} — system-standard pull-to-refresh
- Sheets: default detent is .large. Use .presentationDetents([.medium, .large]) for half-sheets
- Dismiss affordance: sheets always have a drag indicator or explicit close button
```

### 3.7 Component Patterns

#### Lists and Cells
```
List styles:
  .plain          — Edge-to-edge rows (messaging, feeds)
  .grouped        — Rounded sections with headers (Settings-style)
  .insetGrouped   — Inset rounded sections (modern default for forms)
  .sidebar        — Sidebar navigation (iPad/Mac)

Cell heights:
  Standard:    44pt minimum (single line)
  Subtitle:    ~60pt (title + subtitle)
  Complex:     Variable — use automatic sizing

Cell components:
  Leading: icon/avatar (SF Symbol or image, 28-40pt)
  Title: .headline or .body weight
  Subtitle: .subheadline, .secondaryLabel color
  Trailing: disclosure indicator (auto), detail text, toggle, stepper

Swipe actions:
  Leading swipe: positive actions (pin, flag, unread)
  Trailing swipe: destructive actions (delete, archive)
  Full swipe: primary action (configurable)
  Use .swipeActions(edge:allowsFullSwipe:content:)
```

#### Buttons
```
Button styles (iOS 15+):
  .bordered          — Filled background, rounded rect. Use for secondary actions
  .borderedProminent — App tint fill, white text. Use for primary actions (1 per screen)
  .borderless        — Text only. Use for tertiary actions, inline actions
  .plain             — No styling. Use inside custom containers

Button sizes:
  .controlSize(.mini)        — Compact UI, toolbars
  .controlSize(.small)       — Secondary actions, inline
  .controlSize(.regular)     — Default
  .controlSize(.large)       — Primary CTA, bottom-anchored
  .controlSize(.extraLarge)  — Full-width prominent actions (iOS 17+)

Rules:
  - Primary action button: ONE per screen, .borderedProminent, placed at bottom or top-trailing
  - Destructive actions: .red tint, require confirmation (.confirmationDialog)
  - Minimum touch target: 44x44pt — always, even if visual size is smaller
  - Button labels: use verbs ("Save", "Send", "Delete") — never "OK" for actions with consequences
  - Loading state: replace label with ProgressView, disable button, keep same frame size
```

#### Forms and Input
```
Form pattern: use Form { } with Section { } grouping

Input types:
  TextField:        .textFieldStyle(.roundedBorder) or plain inside Form
  SecureField:      Passwords — system shows/hides toggle
  TextEditor:       Multi-line text (provide min height)
  Picker:           Use .pickerStyle appropriate to context
                    .menu (compact), .wheel (time/date), .segmented (2-5 options)
  DatePicker:       Use .datePickerStyle(.graphical) for full calendar, .compact for inline
  Toggle:           Standard switch control — always include visible label
  Slider:           Use with .accessibilityValue for screen readers
  Stepper:          Increment/decrement — show current value in label

Validation:
  - Inline validation: show error below the field with .foregroundColor(.red)
  - Use .focused() and @FocusState to manage keyboard and field focus
  - Keyboard type: .keyboardType(.emailAddress), .textContentType(.emailAddress) for autofill
  - Submit: .onSubmit {} for return key action, .submitLabel(.done/.send/.search)
```

### 3.8 Motion and Haptics

#### Animation Principles
```
HIG animation rules:
  - Animations serve function — never purely decorative
  - Standard duration: 0.25-0.35s for most transitions
  - Spring animations preferred: .spring(response: 0.3, dampingFraction: 0.7)
  - System transitions: .default uses platform-standard timing
  - Navigation push/pop: system-managed, never custom
  - Sheet presentation: system-managed spring animation
  - State changes: .animation(.default, value: stateProperty)
  - List insertions/deletions: .animation(.default) with .transition(.slide/.opacity)
  - Respect Reduce Motion: check accessibilityReduceMotion, use crossfade instead of movement

Transition types:
  .opacity          — Fade in/out (safest for reduce motion)
  .slide            — Slide from edge
  .scale            — Scale up/down
  .push(from:)      — Push from direction (iOS 16+)
  .move(edge:)      — Move from specific edge
  .asymmetric       — Different insertion/removal transitions
  Combined: .opacity.combined(with: .scale(scale: 0.8))
```

#### Haptic Feedback
```
UIImpactFeedbackGenerator:
  .light     — Subtle feedback (toggle, selection change)
  .medium    — Moderate feedback (snap to position, significant state change)
  .heavy     — Strong feedback (drop, impact)
  .soft      — Soft physical contact
  .rigid     — Rigid physical contact

UISelectionFeedbackGenerator:
  .selectionChanged — Scrolling through picker values, segment changes

UINotificationFeedbackGenerator:
  .success   — Task completed successfully (checkmark, save)
  .warning   — Attention needed (destructive action confirmation)
  .error     — Action failed (form validation error)

Rules:
  - Haptics MUST correspond to visual feedback — never haptic alone
  - Do not over-use — haptic fatigue reduces effectiveness
  - Prepare generators before use: generator.prepare()
  - Match intensity to action significance
```

### 3.9 Widgets, Live Activities, and StandBy

#### Widget Design
```
Widget families:
  .systemSmall      — 169×169pt (2×2 grid) — single tap target, no scrolling
  .systemMedium     — 360×169pt (4×2) — small amount of info, 2-3 tap targets
  .systemLarge      — 360×379pt (4×4) — more detail, multiple tap targets
  .systemExtraLarge — 715×379pt (iPad only, 8×4)
  .accessoryCircular — Lock Screen circular
  .accessoryRectangular — Lock Screen rectangular
  .accessoryInline  — Lock Screen single line of text

Widget rules:
  - Widgets are NOT mini apps — show glanceable information, not interactive controls
  - Tap target = deep link into the app at the relevant screen
  - Use .widgetURL() for single target, Link() for multiple tap targets
  - Timeline: provide entries for known future states (calendar events, weather forecasts)
  - Relevance: provide TimelineEntryRelevance to help the system surface your widget
  - Content margins: system-managed in iOS 17+ — do not add your own
  - Backgrounds: use .containerBackground(for: .widget) {} for iOS 17+ removable backgrounds
```

#### Live Activities
```
Compact:           Lock Screen banner — leading + trailing HStack
Minimal:           Dynamic Island minimal — small circular view
Expanded:          Dynamic Island expanded — leading, trailing, center, bottom regions

Rules:
  - Update frequency: system-limited — push notifications for real-time
  - Duration: 8 hours max active, then moves to Lock Screen as static
  - Content: time-sensitive, actively progressing (deliveries, sports, timers)
  - Deep link: every tap target links to relevant in-app screen
  - StandBy: Live Activities appear in StandBy mode — ensure readability at distance
```

### 3.10 Dark Mode and Appearances

```
Design rules:
  - Dark mode is NOT an inversion — it uses elevated surfaces with depth
  - Light mode: flat hierarchy, shadows for depth
  - Dark mode: elevated surfaces (lighter grays) for depth, no shadows
  - System colors auto-adapt — use them exclusively for standard UI
  - Custom colors: MUST provide both light and dark variants in Asset Catalog
  - Images: provide separate assets if needed, or use .renderingMode(.template) for tintable icons
  - Test in BOTH appearances — never ship without dark mode verification

Background elevation (Dark Mode):
  Base:      #000000 (pure black on OLED)
  Elevated:  #1C1C1E (system gray 6)
  Higher:    #2C2C2E (system gray 5)
  Highest:   #3A3A3C (system gray 4)

  Sheets/modals auto-elevate one level from their parent
```
