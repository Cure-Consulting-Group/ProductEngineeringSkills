# Apple platforms: iOS, iPadOS, macOS, watchOS, tvOS, visionOS

Judgment layer. For component-level SwiftUI specs and code, invoke `ios-design-expert`; for architecture, `ios-architect`. An "iOS-style skin" on a generic layout is a defect; the interface must behave like it belongs on the platform.

## Structure and navigation

| Need | Use | Not |
|---|---|---|
| 2 to 5 top-level destinations | Tab bar (iPhone); sidebar with tab-bar fallback in compact width (iPad) | Hamburger; more than 5 tabs |
| Drill into an object | Navigation stack with a real back title | Modal for navigation |
| Focused task that starts and ends | Sheet (medium and large detents), full-screen cover for immersive | Pushing a task onto the stack |
| Secondary options for one control | Popover (iPad, Mac), menu (iPhone) | A new screen |
| Object inspection alongside content | Sidebar plus inspector (iPad, Mac) | Overlays |
| Searching a collection | Searchable in the navigation bar, scoped by segments | A search screen |

Toolbars carry actions for the current screen; the navigation bar carries title, back, and at most two trailing actions. Context menus on long press for object-level actions. Menus for anything with more than three options.

## Layout and safe areas

- Safe areas: status bar, Dynamic Island, home indicator, sidebars in landscape. Content scrolls under bars; controls never sit under them.
- Size classes: compact and regular width drive layout, not device names. iPad multitasking (Split View, Slide Over, Stage Manager) means an iPad app runs at iPhone width; design for it.
- Orientation on iPad is a first-class state; on iPhone, lock only with a reason (camera, games).
- Window resizing on macOS and visionOS: minimum sizes stated; layouts reflow, never clip.
- Keyboard and pointer: iPad and Mac users tab through controls, hover reveals affordances, keyboard shortcuts for the top five actions.

## Components and system behaviours

Sheets, popovers, sidebars, inspectors, segmented controls, menus, context menus, search, widgets (small, medium, large, lock screen), notifications (with actions), Live Activities (Dynamic Island and lock screen), gestures (swipe actions on rows, edge swipe back, pull to refresh), haptics (selection, impact, notification, mapped to meaning, never decorative).

Use SF Symbols with the matching weight and scale of the adjacent text; custom symbols follow the same grid. Never mix icon families on one screen.

## Type, colour, material

- San Francisco text styles by role (Large Title to Caption 2); Dynamic Type supported to at least the accessibility sizes for reading surfaces; layouts that stack when text grows.
- Semantic colours (label, secondaryLabel, systemBackground, and tints) so Dark Mode and Increase Contrast work without a second palette.
- Materials and the current Liquid Glass conventions for bars and floating controls: translucency belongs on chrome over content, never on content itself. Legibility of text over material is checked in both appearances.
- Minimum hit target 44 x 44 pt.

## Motion

System transitions (push, sheet present, zoom) unless a shared-element transition tells a better story. Spring-based easing; 250 to 400 ms; Reduce Motion replaces movement with cross-fade.

## Accessibility

VoiceOver labels, traits, and rotor order; Dynamic Type; Bold Text; Increase Contrast; Reduce Transparency; Voice Control names visible; colour never the sole carrier.

## Assets

- App icon: 1024 x 1024 master, no transparency, no rounded corners (the system masks); alternate icons if the product has a reason; dark and tinted variants for current iOS.
- Launch: a static launch screen that matches the first screen's chrome, not a splash animation.
- App Store: screenshots per device family at the required sizes, first three tell the story; preview video optional.
- Widgets and Live Activities need their own mark and type treatment at small sizes.

`export_asset_matrix.py --platforms ios` produces the icon set from the master SVG.

## Implementation mapping

Navigation stack and tab view, sheets with detents, searchable, toolbars, context menus, Live Activities: SwiftUI first; UIKit where a collection layout or a custom transition needs it. Flag anything that needs Metal, custom gesture recognisers, or a third-party animation engine.
