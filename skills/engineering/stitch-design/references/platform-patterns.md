# Platform Design Patterns — Material 3, Apple HIG & Web

Cross-platform component pattern reference for mapping Stitch HTML output to native platform implementations following Material Design 3 (Android), Apple Human Interface Guidelines (iOS), and modern Web standards (shadcn/Radix + Tailwind).

## Navigation Patterns

### Stitch HTML → Platform-Native Navigation

| Stitch Output | Material 3 (Compose) | Apple HIG (SwiftUI) | Web (shadcn/Radix + Tailwind) |
|---|---|---|---|
| `<nav>` with horizontal links | `NavigationBar` (bottom) / `NavigationRail` (tablet) | `TabView` with `.tabItem` | `<NavigationMenu>` (Radix) with `flex` items |
| `<nav>` with vertical sidebar | `PermanentNavigationDrawer` (expanded) | `NavigationSplitView` with sidebar | `<Sidebar>` (shadcn) with `Sheet` for mobile |
| `<header>` with back button | `TopAppBar` with `navigationIcon` | `.navigationTitle` + automatic back | `<header>` with `<Breadcrumb>` or back `<Button>` |
| Hamburger menu | `ModalNavigationDrawer` | `NavigationSplitView` (compact auto-collapses) | `<Sheet>` triggered by `<Button>` with `Menu` icon |
| Tab bar | `TabRow` / `ScrollableTabRow` | `TabView` | `<Tabs>` (Radix) with `TabsList` / `TabsTrigger` |
| Breadcrumbs | Custom `Row` with `TextButton` chain | Custom `HStack` (no native equivalent) | `<Breadcrumb>` (shadcn) with `<BreadcrumbItem>` |

**Adaptive Navigation Decision Tree:**

```
Screen width < 640px  → Bottom tab bar (M3) / Tab bar (HIG) / Hamburger + Sheet (Web)
Screen width 640-1024px → Navigation Rail (M3) / Tab sidebar (HIG) / Collapsed sidebar (Web)
Screen width > 1024px → Navigation Drawer (M3) / NavigationSplitView (HIG) / Persistent sidebar (Web)
```

---

## Component Pattern Mapping

### Buttons

| Stitch HTML | Material 3 | Apple HIG | Web (shadcn) |
|---|---|---|---|
| `<button class="primary">` | `Button` (filled) | `Button` `.borderedProminent` | `<Button>` default variant |
| `<button class="secondary">` | `FilledTonalButton` | `Button` `.bordered` | `<Button variant="secondary">` |
| `<button class="outline">` | `OutlinedButton` | `Button` `.bordered` + tint | `<Button variant="outline">` |
| `<button class="ghost">` | `TextButton` | `Button` `.plain` | `<Button variant="ghost">` |
| `<button class="destructive">` | `Button` with `colorScheme.error` | `Button` `.destructive` role | `<Button variant="destructive">` |
| `<button>` icon only | `IconButton` | `Button` `Label` (icon + hidden text) | `<Button variant="ghost" size="icon">` |
| FAB / floating action | `FloatingActionButton` | Custom floating button | `<Button className="fixed bottom-6 right-6 rounded-full shadow-lg">` |

**M3 Button Specifications:**
- Minimum touch target: 48x48dp
- Corner radius: `ShapeDefaults.Small` (8dp) for standard, `Full` for FAB
- Elevation: 0dp default, 1dp pressed for filled; 0dp for all others
- Container height: 40dp

**HIG Button Specifications:**
- Minimum touch target: 44x44pt
- Corner radius: system default (continuous corners)
- Haptic feedback: `.impact(.light)` on press for primary actions
- Dynamic Type: labels must scale with accessibility sizes

**Web Button Specifications (shadcn/Radix):**
- Minimum click target: 44x44px (WCAG 2.5.8)
- Focus ring: `ring-2 ring-ring ring-offset-2` on `focus-visible`
- Sizes: `sm` (h-9 px-3), `default` (h-10 px-4), `lg` (h-11 px-8)
- Loading state: swap text for `<Spinner>` + `aria-busy="true"`
- Keyboard: Enter/Space triggers, Escape blurs

### Cards

