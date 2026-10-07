You are the Creative Director on a design review panel. You own: concept, originality, brand, art direction, visual storytelling, emotional resonance.
You ask: Is there one idea? Could another product look identical? What is memorable? Where is it generic? Does the register (expressive vs utility) fit the assignment?

BRIEF
# Design Brief: Cure Claude Code Mods Suite

## Step 1: Classification

```
KIND       mixed (product UX + terminal design system)
REGISTER   utility
PLATFORMS  terminal (Claude Code TUI, Ghostty, Kitty, iTerm2, Apple Terminal), desktop
DEPTH      product
```

---

## 1. Executive Summary & Business Goal

Cure Consulting Group distributes five modular Claude Code plugins ("mods") through its internal marketplace (`marketplace.json`):
1. `cure-policy-guard`: Enforces organizational safety and compliance rules before file modifications land.
2. `cure-lane-verifier`: Audits subagent and multi-lane git mutations, flagging empty branch completions.
3. `cure-spend-band`: Monitors daily GitHub Actions burn and projects monthly usage against the $300 allowance.
4. `cure-cache-band`: Visualizes Anthropic prompt cache TTL countdown, hit rates, and cold-start token penalties.
5. `cure-image-viewer`: Renders pasted image thumbnails in-line above the prompt via modern terminal graphics protocols.

### Problem Statement
The mods were authored as independent, isolated scripts. As a result:
- **Spatial collisions:** Multiple mods compete for the `AbovePrompt` surface (`cure-cache-band`, `cure-image-viewer`, and future `cure-rules-band`) without an agreed composition layout, vertical height budget, or stacking protocol.
- **Inconsistent visual grammar:** Some mods use ANSI colors, others raw text, others unicode blocks, without a unified token hierarchy or light/dark terminal parity.
- **Cognitive friction:** Slash commands (`/spend`, `/cache`, `/policy-guard`) return raw unstructured strings instead of structured, glanceable executive consoles.
- **Interruptive vs Ambient UX:** Interactive prompts (such as `cure-policy-guard` write interceptions) lack clear severity grading, and toast alerts (`cure-lane-verifier`) risk being overlooked or jarring.

### Objective
Design an end-to-end Terminal UI (TUI) and UX architecture for the Cure Claude Code Mods suite that makes Claude Code feel like a world-class, cockpit-grade engineering environment.

---

## 2. User & Situation

- **Target User:** Senior software engineers, engineering managers, and technical founders operating inside Claude Code CLI for 4–10 hours daily across 30+ repositories.
- **Context & Posture:**
  - High focus, rapid keystroke cadence, keyboard-only or keyboard-first navigation.
  - Viewport: Terminal windows ranging from 80 columns (split pane / mobile SSH) to 140+ columns (full-screen ultrawide / 4K monitor), height typically 24–50 rows.
  - Cognitive state: Deep context switching; cannot tolerate vertical prompt jumping, flickering redrawing, or verbose wall-of-text interruptions.
- **Frequency:**
  - Ambient telemetry (cache, spend, images): Constantly visible or on-turn completion.
  - Guardrail intercepts (policy): Intermittent (0–3 times per session), but mission-critical when active.
  - Deep-dive audits (`/spend`, `/cache`, `/policy-guard`): On-demand, 1–5 times per day.

---

## 3. Real Content & Working Scenarios

| Surface | Real Content / Scenarios |
|---|---|
| **Cache Band** | • Warm: `1h` TTL, 54m remaining, 76% hit rate, 0 misses.<br>• Expiring: `5m` TTL, 42s remaining, amber alert.<br>• Cold: Lapsed cache, penalty calculation ("next turn pays +82,410 write tokens"). |
| **Spend Band** | • Safe pace: $6.40 today, MTD $112, projected $248 vs $300 allowance.<br>• Overage warning: MTD $210, projected $384 (+$84 overage), amber warning banner under prompt.<br>• Failure state: `gh` token expired or rate limited, showing graceful fallback with last cached data. |
| **Policy Guard** | • Rule violations: `no-cron` (schedule trigger in GitHub workflow), `level5-vertex-only` (unauthorized Gemini consumer key), `minors-new-ai-vendor` (unapproved vendor in youth app), `hardcoded-secret` (Stripe sk_live key).<br>• Decision flow: Interactive dialog (`Refuse write` vs `Allow once (logged)`).<br>• Audit trail: 10 most recent recorded overrides with timestamp, repository, path, and violated rule. |
| **Lane Verifier** | • Verified lane: Subagent reports 42 passing tests; Git verifies `lane/auth-mvi` has 3 commits ahead, `+142 -18` diff across 4 files.<br>• Empty completion alarm: Subagent claims "Task completed successfully"; Git reports 0 commits ahead, 0 files changed (`EMPTY COMPLETION`).<br>• Dirty worktree detection: Target worktree has uncommitted modifications. |
| **Image Viewer** | • Single image: 1200x800 diagram pasted via clipboard.<br>• Multi-image: 3 UI mockups pasted in draft prompt.<br>• Fallback: Terminals lacking Kitty protocol (e.g., standard Apple Terminal) rendering clean dimensional badges with captioning. |

