---
name: stitch-design
version: "1.0.0"
description: "AI-native UI design and screen generation via Stitch MCP — vibe design, mockup creation, screen generation, UI prototyping, design system management, DESIGN.md authoring, component export, screen-to-code handoff, design token sync, visual consistency audits, Stitch canvas manipulation, and high-fidelity wireframe production"
when_to_use: "Use when generating UI screens via Stitch MCP, creating mockups, exporting design tokens, or running visual consistency audits. Requires Stitch API key."
argument-hint: "[screen-or-feature-description]"
compatibility:
  tools: [stitch-mcp]
  env: [STITCH_API_KEY, GOOGLE_APPLICATION_CREDENTIALS]
---

# Stitch Design — AI-Native UI Generation

## 1. Overview

This skill makes Stitch a first-class design agent in the Antigravity pipeline. Stitch is an AI-native infinite canvas that converts natural language into high-fidelity UI screens, exports DESIGN.md design system files, and exposes a fully functional MCP server.

**Pipeline position:** User prompt → stitch-design skill → Stitch MCP → HTML export → platform code (Compose/React/SwiftUI)

The skill handles three core workflows:
1. **Generate** — Create new screens from natural language descriptions
2. **Sync** — Pull existing Stitch project screens into the local repo
3. **Audit** — Validate design consistency against the project's DESIGN.md

## 2. MCP Configuration

Add the Stitch MCP server to your project's `.mcp.json` or Claude Code settings.

### Option A: API Key Authentication

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["@_davideast/stitch-mcp", "proxy"],
      "env": {
        "STITCH_API_KEY": "${STITCH_API_KEY}"
      }
    }
  }
}
```

### Option B: gcloud Application Default Credentials

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["@_davideast/stitch-mcp", "proxy"],
      "env": {
        "STITCH_USE_SYSTEM_GCLOUD": "1"
      }
    }
  }
}
```

Run `npx @_davideast/stitch-mcp init` for guided setup. See [references/mcp-tools.md](references/mcp-tools.md) for full tool schemas.

## 3. Trigger Conditions

Activate this skill when the user's prompt matches ANY of these:

| Trigger Phrase / Context | Example |
|---|---|
| "design a screen/page/view" | "Design a checkout screen" |
| "generate UI/mockup/wireframe" | "Generate a mockup for the settings page" |
| "create a [component] layout" | "Create a dashboard layout" |
| "vibe design" or "vibe code" | "Vibe design a landing page" |
| "stitch" mentioned explicitly | "Use Stitch to make a login screen" |
| "DESIGN.md" mentioned | "Update the DESIGN.md with new tokens" |
| "screen-to-code" or "design handoff" | "Convert this screen to Compose" |
| "design system" + generation context | "Generate screens using our design system" |
| New feature requiring UI scaffolding | "Build the onboarding flow" (when UI is implied) |
| "design audit" or "design consistency" | "Audit our screens for consistency" |
| "pull screens from Stitch" | "Sync the latest designs from Stitch" |
| "export design" or "export components" | "Export the dashboard as React components" |

**Rule:** If a new screen, mockup, or UI component is being discussed, this skill fires. Be aggressive — design intent triggers this skill even without explicit "Stitch" mentions.

## 4. Prompt Enhancement Protocol

Before sending any prompt to the Stitch MCP, enhance it through this pipeline:

### Step 1: Detect Platform Target

Check the project for platform signals:

| Signal | Platform | Token Set |
|---|---|---|
| `build.gradle.kts`, `*.kt` files | Android | Material 3 tokens |
| `Package.swift`, `*.swift` files | iOS | HIG tokens |
| `package.json` + Next.js/React | Web | shadcn/Tailwind tokens |
| No signals detected | Web (default) | shadcn/Tailwind tokens |

### Step 2: Load DESIGN.md Context

1. Check `[repo]/.stitch/DESIGN.md` — use if present
2. Check `[repo]/DESIGN.md` — use if present
3. Fall back to skill asset seeds (see Section 10 for product mapping)
4. If no DESIGN.md exists anywhere, use `assets/DESIGN.md.default`

Extract: color palette, typography scale, spacing grid, component defaults, and platform notes.

### Step 3: Inject Platform-Specific Design Vocabulary

Replace vague terms with professional, platform-aware design terminology. Use Material 3 patterns for Android, Apple HIG patterns for iOS, and shadcn/Radix patterns for Web.

**General UI/UX Vocabulary:**

| Vague Input | Enhanced Output |
|---|---|
| "nice header" | "Sticky navigation bar with brand logo, primary nav items, and user avatar" |
| "list of things" | "Vertical card list with thumbnail, title, subtitle, and action affordance" |
| "button" | "Primary call-to-action button with label and optional leading icon" |
| "form" | "Form with labeled input fields, validation states, and submit CTA" |
| "menu" | "Navigation drawer / bottom sheet with grouped menu items and icons" |

**Platform-Specific Injection (applied automatically based on Step 1 detection):**

