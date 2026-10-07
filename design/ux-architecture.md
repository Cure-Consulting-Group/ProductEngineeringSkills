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

