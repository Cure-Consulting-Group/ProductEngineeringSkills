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

