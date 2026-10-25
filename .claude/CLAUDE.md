# ProductEngineeringSkills — Cure Consulting Group

This is the central skill library for all Cure Consulting Group projects. It is distributed as a Claude Code plugin.

## What This Repo Is

A **Claude Code plugin** containing 106 production-grade skills (organized into 9 domain folders), 41 custom agents, 4 personas (cross-domain engagement archetypes), command hooks (deterministic Stop check, Bash/edit safety guard, skill security guard), LSP server configs, an opt-in MCP template, and path-specific rules. Other projects install this plugin to get consistent standards.

**What a plugin install actually delivers** (Wave 7): skills, agents, hooks and LSP config. It cannot deliver permissions (plugin `settings.json` applies only `agent` and `subagentStatusLine`), rules, or personas; settings and rules reach a project only through the npm postinstall or cure-infra-bootstrap, and `hooks/cure_guard.py` is the safety layer every consumer gets. This dev file lives at `.claude/CLAUDE.md` because a plugin-root CLAUDE.md is never loaded and fails `claude plugin validate --strict`.

## Machine Setup (every machine, every release)

Codex and Antigravity hold snapshots of this library. On any machine with this repo, run
`scripts/install-runtimes.sh` once after checkout and again after every release — details and
the done criteria are in `STATE.md`. If `STATE.md`'s "Machines verified" row doesn't list this
machine, offer to run it.

## Repository Structure

```
.claude-plugin/plugin.json     — Plugin manifest (name, version, metadata)
skills/{domain}/{name}/SKILL.md — 106 skills, organized by domain folder
                                 Domains: engineering (40), platform (11), product (11), business (14),
                                 finance (4), marketing (6), security (4), legal (4), tax (12)
skills/{domain}/{name}/scripts/ — Optional bundled stdlib Python scripts (zero pip)
agents/*.md                    — 41 specialized subagents with tool/skill bindings
personas/*.md                  — Cross-domain engagement archetypes (tech-lead, product-lead, engagement-pm, solo-consultant); documentation, nothing loads them
hooks/hooks.json               — Command hooks across 6 event types (no prompt hooks, no model calls): deterministic Stop check, post-compaction standards re-injection, Bash/edit safety guard, skill security guard, failure triage
rules/*.md                     — 11 path-specific coding standards (`paths:` frontmatter; delivered by npm/bootstrap, not the plugin)
.mcp.json.example              — Opt-in MCP server template (GitHub, Sentry, Firestore, PostgreSQL); see docs/MCP-SETUP.md. NOT auto-loaded — needs per-project secrets.
.lsp.json                      — LSP server configurations (TypeScript, Python/Pyright)
.claude-plugin/marketplace.json — Private plugin-marketplace manifest (name: "cure"); see docs/DISTRIBUTION.md
settings.json                  — Default permission rules (deny list; copied by npm/bootstrap — a plugin can't ship permissions)
claude-commands/*.md           — Legacy command format (backwards compat)
.claude/CLAUDE.md              — Project instructions (Claude) for developing this repo
GEMINI.md                      — Project instructions (Gemini CLI)
AGENT-GUIDE.md                 — How to structure prompts for agents & skills
docs/OVERVIEW.md               — Auto-generated overview (regenerate via scripts/generate-overview.py)
docs/SCRIPTS_CONVENTION.md     — Convention for bundled Python scripts in skills
scripts/generate-overview.py   — Regenerates docs/OVERVIEW.md from frontmatter
scripts/verify-skill-scripts.sh — Smoke-tests every bundled skill script via --help
scripts/export-antigravity.py  — Builds the flat Antigravity plugin (dist/antigravity/cure, gitignored); --install for agy
scripts/antigravity-smoke.py   — Zero-model agy listing check (skips when agy is absent)
scripts/install-runtimes.sh    — Per-machine Codex + Antigravity install/refresh + verify (see STATE.md)
STATE.md                       — Machine setup steps and current library state
hooks/cure_guard.py            — Stdin-JSON hook guard (edit/bash/skill-content/telemetry); tests: hooks/test_cure_guard.py
docs/AUTHORING.md              — How a skill is written for Claude Code, Codex, and Antigravity (Wave 5 standard)
BACKLOG.md                     — Internal improvement backlog (not for distribution)
tri-lane/                      — cure-tri-lane plugin (Claude architect + Codex + Antigravity lanes); own version, own tests
mods/*/                        — Claude Code mods (TypeScript function hooks, in-process) in the cure marketplace; each versioned on its own, tested with `claude plugin test` in CI
```