---

## 4. Constraints

1. **Terminal Canvas Budget:**
   - Vertical real estate is precious. The total `AbovePrompt` shelf height must not exceed 2–4 rows when all mods are active.
   - Horizontal width must gracefully adapt from 80 columns (compact) to 160 columns (expanded).
2. **Platform & Protocol Capabilities:**
   - Claude Code Mod Hooks (2.1.289 API): `AbovePrompt`, `Spinner`, `ui.status`, `ui.toast`, `ui.ask`, `command.run`.
   - Terminal Graphics: Kitty graphics protocol supported in Ghostty, Kitty, WezTerm; absent in Apple Terminal, Warp, VSCode integrated terminal (requires graceful ASCII/Unicode badge fallback).
   - Color Modes: Light and dark terminal profiles. Minimum 4.5:1 text contrast and 3:1 graphical border/indicator contrast under WCAG 2.2 AA.
3. **Performance & Stability:**
   - 0 ms perceptible typing lag; render invalidations must be throttled (1 Hz during final minute, 1/60 Hz prior).
   - No terminal flicker; no raw ANSI leaks.

---

## 5. Competitors & Prior Art

1. **Starship Prompt:**
   - *Strengths:* Renowned for instantaneous, compact glyph status indicators without clutter; zero vertical waste.
   - *Lesson for Cure:* Status indicators must be concise, micro-dense, and unified into an cohesive horizontal shelf rather than disparate lines.
2. **Charm.sh (Lip Gloss & Bubble Tea / Lazygit):**
   - *Strengths:* Best-in-class TUI spatial hierarchy, disciplined rounded box borders (`╭──╮`), muted semantic tints, and structured multi-column tables.
   - *Lesson for Cure:* Command outputs (`/spend`, `/cache`, `/policy-guard`) should borrow Lip Gloss's structural dignity: clean borders, distinct column alignments, and muted secondary text.
3. **GitHub CLI (`gh`):**
   - *Strengths:* Standard-setting command line tool with rock-solid, scannable tabular reports and quiet failure states.
   - *Lesson for Cure:* Command reports must display timestamped freshness, clean summary statistics, and concise error messages when subcommands fail.

---

## 6. Inventory of Current Mod Surfaces & Gaps

| Mod | Current Surface | Current UI Treatment | Deficiencies / Gaps |
|---|---|---|---|
| `cure-cache-band` | `AbovePrompt` | Block meter `cache ● 1h ██████ 59m left · hit 76%` | Hardcoded colors; collides with other `AbovePrompt` consumers; no compact 80-col mode. |
| `cure-image-viewer` | `AbovePrompt` | Grid of images or text captions | Pushes prompt down significantly; lacks responsive vertical cap; doesn't share shelf with cache-band. |
| `cure-spend-band` | `Spinner` + `ui.status` + `/spend` | Suffix `· Actions $X today`, warning line | Suffix can cause spinner wobble; warning line format lacks clear visual severity tag; `/spend` is unstyled text. |
| `cure-policy-guard` | `ui.ask` + `/policy-guard` | Plain question box with 2 options | No visual risk level; doesn't show code diff or line preview; `/policy-guard` is plain string dump. |
| `cure-lane-verifier` | `context` + `ui.toast` | Context text block + standard toast | Plain text in context; toast duration may flash by; lack of unified badge styling for diff verification. |



ARTEFACTS
===== design/ux-architecture.md =====
# UX Architecture: Cure Claude Code Mods Suite

## 1. The Ten Questions

### 1. Who is using this, and in what situation?
- **User:** High-output engineers, technical founders, and autonomous agent orchestrators.
- **Posture & Situation:** Terminal workspace (Ghostty, Kitty, iTerm, macOS Terminal), split screens, 80 to 160 columns, 24 to 50 rows.
- **Attention:** Focused on code problem-solving. Mod UI must be non-distracting, ambient, and readable at a peripheral glance.

### 2. What are they trying to accomplish, in their words?
- "Let me write code without worrying about blowing my GitHub Actions budget, getting burned by expired cache fees, pasting uninspected images, committing house rule violations, or accepting empty agent hand-backs."

### 3. What information do they need to decide or act?
- **Cache:** How much TTL is left before my next prompt pays full re-cache write pricing?
- **Spend:** Is my monthly Actions budget on track or pacing into an overage?
- **Images:** Did my clipboard paste the right graphic, and how big will it look to the model?
- **Policy:** Exactly what file and rule did the tool call violate, why is it forbidden, and do I need to permit an exception?
- **Lane Verifier:** Did this subagent actually commit the code it claimed, or did it report 100% tests passed with an empty git diff?

### 4. What single action has the highest priority on this screen?
- Maintain flow state and submission readiness in the prompt box without visual interruption, unless a security/budget policy is actively breached.

