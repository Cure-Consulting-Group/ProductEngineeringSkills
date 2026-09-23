# iOS Design Expert — Apple Human Interface Guidelines

**Outcome:** a screen, component, or navigation spec (or a design review) that reads as native on iOS 26+ with Liquid Glass, with every state, Dynamic Type behavior, and accessibility detail an engineer needs to build it in SwiftUI. Done when the spec covers the items in the Step 4 contract for its type; code is written only when Step 1 says so.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Deployment target: !`grep -rhoE "IPHONEOS_DEPLOYMENT_TARGET = [0-9.]+|\.iOS\(\.v[0-9]+\)" --include=project.pbxproj --include=Package.swift . 2>/dev/null | sort -u | head -3 || echo "(not found)"`
- Existing design system: !`find . -path ./node_modules -prune -o \( -path "*DesignSystem*" -o -path "*/Theme/*" \) -name "*.swift" -print 2>/dev/null | head -8`
- Custom glass / bar backgrounds: !`grep -rlE "glassEffect|toolbarBackground|UITabBarAppearance|UINavigationBarAppearance" --include=*.swift . 2>/dev/null | head -5 || echo "(none)"`

## Step 1: Classify the Request

| Request | Output |
|---|---|
| Screen design / layout | Screen spec (Step 4) |
| Component design | Component spec with all states |
| Navigation architecture | Navigation spec (tab bar, stacks, split view, sheets) |
| Design review of existing UI | Findings list — every issue with severity, no code |
| Liquid Glass adoption / iOS 26 migration | Migration findings + changes (Step 3.1) |
| Typography, color, SF Symbols, haptics, motion | Focused spec for that dimension |
| Widget / Live Activity | Widget spec per family |
| "Build it" / design-to-SwiftUI handoff | Spec, then Code/Artifact Generation |

## Step 2: Gather Context

Ask only what the auto-context didn't answer: platforms (iPhone, iPad, visionOS), deployment target (below iOS 26 means two appearances to design for), SwiftUI vs UIKit, brand constraints, and accessibility target (WCAG 2.2 AA is the Cure default).

## Step 3: Cure Defaults and Current-Platform Rules (always apply)

### 3.1 Liquid Glass (iOS 26+)

- **Layering.** Liquid Glass is the functional layer for controls and navigation (tab bars, toolbars, sidebars, sheets) floating above content. Don't put it in the content layer (cards, list rows, app backgrounds) — use standard materials there. Exception per HIG: transient controls like sliders and toggles take on glass while active.
- **Use standard components first.** Bars, sheets, popovers, and controls adopt glass automatically. Remove custom backgrounds on `NavigationStack`, `NavigationSplitView`, `toolbar`, `UITabBar`, `UINavigationBar` — they fight the system glass and the scroll-edge effect.
- **Custom glass sparingly**, on the few most important functional elements: `.glassEffect()` (default `.regular` in a capsule), `.glassEffect(.regular.tint(…).interactive())`, `.glassEffect(in: .rect(cornerRadius:))`; group multiple glass views in a `GlassEffectContainer` for performance and morphing; buttons use `.buttonStyle(.glass)` / `.glassProminent`.
- **Variants.** `regular` for anything with text (alerts, sidebars, popovers). `clear` only over visually rich media; add a ~35% dark dimming layer if the media underneath is bright.
- **No glass on glass**, and don't tint bar items the same hue as colorful content — prefer a monochrome tab bar over busy content.
- **Opt-out is gone.** `UIDesignRequiresCompatibility` was a temporary iOS 26 escape hatch; the system ignores it when building with the iOS 27 SDK. Plan the redesign rather than relying on it.
- **Test** with Reduce Transparency, Increase Contrast, Reduce Motion, and the user's Liquid Glass look preference; custom glass must stay legible in all of them.

### 3.2 Navigation and bars

