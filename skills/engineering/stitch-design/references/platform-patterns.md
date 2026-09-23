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

## Platform tokens, type, symbols, haptics

Not repeated here — the platform design skills own them. Read `ios-design-expert` (HIG colors, Dynamic Type, SF Symbols, haptics, Liquid Glass), `android-design-expert` (M3 tonal palettes, Material Symbols, M3 Expressive) or `web-design-expert` (Tailwind v4 tokens, dark mode, motion, Core Web Vitals) when a conversion needs platform detail beyond the mapping tables in this file.

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

### Dark mode, motion, icons, forms, Core Web Vitals (web)

Follow `web-design-expert`. Stitch conversion specifics: map DESIGN.md colors to shadcn's CSS variables in OKLCH under `@theme inline` (Tailwind v4 — no `tailwind.config.ts`, no HSL triplets); class-based dark mode is `@custom-variant dark (&:where(.dark, .dark *));`; Lucide icons at `size-4` with `currentColor`; forms use react-hook-form + zod via shadcn `Form`.