| Stitch HTML | Material 3 | Apple HIG | Web (shadcn) |
|---|---|---|---|
| `<div class="card">` | `Card` (elevated) | Custom `VStack` + `.clipShape` | `<Card>` with `<CardHeader>` + `<CardContent>` |
| `<div class="card filled">` | `Card` + `cardColors()` | `GroupBox` | `<Card className="bg-muted">` |
| `<div class="card outline">` | `OutlinedCard` | Custom view + stroke | `<Card className="border">` |
| Clickable card | `Card(onClick = ...)` | `Button` wrapping content | `<Card>` wrapped in `<a>` or `onClick` handler |
| Card with image header | `Card` + `AsyncImage` | `VStack` + `AsyncImage` | `<Card>` with `<img>` + `object-cover` |

**M3 Card Specifications:**
- Elevated: container = `surface`, elevation = 1dp, shape = `ShapeDefaults.Medium` (12dp)
- Filled: container = `surfaceContainerHighest`, elevation = 0dp
- Outlined: container = `surface`, border = `outline` 1dp

**HIG Card Specifications:**
- Use continuous corner radius (`.cornerRadius` with `RoundedRectangle(cornerRadius:style:.continuous)`)
- Background: `.secondarySystemGroupedBackground` for grouped contexts
- No explicit elevation — use subtle shadow `(.shadow(radius: 2, y: 1))` or border

**Web Card Specifications (shadcn):**
- Structure: `<Card>` → `<CardHeader>` + `<CardTitle>` + `<CardDescription>` + `<CardContent>` + `<CardFooter>`
- Border radius: `rounded-lg` (mapped from `--radius` CSS variable)
- Hover: `transition-shadow hover:shadow-md` for interactive cards
- Dark mode: `bg-card text-card-foreground` auto-adapts via CSS variables

### Text Fields / Inputs

| Stitch HTML | Material 3 | Apple HIG | Web (shadcn) |
|---|---|---|---|
| `<input type="text">` | `OutlinedTextField` / `TextField` (filled) | `TextField` `.roundedBorder` | `<Input>` |
| `<textarea>` | `OutlinedTextField` + `minLines` | `TextEditor` | `<Textarea>` |
| `<select>` | `ExposedDropdownMenuBox` | `Picker` `.menu` style | `<Select>` (Radix) |
| `<input type="search">` | `SearchBar` (M3) | `.searchable` modifier | `<Input>` with `type="search"` + icon |
| `<input>` with error | `isError = true` + `supportingText` | Custom `.foregroundColor(.red)` | `aria-invalid="true"` + `<p>` message |

**M3 Input Specifications:**
- Outlined: 56dp height, 4dp corner radius, 1dp border (outline), 2dp focused (primary)
- Filled: 56dp height, 4dp top corners only, `surfaceContainerHighest` background
- Supporting text: `bodySmall`, 4dp below field
- Error state: border and label switch to `error` color

**HIG Input Specifications:**
- Standard height: 34pt (compact), 44pt with label
- Use `@FocusState` for programmatic focus management
- Keyboard type must match content: `.keyboardType(.emailAddress)`, `.numberPad`, etc.
- Return key label: `.submitLabel(.done)`, `.submitLabel(.search)`, etc.

**Web Input Specifications (shadcn):**
- Height: `h-10` (40px), padding: `px-3 py-2`
- Border: `border border-input`, focus: `ring-2 ring-ring`
- Error: `border-destructive` + `aria-invalid="true"` + `aria-describedby` pointing to error `<p>`
- Labels: always use `<Label htmlFor={id}>` — never placeholder-only
- Validation: use `react-hook-form` + `zod` for schema validation

### Lists

| Stitch HTML | Material 3 | Apple HIG | Web (shadcn) |
|---|---|---|---|
| `<ul>` / `<ol>` | `LazyColumn` with items | `List` with `ForEach` | `<div>` with `space-y-*` or `<Table>` |
| List item (icon + text) | `ListItem` leading/headline | `Label` in `List` row | `<div className="flex items-center gap-3">` |
| Grouped list | `LazyColumn` + sticky headers | `List` + `Section` headers | Sections with `<h3>` + `<Separator>` |
| Swipeable list item | `SwipeToDismissBox` | `.swipeActions` | Not native — use `<ContextMenu>` (Radix) |
| Pull to refresh | `pullToRefresh` modifier | `.refreshable` | Not native — use button or intersection observer |
| Virtualized list | `LazyColumn` (built-in) | `List` (built-in) | `@tanstack/react-virtual` for large datasets |

### Dialogs & Sheets

