# STATE — machine setup and current library state

Read this on any machine that has this repo checked out. `.claude/CLAUDE.md` points here.

## Every machine: install the library into Codex and Antigravity

Claude Code installs from the `cure` marketplace, but **auto-update is off by default for
third-party marketplaces**: turn it on per machine in `/plugin` → Marketplaces, or run
`claude plugin update cure-product-engineering@cure` after each release.
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
   106 skill descriptions and hurt routing).
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
| Library version | 7.14.0 — Wave 7, 2026-10-24; 106 skills, 41 agents, 4 personas, 11 rules, 0 output styles |
| Last wave | Wave 7 — truth in delivery (T71–T87 done, T88 deferred, T89–T92 new); first measured eval sweep: mean Δ +0.01, audit 9.81; see BACKLOG.md |
| Plugins in this repo | cure-product-engineering 7.14.0; cure-tri-lane 1.16.0; 9 mods (160 tests, gate `mods/check.py`); bootstrap 0.4.0 |
| Runtimes on the primary Mac (2026-10-24) | Claude Code 2.1.306 (2.1.310 available); codex 0.163.0 (0.164.0 available); agy 1.4.7 |
| Machines verified with `install-runtimes.sh` | primary Mac — v7.13.0, 2026-10-23 (codex 0.163.0, agy 1.4.5). Re-run after the Wave 7 PR merges: the real Antigravity install still carries the 7 empty-globs rules until then |
| Vetted-mods local patches | cc-pr-tracker 0.3.1-cure.1 (clear merged PRs; upstream PR prepared, not opened); secret-redactor 1.0.0-cure.1 (failed-Bash result shape). Originals in `../vetted-mods-backups/` |
| Open owner decisions | Upstream cc-pr-tracker PR (public action, needs rebase onto upstream 0.6.0); Level5 audio-retention flag (from Wave 6) |

## Runtime architecture audit — 2026-10-22

Saved 2026-10-23 at the user's request. **Conclusion: packaging is compatible with the
tested runtimes, but the library is not fully current or behaviorally validated across all
three platforms.** This was a read-only audit; the follow-up work below has not been implemented.
The older `install-runtimes.sh` verification row above is historical; the audit did not rerun
that installer or refresh real installations.

### Evidence from the audit

| Surface | Observed result |
|---|---|
| Codex CLI 0.163.0 | Cure 7.13.0 installed and enabled. Temporary-install smoke passed: 104 automatic skills listed, two manual-only skills hidden (`legal-doc-scaffold`, `proposal-generator`), no dropped skills or hidden-skill leaks. Claude hooks fenced off. |
| Claude Code 2.1.306 | Installed-plugin metadata reports Cure 7.13.0. Library structure checks passed; a full behavioral eval on this runtime was not run. |
| Antigravity CLI 1.4.5 | Temporary-workspace smoke passed: 106 skills and four personas listed, zero model turns. Real `agy plugin list --json` returned `[]`; no Cure plugin was installed in the normal CLI environment inspected. Temporary loading does not establish availability in normal sessions or other machines. |
| Structural checks | `audit-library.py`: 147 scored skills/agents, mean 9.99/10. Metadata sync and doc-path checks passed. These checks do not establish content currency or behavioral quality. |
| Verification dates | 73 skills record 2026-09-23, three record 2026-09-28, and 30 have no `metadata.verified` date. A missing date is an evidence gap, not proof the content is wrong. |
| Native Claude eval suite | 43 cases cover 35 of 106 skills; structural validation passes. Current behavior across all skills and runtimes remains unproven. |

### Follow-up work — resolved by Wave 7 (2026-10-24)

Items 1–5 shipped as T79, T83, T82, T82 and T85; item 6 was done 2026-10-23. Kept below as the record.

1. Update [engagement-automation](skills/platform/engagement-automation/SKILL.md): it says
   Antigravity has no session loop or cloud routine and routes scheduling to external
   schedulers. Current Antigravity supports conversation-scoped timers and recurring cron
   through `/schedule`; persistent work uses sidecars or Automations. Distinguish those
   lifetimes rather than treating the runtimes as interchangeable.
2. Reconcile platform guidance in `STATE.md`, `GEMINI.md`, `CLAUDE.md`, and authoring docs.
   This save corrects STATE's version/count; GEMINI still reports 6.0.3 and gives stale
   `allowed-tools` guidance. `allowed-tools` grants permission in Claude Code; it does not
   establish a read-only sandbox, and enforcement differs across runtimes.
3. Update the runtime validation strategy: `.github/workflows/validate.yml` pins Codex
   0.155.0; include checks against supported current versions and distinguish skipped checks
   from passes. The Antigravity listing smoke can skip when the CLI or authentication is absent.
4. Resolve maintenance liveness: `.github/workflows/nightly-drift.yml` has only
   `workflow_dispatch`, despite its name and comments describing scheduled checks. Decide
   whether to schedule it or document manual operation; saving this audit does not enable it.
5. Expand behavioral evals beyond the 35 covered skills. Measure triggering, output quality,
   and with/without-skill outcomes on supported runtimes; do not substitute structural scores
   or successful listing for those measurements.
6. ~~Refresh the real Antigravity install~~ — done 2026-10-23 via `install-runtimes.sh`
   (see the Machines row). Normal-session behavior is still unverified, and the glob-rule
   export bug noted there needs fixing in `scripts/export-antigravity.py`.

The existing shared skill source, focused descriptions, progressive disclosure, and
runtime-specific adapters broadly match current guidance. A targeted refresh is recommended;
this audit does not certify every skill's engineering, legal, tax, or other domain advice.

Official sources consulted 2026-10-22 (recheck before implementation):

- [OpenAI: skill authoring and invocation policy](https://learn.chatgpt.com/docs/build-skills)
- [OpenAI: current skill and prompt patterns](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Claude Code: skills and behavioral evaluation](https://code.claude.com/docs/en/skills)
- [Claude Code: plugin evals](https://code.claude.com/docs/en/plugin-evals)
- [Antigravity: skills](https://www.antigravity.google/docs/skills)
- [Antigravity: scheduling](https://www.antigravity.google/docs/commands/schedule/)

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
