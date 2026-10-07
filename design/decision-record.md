# Architectural Decision Record: Cure Claude Code Mods Suite

## ADR-001: Unified AbovePrompt Vertical Budget Cap (Max 4 Rows)
- **Status:** Accepted
- **Context:** `cure-cache-band`, `cure-image-viewer`, and future `cure-rules-band` all inject UI into Claude Code's `AbovePrompt` hook. Unchecked, stacked components could consume 10–15 rows of vertical terminal height, pushing prompt input off-screen on laptops and split-screen setups (24–35 row viewports).
- **Decision:** Enforce a hard ceiling of 4 terminal rows for all combined `AbovePrompt` components.
  - Image thumbnails are constrained to 8 rows max in tall viewports, and 3–4 rows in compact viewports.
  - Cache telemetry is constrained to exactly 1 row.
  - If additional bands are mounted (e.g. repo rules banner), they must condense into the single telemetry row using delimiter bullets (`·`) rather than creating a new vertical line.
- **Consequences:** Eliminates prompt jumping and viewport overflow; preserves developer focus.

---

## ADR-002: Monospaced Glyph & Unicode System over Rich Graphics/Emojis
- **Status:** Accepted
- **Context:** Earlier mockups risked looking like generic AI dashboards with colored emojis, rounded card containers, and neon gradients that fail in standard POSIX terminals.
- **Decision:** Standardize on disciplined Unicode blocks (`█`, `░`, `▌`), standard status bullets (`●`, `○`, `▲`, `✓`, `✗`), and Charm Lip Gloss-style box-drawing borders (`╭───╮`). Emojis are strictly banned as structural elements.
- **Consequences:** Renders reliably across 100% of terminal emulators (macOS Terminal, iTerm2, Ghostty, Kitty, Alacritty, VSCode terminal, Linux console); zero visual degradation over SSH.

---

## ADR-003: Policy Guard Fail-Closed Interception Flow
- **Status:** Accepted
- **Context:** `cure-policy-guard` intercepts file write tool calls that violate written house rules. A developer might dismiss the prompt quickly or run Claude Code headlessly (`-p`).
- **Decision:** Interception defaults to **Refuse the write** (Option 1). In headless sessions or when `$.ui.ask` times out or is dismissed, the write fails closed immediately. Overrides require deliberate selection of Option 2 and are written to the persistent audit log.
- **Consequences:** Guarantees organizational compliance and prevents inadvertent automated security or billing violations.

---

## ADR-004: Three-Tier W3C DTCG Token Hierarchy with 100% Light/Dark Parity
- **Status:** Accepted
- **Context:** Terminal users switch between dark themes (Dracula, Tokyo Night, GitHub Dark) and light themes (GitHub Light, Solarized Light). Hardcoded ANSI codes produce unreadable low-contrast text.
- **Decision:** Implement tokens under the W3C DTCG schema across 3 strict tiers (`primitive` -> `semantic` -> `component`). Every semantic color token defines light and dark modes in `$extensions.modes`. Contrast ratios verified with `contrast_check.py` to meet WCAG 2.2 AA (minimum 4.5:1 text, 3:1 graphical borders).
- **Consequences:** 24/24 color pairs pass WCAG 2.2 AA; seamless readability across all terminal themes.

---

## ADR-005: Ground-Truth Git Mutation Verification for Agent Hand-backs
- **Status:** Accepted
- **Context:** Autonomous subagents frequently report "Task complete; 42 tests passing" when their target git worktree or branch contains zero commits and an empty diff (`EMPTY COMPLETION`).
- **Decision:** `cure-lane-verifier` intercepts agent reports, executes read-only git queries (`rev-list`, `diff --shortstat`, `status`), and appends a structured verification card to model context. If diff is 0, a 10-second alert toast is triggered to the human operator.
- **Consequences:** Eliminates phantom completions; enforces verification by mutation.

