# Stitch Design — AI-Native UI Generation

**Outcome:** Stitch screens (HTML + PNG, optionally converted to React/Compose/SwiftUI) saved under `design/screens/`, consistent with the project's `DESIGN.md`, or a drift report against it. Done when the requested screens or report are on disk and any DESIGN.md changes have been proposed as a diff — never written without the user's approval.

Stitch is Google's AI UI-generation canvas; it exposes an MCP server. This skill runs only when the work goes through Stitch. General "design a screen" requests without Stitch belong to `design-studio`.

## Step 1: Classify

| Request | Workflow |
|---|---|
| "Generate / mock up X in Stitch", new screen from a prompt | Generate (Step 4) |
| "Pull / sync screens from Stitch project …" | Sync (Step 5) |
| "Audit our screens against DESIGN.md", design drift | Audit (Step 6) — findings only, no generation |
| Create or update DESIGN.md, extract a design system from a Stitch project | DESIGN.md lifecycle (Step 3) |
| Screen-to-code for an existing Stitch screen | Generate, steps 4–6 only |

## Step 2: Gather Context and Connect

1. **Platform target** — detect from the repo: `build.gradle.kts`/`*.kt` → Android (M3); `Package.swift`/`*.swift` → iOS (HIG); Next.js/React `package.json` → web (shadcn + Tailwind v4); nothing → web.
2. **Active DESIGN.md** — `.stitch/DESIGN.md`, then `DESIGN.md` at repo root. If neither exists, start from [assets/DESIGN.md.default](assets/DESIGN.md.default) and save the result to `.stitch/DESIGN.md` in the project. Client brand systems live in each client's repo, never in this skill.
3. **Stitch project ID** — from the user, STATE.md, or `list_projects`.
4. **MCP connection.** If the Stitch tools aren't available, configure the server. Google hosts a remote endpoint that takes an API key from stitch.withgoogle.com settings (reported URL `https://stitch.googleapis.com/mcp` with header `X-Goog-Api-Key` — confirm before use against Stitch's own MCP setup docs). The community stdio proxy `@_davideast/stitch-mcp` (individual-scoped npm package, also handles gcloud ADC) works too; if you use it, pin an exact version instead of bare `npx`, because an unpinned third-party package runs with the user's credentials.
   - Claude Code: `.mcp.json` / `claude mcp add`; Codex: `[mcp_servers.stitch]` in `~/.codex/config.toml`; Antigravity: its MCP store ("Stitch") or `mcp_config.json`.
   - Keep the key in an env var (`STITCH_API_KEY`); never write it into a committed file.

Read [references/mcp-tools.md](references/mcp-tools.md) when you need a tool's exact input/output schema.

## Step 3: DESIGN.md Lifecycle

- **Read** the active DESIGN.md before every generation or audit; extract palette, type scale, spacing, component defaults, platform notes.
- **Extract from Stitch:** `list_screens` → `get_screen` per screen → `extract_design_system` if exposed, otherwise synthesize from screen HTML → propose as `.stitch/DESIGN.md`.
- **After generation**, diff the new screen's colors/sizes/spacing against DESIGN.md. Propose additions as a marked diff and wait for approval — DESIGN.md is the client's source of truth, and silent edits propagate into every later screen.
- Read [references/design-system-guide.md](references/design-system-guide.md) when authoring a DESIGN.md from scratch or fixing one Stitch reads poorly.

## Step 4: Generate

1. **Enhance the prompt.** Replace vague terms with platform vocabulary, then structure it:
   ```markdown
   [One-line page purpose and visual atmosphere]
   **DESIGN SYSTEM (REQUIRED):** platform + mobile/desktop-first; palette with hex; font + weight rules; radius, elevation, spacing scale
   **PAGE STRUCTURE:** 1. [Section]: [components in specific UI terms] …
   **CONSTRAINTS:** accessibility, locale/RTL, platform patterns
   ```
   | Context | Android (M3) | iOS (HIG) | Web |
   |---|---|---|---|
   | Navigation | NavigationBar 3–5 destinations; NavigationRail on tablet | TabView with SF Symbols (Liquid Glass bar, iOS 26+); NavigationSplitView on iPad | Sidebar: Sheet on mobile, persistent on desktop |
   | Cards | ElevatedCard, surfaceContainerHighest, 12dp | Grouped list section, secondarySystemGroupedBackground | shadcn Card |
   | Inputs | OutlinedTextField with supportingText | TextField, Dynamic Type | shadcn Input + Label + FormMessage (zod) |
   | Icons | Material Symbols Outlined 24dp | SF Symbols, hierarchical | Lucide, `size-4`, currentColor |
2. **Mode.** Stitch offers a faster ideation mode and a higher-fidelity mode; its model lineup changes, so pick by intent (explore vs final) from what the Stitch UI/tool schema currently lists. Default to final unless the user says explore, try, brainstorm, or quick.
3. **Call** `generate_screen_from_text` (or the current generation tool) with the enhanced prompt, then `get_screen_code` and `get_screen_image`.
4. **Convert** (only if asked or the classification is screen-to-code): map to shadcn/React, Compose, or SwiftUI using [references/platform-patterns.md](references/platform-patterns.md) — read it when converting; read [references/platform-tokens.md](references/platform-tokens.md) when translating DESIGN.md tokens into Compose, Tailwind v4, or SwiftUI.
5. **Write** to `design/screens/<feature>/`: `<screen>.html`, `<screen>.png`, and `<Screen>.tsx` / `<Screen>Screen.kt` if converted. Kebab-case files, PascalCase components.
6. **Record** the asset in STATE.md (`<feature>/<screen>: generated <date>, Stitch project <id>`).

## Step 5: Sync

Resolve the project → `list_screens` → for each screen `get_screen_code` + `get_screen_image` → write `design/screens/<screen-title>/index.html` and `preview.png` → record the sync date and screen list in STATE.md.

## Step 6: Audit

1. Load DESIGN.md; `list_screens`; for each screen fetch code and image.
2. Parse colors, font sizes/weights, spacing, radius, and elevation from the CSS; compare to DESIGN.md tokens.
3. Report every drift item with severity (undefined color, off-scale spacing or type, inconsistent radius/elevation). Rank afterwards; don't drop low-severity items.
4. Write `design/audit-report.md`:
   ```markdown
   # Design Audit Report — <date>
   Screens analyzed: N · Token compliance: X% · Drift items: N
   | Screen | Issue | Expected | Actual | Severity |
   ```

## Handoff

- Output tree: `design/screens/<feature>/…`, `design/audit-report.md`, and `.stitch/DESIGN.md` (canonical).
- Add a short "Design Context" block (DESIGN.md path, screens dir, Stitch project ID, last sync) to the project's agent instructions file — CLAUDE.md, AGENTS.md, or GEMINI.md, whichever the project uses.
- The `workflows/*.yaml` files describe the three workflows declaratively for humans; no runtime executes them.

Deliver the requested screens or report; don't restyle unrelated screens or add unrequested conversions. Match length to the need; no filler sections.

## Related

`design-studio` (design direction and systems without Stitch) · `ios-design-expert`, `android-design-expert`, `web-design-expert` (platform depth) · `design-system` (component governance) · `accessibility-audit` (WCAG verification)