| Context | Android (M3) Injection | iOS (HIG) Injection | Web Injection |
|---|---|---|---|
| Navigation | "Bottom NavigationBar with 3-5 destinations, NavigationRail on tablet" | "TabView with SF Symbol icons, NavigationSplitView on iPad" | "Responsive sidebar (Sheet on mobile, persistent on desktop)" |
| Cards | "M3 ElevatedCard with surfaceContainerHighest fill, 12dp rounding" | "Grouped list section with .secondarySystemGroupedBackground" | "shadcn Card with CardHeader/CardContent, hover:shadow-md" |
| Inputs | "M3 OutlinedTextField with supportingText, 56dp height" | "TextField with .roundedBorder, Dynamic Type scaling" | "shadcn Input with Label, FormMessage for zod validation" |
| Colors | "M3 tonal palette: primary, primaryContainer, surface roles" | "HIG system colors: .label, .systemBackground, .tint" | "CSS variables: --primary, --background, --foreground HSL" |
| Icons | "Material Symbols Outlined, 24dp, onSurface tint" | "SF Symbols with hierarchical rendering, Dynamic Type scaling" | "Lucide icons, h-4 w-4 className, currentColor" |
| Motion | "M3 motion: FastOutSlowIn 300ms for shared axis transitions" | "Spring animation with .sensoryFeedback for haptics" | "Tailwind duration-300 ease-in-out, prefers-reduced-motion" |

Cross-reference [references/platform-patterns.md](references/platform-patterns.md) for complete component mapping tables.

### Step 4: Select Generation Mode

| Mode | Model | Use When |
|---|---|---|
| Ideation | Gemini Flash | Exploring multiple directions, early concepts, rapid iteration |
| Production | Gemini Pro | Final screens, pixel-perfect output, client-ready designs |

Default to **Production** unless the user says "explore", "try", "brainstorm", or "quick".

### Step 5: Structure the Enhanced Prompt

Format the final prompt for Stitch:

```markdown
[One-line page purpose and visual atmosphere]

**DESIGN SYSTEM (REQUIRED):**
- Platform: [Web/Mobile], [Desktop/Mobile]-first
- Palette: [Primary] (#hex), [Secondary] (#hex), [Surface] (#hex)
- Typography: [Font family], [weight rules]
- Styles: [Border radius], [elevation], [spacing scale]

**PAGE STRUCTURE:**
1. **[Section]:** [Component breakdown with specific UI terms]
2. **[Section]:** [Component breakdown]
...

**CONSTRAINTS:**
- [Accessibility requirements]
- [Locale/RTL considerations]
- [Platform-specific patterns]
```

## 5. DESIGN.md Lifecycle

### Locate Active DESIGN.md

Search in order:
1. `[repo]/.stitch/DESIGN.md` (primary location)
2. `[repo]/DESIGN.md` (project root)
3. Skill asset seed (mapped by product — see Section 10)

### Create from Seed

If no DESIGN.md exists, copy the appropriate seed:

```bash
mkdir -p [repo]/.stitch
cp [skill-root]/assets/DESIGN.md.[product] [repo]/.stitch/DESIGN.md
```

### Update After Generation

After any screen generation that introduces new patterns:
1. Diff new screen tokens against existing DESIGN.md
2. Identify new colors, components, or spacing values not in the system
3. Propose additions as a clearly marked diff block
4. Wait for user approval before writing changes

### Extract from Stitch URL

To pull a design system from an existing Stitch project:
1. Call `list_projects` to find the project by name or URL
2. Call `list_screens` to get all screens in the project
3. Call `get_screen` for each screen to retrieve design metadata
4. Call `extract_design_system` if available, or synthesize from screen HTML
5. Write the extracted system to `[repo]/.stitch/DESIGN.md`

See [references/design-system-guide.md](references/design-system-guide.md) for the full DESIGN.md schema.

## 6. Screen Generation Workflow

Execute these steps in order. Maps to [workflows/generate.yaml](workflows/generate.yaml).

1. **Load DESIGN.md** — Read the active DESIGN.md (see Section 5)
2. **Enhance prompt** — Run the Prompt Enhancement Protocol (Section 4)
3. **Generate screen** — Call `generate_screen` (or `generate_screen_from_text`) via Stitch MCP with the enhanced prompt and DESIGN.md context
4. **Retrieve HTML** — Call `get_screen_code` with the returned screen ID to download the generated HTML
5. **Convert to platform code** (optional) — If targeting Compose or React:
   - Run `react:components` conversion for shadcn/React output
   - Map HTML components to Compose equivalents for Android
6. **Write outputs** — Save files to `[repo]/design/screens/[feature]/`:
   - `[screen-name].html` — raw Stitch HTML
   - `[screen-name].png` — screenshot (from `get_screen_image`)
   - `[screen-name].tsx` or `.kt` — converted platform code (if applicable)
7. **Update STATE.md** — Append new design asset entry:
   ```markdown
   ## Design Assets
   - [feature]/[screen-name]: Generated [date], Stitch project [project-id]
   ```

## 7. Sync Workflow

Pull all screens from an existing Stitch project. Maps to [workflows/sync.yaml](workflows/sync.yaml).