## Development Rules

- When adding a new skill, create it in `skills/{domain}/{name}/SKILL.md` with proper YAML frontmatter. Domain is one of: engineering, platform, product, business, finance, marketing, security, legal, tax. If unsure, run `python3 scripts/generate-overview.py` after — it categorizes by name patterns and will surface the inferred domain.
- Domain folders are an authoring convention only — the Claude Code plugin loader scans one level deep (`<dir>/<name>/SKILL.md`), so every `skills/{domain}` directory MUST be listed in the `skills` array in `.claude-plugin/plugin.json` or none of its skills load in consuming projects. When you create a new domain folder, add it to that array in the same commit (`audit-library.py` fails if you forget). `claude-commands/` is deliberately NOT mapped as the plugin `commands` dir — the skills already register `/cure-product-engineering:<name>`, and mapping the stubs too would register 81 duplicate names; it exists only for the npm/legacy vendoring path.
- Every skill must have: `name`, `description`, and `argument-hint` in frontmatter. Fold the trigger ("Use when…") into `description` itself (or `when_to_use`) — it drives auto-discovery. Keep `description` + `when_to_use` combined under 1,536 chars (the skill-listing truncates past that). Skill `name` must be lowercase/hyphens, ≤64 chars, and **must not contain "claude" or "anthropic"** (reserved words — the harness rejects them).
- To make a skill genuinely read-only, set `disallowed-tools` (e.g. `Write Edit Bash`). NOTE: `allowed-tools` does **not** restrict anything — it only grants no-prompt permission for the listed tools; every other tool stays callable. Do not rely on `allowed-tools` as a sandbox.
- Destructive or sensitive skills should set `disable-model-invocation: true`. NOTE: this also makes a skill un-loopable — `/loop` scheduled fires only run skills Claude may auto-invoke (v2.1.196+). Never add it to a skill with a Recurring Mode section; to hide a loopable skill from the `/` menu use `user-invocable: false` instead.
- Keep SKILL.md bodies under 500 lines; push long reference material into sibling files (one level deep) per progressive disclosure.
- **Escape literal dollars in skill bodies.** The harness substitutes bare `$0`–`$9` (and `$ARGUMENTS`) with the user's invocation arguments at load time — `$0.15` becomes `<first-arg>.15` silently. Write `\$0.15`, `\$1`; braced `${...}`, `$$`, and `$UPPERCASE` are safe. Enforced by the audit (T37); regression fixture: evals/tasks/t16-substitution-integrity. Found live by the statledger canary (F-1, 2026-08-14).
- **No inline `!`cmd`` injection unless `allowed-tools` pre-approves Bash.** Injection runs through the Bash permission check at skill-load time; where Bash isn't pre-approved (headless, CI, routines) the whole skill fails to load (Wave 5: 69 skills were silently broken this way). Write context commands as plain `` `cmd` `` "run these first" bullets instead. Enforced by the audit (CRIT).
- Do NOT add a `version:` field to skills — it is not read by the harness. Library version lives only in `.claude-plugin/plugin.json`.
- **Wave 7 hard gates (audit-library.py):** a description's "Use when/for…" trigger must end by char 100 (bare "when" doesn't count); never pre-approve unrestricted `Bash` together with WebFetch/WebSearch (scope it: `Bash(ls:*)`); rules use `paths:`, never `globs:`; no retired model IDs (claude-3*, gpt-4o*, gemini-2.x…) in shipped files unless the line carries `retired-id-ok`; an agent with `memory:` (which grants Write/Edit) must not be documented as read-only.
- After any change to skills/agents/personas, run `python3 scripts/audit-library.py` (must stay green) and `python3 scripts/sync-metadata.py --write` (keeps all docs/counts in sync).
- Keep the legacy `claude-commands/` format in sync for backwards compatibility
- Follow the existing format: Step 1 (Classify), Step 2 (Gather Context), Step 3+ (Framework/Output)
- When adding a new persona, create it in `personas/{name}.md` with frontmatter (`name`, `description`, `type: persona`). Personas reference only existing skills/agents — never invent names. Match Cure's voice: terse, opinionated, concrete with numbers, no marketing fluff.
- A skill MAY ship `skills/{domain}/{name}/scripts/*.py` — Python stdlib only, zero pip installs. Every script must support `--help` and ideally `--json`. See `docs/SCRIPTS_CONVENTION.md` for the full convention.
- After adding/modifying skills, agents, or personas: run `python3 scripts/generate-overview.py` to regenerate `docs/OVERVIEW.md`.
- Library upkeep follows `docs/MAINTENANCE.md`: monthly `/loop` + liveness check, quarterly platform re-evaluation as a new BACKLOG wave (research → verify → tickets → execute). Never bypass `scripts/release.sh`.