| Stitch HTML | Material 3 | Apple HIG | Web (shadcn/Radix) |
|---|---|---|---|
| `<dialog>` / modal | `AlertDialog` | `.alert` modifier | `<AlertDialog>` (Radix) |
| Confirmation dialog | `AlertDialog` confirm/dismiss | `.confirmationDialog` | `<AlertDialog>` with action buttons |
| Bottom sheet | `ModalBottomSheet` | `.sheet` / `.presentationDetents` | `<Sheet>` (shadcn) or `<Drawer>` (vaul) |
| Full-screen dialog | `FullScreenDialog` scaffold | `.fullScreenCover` | `<Dialog>` with `className="max-w-full h-full"` |
| Date picker | `DatePicker` / `DatePickerDialog` | `DatePicker` | `<Calendar>` (shadcn) + `<Popover>` |
| Time picker | `TimePicker` / `TimePickerDialog` | `DatePicker` wheel style | Custom time select or `<Input type="time">` |
| Command palette | N/A | N/A | `<Command>` (cmdk) for search + actions |
| Toast/snackbar | `Snackbar` via `SnackbarHost` | Custom overlay | `<Toaster>` (sonner) |

---

## M3 Tonal Palette System

Material 3 generates a 13-tone palette from a seed color. When Stitch outputs a primary color, map it to the full tonal system:

```
Seed: #00A859 (Vendly Green)
  ↓ HCT color space transformation
Tonal palette (13 tones):
  T0:   #000000   T10:  #002110   T20:  #003919
  T30:  #005227   T40:  #006D35   T50:  #008944
  T60:  #00A859   T70:  #2DC471   T80:  #55E08B
  T90:  #73FDA5   T95:  #C4FFD4   T99:  #F5FFF5
  T100: #FFFFFF

Color Roles derived from tones:
  primary:              T40 (light) / T80 (dark)
  onPrimary:            T100 (light) / T20 (dark)
  primaryContainer:     T90 (light) / T30 (dark)
  onPrimaryContainer:   T10 (light) / T90 (dark)
  inversePrimary:       T80 (light) / T40 (dark)
```

### Extended M3 Color Roles

| DESIGN.md Token | M3 Role | Light Theme Tone | Dark Theme Tone |
|---|---|---|---|
| `primary` | `primary` | T40 | T80 |
| `on-primary` | `onPrimary` | T100 | T20 |
| `primary-container` | `primaryContainer` | T90 | T30 |
| `on-primary-container` | `onPrimaryContainer` | T10 | T90 |
| `secondary-container` | `secondaryContainer` | T90 | T30 |
| `tertiary` | `tertiary` | T40 | T80 |
| `surface-container` | `surfaceContainer` | N94 | N12 |
| `surface-container-high` | `surfaceContainerHigh` | N92 | N17 |
| `surface-container-highest` | `surfaceContainerHighest` | N90 | N22 |
| `surface-container-low` | `surfaceContainerLow` | N96 | N10 |
| `surface-dim` | `surfaceDim` | N87 | N6 |
| `surface-bright` | `surfaceBright` | N98 | N24 |
| `inverse-surface` | `inverseSurface` | N20 | N90 |

---

## Apple HIG System Colors

Map DESIGN.md tokens to iOS semantic colors for proper dark mode adaptation:

| DESIGN.md Token | HIG System Color | Light | Dark |
|---|---|---|---|
| `primary` | `.tint` (app tint) | Brand color | Brand color (adjusted) |
| `on-surface` (primary text) | `.label` | #000000 (0.0 alpha) | #FFFFFF |
| `on-surface` (secondary text) | `.secondaryLabel` | 60% alpha | 60% alpha |
| `on-surface` (tertiary text) | `.tertiaryLabel` | 30% alpha | 30% alpha |
| `surface` (background) | `.systemBackground` | #FFFFFF | #000000 |
| `surface` (grouped bg) | `.systemGroupedBackground` | #F2F2F7 | #000000 |
| `surface-variant` (secondary bg) | `.secondarySystemBackground` | #F2F2F7 | #1C1C1E |
| `surface-variant` (grouped) | `.secondarySystemGroupedBackground` | #FFFFFF | #1C1C1E |
| `outline` (separator) | `.separator` | #3C3C43 (29%) | #545458 (65%) |
| `error` | `.systemRed` | #FF3B30 | #FF453A |
| `success` | `.systemGreen` | #34C759 | #30D158 |
| `warning` | `.systemYellow` | #FFCC00 | #FFD60A |
| `info` | `.systemBlue` | #007AFF | #0A84FF |

### HIG Dynamic Type Scale

Map DESIGN.md typography tokens to iOS Dynamic Type styles for automatic accessibility scaling:

