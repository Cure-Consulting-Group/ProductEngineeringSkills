# ios-design-expert: detailed reference

Exact values for `ios-design-expert`. The rules that always apply (Liquid Glass, navigation, Cure defaults) are in SKILL.md; read this file when a spec needs a number or an API name. Values checked against Apple HIG/developer docs 2026-09-23.

### 3.2 Layout System

#### Safe Areas and Margins
```
Bars:                Don't hard-code heights. iOS 26 bars float on Liquid Glass and the tab bar
                     can minimize on scroll — lay out against safeAreaInsets, let content
                     scroll under bars (scroll-edge effect handles legibility)
Layout margins:      16pt (compact width), 20pt (regular width) — use system layout margins
Readable content:    readableContentGuide / .containerRelativeFrame for text-heavy iPad layouts
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

Design compact width first, then adapt (ViewThatFits / AnyLayout); iPad windows are
freely resizable in iPadOS 26, so never assume a fixed size.
```

#### Grid and Spacing
```
Base unit:           4pt (iOS uses a 4pt sub-grid within the 8pt macro grid)
Spacing scale:       4, 8, 12, 16, 20, 24, 32, 40, 48, 64
Component padding:   Standard system spacing — 16pt horizontal, 12pt vertical (cells)
Section spacing:     35pt between grouped sections in List/Form
Corner radius:       continuous curve (RoundedRectangle(cornerRadius:style: .continuous));
                     nested shapes concentric with their container (ConcentricRectangle, iOS 26)
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

Truncation: .lineLimit(nil) for primary content, truncate only secondary content;
.minimumScaleFactor only in fixed-width containers. Test at AX5.
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

Materials (content layer): .ultraThinMaterial … .thickMaterial. Liquid Glass (functional
layer): Glass.regular / Glass.clear via .glassEffect — see SKILL.md 3.1.

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

2-5 primary sections?
  → TabView (avoid overflow into "More"); iPad: .tabViewStyle(.sidebarAdaptable)

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

  .glass / .glassProminent — Liquid Glass styles (iOS 26) for controls in the functional layer

Loading state: replace label with ProgressView, disable, keep the same frame size.
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

SwiftUI: .sensoryFeedback(.success | .impact(weight:) | .selection, trigger:)
Haptics always pair with visible feedback.
```

### 3.9 Widgets, Live Activities, and StandBy

#### Widget Design
```
Widget families (point sizes vary by device — take exact sizes from the HIG widget size table):
  .systemSmall      — 169×169pt (2×2 grid) — single tap target, no scrolling
  .systemMedium     — 360×169pt (4×2) — small amount of info, 2-3 tap targets
  .systemLarge      — 360×379pt (4×4) — more detail, multiple tap targets
  .systemExtraLarge — 715×379pt (iPad only, 8×4)
  .accessoryCircular — Lock Screen circular
  .accessoryRectangular — Lock Screen rectangular
  .accessoryInline  — Lock Screen single line of text

Widget rules:
  - Glanceable first; interactive controls only as Button/Toggle backed by App Intents (iOS 17+)
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
  - Duration: up to 8 hours active, then the system ends it (stays on Lock Screen up to 4 more hours — confirm before use)
  - Content: time-sensitive, actively progressing (deliveries, sports, timers)
  - Deep link: every tap target links to relevant in-app screen
  - StandBy: Live Activities appear in StandBy mode — ensure readability at distance
```

### 3.10 Dark mode elevation

Base #000000 (OLED) → elevated #1C1C1E (systemGray6) → #2C2C2E (systemGray5) → #3A3A3C (systemGray4); sheets auto-elevate one level. Use semantic background colors rather than these hex values.
