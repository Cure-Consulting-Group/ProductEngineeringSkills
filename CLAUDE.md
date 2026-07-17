# ProductEngineeringSkills — Cure Consulting Group

This is the central skill library for all Cure Consulting Group projects. It is distributed as a Claude Code plugin.

## What This Repo Is

A **Claude Code plugin** containing 81 production-grade skills (organized into 7 domain folders), 39 custom agents, 4 personas (cross-domain engagement archetypes), multi-layer hooks (command + prompt) with a Stop-hook quality gate and skill security guard, MCP server configs, LSP server configs, output styles, and path-specific rules. Other projects install this plugin to get consistent standards.

## Repository Structure

```
.claude-plugin/plugin.json     — Plugin manifest (name, version, metadata)
skills/{domain}/{name}/SKILL.md — 81 skills, organized by domain folder
                                 Domains: engineering (39), platform (11), product (10),
                                 business (7), finance (4), marketing (5), security (4), legal (1)
skills/{domain}/{name}/scripts/ — Optional bundled stdlib Python scripts (zero pip)
agents/*.md                    — 39 specialized subagents with tool/skill bindings
personas/*.md                  — Cross-domain engagement archetypes (tech-lead, product-lead, engagement-pm, solo-consultant)
hooks/hooks.json               — Multi-layer hooks (command + prompt) across 9 event types incl. Stop quality gate, ConfigChange audit, skill security guard
rules/*.md                     — 11 path-specific coding standards
output-styles/*/output-style.md — 9 custom output styles (PRD, code, financial, audit, API spec, ADR, runbook, test plan, alerts)
.mcp.json.example              — Opt-in MCP server template (GitHub, Sentry, Firestore, PostgreSQL); see docs/MCP-SETUP.md. NOT auto-loaded — needs per-project secrets.
.lsp.json                      — LSP server configurations (TypeScript, Python/Pyright)
.claude-plugin/marketplace.json — Private plugin-marketplace manifest (name: "cure"); see docs/DISTRIBUTION.md
settings.json                  — Default permission rules (35 deny rules)
claude-commands/*.md           — Legacy command format (backwards compat)
gemini skills/*.skill          — Google Gemini skill packages (flat, .skill zip files)
CLAUDE.md                      — Project instructions (Claude)
GEMINI.md                      — Project instructions (Gemini CLI)
AGENT-GUIDE.md                 — How to structure prompts for agents & skills
docs/OVERVIEW.md               — Auto-generated overview (regenerate via scripts/generate-overview.py)
docs/SCRIPTS_CONVENTION.md     — Convention for bundled Python scripts in skills
scripts/generate-overview.py   — Regenerates docs/OVERVIEW.md from frontmatter
scripts/verify-skill-scripts.sh — Smoke-tests every bundled skill script via --help
BACKLOG.md                     — Internal improvement backlog (not for distribution)
```


## Development Rules

