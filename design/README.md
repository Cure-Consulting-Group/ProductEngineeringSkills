# Cure Claude Code Mods — Design Studio Package

Complete UX architecture, Terminal UI (TUI) design system, W3C DTCG tokens, wireframes, and high-fidelity specifications for the five Cure Claude Code mods:
1. `cure-policy-guard`
2. `cure-lane-verifier`
3. `cure-spend-band`
4. `cure-cache-band`
5. `cure-image-viewer`

Authored using the Cure **Design Studio** skill (`skills/product/design-studio/SKILL.md`).

---

## Deliverable Directory Structure

```
design/
├── README.md                      # Master index, implementation roadmap, fallbacks & limitations
├── brief.md                       # Step 1 Classification & Step 2 Context brief
├── ux-architecture.md             # The Ten Questions, model chain, terminal viewport budget, state matrices
├── creative-direction.md          # Utility register defense, monospaced glyph grammar, 60-30-10 palette
├── surface-specifications.md      # AbovePrompt compositor protocol & detailed specs for all 5 mods
├── decision-record.md             # Architectural Decision Records (ADR-001 through ADR-005)
├── tokens.json                    # W3C DTCG 3-tier tokens (0 errors, 24/24 WCAG AA contrast pairs)
├── spec.json                      # Machine-readable wireframe & flow specification
├── critique-gate.md               # 10-row quality bar evaluation (10/10 PASS)
├── screens.html                   # Interactive high-fidelity terminal UI simulator (Dark/Light toggle)
├── wireframes/                    # Low/mid fidelity SVG wireframes & flow diagrams
│   ├── flow.svg                   # Navigation and transition flow diagram
│   ├── inventory.md               # Screen & region inventory
│   └── screens/
│       ├── ambient-shelf.svg      # AbovePrompt composite shelf
│       ├── policy-guard-modal.svg # Write intercept modal dialog
│       ├── lane-verifier-card.svg # Hand-back verification card
│       └── spend-dashboard.svg    # /spend scrollback telemetry card
└── review/                        # Three-perspective review panel
    ├── prompts/                   # Emitted prompts (Creative Director, UX, Systems)
    ├── results/                   # Panel findings from each perspective
    └── synthesis.md               # Synthesized decisions & final ship verdict
```

---

## Summary of the Design System

### 1. The AbovePrompt Unified Shelf Protocol
- **Vertical Budget:** Strictly capped at **4 rows** maximum across all active mods.
- **Single-row Telemetry:** When no images are drafted, `cure-cache-band` renders a 1-row micro-dense meter.
- **Image Tray:** `cure-image-viewer` renders inline thumbnails (Kitty protocol) or Unicode bounding cards clamped to 8 rows max (3–4 rows on small viewports).
- **Responsive Width:**
  - **Wide (>= 110 cols):** Full 16-char progress meter, full duration, complete hit/miss stats.
  - **Standard (80–109 cols):** 8-char progress meter, shortened stats (`42m · 76% hit`), middle-truncated paths.
  - **Narrow (< 80 cols):** Text-only micro badge (`cache 42m (76%)`), 1 image preview + overflow indicator.

### 2. Design Tokens & Parity
- **Schema:** Strict W3C Design Tokens Community Group (DTCG) specification with three tiers: `primitive` ➔ `semantic` ➔ `component`.
- **Validation:**
  - `tokens_lint.py`: **68 tokens, 0 errors, 0 warnings**.
  - `contrast_check.py`: **24/24 color pairs pass WCAG 2.2 AA** (>= 4.5:1 text, >= 3:1 graphical elements).
- **Light/Dark Parity:** Automatic mode switching via `$extensions.modes.light` and `$extensions.modes.dark`.

---

## Implementation Notes & Engineering Fallbacks

| Feature / Component | Ideal Implementation | High-Cost Risk | Cheaper Fallback (Designed & Supported) |
|---|---|---|---|
| **Pasted Images** | Inline Kitty Graphics Protocol (Ghostty / Kitty) | Terminals without protocol support fail to render image bytes | Renders a structured Unicode box `[🖼 Image #1 · 1200×800 PNG]` with file size and dimension tags. |
| **Spend Telemetry** | Polling `gh api` every 15 minutes | Token expiration, API rate limits, or offline airplane mode | Displays last cached telemetry with timestamp `(offline · last 14:32 UTC)`; never throws or blocks prompt. |
| **Cache Countdown** | 1 Hz timer tick during the final 60 seconds | Terminal redraw churn / CPU wakeups during long idle pauses | Throttles to once per minute until TTL < 60s; halts timer entirely if session is inactive. |
| **Policy Guard** | Interactive `$.ui.ask` modal selection dialog | Non-interactive runs (`-p`), headless subagents, or dismissed dialog | Fails closed automatically; outputs refusal reason and house rule citation to model context. |
| **Lane Verification** | Deep `git diff` calculation across multiple worktrees | Massive repositories with slow filesystem I/O | Limits git calls to `rev-list --count` and `diff --shortstat` with a strict 10s timeout. |

---

## Limitations

1. **Terminal Protocol Fragmentations:** While Ghostty and Kitty support the Kitty graphics protocol, macOS Terminal, Warp, and Windows Terminal do not. The fallback Unicode bounding boxes provide metadata clarity but cannot display raw raster pixels.
2. **Bash-Level Write Bypasses:** The policy guard inspects Claude Code's native file editing tools (`Write`, `Edit`, `MultiEdit`). Writes executed via raw Bash commands (`cat > file.yml`) cannot be intercepted by the mod hook and rely on CI/CD scanners.
3. **Cache TTL Inference:** The Anthropic API does not return remaining cache TTL per message response. TTL is inferred based on subscription plan defaults (1h subscription vs 5m API key) or manual `CURE_CACHE_TTL` override.

---

## How to Verify Design Assets

```bash
# 1. Lint design tokens for schema and mode parity
python3 skills/product/design-studio/scripts/tokens_lint.py --tokens design/tokens.json --modes light,dark

# 2. Run WCAG 2.2 AA contrast checks
python3 skills/product/design-studio/scripts/contrast_check.py --tokens design/tokens.json

# 3. View low/mid fidelity wireframes
open design/wireframes/screens/ambient-shelf.svg
open design/wireframes/flow.svg

# 4. Open high-fidelity interactive terminal simulator in browser
open design/screens.html
```
