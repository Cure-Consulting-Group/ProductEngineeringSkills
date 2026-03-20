# Stitch Design — AI-Native UI Generation

Generate high-fidelity UI screens, manage design systems, and sync designs from Stitch's AI-native infinite canvas via MCP.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls .stitch/ design/ 2>/dev/null` to check for existing design assets
- Check for `.stitch/DESIGN.md` or `DESIGN.md` in the project root
- Use this context to tailor all output to the actual project

## Step 1: Classify the Design Request

| Request Type | Workflow | Primary MCP Tools |
|---|---|---|
| New screen/page/mockup | Generate | `generate_screen` → `get_screen_code` |
| Edit existing screen | Edit | `edit_screen` → `get_screen_code` |
| Pull designs from Stitch project | Sync | `list_screens` → `get_screen_code` |
| Design consistency check | Audit | `list_screens` → `get_screen_image` |
| Create/update DESIGN.md | Design System | `extract_design_system` |
| Export to platform code | Handoff | `get_screen_code` → platform conversion |

If the user's request is ambiguous, ask: "Are you looking to generate a new screen, sync existing designs, or audit consistency?"

## Step 2: Gather Context

1. **Screen/feature name** — e.g., "checkout flow", "settings page"
2. **Platform** — Android (Compose) / Web (React) / both
3. **Design system** — check for DESIGN.md, fall back to product seed
4. **Stitch project** — existing project ID, or create new
5. **Fidelity** — ideation (Gemini Flash) or production (Gemini Pro)

If missing, infer from project files or ask one clarifying question max.

## Step 3: MCP Configuration

Ensure Stitch MCP is configured:

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["@_davideast/stitch-mcp", "proxy"],
      "env": { "STITCH_API_KEY": "${STITCH_API_KEY}" }
    }
  }
}
```

Alternative: Use `STITCH_USE_SYSTEM_GCLOUD=1` for gcloud ADC auth.

## Step 4: Prompt Enhancement with Platform Patterns

Before sending to Stitch MCP, enhance the user's prompt with platform-aware design vocabulary:

1. Detect platform target from project files (build.gradle.kts → M3, Package.swift → HIG, package.json → Web)
2. Load DESIGN.md tokens (colors, typography, spacing) including M3 tonal palette or HIG system colors
3. Replace vague UI terms with platform-specific design vocabulary:
   - **Android:** M3 components (NavigationBar, ElevatedCard, OutlinedTextField), Material Symbols, tonal elevation
   - **iOS:** HIG components (TabView, NavigationSplitView, .sheet), SF Symbols, Dynamic Type, haptic feedback
   - **Web:** shadcn/Radix components (Card, Sheet, Command), Lucide icons, responsive breakpoints, CSS variables
4. Structure as: atmosphere → design system → page sections → constraints
5. Select generation mode (Flash for ideation, Pro for production)

## Step 5: Execute Workflow

### Generate Flow
1. Load DESIGN.md context
2. Enhance the prompt
3. Call `generate_screen` via Stitch MCP
4. Retrieve HTML via `get_screen_code`
5. Convert to platform code if targeting Compose or React
6. Write outputs to `design/screens/[feature]/`
7. Update STATE.md

### Sync Flow
1. Get project ID from user or `list_projects`
2. Call `list_screens` to enumerate all screens
3. Download each screen (HTML + image)
4. Write to `design/screens/[screen-title]/`
5. Update STATE.md

### Audit Flow
1. Load DESIGN.md token definitions
2. List and download all screens
3. Parse CSS for color, font, spacing values
4. Compare against DESIGN.md tokens
5. Write drift report to `design/audit-report.md`
6. Update STATE.md

## Step 6: Output Conventions

```
[repo]/design/
├── screens/
│   └── [feature]/
│       ├── screen-name.html     ← Stitch raw HTML
│       ├── screen-name.png      ← Screenshot
│       └── screen-name.tsx/.kt  ← Platform code
├── audit-report.md              ← Latest audit
└── .stitch/DESIGN.md            ← Design system source of truth
```

## Per-Product Design Systems

| Product | Primary Color | Font | Platform | Locale |
|---|---|---|---|---|
| Vendly | #00A859 (Green) | Inter | Android/Compose | es-DO |
| The Initiated | #C9A84C (Gold) | Bebas Neue + Inter | Android + Web | en-US |
| Autograph | Neutral clinical | Inter | Web | en-US |
| Default | #2563EB (Blue) | Inter | Web | en-US |

## Cross-References

- `/android-design-expert` — Deep Material 3 patterns (tonal palettes, M3 components, motion, Material Symbols)
- `/ios-design-expert` — Deep Apple HIG patterns (Dynamic Type, SF Symbols, haptics, system colors)
- `/web-design-expert` — Deep web patterns (responsive, container queries, Core Web Vitals, accessibility)
- `/design-system` — Design token architecture, component libraries, cross-platform consistency
- `/android-feature-scaffold` — Compose implementation after design handoff
- `/nextjs-feature-scaffold` — React implementation after design handoff
- `/product-design` — Platform detection router, design principles, Figma handoff
- `/accessibility-audit` — WCAG compliance verification of generated screens