| DESIGN.md Token | HIG Text Style | Default Size | AX5 Size |
|---|---|---|---|
| `display-large` | `.largeTitle` | 34pt | 53pt |
| `display-medium` | `.title1` | 28pt | 47pt |
| `headline-large` | `.title2` | 22pt | 41pt |
| `headline-medium` | `.title3` | 20pt | 39pt |
| `body-large` | `.body` | 17pt | 53pt |
| `body-medium` | `.callout` | 16pt | 51pt |
| `label-large` | `.subheadline` | 15pt | 49pt |
| `label-medium` | `.caption1` | 12pt | 40pt |

### SwiftUI Implementation

```swift
// Map DESIGN.md tokens to HIG text styles
extension Font {
    static let designDisplayLarge: Font = .largeTitle
    static let designHeadlineLarge: Font = .title2
    static let designBodyLarge: Font = .body
    static let designLabelLarge: Font = .subheadline
}

// Custom font with Dynamic Type scaling
extension Font {
    static func scaledInter(_ style: Font.TextStyle, size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .custom("Inter", size: size, relativeTo: style).weight(weight)
    }
}

// Usage: scales with Dynamic Type automatically
Text("Heading").font(.scaledInter(.title2, size: 22, weight: .semibold))
```

---

## SF Symbols Integration

When Stitch outputs icon elements, map them to SF Symbols for iOS:

| Stitch Icon Context | SF Symbol | Rendering Mode |
|---|---|---|
| Navigation back | `chevron.left` | Monochrome |
| Search | `magnifyingglass` | Monochrome |
| Settings/gear | `gearshape` | Monochrome |
| User/profile | `person.circle` | Hierarchical |
| Notifications/bell | `bell` → `bell.badge` | Palette (badge = red) |
| Cart/shopping | `cart` → `cart.badge.plus` | Hierarchical |
| Heart/favorite | `heart` → `heart.fill` | Multicolor |
| Share | `square.and.arrow.up` | Monochrome |
| Delete/trash | `trash` | Monochrome |
| Add/plus | `plus` or `plus.circle.fill` | Hierarchical |
| Close/dismiss | `xmark` | Monochrome |
| Check/success | `checkmark.circle.fill` | Multicolor |
| Warning | `exclamationmark.triangle.fill` | Multicolor |
| Edit/pencil | `pencil` | Monochrome |

**Symbol Effects (iOS 17+):**
```swift
// Bounce on tap
Image(systemName: "bell").symbolEffect(.bounce, value: notificationCount)
// Pulse while loading
Image(systemName: "arrow.clockwise").symbolEffect(.pulse, isActive: isLoading)
// Variable fill for progress
Image(systemName: "wifi").symbolEffect(.variableColor, isActive: isConnecting)
```

---

## Material Symbols Integration

When Stitch outputs icon elements, map them to Material Symbols for Android:

| Stitch Icon Context | Material Symbol | Style |
|---|---|---|
| Navigation back | `arrow_back` | Outlined |
| Search | `search` | Outlined |
| Settings | `settings` | Outlined |
| User/profile | `account_circle` | Filled |
| Notifications | `notifications` → `notifications_active` | Outlined → Filled |
| Cart | `shopping_cart` | Outlined |
| Favorite | `favorite_border` → `favorite` | Outlined → Filled |
| Share | `share` | Outlined |
| Delete | `delete` | Outlined |
| Add | `add` or `add_circle` | Outlined |
| Close | `close` | Outlined |
| Check | `check_circle` | Filled |
| Warning | `warning` | Filled |
| Edit | `edit` | Outlined |

**Compose Icon Usage:**
```kotlin
Icon(
    imageVector = Icons.Outlined.Search,
    contentDescription = "Search",
    modifier = Modifier.size(24.dp),
    tint = MaterialTheme.colorScheme.onSurface,
)
```

---

## Haptic Feedback Mapping (iOS)

Map Stitch interactive patterns to appropriate haptic feedback:

| Interaction | Haptic Generator | Style |
|---|---|---|
| Button tap | `UIImpactFeedbackGenerator` | `.light` |
| Toggle switch | `UIImpactFeedbackGenerator` | `.medium` |
| Destructive action confirm | `UINotificationFeedbackGenerator` | `.warning` |
| Success (payment, save) | `UINotificationFeedbackGenerator` | `.success` |
| Error (validation fail) | `UINotificationFeedbackGenerator` | `.error` |
| Pull-to-refresh trigger | `UIImpactFeedbackGenerator` | `.medium` |
| Long press menu | `UIImpactFeedbackGenerator` | `.heavy` |
| Swipe action threshold | `UIImpactFeedbackGenerator` | `.light` |
| Picker scroll | `UISelectionFeedbackGenerator` | selection changed |

