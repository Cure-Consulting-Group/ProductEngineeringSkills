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