## Token Economy (Wave 2 conventions)

The library's biggest token cost is fixed overhead multiplied across every session and agent spawn in every consuming project. Rules:

- **Trigger text is budgeted.** Combined `description` + `when_to_use` per skill: target ≤350 chars (audit warns above 350, flags at 500). All 106 skills compete for the session skill-listing budget (~1% of model context by default); skill-heavy consuming projects can raise `skillListingBudgetFraction` — see `docs/CONSUMING-PROJECTS.md`.
- **Agents preload at most ~300 lines of skills.** Anything more becomes an on-demand body reference ("invoke `/x` when needed"). The audit flags preloads >800 lines.
- **Don't pin `model:` or `effort:` without measured evidence.** Agents and skills inherit the session model and effort; a blanket `model:` pin silently downgrades them. Opus 5.5 defaults to `medium` effort, which matches Opus 5 at `high`, and thinks more per turn at a given level. The Wave 5 sweep (2026-09-23) found `high` bought no recall on reviewer tasks at equal cost, so the 14 carried-over `effort: high` pins were removed. Add one back only with an eval showing the gain.
- **Heavy analysis skills fork.** Use `context: fork` so their exploration doesn't bloat the main conversation.
- **Hooks stay quiet and non-blocking.** No echo-per-tool-call hooks; no network I/O in SessionStart hooks (a slow registry blocks every session and every loop iteration in every consuming project); prompt-type hooks only on Stop/PostToolUseFailure with timeout ≤30s and fail-open (CI-enforced). The Stop gate never blocks automated runs (/loop iterations, routines) and never blocks twice in one turn.

## Versioning

Current version: **7.13.0**

Bump the version in `.claude-plugin/plugin.json` when making changes:
- Patch (x.x.x): Fix typos, clarify wording
- Minor (x.x.0): Add new skills, add hooks, add rules
- Major (x.0.0): Breaking changes to skill interfaces or structure

## Custom Agents (41)

> Canonical, always-current agent and skill inventory is generated in `docs/OVERVIEW.md` (run `python3 scripts/generate-overview.py`). The tables below are a curated summary — if they disagree with OVERVIEW.md, OVERVIEW.md wins.

**Tools column = effective tools** (Wave 7, T84). `memory:` grants Read/Write/Edit, so only agents without memory and with `disallowedTools: Write, Edit` are read-only. "Read + Bash" agents can't use Write/Edit, but Bash can still write; their prompts forbid it.