- When adding a new skill, create it in `skills/{domain}/{name}/SKILL.md` with proper YAML frontmatter. Domain is one of: engineering, platform, product, business, finance, marketing, security, legal. If unsure, run `python3 scripts/generate-overview.py` after — it categorizes by name patterns and will surface the inferred domain.
- Domain folders are an authoring convention only — the Claude Code plugin loader scans one level deep (`<dir>/<name>/SKILL.md`), so every `skills/{domain}` directory MUST be listed in the `skills` array in `.claude-plugin/plugin.json` or none of its skills load in consuming projects. When you create a new domain folder, add it to that array in the same commit (`audit-library.py` fails if you forget). `claude-commands/` is deliberately NOT mapped as the plugin `commands` dir — the skills already register `/cure-product-engineering:<name>`, and mapping the stubs too would register 81 duplicate names; it exists only for the npm/legacy vendoring path.
- Every skill must have: `name`, `description`, and `argument-hint` in frontmatter. Fold the trigger ("Use when…") into `description` itself (or `when_to_use`) — it drives auto-discovery. Keep `description` + `when_to_use` combined under 1,536 chars (the skill-listing truncates past that). Skill `name` must be lowercase/hyphens, ≤64 chars, and **must not contain "claude" or "anthropic"** (reserved words — the harness rejects them).
- To make a skill genuinely read-only, set `disallowed-tools` (e.g. `Write Edit Bash`). NOTE: `allowed-tools` does **not** restrict anything — it only grants no-prompt permission for the listed tools; every other tool stays callable. Do not rely on `allowed-tools` as a sandbox.
- Destructive or sensitive skills should set `disable-model-invocation: true`. NOTE: this also makes a skill un-loopable — `/loop` scheduled fires only run skills Claude may auto-invoke (v2.1.196+). Never add it to a skill with a Recurring Mode section; to hide a loopable skill from the `/` menu use `user-invocable: false` instead.
- Keep SKILL.md bodies under 500 lines; push long reference material into sibling files (one level deep) per progressive disclosure.
- Do NOT add a `version:` field to skills — it is not read by the harness. Library version lives only in `.claude-plugin/plugin.json`.
- After any change to skills/agents/personas, run `python3 scripts/audit-library.py` (must stay green) and `python3 scripts/sync-metadata.py --write` (keeps all docs/counts in sync).
- Keep the legacy `claude-commands/` format in sync for backwards compatibility
- Create both Claude and Gemini versions of each skill (Gemini files are flat zips in `gemini skills/`, regenerated via `generate-gemini-skills.sh`)
- Follow the existing format: Step 1 (Classify), Step 2 (Gather Context), Step 3+ (Framework/Output)
- When adding a new persona, create it in `personas/{name}.md` with frontmatter (`name`, `description`, `type: persona`). Personas reference only existing skills/agents — never invent names. Match Cure's voice: terse, opinionated, concrete with numbers, no marketing fluff.
- A skill MAY ship `skills/{domain}/{name}/scripts/*.py` — Python stdlib only, zero pip installs. Every script must support `--help` and ideally `--json`. See `docs/SCRIPTS_CONVENTION.md` for the full convention.
- After adding/modifying skills, agents, or personas: run `python3 scripts/generate-overview.py` to regenerate `docs/OVERVIEW.md`.
- Library upkeep follows `docs/MAINTENANCE.md`: monthly `/loop` + liveness check, quarterly platform re-evaluation as a new BACKLOG wave (research → verify → tickets → execute). Never bypass `scripts/release.sh`.

## Token Economy (Wave 2 conventions)

The library's biggest token cost is fixed overhead multiplied across every session and agent spawn in every consuming project. Rules:

- **Trigger text is budgeted.** Combined `description` + `when_to_use` per skill: target ≤350 chars (audit warns above 350, flags at 500). All 80 skills compete for the session skill-listing budget (~1% of model context by default); skill-heavy consuming projects can raise `skillListingBudgetFraction` — see `docs/CONSUMING-PROJECTS.md`.
- **Agents preload at most ~300 lines of skills.** Anything more becomes an on-demand body reference ("invoke `/x` when needed"). The audit flags preloads >800 lines.
- **Don't pin `model:` on agents without a reason.** Agents inherit the session model; a blanket pin silently downgrades them. Spend via `effort:` instead — `high` only where judgment lives (reviewers, auditors, validators).
- **Heavy analysis skills fork.** Use `context: fork` so their exploration doesn't bloat the main conversation.
- **Hooks stay quiet and non-blocking.** No echo-per-tool-call hooks; no network I/O in SessionStart hooks (a slow registry blocks every session and every loop iteration in every consuming project); prompt-type hooks only on Stop/PostToolUseFailure with timeout ≤30s and fail-open (CI-enforced). The Stop gate never blocks automated runs (/loop iterations, routines) and never blocks twice in one turn.

## Versioning

Current version: **7.4.5**