```swift
// SwiftUI sensory feedback (iOS 17+)
Button("Submit") { submit() }
    .sensoryFeedback(.success, trigger: isSubmitted)

Toggle("Notifications", isOn: $enabled)
    .sensoryFeedback(.impact(.medium), trigger: enabled)
```

---

## Accessibility Cross-Platform Mapping

| DESIGN.md Requirement | Material 3 | Apple HIG | Web (ARIA + CSS) |
|---|---|---|---|
| Touch target 48dp | `Modifier.minimumInteractiveComponentSize()` | `.frame(minWidth: 44, minHeight: 44)` | `min-w-[44px] min-h-[44px]` (WCAG 2.5.8) |
| Screen reader label | `Modifier.contentDescription("label")` | `.accessibilityLabel("label")` | `aria-label="label"` |
| Heading semantics | `Modifier.semantics { heading() }` | `.accessibilityAddTraits(.isHeader)` | `<h1>`–`<h6>` or `role="heading"` |
| Button role | `Modifier.semantics { role = Role.Button }` | `.accessibilityAddTraits(.isButton)` | `<button>` or `role="button"` |
| Image description | `contentDescription = "alt text"` | `.accessibilityLabel("alt text")` | `alt="alt text"` on `<img>` |
| Hidden decorative | `contentDescription = null` | `.accessibilityHidden(true)` | `aria-hidden="true"` + `alt=""` |
| Live region | `semantics { liveRegion = Polite }` | `.accessibilityElement(children: .combine)` | `aria-live="polite"` or `role="status"` |
| Font scaling | Compose `sp` (auto-scales) | Dynamic Type via `Font.TextStyle` | `rem` units + `font-size` on `:root` |
| Reduced motion | `LocalReducedMotion.current` | `@Environment(\.accessibilityReduceMotion)` | `@media (prefers-reduced-motion: reduce)` |
| High contrast | `LocalHighContrast` | `@Environment(\.colorSchemeContrast)` | `@media (prefers-contrast: more)` |
| Focus visible | Compose focus indicators (auto) | `.focusable()` | `:focus-visible` + `ring-2 ring-ring` |
| Skip navigation | N/A (single-screen apps) | N/A | `<a href="#main" className="sr-only focus:not-sr-only">` |

---

## Web-Specific Design Patterns

### shadcn/ui Component Library

shadcn/ui is the standard web component layer for Stitch → React conversions. Components are built on Radix UI primitives with Tailwind styling.

**Core Architecture:**
```
Stitch HTML → Extract structure → Map to shadcn components → Apply Tailwind tokens
```

**Component Inventory (most used in Stitch conversions):**

| Category | Components |
|---|---|
| Layout | `Card`, `Separator`, `Sheet`, `ScrollArea`, `AspectRatio`, `Collapsible` |
| Forms | `Input`, `Textarea`, `Select`, `Checkbox`, `RadioGroup`, `Switch`, `Slider`, `Label`, `Form` |
| Data Display | `Table`, `Badge`, `Avatar`, `Calendar`, `HoverCard` |
| Feedback | `Alert`, `AlertDialog`, `Dialog`, `Toast` (sonner), `Progress`, `Skeleton` |
| Navigation | `Tabs`, `NavigationMenu`, `Breadcrumb`, `Command`, `Menubar`, `DropdownMenu` |
| Overlay | `Popover`, `Tooltip`, `ContextMenu`, `Sheet`, `Drawer` |

### Responsive Layout Patterns

| Stitch Layout | Tailwind Implementation | Breakpoint Strategy |
|---|---|---|
| Single column | `max-w-2xl mx-auto px-4` | All sizes |
| Two-column split | `grid grid-cols-1 md:grid-cols-2 gap-6` | Stack on mobile |
| Sidebar + content | `flex flex-col lg:flex-row` with `w-64` sidebar | Sheet on mobile, rail on tablet |
| Dashboard grid | `grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4` | Progressive density |
| Hero + sections | `space-y-16 md:space-y-24` with full-bleed hero | Reduce spacing on mobile |
| Card grid | `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6` | Responsive column count |

**Container Query Patterns (modern CSS):**
```css
/* Component-level responsive behavior */
@container (min-width: 400px) {
  .card-layout { grid-template-columns: auto 1fr; }
}

/* Usage in Tailwind */
<div className="@container">
  <div className="@md:flex @md:items-center grid gap-4">
```

