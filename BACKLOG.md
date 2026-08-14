# BACKLOG

Internal improvement backlog, organized in waves. Wave 1 (2026-04-29, resolved) came from a comparative evaluation against `alirezarezvani/claude-skills`. Wave 2 (2026-07-11, resolved) aligned the library with Claude Code's continuous-execution layer (loops, routines, workflows, hooks). Wave 2.5 (2026-07-13, open) makes the library consumable from Gemini CLI and Antigravity via the Agent Skills open standard — motivated by real engagements falling back to Gemini when Claude credits run out. Wave 3 (2026-08-13, open) is the quarterly re-evaluation (originally due October 2026, pulled forward): evidence over conformance — eval harness, fleet drift control, parallel-agent operating model, and Codex as a third runtime.

This repo is **internal-only** — not for public distribution, no marketplace. Tickets reflect that constraint.

---

# Wave 3 (2026-08-13) — Evidence, Fleet Health, and Parallel Operations

**Execution status (2026-08-14, branch `feat/wave-3`):** T34, T30, T31, T35, T36, T32 built and committed. Deviations:

| Ticket | Status | Deviation |
|---|---|---|
| T34 | ✅ Done | Root cause refined: the gather bullets never existed pre-T20 (header inserted with nothing under it) — authored them rather than restored |
| T30 | ✅ Done | 15 tasks/13 skills; live-verified (t01 real claude run PASS, 23.4s). CI runs harness self-test only (no authenticated CLI on runners); real Ring-0 runs locally via release.sh vs last tag. Rubric judge deferred until deterministic gates prove insufficient |
| T31 | ✅ Done | Census found 10 vendored projects (not 6), 79/79 files drifted in each. Manifests written across 17 projects. Vendored-tree removal blocked by permission classifier (correctly — high blast radius): packaged as `scripts/migrate-to-plugin.sh` for human execution, statledger first |
| T35 | ✅ Done | Hook verified fail-open with malformed input. First SCORECARD.md honest: effectiveness "no data", fleet 10 drifted |
| T36 | ✅ Done | 14 prose-only flags triaged: 1 enforced (env-secrets-manager — was allowed-tools-as-sandbox), 6 labeled advisory (per-mode restriction inexpressible), 7 false positives cleared. Register: docs/GUARDRAILS.md |
| T32 | ✅ Done | Skill ships at 105 lines / 338-char trigger |
| T33 | ⏳ Deferred | Depends on T25 (Wave 2.5 exporter) — unbuilt. Runs with Wave 2.5 |

Captured 2026-08-13 from two evaluations: (a) a self-assessment of the library against Anthropic's published Agent Skills / context-engineering guidance, and (b) a census of six consuming projects (Level5, initiated-recruiting, statledger, Finality, DistrictZero, NationalLacrosseTourApp). Theme: **the library measures conformance, not effectiveness, and the fleet has drifted.** Every quality signal today is a proxy (frontmatter validity, char budgets, line counts); nothing measures whether a skill improves output, and the consuming projects prove the gap.

## Verified fleet facts (censused 2026-08-13; do not re-research)

- **Vendored copies, not plugin installs.** 5 of 6 censused projects carry a full vendored copy of the library in `.claude/` (80 skills + 39 agents each). Their CLAUDE.md files *also* instruct installing the plugin from the marketplace — a double-load / double-listing risk if anyone follows both paths.
- **No manifest anywhere.** Zero projects have a `cure-manifest.json` or any version pin, despite `cure-infra-bootstrap` describing itself as "manifest-driven, version-pinned." Drift is currently unmeasurable by construction.
- **Drift is real.** Sampled `sdlc/SKILL.md` in Level5, statledger, and Finality: all three differ from the library copy (~20 diff lines each). Vendored trees are stale at unknown versions.
- **Local innovation is stranded.** statledger grew 7 project-local skills (`app-review-3-1-1`, `ci-workflow-guard`, `claude-bootstrap`, `ledger-invariants`, `prod-deploy-hooptrace`, `seed-and-sim`, `story-adr-discipline`). None have been reviewed for upstreaming; some (`story-adr-discipline`, `ci-workflow-guard`) look generalizable.
- **One project consumes nothing.** NationalLacrosseTourApp has only `loop.md` + workflows — no skills, no agents, no CLAUDE.md wiring to the library.
- **Multi-runtime is aspirational, not real.** initiated-recruiting's `.agents/skills/` is **empty**; its `AGENTS.md` is project auth notes, not a skill surface. Codex (which reads `AGENTS.md`) is now a stated runtime target but appears nowhere in Wave 2.5. Antigravity remains covered by T25–T29.
- **Prose corruption invisible to the audit.** `skills/engineering/sdlc` and `skills/engineering/finops` have truncated Pre-Processing blocks ("Additionally gather (domain-specific):" followed by unrelated prose — the T20 injection migration clobbered the bullet lists). They score 9.9 and 10.0 in `audit-library.py`. `EVALUATION.md` (referenced from README.md and GEMINI.md) still claims "24 commands, no hooks exist" — false since March 2026.

## Release plan

| Release | Bump | Tickets | Theme |
|---------|------|---------|-------|
| v7.5.1 | patch | T34 | Fix corrupted skills, retire stale docs, prose-drift lint |
| v7.6.0 | minor | T30, T31, T35, T36 | Eval harness, fleet manifest + drift CI + canary channel, usage telemetry + scorecard, guardrail enforcement |
| v7.7.0 | minor | T32, T33 | Parallel-agent orchestration skill, Codex runtime + selection guide |

Dependencies: T33's selection guide consumes T30's benchmark data; T33's Codex export builds on T25's exporter (Wave 2.5 ships first). T34 has no dependencies — ship immediately. Total estimate: **9–12 dev-days** across three releases.

**Definition of done for the wave (the "sound" bar):** every skill either has measured effectiveness (T30) or a dated deprecation candidate flag (T35); every consuming project on a manifested, current version (T31); every safety-relevant guardrail enforced by the harness or explicitly labeled advisory (T36); no prose anywhere load-bearing without a lint (T34). Conformance score stays; it stops being the headline number.

---

## T30 — Eval harness: golden task suite for skills AND models

**Status:** Open
**Release:** v7.6.0 (minor)

**Scope:**
1. New `evals/` tree: `evals/tasks/{task-id}/` with `task.md` (prompt + fixture repo ref), `expected.md` (acceptance oracle), `score.sh` (deterministic gates: build/test/grep checks, exit 0/1).
2. Seed 15–25 golden tasks drawn from **closed BACKLOG tickets and real consuming-project commits** (Level5, statledger, initiated-recruiting have the richest history) — not synthetic puzzles. Each task must exercise at least one library skill.
3. `scripts/run-evals.sh`: runs each task N times (default 3) via headless CLI (`claude -p`; `codex exec` and Gemini CLI as optional backends) in throwaway worktrees; collects pass/fail, diff hygiene (lines changed vs. necessary, unrequested-edit count), wall-clock, and token cost where reported.
4. LLM-judge rubric scoring for non-deterministic dimensions — **judge model must be a different family than the candidate** (self-preference bias).
5. Two run modes from the same suite: `--mode skill` (skill on vs. skill off, same model — measures whether the skill earns its context) and `--mode model` (same task, different backend — the model benchmark).
6. Results land in `evals/results/{date}.json` + a generated `evals/RESULTS.md` scoreboard, committed. Quarterly re-run is added to `docs/MAINTENANCE.md` cadence.
7. API-key note: subscription seats don't grant benchmark API quota; the harness drives the CLIs we already pay for. Document a small pay-as-you-go budget as the upgrade path for controlled temperature/seeds.
8. **Incremental mode (Ring 0):** `run-evals.sh --changed <ref>` maps a diff to affected skills (via the golden-task → skill index) and runs only their tasks, 1 rep. Wire into `validate.yml` as a PR gate: on/off delta may not regress vs. the last committed results. Quarterly sweep stays the full-suite mode.
9. **Audit calibration:** eval outcomes feed back into `audit-library.py` — a skill whose measured on/off delta is ≤0 cannot score above 8.0 regardless of conformance. Kills the saturated-metric problem: the 9.99 headline is retired in favor of the eval-weighted score once ≥half the library has coverage.

**Why:** The library's 9.99/10 audit score measures spec conformance; two silently corrupted skills scoring 9.9/10.0 prove it cannot see quality. Skill-on/skill-off deltas are the only honest answer to "are the skills working," and the same harness answers "which runtime should we use" (T33) for free.

**Blast radius:** Low-medium — additive `evals/` tree; no skill-body changes. Eval runs cost real tokens: cap at N=3 runs × ~25 tasks per quarterly sweep and run mechanical tasks on cheaper models.

**Acceptance:**
- [ ] ≥15 golden tasks, each traceable to a real ticket/commit, each exercising ≥1 skill
- [ ] `run-evals.sh --mode skill` produces per-skill on/off deltas; `--mode model` produces a per-backend matrix
- [ ] Judge model family ≠ candidate family, enforced in the script
- [ ] `evals/RESULTS.md` scoreboard generated; MAINTENANCE.md gains the quarterly sweep
- [ ] A deliberately broken skill (e.g. pre-fix `sdlc`) shows a measurable delta vs. its fixed version — harness sanity check
- [ ] `--changed` mode runs in validate.yml on a PR touching a covered skill, and blocks on regression
- [ ] Calibration rule live in audit-library.py once coverage ≥50%; documented in the audit header
- [ ] `audit-library.py` green

