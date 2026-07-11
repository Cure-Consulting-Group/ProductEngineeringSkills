# BACKLOG

Internal improvement backlog, organized in waves. Wave 1 (2026-04-29, resolved) came from a comparative evaluation against `alirezarezvani/claude-skills`. Wave 2 (2026-07-11, active) aligns the library with Claude Code's continuous-execution layer (loops, routines, workflows, hooks).

This repo is **internal-only** — not for public distribution, no marketplace. Tickets reflect that constraint.

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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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

**Status:** Pending
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
