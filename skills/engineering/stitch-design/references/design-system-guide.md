# DESIGN.md Authorship Guide

Comprehensive guide for creating, maintaining, and using DESIGN.md files with Stitch.

## What is DESIGN.md?

DESIGN.md is the source of truth for a project's visual design language. Stitch reads DESIGN.md during screen generation to ensure every screen follows the same visual system. It uses semantic, natural language descriptions paired with precise technical values.

## Full DESIGN.md Schema

A complete DESIGN.md includes these sections in order:

```markdown
# Design System: [Project Name]
**Project ID:** [Stitch project ID, if linked]

## 1. Visual Theme & Atmosphere
[Describe the overall mood, density, and aesthetic philosophy.
Use evocative adjectives: "Airy", "Dense", "Minimalist", "Bold", "Clinical".]

## 2. Color Palette & Roles
[List every color by: Descriptive Name (#hexcode) — functional role.
Group by: Primary, Secondary, Surface, Error, Text, Border, Overlay.]

## 3. Typography Rules
[Font families, weight rules per heading level, size scale with names,
letter-spacing, line-height conventions.]

## 4. Spacing Scale
[Base unit (e.g., 4px), named steps with pixel values.
Must define: xs, sm, md, lg, xl, 2xl at minimum.]

## 5. Elevation & Depth
[Shadow levels 0-5 with CSS shadow specs or descriptions.
Describe layering strategy: flat, subtle, pronounced.]

## 6. Component Defaults
[Default styles for core components:
Buttons, Cards, Inputs, Modals, Navigation, Lists.]

## 7. Motion & Animation
[Duration tokens: fast, medium, slow with ms values.
Easing curves: standard, decelerate, accelerate.
Reduced-motion policy.]

## 8. Platform Notes
[Target platform(s), framework specifics,
platform-appropriate deviations.]

## 9. Locale & Accessibility Notes
[RTL support, numeric formatting, date format,
WCAG level, contrast requirements, touch targets.]
```

## How Stitch Reads DESIGN.md

Stitch interprets DESIGN.md through "Visual Descriptions" — semantic language paired with exact values. When generating screens:

1. **Color matching** — Stitch maps color role names (Primary, Surface, etc.) to hex values and applies them to appropriate UI elements
2. **Typography** — Font family and scale are applied to headings, body text, labels, and captions
3. **Component patterns** — Button radius, card rounding, input height, and elevation inform all generated components
4. **Atmosphere** — The Visual Theme description guides overall layout density, whitespace, and decorative choices

### Best Practices for Stitch Readability

- Use descriptive color names with hex codes: `Deep Ocean Blue (#1A365D)` not just `#1A365D`
- Explain functional roles: "for primary buttons and links" not just "primary"
- Describe shapes in natural language: "Subtly rounded corners (8px)" not just `border-radius: 8px`
- Include the mood explicitly: "Clean and clinical" or "Bold and athletic"

## Extracting a Design System from a URL via MCP

To create a DESIGN.md from an existing Stitch project:

```
1. Call list_projects to find the project by name
2. Call extract_design_system with the project ID
   → Returns a raw design system document
3. Review the output for completeness
4. Restructure into the DESIGN.md schema above
5. Add any missing sections (motion, locale notes)
6. Write to [repo]/.stitch/DESIGN.md
```

To extract from a non-Stitch website URL:

```
1. Call generate_screen with the URL as reference
2. Call get_screen_code on the generated screen
3. Parse the HTML/CSS for color values, fonts, spacing
4. Synthesize into DESIGN.md format manually
```

## Keeping DESIGN.md in Sync Across Products

For organizations with multiple products sharing a design foundation:

### Shared Base + Product Overrides

```
design-systems/
├── base.design.md          ← Shared tokens (spacing, motion, elevation)
├── vendly.design.md        ← Product-specific (colors, typography, locale)
├── initiated.design.md     ← Product-specific
└── autograph.design.md     ← Product-specific
```

### Sync Strategy

1. **Base tokens** (spacing scale, elevation levels, motion durations) live in a shared base file
2. **Product tokens** (colors, typography, component overrides) live in product-specific files
3. When updating base tokens, regenerate product files by merging base + product overrides
4. After any generation, diff the screen's actual tokens against DESIGN.md — flag drift immediately

### Version Control

- Commit DESIGN.md alongside code changes
- Use descriptive commit messages: `design: add error state tokens to Vendly palette`
- Review DESIGN.md changes in PRs — treat them as API changes

## Anti-Patterns to Avoid

### Token Name Collisions

**Bad:** Using the same token name with different values across sections
```markdown
## Colors
- Blue (#2563EB) — primary actions
## Component Defaults
- Button color: Blue (#3B82F6)  ← Different blue!
```

**Good:** Reference by role, define once
```markdown
## Colors
- Action Blue (#2563EB) — primary interactive elements
## Component Defaults
- Button background: Action Blue
```

### Over-Specified Constraints

**Bad:** Dictating exact pixel values for every possible element
```markdown
- Login button: 48px height, 16px padding, 8px radius, 14px font
- Signup button: 48px height, 16px padding, 8px radius, 14px font
- Settings button: 48px height, 16px padding, 8px radius, 14px font
```

**Good:** Define component-level defaults, let Stitch apply consistently
```markdown
## Component Defaults
- Primary buttons: Medium height (48px), comfortable padding, subtle rounding (8px)
```

### Missing Functional Roles

**Bad:** Listing colors without explaining their purpose
```markdown
- #2563EB
- #10B981
- #EF4444
```

**Good:** Every color has a name and role
```markdown
- Confident Blue (#2563EB) — primary actions, links, focused states
- Success Green (#10B981) — success messages, positive indicators
- Alert Red (#EF4444) — error states, destructive actions, validation failures
```

### Ignoring Dark Mode

**Bad:** Defining only light mode tokens
```markdown
## Colors
- Background: White (#FFFFFF)
- Text: Near Black (#111827)
```

**Good:** Define both modes explicitly
```markdown
## Colors
### Light Mode
- Background: Clean White (#FFFFFF)
- Text: Near Black (#111827)
### Dark Mode
- Background: Deep Charcoal (#111827)
- Text: Soft White (#F9FAFB)
```

### Vague Atmosphere Descriptions

**Bad:** "Modern and clean"

**Good:** "Airy and spacious — generous whitespace between sections, subtle gray dividers, content-focused with minimal decorative elements. Conveys trust and professionalism without feeling corporate."