**Effort:** 2.5–3 days (largest single ticket; task curation is most of it).

---

## T31 — Fleet manifest + drift CI for consuming projects

**Status:** Open
**Release:** v7.6.0 (minor)

**Scope:**
1. Make `cure-infra-bootstrap`'s "manifest-driven, version-pinned" claim true: define `.claude/cure-manifest.json` (library version, install mode `plugin|vendored|hybrid`, **channel `stable|next`**, install date, local-skill allowlist) and have bootstrap write it.
2. `scripts/fleet-census.py` (stdlib, `--help`/`--json`): given a directory of project checkouts, reports per-project install mode, manifest version vs. library HEAD, vendored-file drift (hash compare), local skills not in the library, and double-install risk (vendored copy + plugin instructions in CLAUDE.md).
3. Remediation pass over the six censused projects: pick **one** install mode per project (recommend: plugin install + manifest; delete vendored trees), migrate, write manifests. NationalLacrosseTourApp gets a standard bootstrap.
4. Upstream-harvest review of statledger's 7 local skills: generalize what belongs in the library (candidates: `story-adr-discipline`, `ci-workflow-guard`), record keep-local verdicts in that project's manifest allowlist.
5. Wire `fleet-census.py` into `nightly-drift.yml` (or a weekly sibling) for repos the runner can reach; drift opens/refreshes the tracking issue.
6. **Canary ring:** statledger (most active, most divergent) runs `channel: next`. New releases sit on `next` ≥5 working days before promotion to `stable`; promotion is a manual call informed by T35 telemetry + any T30 regression from real use. Rollback = flip the manifest pin; census confirms. Release flow documented in docs/MAINTENANCE.md: merge → release.sh → next → soak → promote → fleet converges.

**Why:** Five projects run stale, unversioned forks of the library while their docs point at the plugin. Every library improvement since their vendor date silently never reached them — the compounding value of the library is being thrown away at the last mile.

**Blast radius:** Medium-high — touches six repos outside this one; deleting vendored trees changes what those sessions load. Migrate one project first (statledger, the most divergent), verify, then roll out.

**Acceptance:**
- [ ] Manifest schema documented in docs/CONSUMING-PROJECTS.md; bootstrap writes it
- [ ] `fleet-census.py` correctly reports all six projects' current (pre-fix) state
- [ ] All six projects on a single declared install mode with manifests; zero double-install
- [ ] statledger local skills dispositioned: upstreamed or allowlisted, none silently forked
- [ ] Drift check scheduled; drift produces an issue, not silence
- [ ] statledger on `channel: next`; one release soaked and promoted through the ring end-to-end; rollback drill executed once

**Effort:** 2–2.5 days.

---

## T32 — `parallel-agent-orchestration` skill: the multi-instance operating model

**Status:** Open
**Release:** v7.7.0 (minor)

**Scope:**
1. New skill `skills/engineering/parallel-agent-orchestration/SKILL.md`: how Cure runs N simultaneous Claude Code instances on one project. Covers: worktree-per-ticket (one ticket = one worktree = one branch = one session), decomposition along module boundaries (not ticket numbers) to keep merge conflicts sub-quadratic, shared rate-limit budgeting (parallelism buys wall-clock, not capacity — N sessions share one account budget), model/effort tiering (mechanical branches on cheap models, judgment work serial on Opus), and mutual exclusion on destructive ops (migrations, deploys, releases are single-owner; a lockfile convention).
2. Blast-radius → autonomy mapping as a table: low = unattended, medium = attended diff review, high = never parallel, never unattended (extends AUTOMATION.md rule 1 to interactive work).
3. Cross-references `git-worktree-manager` (mechanics) rather than duplicating it; this skill owns the *operating model*.
4. Routing hygiene: `when_to_use` gets NOT-clauses vs. `git-worktree-manager` (single-operator worktree mechanics) and `engagement-automation` (recurring/unattended).

**Why:** The question "can we spin up the same project in different instances on different branches" is now standard Cure practice with zero written doctrine. The mechanics exist in `git-worktree-manager`; the judgment layer (what parallelizes safely, who owns the merge, how the token budget splits) exists only in one consultant's head.

**Blast radius:** Low — one additive skill.

**Acceptance:**
- [ ] Skill passes audit; combined desc+when_to_use ≤350 chars; body ≤500 lines with sibling reference file if needed
- [ ] NOT-clause routing vs. git-worktree-manager and engagement-automation in both directions
- [ ] Blast-radius/autonomy table present; destructive-op mutual exclusion convention documented
- [ ] `sync-metadata.py --write` + `generate-overview.py` run; Wave 2.5 exporter picks it up automatically

**Effort:** 1 day.

---

## T33 — Codex as a third runtime + evidence-based runtime selection guide

**Status:** Open
**Release:** v7.7.0 (minor)
**Depends on:** T25 (exporter), T30 (benchmark data)

**Scope:**
1. Extend `scripts/export-agent-skills.py` with an `--codex` target: generate a per-project `AGENTS.md` **section** (Codex's discovery surface) that indexes the exported skills with one-line descriptions and "read `dist/agent-skills/<name>/SKILL.md` when…" pointers. Must **append/manage a marked block**, never overwrite — initiated-recruiting's AGENTS.md already carries hand-written project content.
2. Verify current Codex skill-discovery behavior before building (docs move fast; do not assume AGENTS.md is still the only surface).
3. Fix the empty-shell installs: initiated-recruiting's `.agents/skills/` is empty and Level5's `.gemini/` is unverified — T26's installer run against both, confirmed working end-to-end in each runtime.
4. New `docs/RUNTIME-SELECTION.md`: when a consultant reaches for Claude Code vs. Codex vs. Antigravity/Gemini — driven by T30's `--mode model` matrix, not vibes. Includes the credit-exhaustion fallback path (the original Wave 2.5 motivation) and what each runtime silently drops (hooks, tool restrictions, forking — extends T28's gap doc).
5. Feeds `technology-radar`: model/runtime choices become Adopt/Trial/Assess/Hold entries with benchmark citations.

**Why:** "We extended our skills for codex and antigravity" is currently half-true — Antigravity has a real export path (Wave 2.5); Codex has an empty directory and a repurposed AGENTS.md. And with three runtimes, "which one for this task" needs data behind it or every consultant decides differently.

**Blast radius:** Medium — touches consuming projects' AGENTS.md files (marked-block discipline is the safety mechanism).

**Acceptance:**
- [ ] `export-agent-skills.py --codex` emits a managed AGENTS.md block; re-run idempotent; hand-written content untouched
- [ ] initiated-recruiting: Codex discovers and activates ≥1 exported skill end-to-end (documented transcript)
- [ ] Level5: Gemini/Antigravity install verified working, not just present
- [ ] RUNTIME-SELECTION.md cites T30 result data for every recommendation
- [ ] T28 gap doc updated with the Codex column

**Effort:** 1.5–2 days.

---

## T34 — Prose-coherence repair + narrative drift detection

**Status:** Open
**Release:** v7.5.1 (patch) — no dependencies, ship first

**Scope:**
1. Fix the two corrupted skills: restore the domain-specific "Additionally gather" bullet lists in `skills/engineering/sdlc/SKILL.md` and `skills/engineering/finops/SKILL.md` (T20 migration clobbered them; reconstruct from git history pre-T20).
2. Sweep all 72 Pre-Processing skills for the same corruption class (header present, bullets missing/truncated, mid-sentence splices) — the census found 2, but the check was crude.
3. Add a structural-coherence lint to `audit-library.py`: every "Additionally gather" / "Pre-Processing" header must be followed by ≥1 bullet; section headers may not be followed immediately by body prose from a different section (heuristic: sentence-fragment detection after list-introducing colons).
4. Retire or regenerate `EVALUATION.md`: it asserts pre-March-2026 state ("24 commands, no hooks") and is linked from README.md and GEMINI.md. Either delete + scrub references, or replace with a pointer to OVERVIEW.md + this backlog. Recommend delete — OVERVIEW.md is the living inventory.
5. Extend `nightly-drift.yml` with a doc-claims check: grep known-falsifiable claims (counts, "no X exists") in prose docs against filesystem truth — the same pattern `sync-metadata.py` already uses for counts, applied to README/GEMINI/EVALUATION references.

**Why:** Two skills shipped corrupted for a month while scoring 9.9 and 10.0 — the audit reads frontmatter and counts lines but never reads prose. And the repo's own front-door docs cite an evaluation that is three major versions stale. Cheap fixes, disproportionate credibility.

**Blast radius:** Low — two skill-body repairs, one doc deletion, additive lint rules.

**Acceptance:**
- [ ] sdlc + finops Pre-Processing blocks restored and coherent; any additional corrupted skills found in the sweep fixed
- [ ] New lint rule catches the pre-fix versions of both files (regression-test the linter against them)
- [ ] EVALUATION.md dispositioned; zero dangling references
- [ ] nightly-drift catches a seeded false doc claim in a dry run
- [ ] `audit-library.py` green; library mean unchanged or better

**Effort:** 0.5–1 day.

---

## T35 — Skill usage telemetry: find the 20% that carries 80%

**Status:** Open
**Release:** v7.6.0 (minor)