Bump the version in `.claude-plugin/plugin.json` when making changes:
- Patch (x.x.x): Fix typos, clarify wording
- Minor (x.x.0): Add new skills, add hooks, add rules
- Major (x.0.0): Breaking changes to skill interfaces or structure

## Custom Agents (39)

> Canonical, always-current agent and skill inventory is generated in `docs/OVERVIEW.md` (run `python3 scripts/generate-overview.py`). The tables below are a curated summary — if they disagree with OVERVIEW.md, OVERVIEW.md wins.

### Engineering Agents (15)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **code-reviewer** | Security + quality review against Cure standards | Read-only |
| **project-bootstrapper** | Set up new projects with correct architecture | Full access |
| **test-runner** | Execute test suites and report coverage gaps | Read + Bash |
| **pr-reviewer** | Automated PR review — diffs, security, performance, test coverage | Read + Bash |
| **refactor-assistant** | Safe refactoring with test validation before/after every change | Full access |
| **ci-debugger** | Diagnose failed CI/CD runs, suggest targeted fixes | Read + Bash |
| **release-coordinator** | Orchestrate version bump, changelog, tag, deploy validation | Read + Edit + Bash |
| **doc-generator** | Generate API docs, ADRs, changelogs, onboarding guides from code | Read + Bash |
| **codebase-explainer** | Onboarding agent — explains architecture, traces data flows | Read + Bash |
| **migration-validator** | Validate database migrations for safety and correctness | Read + Bash |
| **deployment-validator** | Pre-deployment checklist and config validation | Read + Bash |
| **dependency-auditor** | Audit dependencies for vulnerabilities and outdated packages | Read + Bash |
| **api-validator** | OpenAPI spec validation, contract testing, breaking change detection | Read + Bash |
| **qa-engineer** | Test planning, edge case discovery, regression analysis, bug triage, quality gates | Read + Bash |

### Product Agents (4)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **product-analyst** | Feature adoption, user journey mapping, analytics instrumentation audit | Read + Bash |
| **ux-researcher** | Usability analysis, friction mapping, form evaluation, cognitive load assessment | Read-only |
| **roadmap-strategist** | RICE scoring, dependency mapping, capacity planning, quarterly roadmaps | Read + Bash |
| **competitive-intel** | Feature comparison matrices, positioning analysis, moat assessment | Read + Web |

### Marketing Agents (4)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **content-strategist** | Editorial calendars, content briefs, SEO strategy, distribution plans | Read + Web |
| **campaign-analyst** | Attribution tracking, funnel analysis, channel ROI, A/B test infrastructure audit | Read + Bash |
| **brand-guardian** | Voice/tone consistency, visual identity audit, microcopy quality, cross-platform consistency | Read-only |
| **growth-analyst** | Activation funnels, retention mechanics, viral coefficients, growth experiment infrastructure | Read + Bash |

### Business & Finance Agents (4)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **financial-analyst** | Revenue forecasts, unit economics, cost structures, scenario analysis from code | Read + Bash |
| **market-intelligence** | TAM/SAM/SOM, Porter's Five Forces, trend analysis, market timing | Read + Web |
| **investor-relations** | Board updates, KPI dashboards, fundraising narratives, investor materials | Read + Bash |
| **contract-reviewer** | SOW/contract risk analysis, missing clauses, unfavorable terms, IP issues | Read-only |

### Data & Analytics Agents (3)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **data-analyst** | Schema exploration, query generation, data quality assessment, anomaly detection | Read + Bash |
| **metrics-dashboard** | KPI definitions, SLO/SLI targets, dashboard wireframes, alert thresholds | Read + Bash |
| **ab-test-analyst** | Experiment design, sample size calculation, statistical significance, result interpretation | Read + Bash |

### Security & Compliance Agents (3)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **accessibility-checker** | Automated WCAG 2.2 compliance checking | Read-only |
| **firebase-security-auditor** | Firestore rules and Cloud Functions security audit | Read + Bash |
| **skill-security-auditor** | Audit new SKILL.md, agent, and persona files for command injection, code execution, exfiltration, prompt injection, supply chain risks, privilege escalation, and secret leakage. Returns PASS/WARN/FAIL. Invoke before merging changes under skills/, agents/, or personas/ (automatic hook wiring: BACKLOG T11). | Read-only |

