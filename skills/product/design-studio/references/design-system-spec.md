# Design System Specification: foundations, tokens, components, cross-platform

For Storybook, Showkase, SwiftUI catalogues, governance, and versioning, invoke `design-system`. This file is what the studio produces so that skill has something to build.

## 1. Foundations (define every one, even if the value is "none")

color, typography, spacing, grids, radius, elevation, borders, shadows, opacity, motion (durations, easings), iconography (grid, stroke, corner, sizes), imagery (crop, treatment, ratios).

## 2. Three token tiers

| Tier | Names | Purpose | Example |
|---|---|---|---|
| Primitive | palette and scale values | raw material, never used in a component | `blue.600`, `space.4`, `font.size.5` |
| Semantic | meaning | what a colour or size is *for*; the tier components consume | `color.surface.primary`, `color.text.secondary`, `spacing.md`, `radius.card`, `motion.duration.fast` |
| Component | one component's knobs | only when a component needs an override or a variant axis | `button.primary.bg`, `input.border.error` |

Rules: components reference semantic or component tokens only; semantic tokens alias primitives; every semantic token has a value per mode (light, dark, high-contrast where offered); naming is `category.property.variant.state`, lower case, dots, no abbreviations except `bg` and `fg`. Write tokens in the W3C Design Tokens format (`w3c_token_schema.json`); `tokens_lint.py` checks tiers, aliases, and mode parity; `contrast_check.py` checks the pairs.

Minimum semantic set for a product, named so `contrast_check.py` knows what to pair: `color.surface.{primary,secondary,tertiary,inverse}`, `color.text.{primary,secondary,tertiary,disabled,inverse,link}` (text is checked on every non-inverse surface; inverse on inverse; disabled skipped), `color.border.{default,strong,focus}` (strong and focus checked at 3:1 on surfaces), `color.brand.{primary,on-primary}` (`on-x` is checked on its sibling `x`), `color.status.<success|warning|error|info>.{fill,on-fill,subtle,text}` (`on-fill` on `fill`, `text` on `subtle`), spacing (xs to 3xl on a 4 or 8 base), radius (none, sm, md, lg, full), elevation (0 to 4), motion (duration fast, base, slow; easing standard, emphasised, exit), typography roles (display, h1 to h4, body-lg, body, body-sm, label, caption, code).

## 3. Component specification template

Every component in the system gets this, in this order. Skip a row only with "n/a" and a reason.

```
COMPONENT     <name>
PURPOSE       one sentence; when to use; when not to (name the alternative)
ANATOMY       numbered parts (container, leading icon, label, trailing action, helper text ...)
VARIANTS      axes and values (emphasis: primary | secondary | tertiary; tone: neutral | danger)
SIZES         values with height, padding, type role, icon size, min target
STATES        default, hover, focused, pressed, selected, disabled, loading, error (+ data states if applicable)
BEHAVIOUR     keyboard (keys and order), pointer, touch, gestures; what changes on activation
RESPONSIVE    what changes across size classes; truncation and wrapping rules
CONTENT       label length limits, casing, icon rules, i18n expansion allowance
ACCESSIBILITY role, name, description, focus ring, contrast, announcements
TOKENS        the semantic tokens consumed
PLATFORMS     web | iOS | Android differences (or "identical")
MOTION        per the motion spec format
```

## 4. Component inventory

Core: button, icon button, link, input, textarea, search, select, dropdown and menu, combobox, checkbox, radio, switch, slider, date and time picker, chip, tag, badge, avatar, card, list and list item, table, tabs, segmented control, navigation (bar, rail, sidebar, tabs), breadcrumb, pagination, tooltip, popover, dialog, sheet, drawer, toast and snackbar, banner, progress and skeleton, empty state, media (image, video, gallery), chart wrappers.

Ship the core with all states before adding anything exotic.

## 5. Cross-platform: shared brand, native interaction

| Concern | Shared | Platform-specific |
|---|---|---|
| Colour | semantic tokens and modes | tonal elevation (Android), materials (Apple) |
| Typography | roles, scale ratio, hierarchy philosophy | SF (Apple), brand or Roboto flex (Android), web stack; platform text-scaling |
| Iconography | one icon language and grid | SF Symbols and Material Symbols rendered to match it |
| Spacing logic | base unit and scale | platform margins (16/20 pt, 16/24 dp) |
| Imagery and tone | identical | none |
| Navigation | destinations and hierarchy | web sidebar; iPad adaptive sidebar; iPhone tab bar; Android phone navigation bar; Android tablet rail or pane |
| Motion | intent and durations | system transitions and easing sets |

Pixel-identical across platforms is a defect. Brand-inconsistent across platforms is a defect. The line between them is written in the decision record.

## 6. Hand-off package

Dimensions, spacing, typography roles, tokens with values per mode, assets (SVG and platform sets), behaviour per component, responsive rules, motion spec, implementation notes mapped to the target stack, and the decision record. An engineer should be able to estimate from it without a meeting.