**Scope:**
1. Lightweight invocation logging via the existing hook layer: a PostToolUse/Skill-invocation hook appends `{timestamp, skill, project}` to a local JSONL (`~/.cure/telemetry/skill-usage.jsonl`). **Constraints are non-negotiable:** append-only local file, no network I/O, fires in <50ms, fail-open, exempt from nothing-blocks-automation rules.
2. `scripts/usage-report.py` (stdlib): per-skill invocation counts, per-project breakdown, never-invoked list, trailing-90-day trend.
3. Feed the quarterly re-eval with a **prune mandate**, not a suggestion: any skill with zero invocations across the fleet for 2 consecutive quarters is auto-filed as a deprecation candidate in the next wave; keeping it requires a written why. Target shape: a smaller, fully-measured library beats 81 skills that are 40% dark matter — breadth is only justified when used.
4. Generated `SCORECARD.md` at repo root: one line per metrics layer (conformance / effectiveness / usage / fleet / outcome) with its current number and trend, regenerated by the nightly job alongside the drift check. The scorecard is the headline quality number; the audit score becomes one row in it.
5. Explicit non-goal: no phone-home, no aggregation service, no per-client data. Single-consultant local files, manually shared if ever needed.

**Why:** 81 skills and zero data on which ones fire. Maintenance hours, listing budget, and eval coverage are all allocated blind. The chaos-engineering skill self-flags "verify the team is ready" — nobody can currently answer whether it has ever run.

**Blast radius:** Low — one quiet hook + one script. Hook must pass the Token Economy rules (quiet, non-blocking) or it gets reverted.

**Acceptance:**
- [ ] Hook logs invocations locally with zero measurable session latency; CI check confirms no network I/O
- [ ] `usage-report.py --json` produces counts, never-invoked list, per-project split
- [ ] MAINTENANCE.md quarterly cadence consumes the report; prune mandate (2 quarters dark → auto-filed deprecation candidate) documented and applied
- [ ] `SCORECARD.md` generated nightly with all five layers; audit score demoted to one row
- [ ] Works in consuming projects via the plugin, not just this repo

**Effort:** 1–1.5 days.

---

## T36 — Guardrail enforcement inventory: prose → mechanism

**Status:** Open
**Release:** v7.6.0 (minor)

**Scope:**
1. Inventory every guardrail currently expressed as prose across the library: skill-body warnings ("read-only", "confirm before", "never in production"), agent prompt constraints, AUTOMATION.md rules, and the Wave 2.5 exported READ-ONLY/DESTRUCTIVE blocks.
2. Classify each: **(a) enforceable now** → move to the mechanism (`disallowed-tools`, `disable-model-invocation`, settings.json deny rules, PreToolUse hooks); **(b) enforceable partially** → mechanism + prose; **(c) prose-only by nature** → keep, but label explicitly `<!-- advisory: not enforced -->` so nobody mistakes it for a control.
3. Add an audit rule: a skill whose body claims a restriction its frontmatter doesn't enforce gets flagged (e.g. "read-only" prose without `disallowed-tools`).
4. Regulated-project overlay: Level5 is medical-scribe software (HIPAA-adjacent today, HIPAA-real the moment PHI flows). Document in docs/CONSUMING-PROJECTS.md which guardrail classes are mandatory-mechanism for regulated projects, and verify Level5's install passes. Same treatment pre-listed for any project taking payments (stripe-integration consumers).
5. Non-Claude runtimes stay prose-only (no enforcement surface exists — verified in Wave 2.5). The gap is documented per T28; RUNTIME-SELECTION.md (T33) inherits it as a selection criterion for sensitive work: **regulated-project work stays on Claude Code where controls are real.**

**Why:** Prose is currently the primary safety control in most of the library — acceptable for a solo consultancy until it isn't: Level5 exists, Stripe skills exist, and a control that's only text is a belief. Cheapest of the soundness tickets, largest reduction in real risk.

**Blast radius:** Medium — frontmatter/settings changes across many skills can change permission-prompt behavior in consuming projects. Roll through the canary ring like any release.

