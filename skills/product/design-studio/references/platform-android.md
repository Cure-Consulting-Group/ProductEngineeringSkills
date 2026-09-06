# Android and Google platforms: phones, tablets, foldables, Wear OS, Android TV

Judgment layer. For Compose component specs and code, invoke `android-design-expert`; for architecture, `android-feature-scaffold`. Android screens are never copies of the iOS screens; the brand is shared, the interaction is native.

## Structure and navigation

| Window size class | Navigation | Layout |
|---|---|---|
| Compact (< 600 dp) | Navigation bar (3 to 5 destinations), top app bar | single pane, list-detail as two screens |
| Medium (600 to 839 dp) | Navigation rail | two panes where content warrants; supporting pane |
| Expanded (>= 840 dp) | Navigation rail or permanent drawer | list-detail side by side; feed with multiple columns |

Foldables: posture-aware layouts (tabletop, book); hinge-aware two-pane; nothing important under the fold. Desktop and windowed Android: resizable windows, keyboard and mouse, right-click context menus.

Top app bar carries title and at most three actions plus overflow; bottom app bar with FAB only for screens whose one primary creation action justifies it. Modal bottom sheets for focused tasks, standard bottom sheets for persistent supplementary content. Dialogs for decisions that block. Snackbars for confirmations with an optional single action; never for errors that need reading.

Predictive back: every screen has a defined back destination and a preview that makes sense.

## Layout, insets, cutouts

- Edge-to-edge is the default: content draws behind system bars; controls respect insets (status, navigation, display cutout, IME).
- IME (keyboard) insets: the focused field and its action stay visible; scrolling containers resize, fixed bottom bars lift.
- 8 dp grid; 16 dp margins compact, 24 dp medium and expanded; 48 x 48 dp minimum touch target.

## Material 3 and Material 3 Expressive

- Colour: dynamic colour from the user's wallpaper is opt-in per brand decision; when the brand must stay fixed, define the full tonal palette (primary, secondary, tertiary, error, neutral, neutral-variant) and state it in the decision record. Surfaces use tonal elevation, not shadows alone.
- Typography: the M3 type scale (display, headline, title, body, label, each in large, medium, small) mapped to the brand faces; font scaling to 200 percent must hold.
- Shape: a shape scale (extra small to extra large) chosen once; expressive shape morphing on state only where the brand is playful.
- Motion: M3 easing sets (emphasised, standard) and duration tokens (short 50 to 200 ms, medium 250 to 400, long 450 to 600); container transform for shared elements; expressive springs where the register allows.
- Component states: enabled, disabled, hovered, focused, pressed, dragged, selected, activated, with state layers, not colour swaps.

## Accessibility

TalkBack content descriptions and traversal order; Switch Access; font scale; colour contrast in both light and dark; touch target 48 dp; no information carried by colour alone; focus visible for keyboard and D-pad (TV).

## Assets

- Adaptive launcher icon: 108 x 108 dp canvas, foreground and background layers, safe zone 66 dp diameter centred; the mark stays inside the safe zone, the background fills the canvas. Monochrome layer for themed icons (single-colour glyph, alpha only).
- Legacy launcher icons at mdpi through xxxhdpi (48 dp base) for older devices.
- Notification icon: 24 dp, white on transparent, alpha only; the coloured logo is a defect here.
- Splash: the system splash screen API (icon centred, brand background colour); no custom launch activity.
- Play Store: 512 x 512 icon, 1024 x 500 feature graphic, screenshots per form factor.
- Widgets: responsive sizes, rounded corners from the system, dynamic colour by default.
- Wear OS: round-first layouts, curved text where the platform provides it, tiles and complications from the mark's simplest form.

`export_asset_matrix.py --platforms android` produces adaptive foreground, legacy launcher sizes, and Play Store sizes from the master SVG. The monochrome layer is authored separately (single-colour glyph).

## Implementation mapping

Compose with Material 3: NavigationBar, NavigationRail, ListDetailPaneScaffold, ModalBottomSheet, TopAppBar with scroll behaviour, WindowSizeClass. Flag anything requiring custom Canvas drawing, RenderEffect shaders, or a custom gesture engine.
