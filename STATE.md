# STATE — machine setup and current library state

Read this on any machine that has this repo checked out. `CLAUDE.md` points here.

## Every machine: install the library into Codex and Antigravity

Claude Code needs nothing: it installs from the `cure` marketplace and auto-updates.
Codex and Antigravity install **snapshots**, so they fall behind until refreshed.

**Run on a new machine, and again after every library release:**

```bash
git pull --ff-only origin main   # the script also pulls when on a clean main
scripts/install-runtimes.sh
```

What it does (idempotent, safe to re-run; `--help` for details):

1. Pulls `main` (skipped on another branch or a dirty tree).
2. **Codex:** adds or upgrades the `cure` marketplace, installs
   `cure-product-engineering@cure`, sets `skills.max_context_tokens = 10000` in
   `~/.codex/config.toml` (Codex caps explicit values at 10000; lower budgets truncate the
   103 skill descriptions and hurt routing).
3. **Antigravity:** builds the flat plugin and installs it to `~/.gemini/config/plugins/cure`
   (`scripts/export-antigravity.py --install`).
4. **Verifies** with zero model calls: packaging smokes plus a check of the *real* installs.
   A runtime whose CLI isn't installed is skipped, not failed.

Done when the output ends with `==> done` and shows both `real … install` lines.

Gemini CLI is not a target (it can't run models on consultant accounts —
`docs/evaluations/2026-09-23/platform-facts.md`).

## Current state (update on each release)

| | |
|---|---|
| Library version | 7.11.0 (2026-09-24) — Opus 5.5 guide alignment |
| Last wave | Wave 5 — tri-runtime (Opus 5.5 / Codex / Antigravity); see BACKLOG.md |
| Machines verified with `install-runtimes.sh` | primary Mac (codex 0.155.0, agy 1.2.9) — v7.11.0, 2026-09-24 |
| Open owner decisions | none (all Wave 5 items resolved 2026-09-23) |

## Next up (proposed, not started — 2026-09-24)

**Tri-lane live metrics** — design agreed in conversation, awaiting a go:

1. **Event stream (~½ day):** a `lane_events.emit()` helper appends one JSON line per lifecycle
   moment (task start, route declared, lane dispatched/finished with status + tokens, VERIFY,
   advisor verdict, task close) to `.git/tri-lane/events.jsonl`. Append-only, never blocks or
   fails a lane. Today metrics are written only at task end (`lane-log.py end`).
2. **Live local dashboard (~1 day):** `lane-live.py serve` — stdlib HTTP on localhost, tails every
   project's `events.jsonl` + `benchmark.jsonl`, refreshes quota pools via `usage-window.py`,
   pushes updates to the browser (SSE), reuses `benchmark-dashboard.py` charts; shows in-flight
   tasks, per-lane pass/partial/refused, tokens and quota by pool, advisor/rework/escaped defects,
   and the adopt/no-adopt decision rule live. One machine, no network.
3. **Optional, multi-machine:** the same events exported as OTLP logs plus Claude Code's native
   OTel metrics to a collector → Grafana. Codex's lane runs via `codex exec`, which emits no OTel
   metrics (openai/codex#12913), so tri-lane's own events stay the source of truth.

**Library path from 7/10 to 9/10** (BACKLOG Wave 5): graders that test Cure-specific conventions
(the only way to measure skill value over bare Opus 5.5); task-verb triggers for skills Opus 5.5
skips on task prompts (12/19 cases); T58 consolidation decided on that data plus a quarter of
real telemetry; Antigravity persona-scoping and glob-rule behaviour tests.