1. **Resolve project** — Get the Stitch project ID from user input, STATE.md, or `list_projects`
2. **List screens** — Call `list_screens` with the project ID
3. **Download each screen** — For each screen returned:
   - Call `get_screen_code` to retrieve HTML
   - Call `get_screen_image` to retrieve screenshot
4. **Write outputs** — Save to `[repo]/design/screens/[screen-title]/`:
   - `index.html` — screen HTML
   - `preview.png` — screen screenshot
5. **Update STATE.md** — Record sync timestamp and screen manifest

## 8. Audit Workflow

Run a design consistency audit. Maps to [workflows/audit.yaml](workflows/audit.yaml).

1. **Load DESIGN.md** — Read the active design system specification
2. **List screens** — Call `list_screens` to enumerate all project screens
3. **Analyze each screen** — For each screen:
   - Call `get_screen_image` for visual reference
   - Call `get_screen_code` to extract HTML/CSS
   - Parse color values, font sizes, spacing, border radius from the CSS
   - Compare against DESIGN.md token definitions
4. **Detect drift** — Flag any value that does not match a defined token:
   - Undefined colors (hex values not in the palette)
   - Non-standard font sizes or weights
   - Spacing values outside the defined scale
   - Inconsistent border radius or elevation
5. **Emit drift report** — Write `[repo]/design/audit-report.md`:
   ```markdown
   # Design Audit Report — [date]
   ## Summary
   - Screens analyzed: [N]
   - Token compliance: [X]%
   - Drift items: [N]
   ## Findings
   | Screen | Issue | Expected | Actual | Severity |
   |---|---|---|---|---|
   ```
6. **Update STATE.md** — Record audit date and compliance score

## 9. Handoff Conventions

### Output Directory Structure

```
[repo]/design/
├── screens/
│   ├── [feature-a]/
│   │   ├── screen-name.html      ← Stitch raw HTML
│   │   ├── screen-name.png       ← Screenshot
│   │   └── screen-name.tsx       ← Converted React component (if web)
│   └── [feature-b]/
│       ├── screen-name.html
│       ├── screen-name.png
│       └── screen-name.kt        ← Mapped Compose scaffold (if Android)
├── audit-report.md               ← Latest audit output
└── DESIGN.md                     ← Symlink or copy of .stitch/DESIGN.md
```

### Naming Conventions

| Context | Convention | Example |
|---|---|---|
| Feature directory | kebab-case from feature name | `checkout-flow/` |
| Screen file | kebab-case from screen title | `payment-summary.html` |
| Compose mapping | PascalCase screen name + `Screen` | `PaymentSummaryScreen.kt` |
| React component | PascalCase screen name | `PaymentSummary.tsx` |

### CLAUDE.md Update

After generating screens, append to the project's CLAUDE.md:

```markdown
## Design Context
- Design system: .stitch/DESIGN.md
- Generated screens: design/screens/
- Stitch project ID: [id]
- Last sync: [date]
```

## 10. Per-Product Context

| Product | DESIGN.md Seed | Platform | Key Rules |
|---|---|---|---|
| **Vendly** | `DESIGN.md.vendly` | Android (Compose) | Material 3, green #00A859 primary, Inter font, es-DO locale, high-contrast for outdoor POS, RTL-ready |
| **The Initiated** | `DESIGN.md.initiated` | Android + Web | Dark-first, gold #C9A84C primary, navy #1B2A4A surface, Bebas Neue/Inter fonts, card-heavy editorial, athletic energy |
| **Autograph** | `DESIGN.md.default` + overrides | Web | HIPAA-neutral density, physician dashboard, high information density, clinical color palette, no decorative elements |
| **Default** | `DESIGN.md.default` | Web | Clean neutral, Inter font, blue #2563EB primary, light-first with dark mode defined |

For Autograph: start with the default seed, then override surface colors to clinical whites/grays, increase information density spacing, and add HIPAA compliance notes.

### Seed Files

- [assets/DESIGN.md.vendly](assets/DESIGN.md.vendly) — Vendly POS design system
- [assets/DESIGN.md.initiated](assets/DESIGN.md.initiated) — The Initiated design system
- [assets/DESIGN.md.default](assets/DESIGN.md.default) — Generic fallback

See [references/platform-tokens.md](references/platform-tokens.md) for token translation tables and [references/platform-patterns.md](references/platform-patterns.md) for Material 3, Apple HIG, and Web component pattern mappings.

### Cross-References

- `/android-design-expert` — Deep Material 3 patterns (tonal palettes, M3 components, motion system, Material Symbols)
- `/ios-design-expert` — Deep Apple HIG patterns (Dynamic Type, SF Symbols, haptics, system colors, Live Activities)
- `/web-design-expert` — Deep web patterns (responsive design, container queries, Core Web Vitals, accessibility)
- `/design-system` — Design token architecture, component libraries, cross-platform consistency rules
- `/product-design` — Platform detection router, design principles, Figma handoff standards
- `/accessibility-audit` — WCAG compliance verification, contrast ratios, screen reader testing