- Tab bar (iPhone) floats at the bottom on glass. It may **minimize on scroll** — `.tabBarMinimizeBehavior(.onScrollDown)` — and an accessory (mini-player style) goes in `.tabViewBottomAccessory { }`, moving inline when minimized. Minimizing is fine; *hiding* the tab bar during normal navigation is not (modal covers are the exception).
- Search goes in a dedicated trailing search tab, `Tab(role: .search)`, or `.searchable()` in the navigation bar.
- iPadOS: the tab bar sits at the top; use `.tabViewStyle(.sidebarAdaptable)` for complex apps, `NavigationSplitView` for sidebar-only.
- 3–5 tabs; avoid the overflow "More" tab; never disable or hide tab items — explain empty sections instead. Tabs navigate; actions go in toolbars.
- Don't hard-code bar heights (49pt tab bar, 44pt nav bar are no longer reliable with floating glass bars); lay out against safe areas and let content scroll under bars.
- Never replace the system back button or break swipe-back. Large titles on top-level screens, inline on pushed detail.

### 3.3 Type, color, symbols, touch

- System text styles only (`.body`, `.headline` …); custom fonts scale via `@ScaledMetric` / `UIFontMetrics`. Layouts must reflow at AX5, not truncate primary content.
- Semantic colors (`.label`, `.systemBackground`, grouped variants); every custom color has light, dark, and increased-contrast variants in the asset catalog. Color never carries meaning alone.
- SF Symbols matched to adjacent text style and weight; filled variants in tab bars.
- 44×44pt minimum hit target; one prominent primary action per screen; destructive actions confirmed via `.confirmationDialog`.
- Continuous (squircle) corners; concentric radii for nested shapes inside glass containers.

Read [reference/details.md](reference/details.md) when you need exact values: size-class matrix, the Dynamic Type size table, system color and material names, SF Symbol rendering modes and effects, haptic generator mapping, widget families, and Live Activity regions.

## Step 4: Output Contract

- **Screen spec:** purpose and user goal; how the user arrives and leaves; layout regions (pt, safe-area relative); states — loading (skeleton), empty, content, error, partial; compact vs regular width; Dynamic Type at default and AX sizes; dark mode and Reduce Transparency appearance; VoiceOver order; haptic points; SwiftUI view hierarchy.
- **Component spec:** anatomy; states (default, pressed, focused, disabled, selected, loading, error); `.controlSize` variants; spacing; text styles; semantic colors; SF Symbols + rendering mode; glass usage (if any, with variant); motion; accessibility label/traits/hints/actions.
- **Navigation spec:** hierarchy diagram; tab configuration (icons, labels, badges, minimize behavior, accessory); stack/split structure; modal strategy; deep-link scheme; state restoration; iPad adaptation.
- **Review:** every finding with severity (blocker / major / minor) and the HIG rule it breaks; don't filter to "top issues".

Match length to the need; no filler sections or restated summaries.

## Code/Artifact Generation

Applies only when Step 1 classified the request as build/handoff or the user asked for code. Extend the existing design system found in auto-context rather than creating a parallel one. Typical files: `DesignSystem/Theme.swift`, `Colors.swift`, `Typography.swift`, and `Components/<Component>View.swift` with `#Preview` blocks covering light/dark and an AX Dynamic Type size. Write only what was asked; don't refactor adjacent views.

## Step 5: Anti-Patterns

- Custom back buttons that break swipe-back; hamburger menus; bottom sheets as primary navigation (Android pattern).
- Hiding the tab bar during regular navigation; more than 5 tabs; custom opaque backgrounds on bars that block Liquid Glass.
- Liquid Glass in the content layer, glass stacked on glass, or custom glass on many controls.
- Fixed font sizes; text that truncates instead of reflowing at large sizes; hard-coded bar heights.
- Custom alerts/action sheets instead of `.alert()` / `.confirmationDialog()`; custom pull-to-refresh instead of `.refreshable`.
- Material ripple effects, web skip links, px units.
- Easy-to-hit destructive actions without confirmation; content under the status bar or home indicator.

## Related

`ios-architect` (code scaffolding) · `product-design` (cross-platform specs) · `design-studio` (brand and full systems) · `accessibility-audit` (WCAG verification) · `stitch-design` (Stitch-generated screens)