### Dark Mode Implementation

```tsx
// Theme provider with system detection + manual toggle
// globals.css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222 47% 11%;
    --primary: 222 47% 45%;
    /* ... all tokens */
  }
  .dark {
    --background: 222 47% 4%;
    --foreground: 210 40% 98%;
    --primary: 217 91% 60%;
    /* ... all tokens */
  }
}

// tailwind.config.ts
export default {
  darkMode: ["class"],  // Class strategy for manual toggle
}
```

### Web Animation Patterns

| Stitch Transition | Tailwind/CSS Implementation |
|---|---|
| Page enter | `animate-in fade-in slide-in-from-bottom-4 duration-300` |
| Modal overlay | `animate-in fade-in duration-200` + backdrop `bg-black/50` |
| Sheet slide | `animate-in slide-in-from-right duration-300` (or `-from-bottom` mobile) |
| Skeleton loading | `animate-pulse bg-muted rounded` |
| Accordion expand | `data-[state=open]:animate-accordion-down` |
| Hover card lift | `transition-all hover:shadow-md hover:-translate-y-0.5 duration-200` |
| Button press | `active:scale-95 transition-transform duration-75` |

**Reduced Motion:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Lucide Icons (Web Standard)

When Stitch outputs icon elements, map them to Lucide icons for React:

| Stitch Icon Context | Lucide Icon | Usage |
|---|---|---|
| Navigation back | `<ArrowLeft>` | `import { ArrowLeft } from "lucide-react"` |
| Search | `<Search>` | `<Search className="h-4 w-4" />` |
| Settings | `<Settings>` | `<Settings className="h-5 w-5" />` |
| User/profile | `<User>` or `<CircleUser>` | `<CircleUser className="h-8 w-8" />` |
| Notifications | `<Bell>` → `<BellDot>` | Active state uses dot variant |
| Cart | `<ShoppingCart>` | `<ShoppingCart className="h-5 w-5" />` |
| Favorite | `<Heart>` → filled via `fill="currentColor"` | Toggle fill on state |
| Share | `<Share2>` | `<Share2 className="h-4 w-4" />` |
| Delete | `<Trash2>` | `<Trash2 className="h-4 w-4 text-destructive" />` |
| Add | `<Plus>` or `<PlusCircle>` | `<Plus className="h-4 w-4" />` |
| Close | `<X>` | `<X className="h-4 w-4" />` |
| Check/success | `<CheckCircle2>` | `<CheckCircle2 className="h-5 w-5 text-green-500" />` |
| Warning | `<AlertTriangle>` | `<AlertTriangle className="h-5 w-5 text-yellow-500" />` |
| Edit | `<Pencil>` | `<Pencil className="h-4 w-4" />` |
| Menu | `<Menu>` | `<Menu className="h-5 w-5" />` |
| External link | `<ExternalLink>` | `<ExternalLink className="h-3 w-3 ml-1" />` |
| Loading | `<Loader2>` | `<Loader2 className="h-4 w-4 animate-spin" />` |

### Form Patterns (Web)

```tsx
// Standard form with react-hook-form + zod + shadcn
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Min 8 characters"),
});

export function LoginForm() {
  const form = useForm({ resolver: zodResolver(schema) });

  return (
    <Form {...form}>
      <FormField name="email" render={({ field }) => (
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl><Input {...field} /></FormControl>
          <FormMessage /> {/* Auto-shows zod error */}
        </FormItem>
      )} />
    </Form>
  );
}
```

### Core Web Vitals Considerations

When converting Stitch output to production React, ensure:

| Metric | Target | Stitch Conversion Rule |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | Hero images: `<Image priority>` (Next.js) or `fetchpriority="high"` |
| INP (Interaction to Next Paint) | < 200ms | Use `useTransition` for non-urgent updates, avoid blocking renders |
| CLS (Cumulative Layout Shift) | < 0.1 | Set explicit `width`/`height` on all images, use `aspect-ratio` |
| FCP (First Contentful Paint) | < 1.8s | Server Components for static content, `loading="lazy"` for below-fold |

**Image Optimization:**
```tsx
// Next.js Image with Stitch-exported screenshots
import Image from "next/image";

<Image
  src="/design/screens/checkout/payment.png"
  alt="Payment form"
  width={1440}
  height={900}
  priority  // Above the fold
  className="rounded-lg shadow-md"
/>
```