## Personas (4)

Personas are cross-domain identities. Skills answer *how*, agents answer *what*, personas answer *who is thinking*. Each persona ships a curated skill loadout, agent loadout, decision frameworks, and voice — designed to slot into a specific Cure consulting engagement role.

| Persona | Engagement Role | Loads |
|---------|----------------|-------|
| **cure-tech-lead** | Engineering lead — architecture, code quality, mentoring | Engineering skills + review/QA agents |
| **cure-product-lead** | Product/PM lead — discovery, roadmap, stakeholder management | Product skills + UX/analytics agents |
| **cure-engagement-pm** | Program/project manager — sprint cadence, scope, handoff | Project + business skills + financial/PM agents |
| **cure-solo-consultant** | Single consultant on small engagements — cross-domain | Bootstrap + pragmatic cross-domain mix |

## Path-Specific Rules (11)

Rules load automatically when editing matching files:

| Rule | Triggers On | Standards |
|------|------------|-----------|
| `android.md` | `*.kt`, `*.java` | Clean Architecture, MVI, Compose, Hilt |
| `ios.md` | `*.swift` | MVVM/TCA, SwiftUI, structured concurrency |
| `web.md` | `*.ts`, `*.tsx`, `*.js` | Next.js App Router, Server Components, Tailwind |
| `firebase.md` | `functions/**`, `*.rules` | Cloud Functions v2, security rules, typed collections |
| `python.md` | `*.py` | PEP 8, type hints, FastAPI/Django conventions |
| `go.md` | `*.go` | Effective Go, error handling, project layout standards |
| `rust.md` | `*.rs` | Ownership patterns, error handling with `thiserror`/`anyhow`, async with Tokio |
| `sql.md` | `*.sql`, `migrations/**` | Migration safety, index strategy, query optimization |
| `docker.md` | `Dockerfile`, `*.dockerfile` | Multi-stage builds, non-root users, layer caching |
| `terraform.md` | `*.tf`, `*.tfvars` | Module structure, remote state, tagging conventions |
| `cicd.md` | `.github/workflows/**`, `*.yml` (CI) | GitHub Actions best practices, secrets handling, job matrix |

## Output Styles (9)

| Style | Used By | Key Rules |
|-------|---------|-----------|
| **prd** | Product skills (PRDs, GTM, research) | Numbered sections, decision matrices, executive summaries |
| **code-generation** | Engineering skills (scaffolds) | File tree first, dependency order, complete runnable code |
| **financial-analysis** | Business skills (costs, models) | ASCII tables, explicit assumptions, sensitivity analysis |
| **audit-report** | Quality skills (audits, reviews) | Severity scoring, checklists, remediation with effort estimates |
| **api-specification** | API design skills | OpenAPI 3.0 blocks, endpoint tables, request/response examples |
| **architecture-decision** | ADR and RFC skills | Context/decision/consequences format, trade-off matrices |
| **runbook** | Incident response, disaster recovery | Numbered steps, command blocks, decision trees, escalation paths |
| **test-plan** | Testing strategy, QA skills | Coverage tables, test case templates, pass/fail criteria |
| **monitoring-alert** | Observability, incident response | Alert definition tables, threshold rationale, runbook links |

## LSP Servers

Pre-configured LSP servers in `.lsp.json`:

| Server | Language | What It Provides |
|--------|----------|-----------------|
| **TypeScript** | `.ts`, `.tsx`, `.js` | Type checking, auto-imports, refactoring, go-to-definition |
| **Python (Pyright)** | `*.py` | Static type analysis, import resolution, error diagnostics |

<!-- README.md and AGENT-GUIDE.md are available as user documentation but not loaded into runtime context to save ~7,400 tokens per session -->