**Acceptance:**
- [ ] Inventory doc committed (docs/ or the audit's --json output): every prose guardrail classified a/b/c
- [ ] All class-(a) guardrails moved to mechanisms; zero skills claiming restrictions their frontmatter doesn't enforce
- [ ] Audit rule catches a seeded prose/frontmatter mismatch
- [ ] Class-(c) guardrails labeled advisory; count reported in SCORECARD.md fleet row
- [ ] Level5 verified against the regulated-project overlay; result recorded in its manifest
- [ ] RUNTIME-SELECTION.md (T33) references the runtime-enforcement gap

**Effort:** 1–1.5 days.

---

# Wave 2.5 (2026-07-13) — Dual-Runtime Distribution (Gemini CLI + Antigravity)

Captured 2026-07-13. Theme: consultants sometimes exhaust Claude credits mid-engagement and fall back to Gemini CLI or Antigravity. Both tools now natively read the Agent Skills open standard (the same SKILL.md format this library uses), so the 81 skills can become a second distribution target generated from the same source tree — replacing the homegrown `gemini skills/*.skill` ZIP pipeline, which predates native support and nothing consumes. This is an interim wave; deferred parity items (personas→Antigravity rules, broader agent re-expression) roll into the Wave 3 quarterly re-evaluation due October 2026.

**Non-goals:** porting hooks, output styles, the Stop gate, or the full 39-agent roster. Those are Claude Code plugin constructs; T28 documents the gap instead of pretending to close it.

## Verified platform facts (do not re-research; verified against geminicli.com/docs, antigravity.google/docs, and Google Cloud community posts, July 2026)

- **Universal workspace location:** `<workspace>/.agents/skills/<skill-dir>/` is read by Gemini CLI AND all three Antigravity variants (IDE, CLI, AGY). This is the one path that serves everything at project level.
- **Global locations diverge:** Gemini CLI reads `~/.gemini/skills/` (alias `~/.agents/skills/`); the only global path all Antigravity variants recognize is `~/.gemini/config/skills/`.
- Gemini CLI discovery tiers (precedence order): built-in → extension-bundled → user → workspace; the `.agents/skills/` alias wins within each tier.
- Gemini CLI skill lifecycle mirrors Claude: name+description injected into the system prompt at session start; `activate_skill` loads the body on demand. `gemini skills install|uninstall` (default user scope, `--scope workspace`), `/skills enable|disable` in-session.
- Gemini CLI **extensions can bundle skills** (plus context files and MCP config) — `gemini extensions install <git-url>` works from a private repo; this is the plugin-parity distribution channel.
- Documented skill frontmatter on both platforms: `name`, `description` only. Claude-only fields (`argument-hint`, `disallowed-tools`, `disable-model-invocation`, `user-invocable`, `context: fork`, `paths`, `hooks`) are **silently ignored** — no error, no enforcement.
- **No tool-restriction or read-only mechanism exists** for Gemini/Antigravity skills. Activation actually widens access (skill dir joins allowed read paths). Guardrails must be expressed as prose in the skill body.
- **No dynamic context injection equivalent.** Our `` !`command` `` / ```` ```! ```` blocks (71 skills post-T20) render as literal text there — the exporter must rewrite them into explicit "run this command first" instructions.
- Bundled `scripts/` directories are supported by both platforms (Antigravity docs explicitly encourage script delegation) — the zero-pip stdlib convention (T3) transfers as-is.
- Skill directories sit flat under the skills root on both platforms — our `skills/{domain}/{name}/` nesting must be flattened on export.

## Release plan

| Release | Bump | Tickets | Theme |
|---------|------|---------|-------|
| v7.5.0 | minor | T25–T29 | Dual-runtime export, install, extension, parity docs, CI |

T23 release mechanics apply as the closing checklist. Total estimate: **3–4 dev-days**.

---

## T25 — Standard-format exporter; retire the `.skill` ZIP pipeline

**Status:** Open
**Release:** v7.5.0 (minor)

**Scope:**
1. New `scripts/export-agent-skills.py` (Python stdlib only, `--help` + `--json`, per SCRIPTS_CONVENTION) that walks `skills/{domain}/{name}/SKILL.md` and emits `dist/agent-skills/{name}/` (flat, one dir per skill: SKILL.md + `scripts/` copied verbatim).
2. Frontmatter translation: keep `name` + `description` (fold `when_to_use` into description); strip all Claude-only fields.
3. Guardrail translation to prose: skills with `disallowed-tools` get a leading **"READ-ONLY SKILL"** block ("do not edit files or run mutating commands; produce analysis only"); skills with `disable-model-invocation: true` get a **"DESTRUCTIVE — explicit user confirmation required before each mutating step"** block. Default policy (decided 2026-07-13): destructive skills ARE exported with the prose warning, not excluded — Gemini is a fallback for the same work, and a missing skill costs more than a softer guardrail. T28 can override per-skill.
4. Injection translation: rewrite inline `` !`command` `` and fenced ```` ```! ```` blocks into a "Gather context first — run:" instruction step preserving the command verbatim. Must handle all 71 migrated skills without manual edits.
5. Flattening safety: fail the export on any duplicate skill name across domains.
6. Delete `gemini skills/` (81 `.skill` ZIPs) and `generate-gemini-skills.sh`; scrub references (GEMINI.md, CLAUDE.md, README if present).

**Why:** The ZIP pipeline targets a format nothing reads; both Google tools consume plain SKILL.md dirs. Without injection/guardrail translation the exported skills are broken (literal `` !`command` `` noise) or unsafe (guardrails silently dropped).

**Blast radius:** Medium — deletes a top-level directory and a script; adds `dist/` output. No Claude-side behavior changes.

**Acceptance:**
- [ ] `python3 scripts/export-agent-skills.py` produces 81 flat skill dirs in `dist/agent-skills/`; idempotent on re-run
- [ ] Zero literal `` !`command` `` or ```` ```! ```` blocks in exported bodies (grep-clean)
- [ ] Every source skill with `disallowed-tools` → exported READ-ONLY block; every `disable-model-invocation` → DESTRUCTIVE block
- [ ] Exported frontmatter contains only `name` + `description`
- [ ] Duplicate-name check fails loudly
- [ ] `gemini skills/` and `generate-gemini-skills.sh` gone; no dangling references
- [ ] `audit-library.py` green

**Effort:** 1–1.5 days.

---

## T26 — Install story: `.agents/skills/` + global scopes, auto-update integration

**Status:** Open
**Release:** v7.5.0 (minor)

**Scope:**
1. New `install-agent-skills.sh` (or a `setup.sh` subcommand): installs `dist/agent-skills/*` into a target. Modes: `--workspace <path>` → `<path>/.agents/skills/` (universal: Gemini CLI + all Antigravity variants); `--global` → both `~/.gemini/skills/` (Gemini CLI) and `~/.gemini/config/skills/` (Antigravity universal global).
2. Symlink by default (so `auto-update.sh` pulls propagate automatically); `--copy` flag for machines where the repo checkout isn't stable.
3. `auto-update.sh` re-runs the exporter after pulling so installed symlinks always point at fresh output.
4. Uninstall flag that removes only what we installed.

**Why:** One flattened export + one install command serves both runtimes at both scopes; symlinks keep the existing auto-update flow as the single freshness mechanism.

**Blast radius:** Low — new script + one hook into auto-update.sh.

**Acceptance:**
- [ ] Workspace install → skills discoverable in Gemini CLI (`/skills` lists them) from `.agents/skills/`
- [ ] Global install writes both global paths
- [ ] `auto-update.sh` regenerates `dist/` post-pull
- [ ] Uninstall leaves foreign skills untouched
- [ ] Scripts pass `scripts/verify-skill-scripts.sh` conventions where applicable

**Effort:** 0.5 day.

---

## T27 — Gemini CLI extension packaging

**Status:** Open
**Release:** v7.5.0 (minor)

**Scope:**
1. `gemini-extension/` with `gemini-extension.json` bundling the exported skills plus a trimmed GEMINI.md context file (Cure standards summary — the analog of the plugin's CLAUDE.md surface).
2. Installable via `gemini extensions install <private-git-url>` — verify against the internal-only constraint (private repo access, no marketplace).
3. Exporter (T25) also refreshes the extension's bundled skill copies, so there is still exactly one source of truth.
4. Document the choice consumers face: extension install (Gemini CLI only, versioned, one command) vs `.agents/skills/` install (works in Antigravity too). Recommendation: workspace `.agents/skills/` for engagement repos; extension for consultants' personal machines.

**Why:** Extensions are the true plugin analog on the Gemini side — versioned, one-command, bundles context. But they don't reach Antigravity, so this complements rather than replaces T26.

**Blast radius:** Low — additive directory.

**Acceptance:**
- [ ] `gemini extensions install` from the private repo succeeds; bundled skills discoverable in a fresh session
- [ ] Extension skill copies are generated, never hand-edited (CI-checked in T29)
- [ ] Consumer guidance written (which install path when)

**Effort:** 0.5–1 day.

---

## T28 — Parity triage + runtime-parity matrix

**Status:** Open
**Release:** v7.5.0 (minor)

**Scope:**
1. Per-skill export triage pass over all 81: confirm the T25 default (export destructive skills with prose warning) or override to exclude, recorded as an explicit exclusion list the exporter reads. Expected exclusions are rare (skills meaningless off-Claude, e.g. anything whose body is purely Claude-harness mechanics like Recurring Mode /loop wiring — trim those sections on export instead where the skill is otherwise useful).
2. `docs/RUNTIME-PARITY.md`: matrix of what each runtime gets — skills (all three), bundled scripts (all three), agents/personas/hooks/Stop gate/output styles/rules/workflows/monitors (Claude only), plus the guardrail downgrade note. Written for a consultant switching mid-engagement: "what you lose when you leave Claude."
3. Decide and document which (if any) of the top agents get re-expressed as exported skills now; default answer is none in this wave — record the shortlist as a Wave 3 candidate instead.

**Why:** Switching runtimes mid-engagement with silent capability loss is worse than a documented, deliberate downgrade. The exclusion list makes safety decisions reviewable instead of buried in exporter code.

**Blast radius:** Low — docs + an exporter config file.

**Acceptance:**
- [ ] Every skill has an explicit disposition (export / export-trimmed / excluded+reason)
- [ ] RUNTIME-PARITY.md covers all nine Claude-only surfaces and the guardrail downgrade
- [ ] Wave 3 candidate list for agent re-expression recorded in BACKLOG

**Effort:** 1 day.

---

## T29 — CI freshness, metadata sync, docs update

**Status:** Open
**Release:** v7.5.0 (minor)

**Scope:**
1. `validate.yml`: fail if `skills/**` changed but `dist/agent-skills/` (and T27 extension copies) weren't regenerated (regenerate-and-diff check, same pattern as overview freshness).
2. `audit-library.py`: assert export invariants (frontmatter shape, no injection blocks, guardrail blocks present, exclusion list entries all have reasons).
3. `sync-metadata.py --write`: include exported-skill count and extension version references.
4. Docs: CLAUDE.md dev rule "Create both Claude and Gemini versions … regenerated via generate-gemini-skills.sh" replaced with the exporter step; GEMINI.md distribution section rewritten; `docs/CONSUMING-PROJECTS.md` gains a dual-runtime install section; `docs/MAINTENANCE.md` adds export freshness to the monthly cadence.

**Why:** Wave 2's lesson (T9/T14): hand-maintained parallel artifacts drift into fiction. The export must be CI-enforced generated output from day one.

**Blast radius:** Low-medium — touches CI, two scripts, four docs.

**Acceptance:**
- [ ] CI red on stale export, green after regeneration
- [ ] `audit-library.py` and `sync-metadata.py --write` green and idempotent
- [ ] No doc still references `.skill` ZIPs or generate-gemini-skills.sh
- [ ] T23 closing checklist run for v7.5.0

**Effort:** 0.5 day.

---

## Wave 2.5 order of execution

T25 → T26 → T27 → T28 → T29. T28's triage reviews T25's default output, so the exporter ships first with the decided default (export destructive skills with prose warnings); T28 refines via the exclusion list. Single release (v7.5.0).

## Wave 2.5 risks

- **Antigravity docs churn** — the product is young; discovery paths were verified July 2026 but variant-specific paths beyond `.agents/skills/` and `~/.gemini/config/skills/` are inconsistent. Mitigation: install only to the two universal paths.
- **Prose guardrails are advisory** — a Gemini agent can ignore a READ-ONLY block in a way Claude's `disallowed-tools` cannot be ignored. RUNTIME-PARITY.md must state this bluntly; T28 exclusion list is the escape hatch for anything where advisory isn't enough.
- **Description budget mismatch** — Gemini injects all skill descriptions into the system prompt like Claude does, but its budget behavior is undocumented. Our ≤350-char trigger policy (T24) likely transfers fine; watch for truncation reports.

---

# Wave 2 (2026-07-11) — Continuous-Execution Alignment

Captured 2026-07-11 from an evaluation against current Claude Code documentation (code.claude.com/docs, verified July 2026). Theme: the library was built for request/response invocation — invoke a skill, get an artifact. Claude Code now has a continuous-execution layer (`/loop` with self-pacing, cloud routines, named workflows, background monitors, Stop-hook goal gates) that the library neither teaches nor exploits. Wave 2 closes that gap plus the correctness debt found during the evaluation.

## Verified platform facts (do not re-research; verified against docs July 2026)

- `maxTurns` and `memory: user|project|local` (plain string) are **valid documented subagent frontmatter** — our 39 agents need NO migration there.
- `proactiveTriggering` is **not documented** — do not adopt; use hook matchers instead.
- Subagent `effort: low|medium|high|xhigh|max` and `isolation: "worktree"` are documented.
- Skill `paths:` (comma-separated string or YAML list of globs) limits when a skill activates.
- Skill-scoped `hooks:` frontmatter is supported (same event→matcher→hooks nesting as settings).
- Hook types: `command`, `prompt`, `agent` (experimental), `http`, `mcp_tool`. Prompt/agent hooks return `{"ok": bool, "reason": "..."}`; Stop hooks block via top-level `{"decision": "block", "reason": "..."}` or exit 2 + stderr.
- Hook `if` argument filters (permission-rule syntax, e.g. `"if": "Bash(git *)"`) work ONLY on PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied.
- `ConfigChange` event has a `skills` matcher (fires when skill files change mid-session).
- Dynamic context injection in skills: inline `` !`command` `` and fenced ```` ```! ```` blocks execute before Claude reads the skill; bash default (`shell: powershell` to override); **works in plugin-shipped skills**. No Gemini equivalent.
- `.claude/loop.md` (project) / `~/.claude/loop.md` (user) replaces the built-in `/loop` maintenance prompt; project wins; 25,000-byte cap.
- Named workflows auto-load from `.claude/workflows/*.js` (closest dir wins in monorepos), invocable as `/workflow-name`, no registration. **Plugins cannot ship workflows** — our installer vendoring into `.claude/` is the only distribution path.
- Since v2.1.196, `/loop` scheduled fires only run skills Claude may auto-invoke: `disable-model-invocation: true` makes a skill unloopable. Loopable-but-hidden pattern: `user-invocable: false`.
- Plugin `monitors/monitors.json` (`name`, `command`, `description`, optional `when: "always" | "on-skill-invoke:<skill>"`) auto-starts monitors; each stdout line reaches Claude as a notification.
- Plugin `bin/` contents join Bash PATH while the plugin is enabled — no manifest wiring.

## Wave 2 — Resolution Status (2026-07-11)

All 17 tickets shipped in a single session across four releases (v7.1.5 → v7.4.0). Deviations from plan:

| Ticket | Deviation |
|--------|-----------|
| T9 | Inventory blobs deleted rather than generated — removal beat generation (the drift-prone content is gone; counts/version in remaining hook text stay synced by sync-metadata) |
| T11 | Security guard shipped as a deterministic command hook (8-fixture test matrix) instead of an experimental agent hook — zero tokens, portable, blocking |
| T12 | maxTurns and memory:project confirmed valid documented syntax — left untouched (first research pass was wrong); proactiveTriggering not documented — not adopted |
| T14 | 9 skills, not 10 — `code-audit` never existed (phantom entry in the old hand-maintained hook inventory, proving T9's point) |
| T18 | cure-release-check dry-run on this repo (4 agents) found a REAL blocker: the repo's own CI banned type:prompt hooks. Gate amended to constrained-allow (Stop/PostToolUseFailure only, timeout ≤30s) in validate.yml. Also fixed: npm files whitelist missing loop.md/workflows/bin/monitors; bootstrap package bumped to 0.3.0 |
| T20 | 71 of 72 skills migrated; cure-infra-bootstrap + self-improving-memory kept prose deliberately (conditional, env-dependent gathering — wrong fit for unconditional injection) |
| T24 | 10 worst trigger texts tightened (580→≤360); library total ~24.5k chars — full ≤10k unrealistic without gutting discovery quality, so the enforced policy is per-skill caps (audit warns >350) + skillListingBudgetFraction documented for consumers |

## Release plan

| Release | Bump | Tickets | Theme |
|---------|------|---------|-------|
| v7.1.5 | patch | T8 | Doc/impl truth reconciliation |
| v7.2.0 | minor | T9–T13, T24 | Hooks + frontmatter modernization, context budget |
| v7.3.0 | minor | T14–T17 | Continuous execution (loops, routines) |
| v7.4.0 | minor | T18–T22 | Orchestration & distribution (workflows, injection, monitors) |

T23 (release mechanics) runs as the closing checklist of every release. Total estimate: **14–18 dev-days**.

---

## T8 — Doc/impl truth reconciliation

**Status:** ✅ Done (2026-07-11)
**Release:** v7.1.5 (patch)

**Scope:**
1. `AGENT-GUIDE.md:27` claims "Stop hook validates tests, security review, docs" — no `Stop` hook exists in `hooks/hooks.json`. Reword to describe what actually fires today; T10 restores the claim truthfully.
2. `CLAUDE.md` claims skill-security-auditor is "Wired into PreToolUse hook" — it isn't (PreToolUse entries are path/command blocklists only). Reword; T11 makes it real.
3. `CLAUDE.md` says "Current version: **7.0.1**"; plugin.json says 7.1.4. Fix, and add the CLAUDE.md version line to `scripts/sync-metadata.py --write` scope so it cannot drift again.

**Why:** The guide sells enforcement that doesn't exist. Consultants plan engagements around these claims.

**Blast radius:** Low — two docs + one script.

**Acceptance:**
- [ ] AGENT-GUIDE.md makes no claim hooks/hooks.json doesn't implement
- [ ] CLAUDE.md hook/agent wiring claims match hooks/hooks.json
- [ ] `sync-metadata.py --write` syncs CLAUDE.md version from plugin.json; idempotent on re-run
- [ ] `audit-library.py` green

**Effort:** 1–2 hours.

---

## T9 — Hook diet: delete noise, scope checklists, generate inventory blocks

**Status:** ✅ Done (2026-07-11)
**Release:** v7.2.0

**Scope:**
1. Delete pure-noise hooks (context tax on every tool call in every consuming project): PostToolUse Bash "Executed: $CMD" echo, PostToolUse Edit/Write "Updated $FILE" echo, the Notification `{"notification_logged": true}` stub, and the PostToolUseFailure "Analyzing output..." echo (T11 replaces it with real triage).
2. SubagentStop: the blanket 6-line quality checklist fires after **every** subagent, including read-only analysts where "PR ready?" is meaningless. Add agent-type matchers so only code-writing agents (refactor-assistant, project-bootstrapper, release-coordinator) trigger it.
3. SessionStart (×4 entries) and PreCompact inventory blobs are hand-maintained duplicates of `docs/OVERVIEW.md` and have already drifted once. Generate both blocks via `sync-metadata.py --write` from the same source as OVERVIEW.md; add a CI drift check.

**Why:** Hooks should be quiet by default and impossible to let rot.

**Blast radius:** Medium — hooks.json ships to every consuming project on next install.

**Acceptance:**
- [ ] hooks.json valid JSON; noise hooks removed
- [ ] SubagentStop checklist fires only for write-capable agent types
- [ ] SessionStart/PreCompact blocks generated, byte-identical on regen, CI fails on drift
- [ ] `audit-library.py` green

**Effort:** 1 day.

---

## T10 — Stop-hook quality gate (prompt-type)

**Status:** ✅ Done (2026-07-11)
**Release:** v7.2.0
**Depends on:** T9

**Scope:**
Add a `Stop` hook of `type: "prompt"` (haiku, 30s timeout): if the turn edited product code but shows no evidence of tests/verification being run, return `{"decision": "block", "reason": "<specific gap>"}` so Claude keeps working; otherwise pass. Guardrails: fail open on timeout/parse error; at most one block per turn (phrase the reason so a justified skip — docs-only change, user said skip tests — passes on re-check) to prevent block loops.

**Why:** This is the "different goals" robustness ask made concrete — done means verified, enforced at the harness level. Also makes AGENT-GUIDE's (currently false) promise true.

**Blast radius:** Medium — behavior change in every consuming project. Must fail open.

**Acceptance:**
- [ ] Stop prompt-hook in hooks/hooks.json using documented `{decision, reason}` contract
- [ ] Blocks once with an actionable reason when code was edited with no test/verify evidence; passes clean turns and justified skips
- [ ] Fails open on timeout/parse failure (verified by test)
- [ ] Manually exercised in a sample consuming project (block path + pass path)
- [ ] AGENT-GUIDE.md Stop-hook claim restored (closes the T8 reword)

**Effort:** 1 day incl. testing.

---

## T11 — Wire skill-security-auditor and failure triage for real

**Status:** ✅ Done (2026-07-11)
**Release:** v7.2.0
**Depends on:** T9

**Scope:**
1. `ConfigChange` hook, matcher `skills`: run a fast `audit-library.py` pass when skill files change mid-session.
2. PreToolUse on `Write|Edit` scoped to `skills/**`, `agents/**`, `personas/**`: agent-type hook (experimental, 60s, `{ok, reason}`) running the skill-security-auditor checks. Verify on implementation whether the `if` permission-rule syntax supports `Write(skills/**)` path filtering; if not, fall back to a command hook that inspects `file_path` and exits 2 with reason.
3. PostToolUseFailure on Bash: prompt-type hook (haiku) that classifies the failure and names the right agent (ci-debugger, dependency-auditor, …) — replaces the deleted echo with signal.

**Why:** CLAUDE.md already promises this wiring; agent/prompt hooks now exist to deliver it.

**Blast radius:** Medium. Agent hooks are experimental — keep the command-hook fallback in the ticket, not just the doc.

**Acceptance:**
- [ ] Editing a SKILL.md mid-session triggers the audit pass
- [ ] A malicious-pattern fixture skill (curl-pipe-bash, secret exfil) is blocked with a reason
- [ ] Bash failures produce one targeted agent suggestion, not boilerplate
- [ ] All three hooks fail open
- [ ] CLAUDE.md wiring claim now true (closes the T8 reword)

**Effort:** 1–1.5 days.

---

## T12 — Agent frontmatter modernization: effort tiers, worktree isolation, model policy

**Status:** ✅ Done (2026-07-11)
**Release:** v7.2.0

**Scope (39 agents):**
1. **Verified no-ops — do not touch:** `maxTurns` and `memory: project` are valid documented syntax. `proactiveTriggering` is undocumented — do not adopt.
2. **Model policy:** remove the blanket `model: sonnet` pin (all 39 agents) so agents inherit the session model by default; keep explicit pins only where a cheap model is deliberately right. Ticket includes a per-agent decision table.
3. **Effort tiers:** `effort: high` for judgment-heavy agents (code-reviewer, pr-reviewer, firebase-security-auditor, skill-security-auditor, migration-validator); `effort: low` for mechanical reporters.
4. **Isolation:** `isolation: "worktree"` on write-capable agents that may run concurrently (refactor-assistant, project-bootstrapper, release-coordinator).
5. **Preload policy (systemic, not just the audit-flagged agent):** 14 of 39 agents preload >800 lines of full skill bodies per spawn via `skills:` (worst: financial-analyst 1,420 lines, investor-relations 1,206, ops-finance 1,188). Adopt a policy: preload at most one short skill (~300 lines); everything else becomes an on-demand reference in the agent body ("invoke /x when needed").
6. Extend `audit-library.py` rubric: validate `effort`/`isolation` values, flag blanket model pins, flag preloads over the policy cap.

**Why:** A universal sonnet pin silently downgrades every agent below the session model now that the Claude 5 family is out; effort tiers are the documented way to spend where judgment lives.

**Blast radius:** Medium-high — all 39 agent files; model-selection behavior changes downstream.

**Acceptance:**
- [ ] Decision table applied to all 39 agents
- [ ] financial-analyst preload trimmed; audit preload finding gone
- [ ] audit-library rubric extended and green
- [ ] OVERVIEW.md regenerated; 3 agents spot-checked by spawning them

**Effort:** 1.5–2 days.

---

## T13 — Skill frontmatter modernization: disallowed-tools, paths, effort

**Status:** ✅ Done (2026-07-11)
**Release:** v7.2.0

**Scope:**
1. The 3 audit-flagged sandbox offenders (feature-audit, accessibility-audit, security-review): add `disallowed-tools: Write Edit` (keep `allowed-tools` for no-prompt reads — the two fields compose). Sweep the other 8 `allowed-tools` skills for the same read-only intent.
2. `paths:` adoption — **only** for file-triggered review/audit skills (e.g. accessibility-audit → web file globs). Do NOT add to scaffold skills; they run before matching files exist. Per-skill decision list in the ticket. A wrong glob silently hides a skill — acceptance includes a reachability check.
3. `effort: high` on heavy analysis skills (security-review, code-audit, performance-review).

**Blast radius:** Medium — activation behavior changes.

**Acceptance:**
- [ ] Audit sandbox findings: 0
- [ ] Every `paths:` skill verified still reachable in a fresh project (manual matrix)
- [ ] Gemini + legacy claude-commands regenerated

**Effort:** 1 day.

---

## T14 — "Recurring Mode" sections in 10 goal-shaped skills

**Status:** ✅ Done (2026-07-11)
**Release:** v7.3.0
**Depends on:** T15 (cross-links the new skill)

**Scope:**
finops, burn-rate-tracker, investor-reporting, technology-radar, performance-review, code-audit, accessibility-audit, security-review, feature-audit, seo-content-engine. Each gets a `## Recurring Mode` section: `/loop` vs cloud-routine choice, recommended cadence, exact invocation (e.g. `/loop 1w /cure-product-engineering:burn-rate-tracker`), stop condition, token budget, unattended guardrails (read-only; never sends anything external).

**Constraint:** these skills must stay model-invocable — since v2.1.196 scheduled fires skip skills Claude can't auto-invoke. Never add `disable-model-invocation` here; `user-invocable: false` is the loopable-but-hidden pattern. Add this as a CLAUDE.md development rule.

**Why:** A third of the business/quality library is naturally recurring goals sold as one-shot templates. "Put this engagement on autopilot" should be a documented move.

**Blast radius:** Low — additive sections + Gemini parity.

**Acceptance:**
- [ ] 10 skills updated, bodies stay under limits
- [ ] CLAUDE.md rule added re: `disable-model-invocation` × `/loop`
- [ ] Gemini parity regenerated

**Effort:** 1–1.5 days.

---

## T15 — New skill: engagement-automation (platform)

**Status:** ✅ Done (2026-07-11)
**Release:** v7.3.0

**Scope:**
Decision framework for harness-level automation: `/loop` fixed-interval vs self-paced vs cloud routine (cron / API / GitHub triggers) vs desktop scheduled task vs CI cron vs hook. Covers: 7-day loop expiry, jitter, per-routine token caps and daily run limits, resumability, the never-unattended list (deploys, migrations, anything write-capable against prod), and monitoring for silent failures. Standard 3-step format. One cross-link paragraph added to agent-workflow-designer distinguishing product-AI workflow patterns (its territory) from Claude Code harness orchestration (this skill's).

**Blast radius:** Low — additive. 80 → 81 skills; counts regenerate via T23.

**Acceptance:**
- [ ] SKILL.md passes audit ≥ 9.5
- [ ] Cross-link paragraph in agent-workflow-designer
- [ ] Gemini version; OVERVIEW/CLAUDE.md counts synced

**Effort:** 1 day.

---

## T16 — Cure maintenance loop: loop.md template + vendoring

**Status:** ✅ Done (2026-07-11)
**Release:** v7.3.0

**Scope:**
`bootstrap/templates/loop.md.ejs` — the Cure-standard maintenance loop: outdated deps (CVE severity first), lint/type drift, TODO/FIXME decay, coverage regression vs the 80% floor, doc staleness. Must stay ≤ 25,000 bytes (documented cap). `install-plugin.js` vendors it to `.claude/loop.md` (respect exists-skip + `CURE_SKILLS_FORCE`). Project-level loop.md overrides `~/.claude/loop.md` — document that.

**Why:** Bare `/loop` in every consuming project becomes "run Cure's maintenance standard" for free.

**Blast radius:** Low-medium — installer change; bootstrap suite (106 tests) must stay green.

**Acceptance:**
- [ ] Template renders; vendored on fresh install, skipped when present
- [ ] Bare `/loop` in a sample project picks it up
- [ ] Bootstrap test suite green

**Effort:** 0.5 day.

---

## T17 — Automation recipes doc (cloud routines)

**Status:** ✅ Done (2026-07-11)
**Release:** v7.3.0

**Scope:**
`docs/AUTOMATION.md` — copy-paste recipes: weekly dependency-audit routine, monthly investor-report draft, GitHub-webhook PR-review routine, API-triggered incident triage. Each names trigger type, token budget, and guardrails. Cover the sharp edges: routines run on Anthropic infra without local permission prompts (always set per-routine token limits + daily caps), interactively-authenticated MCP servers are absent headless, secrets never in routine prompts.

**Blast radius:** Low — docs only.

**Acceptance:**
- [ ] Doc exists, linked from README and the engagement-automation skill
- [ ] Every recipe has trigger, budget, guardrails

**Effort:** 0.5 day.

---

## T18 — Ship named workflows via installer vendoring

**Status:** ✅ Done (2026-07-11)
**Release:** v7.4.0

**Scope:**
New top-level `workflows/` directory with three orchestration scripts (each: `meta` block, JSON-schema agent outputs, budget guards, `log()` on any coverage cap):
- `cure-code-audit.js` — fan out reviewers per dimension (security / architecture / perf / a11y), adversarially verify each finding, synthesize. Existing audit skills supply the stage prompts.
- `cure-release-check.js` — migration-validator + deployment-validator + dependency-auditor + api-validator in parallel, gate on all green.
- `cure-migration-sweep.js` — discover call sites → transform each with worktree isolation → verify.

`install-plugin.js`: map `workflows/` → `.claude/workflows/` (near one-line via the existing FLAT_DIRS mechanism). Plugins cannot ship workflows natively (verified) — vendoring is our distribution path, and a genuine differentiator. Once vendored they're invocable as `/cure-code-audit` etc.

**Blast radius:** Medium — a new execution surface in every consuming project; workflows spawn many agents, so every script carries conservative defaults and budget guards.

**Acceptance:**
- [ ] `node --check` passes on all three
- [ ] Each workflow dry-run against this repo or a fixture
- [ ] Installer vendors, skips-if-exists, honors FORCE
- [ ] Documented in AGENT-GUIDE (T19)

**Effort:** 2–3 days (testing dominates).

---

## T19 — AGENT-GUIDE.md rewrite for the Workflow era

**Status:** ✅ Done (2026-07-11)
**Release:** v7.4.0
**Depends on:** T18

**Scope:**
Replace the "list agents in your prompt" chaining patterns (pre-Workflow-tool era, now the worse option: non-deterministic, no resume, no budget control) with the current decision ladder: single agent → parallel Agent fan-out → named workflow (`/cure-code-audit`) → ultracode. Cover `/workflows` monitoring, resume semantics, budget directives, and one paragraph on agent teams.

**Blast radius:** Low — doc.

**Acceptance:**
- [ ] No pattern in the guide contradicts hooks.json or the shipped workflows
- [ ] Examples runnable as written

**Effort:** 0.5–1 day.

---

## T20 — Dynamic context injection migration (72 skills)

**Status:** ✅ Done (2026-07-11)
**Release:** v7.4.0

**Scope:**
72 of 80 skills carry a prose "Pre-Processing (Auto-Context)" block instructing Claude to run `cat package.json` etc. Replace with dynamic injection — e.g. `` - Stack: !`cat package.json 2>/dev/null | head -40` `` — which executes before Claude reads the skill: deterministic, and saves a round of tool calls per invocation × 72 skills. `shared/pre-processing.md` becomes the canonical injected block. Constraints: injected commands auto-execute, so they must be fast, read-only, and exit 0 on any repo including an empty one. Gemini has no injection equivalent — `generate-gemini-skills.sh` must keep the prose form (divergence handled in the generator, never by hand).

**Phasing:** pilot 5 high-traffic skills → measure context size/latency → scripted sweep (stdlib Python) + hand review of each skill's domain-specific extensions.

**Blast radius:** HIGH — 72 files, auto-executing commands, cross-generator divergence. Biggest ticket of the wave.

**Acceptance:**
- [ ] Pilot measured and reviewed before sweep
- [ ] Every injected command is read-only and exits 0 on an empty repo (new audit-library check enforces this)
- [ ] Gemini regen keeps prose; legacy commands synced
- [ ] audit-library + verify-skill-scripts green

**Effort:** 2–3 days.

---

## T21 — Adopt monitors/ and bin/ plugin surfaces

**Status:** ✅ Done (2026-07-11)
**Release:** v7.4.0

**Scope:**
1. `bin/`: wrap the bundled stdlib Python scripts as PATH commands (`cure-dora-metrics`, `cure-cost-model`, …) — presence in `bin/` is sufficient, no manifest wiring. Update `docs/SCRIPTS_CONVENTION.md`; skills reference bare command names.
2. `monitors/monitors.json`: ship only `when: "on-skill-invoke:<skill>"`-scoped monitors (e.g. incident-response tails app logs when invoked). NO `"always"` monitors — auto-start noise in projects that lack the watched files.

**Blast radius:** Low-medium — additive; a bad monitor command means noisy notifications.

**Acceptance:**
- [ ] bin commands runnable by bare name in a consuming project
- [ ] monitors.json valid; every entry `when`-scoped
- [ ] SCRIPTS_CONVENTION.md updated

**Effort:** 1 day.

---

## T22 — Verification discipline in the QA surface

**Status:** ✅ Done (2026-07-11)
**Release:** v7.4.0

**Scope:**
qa-engineer + test-runner agents, testing-strategy + e2e-testing skills: add the verify contract — a "done" claim requires exercising the affected flow end-to-end and observing behavior, not just green unit tests. Align wording with Claude Code's bundled `/verify`. Pairs with T10: the Stop gate checks; this teaches.

**Blast radius:** Low.

**Acceptance:**
- [ ] 2 agents + 2 skills updated with consistent wording
- [ ] Gemini parity

**Effort:** 0.5 day.

---

## T23 — Release mechanics (closing checklist, per release)

Runs at the end of each of v7.1.5 / v7.2.0 / v7.3.0 / v7.4.0 — not a standalone ticket:

- [ ] `audit-library.py` green, no score regressions
- [ ] `sync-metadata.py --write` (now covers CLAUDE.md version + generated hook blocks)
- [ ] `generate-overview.py`
- [ ] `generate-gemini-skills.sh`
- [ ] `sync-legacy-commands.py`
- [ ] `verify-skill-scripts.sh`
- [ ] plugin.json bump; CI manifest validation; bootstrap suite green

**Effort:** ~1 hour per release.

---

## T24 — Context budget & token economy

**Status:** ✅ Done (2026-07-11)
**Release:** v7.2.0

Measured 2026-07-11 (chars ≈ tokens × 4):

| Surface | Measured | Cost model |
|---------|----------|-----------|
| Skill listing (`description` + `when_to_use`, 80 skills) | 25,893 chars (~6.5k tokens) | Every session, every consuming project |
| Default listing budget | ~1% of context (≈2k tokens / 8k chars on a 200k model) | — |
| Agent skill preloads | 14 of 39 agents inject >800 lines/spawn | Every agent spawn (→ T12) |
| PreCompact re-injection blob | ~3,686 chars | Every compaction |
| SessionStart echoes | ~1,797 chars | Every session |
| CLAUDE.md | ~13.7k chars (~3.4k tokens) | Every session in this repo |
| Skill bodies | only 2 of 80 over the 500-line rule (505 each) | On invocation — healthy |

**Scope:**
1. **Listing overflow (the headline):** 25.9k chars vs a ~8k-char default budget means roughly two-thirds of the skill listing is at risk of truncation — auto-discovery silently fails for whichever skills fall past the cut. First, verify truncation empirically in a fresh session (which skills are actually visible?). Then attack from both ends: (a) tighten `description`/`when_to_use` toward a ~250-char average with an audit-library max-length check (the 5 worst are 490–580 chars each); (b) T13's `paths:` scoping removes file-specific skills from irrelevant sessions; (c) `user-invocable: false` + model-invocable stays for niche skills; (d) as a last resort, document `skillListingBudgetFraction` in CONSUMING-PROJECTS.md for skill-heavy setups.
2. **PreCompact blob:** slim the ~3.7k-char re-injection to standards-only (~1k chars) + a pointer to `docs/OVERVIEW.md`; the full inventory list is redundant with the skill listing itself. (Generation mechanics land in T9; the size target lands here.)
3. **Trim the 2 skills over 500 lines** (technology-radar, client-handoff — 505 each) into sibling reference files per progressive disclosure.
4. **Token-economy conventions section in CLAUDE.md:** `context: fork` for heavy analysis skills (17 use it today — sweep for more candidates), preload policy (T12), effort tiers = output-token budget, haiku for prompt-type hooks, description length cap.

**Why:** The library's biggest token line-item isn't verbosity — it's fixed overhead multiplied across every session and every spawn in every consuming project. And the listing overflow isn't just cost: it silently disables auto-discovery, which is a capability regression.

**Blast radius:** Medium — description rewrites across many skills change auto-discovery behavior (for the better, but verify).

**Acceptance:**
- [ ] Truncation verified empirically before and after; all 80 skills visible in a fresh session's listing afterward (or consciously scoped out via `paths`/`user-invocable`)
- [ ] Listing total ≤ ~10k chars or every over-budget skill deliberately scoped
- [ ] audit-library check: combined `description` + `when_to_use` ≤ 350 chars warns, ≥ 500 fails
- [ ] PreCompact payload ≤ ~1k chars
- [ ] 0 skills over 500 lines
- [ ] CLAUDE.md token-economy conventions section added

**Effort:** 1–1.5 days (description rewrites dominate).

---

## Wave 2 order of execution

1. **T8** → ship v7.1.5 same day.
2. **T9** first (T10, T11 build on the cleaned hooks file); **T12, T13, T24** parallelizable — do T24's truncation measurement before T13's `paths:` decisions so both attack the listing budget coherently → ship v7.2.0.
3. **T15** before **T14** (sections cross-link the new skill); **T16, T17** anytime → ship v7.3.0.
4. **T18** before **T19** (guide documents shipped workflows); **T20** pilot early, sweep last; **T21, T22** anytime → ship v7.4.0.

## Wave 2 risks

- **Agent-type hooks are experimental** — T11 keeps command-hook fallbacks as first-class, not a footnote.
- **`paths` can silently hide a skill** — T13 acceptance requires a reachability matrix.
- **Injected commands auto-execute** — T20 adds an audit-library check: read-only, exit 0 on empty repo.
- **Workflows spend real tokens** — every shipped script has budget guards and conservative defaults.
- **Platform floor:** features verified against Claude Code v2.1.196+ docs (July 2026). State the minimum version in README; unknown frontmatter is ignored harmlessly on older clients, but `paths`/skill-hooks behavior should be spot-checked on rollout.

---

## Wave 1 — Resolution Status (2026-04-29)

All initial tickets resolved in a single batch session.

| # | Ticket | Status | Outcome |
|---|--------|--------|---------|
| T1 | Filesystem reorg | ✅ Done | 80 skills moved into 7 domain folders: engineering (39), platform (10), product (10), business (7), marketing (4), security (4), legal (1) |
| T2 | Personas | ✅ Done | 4 personas: cure-tech-lead, cure-product-lead, cure-engagement-pm, cure-solo-consultant |
| T3 | Scripts pattern + 5 pilots | ✅ Done | 7 stdlib Python scripts across dora-metrics, engineering-cost-model, saas-financial-model, burn-rate-tracker, accessibility-audit; convention doc + smoke test |
| T4 | 8 POWERFUL skills | ✅ Done | mcp-server-builder, rag-architect, agent-designer, agent-workflow-designer, monorepo-navigator, git-worktree-manager, env-secrets-manager, interview-system-designer (+ Gemini parity) |
| T5 | Skill security auditor | ✅ Done | New agent + PreToolUse hook on Write/Edit to skills/agents/personas |
| T6 | Self-improving memory | ✅ Done | New skill + 3 templates (MEMORY.md.template, feedback_template.md, project_template.md) |
| T7 | Internal overview doc | ✅ Done | scripts/generate-overview.py + docs/OVERVIEW.md (re-runnable) |

**Net delta:** 65 → 80 skills, 34 → 39 agents, 0 → 4 personas. Bootstrap test suite (106 tests) still green. JSON configs valid. All bundled scripts pass `--help` smoke test.

Detailed tickets below kept for historical reference.

---

## T1 — Reorganize `skills/` into domain subfolders

**Status:** Pending — needs user confirmation before starting

**Scope:**
Move flat `skills/{name}/SKILL.md` into `skills/{domain}/{name}/SKILL.md`. Domains: `engineering`, `product`, `marketing`, `business`, `legal`, `security`, `platform`.

**Why:** With 66 skills (and growing toward ~100 after T4 + T6), the flat structure is becoming hard to navigate. Domain subfolders match how skills are already grouped in `CLAUDE.md`.

**Why this changed from the eval:** Originally framed as marketplace sub-plugin bundles. Without a marketplace, granular install loses its value — this becomes a pure navigation/maintenance benefit.

**Blast radius:** Medium-high. Moving 66 directories breaks every reference: hooks/hooks.json, bootstrap CLI templates, plugin.json globs, internal links in CLAUDE.md, gemini-skills mirror.

**Acceptance:**
- [ ] All `skills/{name}/` → `skills/{domain}/{name}/`
- [ ] `gemini-skills/` mirrored
- [ ] `hooks/hooks.json` paths updated
- [ ] `bootstrap/` templates updated
- [ ] `CLAUDE.md` repo structure section updated
- [ ] Plugin still loads cleanly (smoke test)
- [ ] No broken internal links (grep for stale paths)

**Effort:** ~1 day with careful grep-and-replace. Worth doing in one PR.

---

## T2 — Add personas (engagement archetypes)

**Status:** In progress (subagent drafting)

**Scope:**
New top-level `personas/` folder. Four initial personas tailored for Cure consulting engagements:
- `cure-tech-lead` — engineering lead on a client engagement
- `cure-product-lead` — product/PM lead
- `cure-engagement-pm` — program/project manager
- `cure-solo-consultant` — single consultant, cross-domain

Each persona = identity + when-to-use + curated skill loadout + curated agent loadout + decision frameworks + voice + anti-patterns. References only skills/agents that already exist.

**Why:** Genuine architectural gap. Skills answer "how", agents answer "what", personas answer "who is thinking". Maps cleanly to Cure's engagement model — "spin up a tech-lead persona for this engagement."

**Blast radius:** Low — purely additive.

**Acceptance:**
- [ ] `personas/cure-tech-lead.md`
- [ ] `personas/cure-product-lead.md`
- [ ] `personas/cure-engagement-pm.md`
- [ ] `personas/cure-solo-consultant.md`
- [ ] Each references only existing skills/agents (verified via glob)
- [ ] `CLAUDE.md` updated with personas section
- [ ] `bootstrap/` CLI optionally provisions personas/ into client repos

**Effort:** ~1 day for the 4 files + CLAUDE.md update.

---

## T3 — Bundled stdlib scripts pattern + 5 pilot skills

**Status:** Pending

**Scope:**
Establish convention: each skill MAY ship `skills/{name}/scripts/*.py` — Python stdlib only, zero pip installs, all support `--help` and `--json`. Update SKILL.md to reference the script.

Pilot on five skills where executable tooling is highest-value:
1. **dora-metrics** — `deployment_frequency.py`, `mttr_calculator.py`, `change_failure_rate.py`
2. **engineering-cost-model** — `cost_estimator.py` (dev hours × rate + infra)
3. **saas-financial-model** — `unit_economics.py` (MRR, churn, LTV/CAC)
4. **burn-rate-tracker** — `runway_calculator.py` (cash, monthly burn, scenarios)
5. **accessibility-audit** — `wcag_check.py` (run static checks, parse axe output)

**Why:** Skills become *executable*, not just instructional. Reproduces alirezarezvani's "305 stdlib Python tools" pattern, which is the single biggest reason their skills feel production-grade.

**Blast radius:** Low — additive.

**Acceptance:**
- [ ] Convention documented in `CLAUDE.md` (script naming, stdlib-only rule, --help/--json convention)
- [ ] 5 pilot skills each have ≥1 working script
- [ ] Each script verified to run with `python3 scripts/<name>.py --help`
- [ ] Each SKILL.md references its script(s) with usage examples
- [ ] Optional: `scripts/verify-skill-scripts.sh` that runs `--help` on all of them as a smoke test

**Effort:** ~3 days for pattern + 5 pilots.

---

## T4 — Port 8 POWERFUL-tier engineering skills

**Status:** Pending

**Scope:**
Add 8 new skills, each shaped to Cure's consulting profile:

| Skill | Why for Cure |
|---|---|
| **mcp-server-builder** | Clients increasingly want MCP integrations |
| **rag-architect** | AI feature builds — chunking, retrieval eval |
| **agent-designer** | Multi-agent orchestration for client products |
| **agent-workflow-designer** | Sequential/parallel/router/orchestrator/evaluator patterns |
| **monorepo-navigator** | Most client codebases are monorepos (Turborepo/Nx/pnpm) |
| **git-worktree-manager** | Parallel work on client engagements |
| **env-secrets-manager** | Every engagement has `.env` hygiene needs |
| **interview-system-designer** | Hiring help for client teams |

Each skill follows the Cure SKILL.md format:
- YAML frontmatter (`name`, `description`, `argument-hint`, `allowed-tools` if read-only, `disable-model-invocation` if sensitive)
- Step 1: Classify (what flavor of the problem)
- Step 2: Gather Context
- Step 3+: Framework / Output

**Why:** Closes the largest skill-breadth gap with alirezarezvani while only including skills that fit consulting work.

**Blast radius:** Low — additive.

**Acceptance:**
- [ ] 8 SKILL.md files in `skills/{name}/SKILL.md`
- [ ] 8 Gemini parity files in `gemini-skills/{name}.skill`
- [ ] Each links to relevant Cure rules where applicable (e.g., mcp-server-builder → web.md and python.md)
- [ ] T3-pattern scripts where executable tooling makes sense (especially: agent-designer, env-secrets-manager, monorepo-navigator)

**Effort:** ~1 day per skill. Parallelizable across subagents — could be 1 calendar day if 4 subagents run in parallel.

---

## T5 — Skill security auditor agent + hook

**Status:** Pending

**Scope:**
- New agent `agents/skill-security-auditor.md` — scans SKILL.md, agent files, and `personas/*.md` for security risks before they enter the repo.
- Detects: command injection patterns, code execution risks (`eval`, `exec`, dynamic imports without validation), data exfiltration, prompt injection patterns, supply chain risks (untrusted URLs, pinned-by-tag dependencies).
- Returns `PASS / WARN / FAIL` with remediation guidance. Uses `audit-report` output style.
- Wire into `hooks/hooks.json` `PreToolUse` for `Write` ops on `skills/**`, `agents/**`, `personas/**`.

**Why:** This repo IS a plugin that gets installed into client environments. Supply-chain hygiene matters — both for our own additions and for any community-contributed skills we adopt.

**Blast radius:** Low. The hook adds latency on writes to those paths only.

**Acceptance:**
- [ ] `agents/skill-security-auditor.md` agent definition
- [ ] Agent uses Read-only tools
- [ ] Documented detection rules with examples
- [ ] PreToolUse hook entry that triggers on `Write` to `skills/**` / `agents/**` / `personas/**`
- [ ] CI step (optional, deferred): run auditor on all skills in `.github/workflows/` on PR

**Effort:** ~2 days.

---

## T6 — Self-improving memory skill

**Status:** Pending

**Scope:**
New skill `skills/self-improving-memory/SKILL.md` codifies Cure's pattern for auto-memory curation, applicable both inside this repo and inside client engagements bootstrapped from this repo.

Captures:
- When to save each memory type (user/feedback/project/reference) — the rules already in our CLAUDE.md auto-memory section
- Pattern detection: when ≥3 similar feedback memories accumulate, propose extracting them as a `feedback` rule or as a new skill
- Memory health checks: identify stale memories, contradictions, duplicates
- How to seed `MEMORY.md` for a new client engagement

**Why:** We already use auto-memory inside this repo. Formalizing the pattern as a skill makes it portable — every client engagement gets the same memory hygiene.

**Blast radius:** Low — additive.

**Acceptance:**
- [ ] `skills/self-improving-memory/SKILL.md` with Cure format
- [ ] Optional script `scripts/memory_health_check.py` (T3 pattern)
- [ ] Bootstrap CLI provisions a starter `MEMORY.md` template
- [ ] Gemini parity version

**Effort:** ~2 days.

---

## T7 — Internal overview doc

**Status:** Pending

**Scope:**
Single `docs/OVERVIEW.md` (or small `docs/` tree if it gets long) — internal-only reference, NOT a public mkdocs site.

Auto-generated content:
- All skills with one-line descriptions, grouped by domain
- All agents with one-line purpose + tool access
- All personas with one-line identity
- All hooks: which event, what they do
- All rules: which globs trigger them
- All output styles
- MCP servers configured
- LSP servers configured
- Bootstrap CLI commands

Generator: `scripts/generate-overview.py` — reads frontmatter from each file, emits the markdown. Re-run after adding new skills/agents.

**Why:** "What does this plugin actually do?" is an annoying question to answer from memory. One file, single source of truth.

**Blast radius:** Low — additive.

**Acceptance:**
- [ ] `scripts/generate-overview.py` (stdlib only, T3 pattern)
- [ ] Generated `docs/OVERVIEW.md`
- [ ] Convention: regenerate on every skill/agent/persona add (mention in CLAUDE.md, optionally enforce via PreCommit hook later)

**Effort:** ~3 days. Could be ~1 day if we keep the generator simple.

---

## Dropped from original eval

- **Marketplace sub-plugin bundles** — repo is internal, no public distribution
- **T8 multi-tool conversion** (Cursor/Codex/Windsurf/etc.) — only worth doing if we actually have client demand for those tools
- **C-suite advisor expansion** (10 advisor roles) — not selling this service
- **Marketing pod expansion** (44 marketing skills) — not selling this service

---

## Wave 1 order of execution (historical)

1. **T2** (personas) — small, additive, fills real gap
2. **T6** (self-improving memory) — small, additive
3. **T3** (scripts pattern + 5 pilots) — establishes convention used by T4, T5, T7
4. **T5** (skill security auditor) — defensive, useful before T4 lands large skill batch
5. **T4** (8 POWERFUL skills) — largest batch, parallelize via subagents
6. **T7** (overview doc) — last, since it consumes everything else
7. **T1** (filesystem reorg) — last, blast radius highest, do once everything else is stable

T1 deliberately last so we only re-shuffle paths once.
