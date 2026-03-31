# ProductEngineeringSkills — Cure Consulting Group

This is the central skill library for all Cure Consulting Group projects. It is distributed as a Claude Code plugin.

## What This Repo Is

A **Claude Code plugin** containing 64 production-grade skills, 31 custom agents (engineering, product, marketing, business, data, security), multi-layer hooks with agent auto-triggering (command + prompt + agent), MCP server configs, LSP server configs, output styles, and path-specific rules. Other projects install this plugin to get consistent standards.

## Repository Structure

```
.claude-plugin/plugin.json    — Plugin manifest (name, version, metadata)
skills/*/SKILL.md             — 64 skills with frontmatter (new format)
agents/*.md                   — 30 custom subagent definitions
hooks/hooks.json              — Multi-layer hooks (command, prompt, agent) across 12 event types
rules/*.md                    — 11 path-specific coding standards
output-styles/*/output-style.md — 9 custom output styles (PRD, code, financial, audit, API spec, ADR, runbook, test plan, alerts)
.mcp.json                     — MCP server configurations (GitHub, Sentry, Firestore, PostgreSQL)
.lsp.json                     — LSP server configurations (TypeScript, Python/Pyright)
marketplace.json              — Plugin marketplace manifest for distribution
settings.json                 — Default permission rules (35 deny rules)
claude-commands/*.md           — Legacy command format (backwards compat)
gemini skills/*.skill          — Google Gemini skill packages
```

## Development Rules

- When adding a new skill, create it in `skills/{name}/SKILL.md` with proper YAML frontmatter
- Every skill must have: `name`, `description`, and `argument-hint` in frontmatter
- Read-only skills (audits, analysis) should set `allowed-tools: ["Read", "Grep", "Glob"]`
- Destructive or sensitive skills should set `disable-model-invocation: true`
- Keep the legacy `claude-commands/` format in sync for backwards compatibility
- Create both Claude and Gemini versions of each skill
- Follow the existing format: Step 1 (Classify), Step 2 (Gather Context), Step 3+ (Framework/Output)

## Versioning

Current version: **4.0.0**

Bump the version in `.claude-plugin/plugin.json` when making changes:
- Patch (x.x.x): Fix typos, clarify wording
- Minor (x.x.0): Add new skills, add hooks, add rules
- Major (x.0.0): Breaking changes to skill interfaces or structure

## Custom Agents (30)

### Engineering Agents (14)

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

### Security & Compliance Agents (2)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **accessibility-checker** | Automated WCAG 2.2 compliance checking | Read-only |
| **firebase-security-auditor** | Firestore rules and Cloud Functions security audit | Read + Bash |

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

@README.md
@AGENT-GUIDE.md