### Engineering Agents (15)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **code-reviewer** | Findings on named files or uncommitted work; no merge verdict | Read-only |
| **pr-reviewer** | Branch vs its base; the only merge verdict | Read + Bash (no Write/Edit) |
| **qa-engineer** | Test planning, edge cases, regression scope, bug triage; recommends, deployment-validator decides | Read + Bash (no Write/Edit) |
| **test-runner** | Execute test suites and report coverage gaps | Read + Bash (no Write/Edit) |
| **codebase-explainer** | Onboarding agent — explains architecture, traces data flows | Read + Bash (no Write/Edit) |
| **migration-validator** | Validate database migrations for safety and correctness | Read + Bash (no Write/Edit) |
| **deployment-validator** | Pre-deployment GO/NO-GO and config validation | Read + Bash (no Write/Edit) |
| **dependency-auditor** | Audit dependencies for vulnerabilities and outdated packages | Read + Bash (no Write/Edit) |
| **api-validator** | OpenAPI spec validation, contract testing, breaking change detection | Read + Bash (no Write/Edit) |
| **project-bootstrapper** | Set up new projects with correct architecture | Full access |
| **refactor-assistant** | Safe refactoring in a worktree, tests before/after every change | Full access |
| **release-coordinator** | Executes a release (bump, changelog, tag); release-management owns policy | Read + Bash + Write/Edit |
| **ci-debugger** | Diagnose failed CI/CD runs, suggest targeted fixes | Read + Bash + Write/Edit (memory) |
| **doc-generator** | Generate API docs, ADRs, changelogs, onboarding guides from code | Read + Bash + Write/Edit (memory) |
| **system-architect** | Architecture reviews, RFCs, and ADRs with explicit trade-offs | Read + Bash + Write/Edit (memory) |

### Product Agents (4)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **product-analyst** | Feature adoption, user journey mapping, analytics instrumentation audit | Read + Bash + Write/Edit (memory) |
| **ux-researcher** | Usability analysis, friction mapping, form evaluation, cognitive load assessment | Read-only |
| **roadmap-strategist** | RICE scoring, dependency mapping, capacity planning, quarterly roadmaps | Read + Bash + Write/Edit (memory) |
| **competitive-intel** | Feature comparison matrices, positioning analysis, moat assessment | Read + Bash + Web + Write/Edit (memory) |

### Marketing Agents (5)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **content-strategist** | Editorial calendars, content briefs, SEO strategy, distribution plans | Read + Bash + Web + Write/Edit (memory) |
| **campaign-analyst** | Attribution tracking, funnel analysis, channel ROI, A/B test infrastructure audit | Read + Bash + Write/Edit (memory) |
| **brand-guardian** | Voice/tone consistency, visual identity audit, microcopy quality | Read-only |
| **growth-analyst** | Activation funnels, retention mechanics, viral coefficients, growth experiments | Read + Bash + Write/Edit (memory) |
| **technical-content-strategist** | Engineering work as plain-language posts and visuals for business readers | Read + Web + Write/Edit (memory) |

### Business & Finance Agents (10)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **financial-analyst** | Revenue forecasts, unit economics, cost structures, scenario analysis from code | Read + Bash + Write/Edit (memory) |
| **ops-finance** | Invoices, 1099 tracking, month-end close, filing inventory | Read + Bash + Write/Edit (local memory) |
| **market-intelligence** | TAM/SAM/SOM, Porter's Five Forces, trend analysis, market timing | Read + Bash + Web + Write/Edit (memory) |
| **investor-relations** | Board updates, KPI dashboards, fundraising narratives, investor materials | Read + Bash + Write/Edit (memory) |
| **equity-analyst** | Public-equity research: filings, earnings, catalysts, valuation thesis | Read + Bash + WebFetch + Write/Edit (memory) |
| **investment-banker** | M&A and capital markets: comps, DCF, LBO, accretion/dilution | Read + Bash + Write/Edit (memory) |
| **private-equity-analyst** | Screening, diligence, LBO returns, IC memos | Read + Bash + Write/Edit (memory) |
| **contract-reviewer** | SOW/contract risk analysis, missing clauses, unfavorable terms, IP issues | Read-only |
| **tax-analyst** | Tax workpapers, return review, estimates, audit risk — drafts for CPA review, never files | Read + Bash (no Write/Edit) |
| **legal-analyst** | NY-first legal research memos (IRAC) with every citation verified or flagged — drafts for attorney review, never advises | Read + Bash (no Write/Edit) |

### Data & Analytics Agents (3)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **data-analyst** | Schema exploration, query generation, data quality assessment, anomaly detection | Read + Bash + Write/Edit (memory) |
| **metrics-dashboard** | KPI definitions, SLO/SLI targets, dashboard wireframes, alert thresholds | Read + Bash + Write/Edit (memory) |
| **ab-test-analyst** | Experiment design, sample size calculation, statistical significance, result interpretation | Read + Bash + Write/Edit (memory) |