### 5. What must they see first?
- When ready to type: Current cache status (warm green vs expiring amber vs cold red) and any pasted image previews.
- When thinking/waiting: Active turn spinner with calm spend telemetry.
- On breach: High-contrast modal dialog explaining the blocked action with binary resolution.

### 6. What is secondary?
- Session aggregate hit rates, token penalty approximations, historical overrides, and breakdown of past day-by-day Actions cost. (Available on demand via `/spend`, `/cache`, `/policy-guard`).

### 7. What stays hidden until needed (progressive disclosure)?
- Detailed cost breakdowns, raw git diff stats, rule source files, and image metadata remain hidden in ambient mode and expand only when invoking the respective slash commands or when a violation occurs.

### 8. Which navigation model fits?
- **Command & Ambient Shelf Model:**
  - Ambient telemetry sits anchored in `AbovePrompt` and `Spinner`.
  - Interruptions sit in transient modal prompts (`ui.ask`).
  - Deep-dive telemetry navigates via slash commands into the terminal scrollback (`/spend`, `/cache`, `/policy-guard`).

### 9. What happens next, and how do they know it worked?
- Submitting a prompt transitions `AbovePrompt` into execution mode (clears image draft, updates cache countdown).
- Overriding a policy guard logs the exception with a persistent audit timestamp and outputs an inline confirmation tag.
- Calling `/spend` or `/cache` prints a self-contained, bordered terminal card into the terminal scrollback.

### 10. What happens when it fails, and how do they recover?
- **Network / API failure (`gh api`):** Spend band falls back quietly to the last known cache timestamp with a subtle `(offline · last 14:32 UTC)` indicator; never crashes or blocks the terminal.
- **Terminal graphics missing:** Image viewer detects lack of Kitty protocol and renders crisp ASCII/Unicode bounding dimension cards.
- **Empty branch alarm:** Lane verifier issues a distinct high-visibility toast and appends a `[EMPTY COMPLETION]` warning block to model context.

---

## 2. The Model Chain

```
User (Senior Engineer / Orchestrator)
  └─► Goal (Maintain flow velocity while maintaining compliance, cost, and agent truth)
        └─► Flow (Ambient Monitoring ──► Prompt Composition ──► Execution/Interception ──► Audit/Deep-dive)
              └─► Surfaces:
                    ├─ Surface 1: AbovePrompt (Unified Telemetry & Asset Shelf)
                    ├─ Surface 2: Spinner / Status Bar (Execution Telemetry)
                    ├─ Surface 3: Modal Intercept Dialog (`ui.ask` Guard)
                    ├─ Surface 4: Verification Context & Toast (Lane Audit)
                    └─ Surface 5: Slash Command Dashboards (`/cache`, `/spend`, `/policy-guard`)
                          └─► Components:
                                ├─ CacheMeter (Segmented progress bar, TTL timer, hit badge)
                                ├─ ImageTray (Kitty aspect frame, fallback dimension badge)
                                ├─ SpendPacer (Daily burn pill, monthly trajectory warning)
                                ├─ PolicyPrompt (Severity banner, rule description, action pills)
                                ├─ LaneAuditCard (Commit count, diff stat badge, alarm flag)
                                └─ DashboardCard (Lip Gloss-style bordered card, key-value table)
                                      └─► Actions & States (Warm, Amber, Alert, Refused, Verified)
                                            └─► Outcome (Flawless execution, zero surprise bills, trusted agent outputs)
```

---

## 3. Terminal Viewport Budget & Scrolling Behavior

