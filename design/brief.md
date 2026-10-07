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

