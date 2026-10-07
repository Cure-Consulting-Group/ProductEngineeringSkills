# Design Review Panel Synthesis: Cure Claude Code Mods

Synthesis conducted by Lead Product & Design Architect.

---

## 1. Finding Evaluations & Labeling

| # | Perspective | Finding | Label | Action / Resolution |
|---|---|---|---|---|
| 1 | Creative Director | Distinguish visually between telemetry cards (`/spend`) and security intercepts (`policy-guard`) | **Confirmed** | Add distinct red-tinted double border `╔═══╗` or high-contrast header banner for policy intercepts. |
| 2 | Creative Director | ASCII image fallback lacks bounding context | **Confirmed** | Add dimensional aspect ratio box `[🖼 Image #1 · 1200×800 PNG]` with dashed Unicode framing. |
| 3 | Creative Director | Add `cure ›` brand prefix to telemetry shelf | **Disputed** | Disputed based on utility register and 80-column viewport budget. Every character above prompt must carry telemetry; brand branding adds clutter. |
| 4 | Product / UX | Middle-path truncation on narrow breakpoints (<100 cols) | **Confirmed** | Incorporated: paths longer than 36 chars middle-truncate (`mods/.../register.ts`) on viewports < 100 cols. |
| 5 | Product / UX | Multi-image grid cramming below 100 columns | **Confirmed** | Incorporated: clamp to max 2 images across + overflow tag `[+N more]` when terminal width < 100 cols. |
| 6 | Product / UX | Toast alone is insufficient for empty completion alarms | **Confirmed** | Incorporated: lane verifier injects persistent `[LANE ALARM: EMPTY COMPLETION]` header into prompt context stream. |
| 7 | Systems / Prod | Fixed-length string formatting for spinner suffix | **Confirmed** | Incorporated: spinner string padded to static width (`Actions $12.40 today`) to eliminate horizontal character wobble. |
| 8 | Systems / Prod | Extreme aspect ratio clamping in image viewer | **Confirmed** | Incorporated: clamp thumbnail heights to [3, 8] rows and widths to [12, 40] cols. |
| 9 | Systems / Prod | Drop 15-minute polling timer for lazy fetching | **Disputed** | Disputed based on user goal: developers need ambient awareness of active CI runaway spend before typing their next prompt, not after manual command invocation. Keep 15m cadence. |

---

## 2. Conflicts & Decisions

### Conflict 1: Brand Prefix vs Character Budget
- **Debate:** Creative Director requested a `cure ›` prefix on all ambient lines. Product/UX Director strongly opposed due to 80-column horizontal constraints.
- **Resolution:** Decided in favor of the **Utility Register** and horizontal budget. No brand prefix on ambient rows; the brand is communicated through structural excellence and cohesive design tokens.

### Conflict 2: Background Polling Cadence vs Battery/Idle Efficiency
- **Debate:** Systems Director argued for removing the 15-minute background spend timer. Product/UX argued that ambient overage warnings prevent $200+ surprise bills.
- **Resolution:** Retain the 15-minute background polling timer, but pause execution if terminal window has been idle for > 2 hours without a user prompt.

---

## 3. Unified Design Direction

The Cure Claude Code Mods Suite design direction is:
1. **The AbovePrompt Unified Shelf:** Strictly capped at 4 vertical rows. Coexists gracefully with image drafts and cache countdowns.
2. **Precision Monospaced Hierarchy:** Glyphs (`●`, `○`, `▲`, `✓`, `✗`, `█`, `░`) and Charm Lip Gloss-style box borders.
3. **Responsive Breakpoints:** Explicit transformations for Wide (>= 110), Standard (80–109), and Narrow (< 80) viewports, including middle-path truncation.
4. **Three-Tier W3C DTCG Tokens:** 100% light/dark mode parity with 24/24 WCAG 2.2 AA verified contrast pairs.
5. **Fail-Closed & Truth-First Guardrails:** Policy Guard intercepts defaults to Refusal; Lane Verifier checks ground-truth git mutations.

---

## 4. Final Panel Verdict

- Creative Director: **SHIP**
- Product / UX Director: **SHIP (Defects addressed)**
- Design Systems Director: **SHIP**

**Overall Panel Determination: CONSENSUS TO SHIP**