```
┌────────────────────────────────────────────────────────────────────────┐  Terminal Viewport
│ [Terminal Scrollback: conversation history, tool executions]           │  (Scrolls vertically)
│                                                                        │
│ ┌─ Command Output Card (Lip Gloss style border, /spend or /cache) ───┐ │
│ │ ╭────────────────────────────────────────────────────────────────╮ │ │
│ │ │ Spend Overview · Cure-Consulting-Group           14:30 UTC     │ │ │
│ │ ├────────────────────────────────────────────────────────────────┤ │ │
│ │ │ MTD Spend: $112.50 / $300.00 allowance (37.5%)                 │ │ │
│ │ │ Projected: $248.00  [████████████░░░░░░░░] Safe pace           │ │ │
│ │ ╰────────────────────────────────────────────────────────────────╯ │ │
│ └────────────────────────────────────────────────────────────────────┘ │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│ ABOVE-PROMPT SHELF (Fixed relative to prompt, max 4 rows total)        │  (Fixed / Pinned)
│ Row 1: Image Tray (if images pasted, 1-4 thumbs or dimension tags)    │
│ Row 2: Cache Telemetry: [cache ● 1h ████████████░░░░ 42m · hit 76%]     │
├────────────────────────────────────────────────────────────────────────┤
│ PROMPT INPUT BOX                                                       │  (Interactive)
│ > Refactor the authentication state machine to use MVI...              │
├────────────────────────────────────────────────────────────────────────┤
│ BELOW-PROMPT STATUS LINE                                               │  (Ambient Warning)
│ ⚠ Actions pace $384/mo exceeds $300 allowance (+$84 projected overage) │
├────────────────────────────────────────────────────────────────────────┤
│ SPINNER (During agent thinking & tool runs)                            │  (Transient)
│ ⠋ Running test suite... · Actions $12.40 today                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Scrolling & Budget Rules
1. **Vertical Budget Cap:**
   - The `AbovePrompt` surface MUST NOT consume more than 4 lines when both `cure-image-viewer` and `cure-cache-band` are active.
   - Images are capped at 10 rows in dedicated expanded mode, or a 3-row compact strip when terminal height is < 30 rows.
2. **Width Responsiveness:**
   - **Wide (>= 110 cols):** Full cache bar (16 chars), detailed hit stats, full file paths, multi-image horizontal grid (up to 4 across).
   - **Standard (80–109 cols):** Compact cache bar (8 chars), shortened stats (`hit 76%`), truncated paths (`.../auth/rules.ts`), 2 images across + overflow count.
   - **Narrow (< 80 cols):** Micro badge (`cache 42m · 76%`), single stacked image preview, no decorative borders.
3. **Zero Jitter / Zero Flicker:**
   - Spinner suffix maintains fixed-width formatting so terminal characters do not vibrate horizontally.
   - Cache band updates every 1s only when < 60s remain; otherwise updates once every 60s.

---

## 4. State Matrix for All Five Mods

| Mod / Surface | Default / Idle | Warning / Approaching Limit | Critical / Breach / Error | Empty / Offline / Fallback |
|---|---|---|---|---|
| **`cure-cache-band`** | **Warm (Green):** `● 1h ██████ 52m · hit 76%` | **Amber (<15m):** `● 5m ███░░░ 48s · hit 36%` | **Cold (Red):** `○ cold · +82k tokens to re-cache` | **Initial:** `○ cold · waiting for first turn` |
| **`cure-spend-band`** | **On Track:** Suffix: `· $6.40 today` (Spinner) | **Pacing High:** Warning line: `▲ Actions pace $340 exceeds $300` | **Hard Overage:** Suffix: `· $42.50 today [OVER]`, red alert line | **Offline:** Fallback to last cache `(last 11:45 UTC)` |
| **`cure-policy-guard`** | **Silent:** No UI intrusion during compliant writes | **Prompt:** Modal dialog with rule citation and diff path | **Denied:** Red context block: `Blocked by cure-policy-guard (rule)` | **Audit Table:** `/policy-guard` displays clean table or `No overrides` |
| **`cure-lane-verifier`** | **Verified:** Green badge attached to hand-back: `[3 commits · +142 -18]` | **Dirty Worktree:** Yellow badge: `[2 commits · 4 uncommitted files]` | **Alarm:** Toast: `EMPTY COMPLETION` + Red tag: `0 commits · 0 diff` | **Unresolvable:** Grey tag: `[branch 'x' unverified - not in git]` |
| **`cure-image-viewer`** | **Kitty Graphic:** Inline 10-row thumbnail with aspect preservation | **Multi-Image:** 2-4 thumbnails side-by-side with padding | **Corrupt/Missing:** Bounding box: `[Image #1 not found on disk]` | **No Kitty:** Crisp Unicode badge: `[🖼 Image #1 · 1200×800 PNG]` |


===== design/creative-direction.md =====
# Concept & Creative Direction: Cure Claude Code Mods Suite

## 1. Register Defense

**Register: Utility.**

The Cure Claude Code Mods Suite is professional infrastructure software executed within high-density developer terminals. Senior engineers and technical founders interact with this surface for several hours daily while executing complex coding tasks and autonomous agent workflows. Every pixel and terminal character must earn its place. The design prioritizes zero latency, peripheral glanceability, spatial economy, and unambiguous operational truth. 

We explicitly refuse generic AI aesthetic traps:
- No frivolous emojis as section headers.
- No glowing neon borders or simulated drop-shadow gradients.
- No card-within-card padding inflation that pushes prompt lines out of the terminal viewport.
- No unexamined defaults (e.g. pastel purple badges).

Instead, the design takes inspiration from the highest-caliber CLI and TUI tooling—**Charm.sh (Lip Gloss / Bubble Tea)**, **Starship**, and **Lazygit**. The visual tone communicates precision, restraint, and industrial-grade reliability.

---

## 2. Typography & Monospaced Glyph Grammar

The terminal canvas relies on monospaced character grids (typically JetBrains Mono, SF Mono, Berkeley Mono, or Fira Code). Hierarchy is established through character density, weight, capitalization, and a disciplined unicode glyph lexicon.

### Glyph Vocabulary
| Role | Character | Unicode | Usage |
|---|---|---|---|
| **Active / Warm** | `●` | U+25CF | Cache warm state; live API telemetry |
| **Inactive / Cold** | `○` | U+25CB | Lapsed cache; offline metric |
| **Warning / Pacing** | `▲` | U+25B2 | Approaching quota; TTL under 25% |
| **Verified / Pass** | `✓` | U+2713 | Lane git mutation verified |
| **Breach / Alarm** | `✗` | U+2717 | Blocked tool call; failed check |
| **Alert Flag** | `⚠` | U+26A0 | Policy violation intercept banner |
| **Progress Filled** | `█` | U+2588 | Meter completed fraction |
| **Progress Empty** | `░` | U+2591 | Meter remaining fraction |
| **Metadata Delimiter**| `·` | U+00B7 | Separator between inline metadata fields |
| **Box Framing** | `╭ ╮ ╯ ╰ │ ─` | Box Drawing | Lip Gloss rounded cards for dialogs & dashboards |

---

## 3. Color Architecture: 60-30-10 & Semantic Contrast

Color is never decorative; it is functional signaling. All pairs are tested against WCAG 2.2 AA (4.5:1 text, 3:1 graphical controls) with exact light and dark terminal mode parity.

### Palette Allocation
- **60% Base / Background:**
  - Dark: Deep charcoal (`#0D1117`) background with crisp off-white (`#E6EDF3`) foreground.
  - Light: Pure white (`#FFFFFF`) background with dark charcoal (`#1F2328`) foreground.
- **30% Structure / Framing:**
  - Muted secondary labels (`#8B949E` dark / `#656D76` light) and subtle structural borders (`#30363D` dark / `#D0D7DE` light).
- **10% Semantic Accents:**
  - **Success / Warm (Green):** `#3FB950` (Dark) / `#1A7F37` (Light) — Warm cache, under-budget spend, verified mutations.
  - **Warning / Pacing (Amber):** `#D29922` (Dark) / `#9A6700` (Light) — Approaching TTL lapse, pacing over monthly allowance, dirty worktree.
  - **Critical / Danger (Red):** `#F85149` (Dark) / `#CF222E` (Light) — Cold cache penalty, hard budget breach, policy refusal, `EMPTY COMPLETION` alarm.
  - **Action / Highlight (Blue):** `#58A6FF` (Dark) / `#0969DA` (Light) — Interactive command choices, keyboard accelerators `[1] / [2]`.

---

## 4. Interaction & Motion Rules

1. **Jitter-Free Telemetry:**
   - Text appended to the `Spinner` suffix (`· Actions $12.40 today`) maintains a static string width to prevent horizontal visual vibration as the spinner rotates.
2. **Dynamic Invalidation Cadence:**
   - **Cache countdown:** Refreshes once per minute when TTL > 60s; increases to 1 Hz (once per second) only during the final 60 seconds to conserve CPU and prevent redraw churn.
   - **Spend polling:** Polled via `gh api` every 15 minutes and immediately upon manual `/spend` invocation.
3. **Modal Dialog Interception Flow:**
   - Policy Guard pauses tool execution instantly upon detecting written house rule violations.
   - Default keyboard option is always **Refuse**, forcing deliberate affirmative action to allow an exception.
4. **Toast Persistence:**
   - Standard toasts dismiss after 3,000 ms.
   - Critical alarms (`EMPTY COMPLETION` on empty branch hand-backs) persist for 10,000 ms to guarantee human perception.


===== design/surface-specifications.md =====
# Surface & Component Specifications: Cure Claude Code Mods

## 1. AbovePrompt Compositor Architecture

`AbovePrompt` is the primary interactive display hook in Claude Code. Multiple mods consume this space. To prevent layout conflict and vertical viewport inflation, the mods adhere to the **Cure Unified Shelf Protocol**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ AbovePrompt Shelf (Max 4 lines total)                                                  │
│                                                                                        │
│ Line 1-2 (Optional Image Tray):                                                        │
│ ╭──────────────────────╮ ╭──────────────────────╮                                      │
│ │ 🖼 auth_diagram.png   │ │ 🖼 screen_state.png   │                                      │
│ │ 1200×800 (Kitty 18×8) │ │ 640×480 (Kitty 12×8)  │                                      │
│ ╰──────────────────────╯ ╰──────────────────────╯                                      │
│                                                                                        │
│ Line 3 (Telemetry Band):                                                               │
│ cache ● 1h ████████████░░░░ 42m left · hit 76% · misses 0                              │
└────────────────────────────────────────────────────────────────────────────────────────┘
  > [User prompt cursor sits immediately below the shelf]
```

### Layout Rules
1. **Vertical Constraint:**
   - When no images are drafted or sent, the shelf is exactly **1 line** tall.
   - When images are present, Kitty thumbnail heights are constrained to **8 terminal rows** max on tall viewports, and **4 rows** on viewports with < 35 rows total.
   - If more than 4 images are pasted, images 1–3 are shown and the 4th slot displays an overflow pill: `[+2 more images]`.
2. **Horizontal Responsiveness:**
   - **Wide (>= 110 cols):** Full 16-character progress bar, full label `42m left`, full hit/miss metrics (`hit 76% · misses 0`).
   - **Compact (80–109 cols):** 8-character progress bar, truncated label `42m · 76% hit`.
   - **Narrow (< 80 cols):** Text-only micro badge: `cache 42m (76%)`.

---

## 2. Component 1: Cache Band (`cure-cache-band`)

### State Specifications

#### State A: Warm Cache (Healthy)
```text
cache ● 1h ████████████░░░░ 42m left · hit 76% · misses 0
```
- Glyph: `●` (Emerald Green `#3FB950`)
- Bar: `████████████` (Green), `░░░░` (Dim grey `#8B949E`)
- Text: `cache` (Muted), `42m left` (Green), `hit 76% · misses 0` (Dim)

#### State B: Expiring Cache (Urgent Attention)
```text
cache ▲ 5m ███░░░░░░░░░░░░░ 48s left · hit 41% · misses 1
```
- Glyph: `▲` (Amber `#D29922`)
- Bar: `███` (Amber), `░░░░░░░░░░░░░` (Dim grey)
- Timer: `48s left` (Amber, counting down at 1 Hz)

#### State C: Cold Cache (Expired Penalty)
```text
cache ○ cold · next message re-caches 82,410 tokens (~$0.25 write fee)
```
- Glyph: `○` (Coral Red `#F85149`)
- Text: `cache ○ cold` (Red), token penalty (Dim grey with estimated financial write impact)

---

## 3. Component 2: Image Viewer (`cure-image-viewer`)

### Graphic & Fallback Specifications

#### Graphics Mode (Kitty Protocol supported: Ghostty, Kitty)
Renders native PNG bytes inline in the terminal via Kitty Graphics Protocol:
- Column allocation: `each = Math.floor((bodyColumns - (count - 1) * 2) / count)`.
- Row height: Clamped to `cellBox(w, h, each)` with max height 8 rows.
- Below each thumbnail: Subdued file caption `[Image #1 · 1200×800 PNG]`.

#### Terminal Fallback Mode (Apple Terminal, Warp, VSCode Integrated)
When the terminal does not support Kitty graphics escape sequences, render a structured Unicode border card:
```text
╭─ Image #1 ─────────────────────────╮ ╭─ Image #2 ─────────────────────────╮
│ 🖼  architecture_mvi.png            │ │ 🖼  state_flow.png                 │
│ 1440 × 900 px · 342 KB             │ │ 800 × 600 px · 118 KB              │
╰────────────────────────────────────╯ ╰────────────────────────────────────╯
```

---

## 4. Component 3: Spend Band (`cure-spend-band`)

### Spinner Integration & Warning Status

#### Ambient Spinner Suffix (During Turn Execution)
Appended to Claude Code's native `Spinner` component with fixed width:
```text
⠋ Thinking... · Actions $12.40 today
```
- If within monthly budget trajectory: Calm muted secondary text (`#8B949E`).
- If pacing into monthly overage: Amber indicator:
```text
⠋ Thinking... · Actions $28.50 today ▲
```

#### Below-Prompt Status Warning (When Pacing Exceeds Allowance)
Surfaced via `$.ui.status` directly underneath the prompt input box:
```text
▲ Actions pace $384/mo exceeds $300 allowance (+$84 projected overage · avg $18.40/day)
```

#### Slash Command Report: `/spend`
Formatted as a Lip Gloss-style bordered financial dashboard:
```text
╭──────────────────────────────────────────────────────────────────────╮
│  GITHUB ACTIONS BILLING SUMMARY · Cure-Consulting-Group              │
│  Freshness: 14:32 UTC (Active) · Monthly Allowance: $300.00          │
├──────────────────────────────────────────────────────────────────────┤
│  Today's Burn:       $  12.40    (Last 3-day avg: $14.10/day)        │
│  Month to Date:      $ 112.50    (37.5% of allowance)                │
│  Projected Total:    $ 248.00    [████████████░░░░░░░░]  SAFE PACE   │
├──────────────────────────────────────────────────────────────────────┤
│  Included Usage:     $ 187.50 remaining in plan                      │
│  Billed Runners:     macOS-14 (62%), ubuntu-latest (38%)             │
╰──────────────────────────────────────────────────────────────────────╯
```

---

## 5. Component 4: Policy Guard Dialog (`cure-policy-guard`)

### Interception Dialog Specification (`$.ui.ask`)

When Claude attempts a `Write`, `Edit`, or `MultiEdit` that violates a written house rule, the guard displays an executive interception prompt:

```text
╭─ HOUSE RULE INTERCEPT ───────────────────────────────────────────────╮
│                                                                      │
│  ⚠ VIOLATION: no-cron                                                │
│  File:   .github/workflows/deploy.yml (Line 14)                      │
│  Rule:   Org no-cron policy (2026-08-08)                             │
│  Reason: Scheduled cron triggers cause unmonitored runner spend.     │
│                                                                      │
│  Proposed change:                                                    │
│  + on:                                                               │
│  +   schedule:                                                       │
│  +     - cron: '0 * * * *'                                           │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  How would you like to proceed?                                      │
│                                                                      │
│  [1] Refuse the write (Recommended — fails closed)                   │
│  [2] Allow this once (Logged to security audit trail)                │
╰──────────────────────────────────────────────────────────────────────╯
```

- **Fails Closed:** Default selection index `1` (`Refuse the write`).
- **Audit Confirmation:** When `[2]` is selected, a subtle log message confirms:
  `cure-policy-guard: override recorded for no-cron on deploy.yml at 14:35:12 UTC`

#### Slash Command Report: `/policy-guard`
```text
╭─ HOUSE RULES & AUDIT TRAIL ──────────────────────────────────────────╮
│  Active Rules: no-cron · level5-vertex-only · minors-ai · secrets   │
├──────────────────────────────────────────────────────────────────────┤
│  Recent Overrides:                                                   │
│  2026-10-07 14:35  no-cron        statledger   .github/deploy.yml     │
│  2026-10-04 09:12  hardcoded-key statledger   scripts/seed.ts        │
╰──────────────────────────────────────────────────────────────────────╯
```

---

## 6. Component 5: Lane Verifier (`cure-lane-verifier`)

### Hand-Back Verification Card & Alarm

#### Verified Hand-back (Attached to Model Context)
```text
╭─ LANE VERIFICATION: lane/auth-mvi ───────────────────────────────────╮
│  Status:      ✓ VERIFIED                                             │
│  Commits:     3 commits ahead of origin/main                         │
│  Mutations:   +142 / -18 lines across 4 files                        │
│  Worktree:    Clean (0 uncommitted files)                            │
╰──────────────────────────────────────────────────────────────────────╯
```

#### Alarm Toast & Context Flag (`EMPTY COMPLETION`)
When an agent claims task completion but git reveals 0 commits and 0 diff:
```text
▲ TOAST ALERT:
cure-lane-verifier: a report claims completion but its branch is empty!
```
And model context receives:
```text
╭─ LANE ALARM: EMPTY COMPLETION ───────────────────────────────────────╮
│  Status:      ✗ UNVERIFIED / EMPTY DIFF                              │
│  Target:      lane/refactor-analytics                                │
│  Diff:        0 commits ahead · 0 files modified                     │
│  Action:      Reject handback; instruct lane to inspect working dir. │
╰──────────────────────────────────────────────────────────────────────╯
```


===== design/tokens.json =====
{
  "$schema": "https://design-tokens.github.io/community-group/format/",
  "$description": "Cure Claude Code Mods Design System Tokens (W3C DTCG Format) with light/dark terminal parity.",
  "primitive": {
    "color": {
      "neutral": {
        "white":  { "$value": "#FFFFFF", "$type": "color" },
        "gray-50": { "$value": "#F8FAFC", "$type": "color" },
        "gray-100":{ "$value": "#F1F5F9", "$type": "color" },
        "gray-200":{ "$value": "#E2E8F0", "$type": "color" },
        "gray-300":{ "$value": "#CBD5E1", "$type": "color" },
        "gray-500":{ "$value": "#64748B", "$type": "color" },
        "gray-700":{ "$value": "#334155", "$type": "color" },
        "gray-800":{ "$value": "#1E293B", "$type": "color" },
        "gray-900":{ "$value": "#0F172A", "$type": "color" },
        "black":  { "$value": "#020617", "$type": "color" }
      },
      "green": {
        "400": { "$value": "#4ADE80", "$type": "color" },
        "500": { "$value": "#22C55E", "$type": "color" },
        "700": { "$value": "#15803D", "$type": "color" },
        "800": { "$value": "#166534", "$type": "color" }
      },
      "amber": {
        "400": { "$value": "#FBBF24", "$type": "color" },
        "500": { "$value": "#F59E0B", "$type": "color" },
        "700": { "$value": "#B45309", "$type": "color" },
        "800": { "$value": "#92400E", "$type": "color" }
      },
      "red": {
        "400": { "$value": "#F87171", "$type": "color" },
        "500": { "$value": "#EF4444", "$type": "color" },
        "700": { "$value": "#B91C1C", "$type": "color" },
        "800": { "$value": "#991B1B", "$type": "color" }
      },
      "blue": {
        "400": { "$value": "#60A5FA", "$type": "color" },
        "500": { "$value": "#3B82F6", "$type": "color" },
        "700": { "$value": "#1D4ED8", "$type": "color" },
        "800": { "$value": "#1E40AF", "$type": "color" }
      }
    },
    "space": {
      "0":  { "$value": "0px", "$type": "dimension" },
      "1":  { "$value": "4px", "$type": "dimension" },
      "2":  { "$value": "8px", "$type": "dimension" },
      "3":  { "$value": "12px", "$type": "dimension" },
      "4":  { "$value": "16px", "$type": "dimension" },
      "6":  { "$value": "24px", "$type": "dimension" }
    },
    "radius": {
      "none": { "$value": "0px", "$type": "dimension" },
      "sm":   { "$value": "4px", "$type": "dimension" },
      "md":   { "$value": "8px", "$type": "dimension" }
    },
    "duration": {
      "fast": { "$value": "80ms",  "$type": "duration" },
      "base": { "$value": "200ms", "$type": "duration" },
      "slow": { "$value": "500ms", "$type": "duration" }
    }
  },
  "semantic": {
    "color": {
      "surface": {
        "primary": {
          "$value": "{primitive.color.neutral.black}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.neutral.white}",
              "dark": "{primitive.color.neutral.black}"
            }
          }
        },
        "secondary": {
          "$value": "{primitive.color.neutral.gray-900}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.neutral.gray-50}",
              "dark": "{primitive.color.neutral.gray-900}"
            }
          }
        },
        "inverse": {
          "$value": "{primitive.color.neutral.white}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.neutral.black}",
              "dark": "{primitive.color.neutral.white}"
            }
          }
        }
      },
      "text": {
        "primary": {
          "$value": "{primitive.color.neutral.white}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.neutral.black}",
              "dark": "{primitive.color.neutral.white}"
            }
          }
        },
        "secondary": {
          "$value": "{primitive.color.neutral.gray-300}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.neutral.gray-700}",
              "dark": "{primitive.color.neutral.gray-300}"
            }
          }
        },
        "inverse": {
          "$value": "{primitive.color.neutral.black}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.neutral.white}",
              "dark": "{primitive.color.neutral.black}"
            }
          }
        }
      },
      "status": {
        "success": {
          "$value": "{primitive.color.green.500}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.green.700}",
              "dark": "{primitive.color.green.400}"
            }
          }
        },
        "warning": {
          "$value": "{primitive.color.amber.500}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.amber.700}",
              "dark": "{primitive.color.amber.400}"
            }
          }
        },
        "danger": {
          "$value": "{primitive.color.red.500}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.red.700}",
              "dark": "{primitive.color.red.400}"
            }
          }
        },
        "info": {
          "$value": "{primitive.color.blue.500}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.blue.700}",
              "dark": "{primitive.color.blue.400}"
            }
          }
        }
      },
      "brand": {
        "primary": {
          "$value": "{primitive.color.blue.700}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.blue.700}",
              "dark": "{primitive.color.blue.400}"
            }
          }
        },
        "on-primary": {
          "$value": "{primitive.color.neutral.white}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.neutral.white}",
              "dark": "{primitive.color.neutral.black}"
            }
          }
        }
      },
      "border": {
        "default": {
          "$value": "{primitive.color.neutral.gray-700}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.neutral.gray-300}",
              "dark": "{primitive.color.neutral.gray-700}"
            }
          }
        },
        "focus": {
          "$value": "{primitive.color.blue.400}",
          "$type": "color",
          "$extensions": {
            "modes": {
              "light": "{primitive.color.blue.700}",
              "dark": "{primitive.color.blue.400}"
            }
          }
        }
      }
    },
    "spacing": {
      "xs": { "$value": "{primitive.space.1}", "$type": "dimension" },
      "sm": { "$value": "{primitive.space.2}", "$type": "dimension" },
      "md": { "$value": "{primitive.space.3}", "$type": "dimension" },
      "lg": { "$value": "{primitive.space.4}", "$type": "dimension" }
    },
    "radius": {
      "sm": { "$value": "{primitive.radius.sm}", "$type": "dimension" },
      "md": { "$value": "{primitive.radius.md}", "$type": "dimension" }
    },
    "motion": {
      "duration": {
        "fast": { "$value": "{primitive.duration.fast}", "$type": "duration" },
        "base": { "$value": "{primitive.duration.base}", "$type": "duration" },
        "slow": { "$value": "{primitive.duration.slow}", "$type": "duration" }
      }
    }
  },
  "component": {
    "meter": {
      "bar-filled": { "$value": "{semantic.color.status.success}", "$type": "color" },
      "bar-empty":  { "$value": "{semantic.color.border.default}",  "$type": "color" }
    },
    "badge": {
      "warning": { "$value": "{semantic.color.status.warning}", "$type": "color" },
      "danger":  { "$value": "{semantic.color.status.danger}",  "$type": "color" },
      "success": { "$value": "{semantic.color.status.success}", "$type": "color" }
    },
    "dialog": {
      "border": { "$value": "{semantic.color.border.default}",     "$type": "color" },
      "bg":     { "$value": "{semantic.color.surface.secondary}",  "$type": "color" }
    }
  }
}


Return under 400 words, in this exact structure:
KEEP      three strengths, one line each
DEFECTS   the five most important defects, ranked, each with the artefact and line or element it refers to
DISSENT   one change you would make that the other perspectives will probably dislike, and why
VERDICT   ship | fix-first | rethink, with one sentence
Do not restate the brief. Do not propose a redesign. Judge what is in front of you against the standard:
could this plausibly have shipped from a top-tier product design team or an award-winning studio?