### Security & Compliance Agents (4)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **accessibility-checker** | Automated WCAG 2.2 compliance checking | Read-only |
| **firebase-security-auditor** | Firestore rules and Cloud Functions security audit | Read + Bash (no Write/Edit) |
| **legal-compliance** | QSBS, FERPA, NCAA, trademark, and entity-compliance risk flags — not legal advice | Read-only |
| **skill-security-auditor** | Audit new SKILL.md, agent, and persona files for command injection, code execution, exfiltration, prompt injection, supply chain risks, privilege escalation, and secret leakage. Returns PASS/WARN/FAIL. Invoke before merging changes under skills/, agents/, or personas/. | Read-only |

## Personas (4) — documentation

Personas are cross-domain identities. Skills answer *how*, agents answer *what*, personas answer *who is thinking*. **Nothing loads them** (Wave 7, D7): a plugin can't ship them, and no skill or agent reads them. They are reference documents a consultant reads, or pastes into a session, when taking an engagement role.

| Persona | Engagement Role | Loads |
|---------|----------------|-------|
| **cure-tech-lead** | Engineering lead — architecture, code quality, mentoring | Engineering skills + review/QA agents |
| **cure-product-lead** | Product/PM lead — discovery, roadmap, stakeholder management | Product skills + UX/analytics agents |
| **cure-engagement-pm** | Program/project manager — sprint cadence, scope, handoff | Project + business skills + financial/PM agents |
| **cure-solo-consultant** | Single consultant on small engagements — cross-domain | Bootstrap + pragmatic cross-domain mix |

## Path-Specific Rules (11)

Rules are **not** a plugin component: they reach a consuming project only through the npm postinstall or cure-infra-bootstrap, which copy them into `.claude/rules/`. Claude Code reads only the `paths:` field, as a YAML list or a comma-separated string; a rule without `paths:` loads in every session. The audit fails on `globs:`.

| Rule | Triggers On | Standards |
|------|------------|-----------|
| `android.md` | `*.kt`, `*.kts`, `*.java`, `libs.versions.toml` | Clean Architecture, MVI, Compose, Hilt, type-safe navigation |
| `ios.md` | `*.swift` | Swift 6 concurrency, SwiftUI + `@Observable`, Swift Testing |
| `web.md` | `*.tsx`, `*.jsx`, `app/`, `components/`, `lib/`, `proxy.ts`, `middleware.ts`, `next.config.*` | Next.js App Router, Server Components, Tailwind v4 |
| `firebase.md` | `functions/**`, `firestore*`, `*.rules`, `firebase.json` | Cloud Functions v2, security rules, typed collections |
| `python.md` | `*.py`, `pyproject.toml` | uv, type hints, ruff, FastAPI/Django conventions |
| `go.md` | `*.go`, `go.mod` | Effective Go, error handling, project layout |
| `rust.md` | `*.rs`, `Cargo.toml` | Edition 2024, `thiserror`/`anyhow`, Tokio |
| `sql.md` | `*.sql`, `migrations/**` | Migration safety, index strategy, identity/UUIDv7 keys |
| `docker.md` | `Dockerfile*`, `*.dockerfile`, `compose*.yaml`, `.dockerignore` | Multi-stage builds, non-root users, layer caching |
| `terraform.md` | `*.tf`, `*.tfvars`, `terraform/**`, `.terraform.lock.hcl` | Module structure, `use_lockfile` state locking, no `-target` in prod |
| `cicd.md` | `.github/workflows/**`, `.github/actions/**` | SHA-pinned actions, least-privilege `permissions:`, secrets handling |

Output styles were retired in Wave 7 (D4): nothing referenced them, and selecting one dropped Claude Code's coding instructions. Each skill owns its output contract.

## LSP Servers

Pre-configured LSP servers in `.lsp.json`:

| Server | Language | What It Provides |
|--------|----------|-----------------|
| **TypeScript** | `.ts`, `.tsx`, `.js` | Type checking, auto-imports, refactoring, go-to-definition |
| **Python (Pyright)** | `*.py` | Static type analysis, import resolution, error diagnostics |

<!-- README.md and AGENT-GUIDE.md are available as user documentation but not loaded into runtime context to save ~7,400 tokens per session -->
