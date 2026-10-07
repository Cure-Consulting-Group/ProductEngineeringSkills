# Cure Claude Code Mods Suite — screen inventory (web, mid-fi)

| Screen | Purpose | Nav | Primary action | Fixed | Sticky | Scrolls | Below fold |
|---|---|---|---|---|---|---|---|
| Ambient Terminal Shelf | Glanceable telemetry above prompt (Cache TTL, Spend Pacer, Pasted Images) without vertical waste | tabs | Submit prompt | Claude Code Terminal (80-140 cols); Spinner / Status: ⠋ Compiling project... · Actions $12.40 today (Safe pace) | AbovePrompt Shelf: [🖼 Image #1 · 800x600] / [cache ● 1h ████████████░░░░ 42m · hit 76%] | Scrollback: Previous turn output and code diffs; Prompt Input: > Refactor auth store to MVI pattern... | 0 px |
| Policy Guard Intercept Dialog | Block non-compliant file writes and prompt user for binary exception decision | none | Refuse the write | Terminal: Write Tool Intercepted; [1] Refuse the write (Default)   /   [2] Allow this once (Logged to audit) | — | ⚠ House Rule Violation: [no-cron] Schedule trigger in .github/workflows/deploy.yml; Source: Org no-cron policy (2026-08-08). Scheduled cron triggers cause uncontrolled runner spend.; Proposed Diff: + schedule: [{cron: '0 * * * *'}] (Line 14) | 0 px |
| Lane Verifier Hand-back Card | Verify subagent completion claims against ground-truth git mutations | none | Accept or re-prompt lane | Agent Hand-back: lane/auth-mvi; Status: [VERIFIED ✓] Branch matches reported hand-back claims | — | Report: 'Implemented MVI pattern with 42 unit tests passing'; Git Ground Truth: 3 commits ahead · +142 -18 lines across 4 files · Clean worktree | 0 px |
| Spend & Cache Dashboard (/spend & /cache) | Executive tabular telemetry printed cleanly into scrollback on slash command | tabs | Review cost pace | /spend · GitHub Actions Financial Telemetry | — | Organization: Cure-Consulting-Group / Freshness: 14:32 UTC (Active); Metrics: Today ($12.40) / MTD ($112.50 / $300.00 allowance - 37.5%) / Projected ($248.00); Pace Meter: [████████████░░░░░░░░] Projected $248 vs $300 ceiling (Within allowance); Historical: Last 3 days burn avg: $9.80/day / Run count: 184 runs | 0 px |

## Notes and states

- **Ambient Terminal Shelf**: Warm state: Cache indicator is calm green; 1h TTL; spend within $300 budget
- **Ambient Terminal Shelf**: Expiring state: Amber indicator when < 15m; countdown ticks by seconds in final minute
- **Ambient Terminal Shelf**: Image paste: Displays Kitty graphics thumbnail or Unicode bounding box
- **Policy Guard Intercept Dialog**: Default action is Refuse to prevent accidental automated allowance
- **Policy Guard Intercept Dialog**: Headless / non-interactive sessions fail closed automatically
- **Policy Guard Intercept Dialog**: Allowed overrides recorded to persistent audit store with timestamp
- **Lane Verifier Hand-back Card**: Alarm state: If diff is 0 lines / 0 commits, triggers loud toast 'EMPTY COMPLETION'
- **Lane Verifier Hand-back Card**: Dirty state: Flags uncommitted files in target worktree
- **Lane Verifier Hand-back Card**: Rides as model context to keep orchestrator informed
- **Spend & Cache Dashboard (/spend & /cache)**: Structured Lip Gloss-style rounded box borders
- **Spend & Cache Dashboard (/spend & /cache)**: Graceful offline indicator if gh api rate limits or network fails
- **Spend & Cache Dashboard (/spend & /cache)**: High-contrast color coding for projected overages
