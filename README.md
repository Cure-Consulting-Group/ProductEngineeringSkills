# Product Engineering Skills

The complete skill library that Cure Consulting Group uses to build apps, platforms, and products. These skills encode our standards, frameworks, and processes — so every project ships with the same level of rigor.

**Now available as a Claude Code Plugin** — install once, get auto-updates across all projects.

## How It's Organized

```
ProductEngineeringSkills/
├── .claude-plugin/           # Plugin manifest
│   └── plugin.json
├── skills/                   # 64 skills (new SKILL.md format with frontmatter)
│   ├── sdlc/
│   ├── android-feature-scaffold/
│   ├── incident-response/     # NEW
│   ├── accessibility-audit/   # NEW
│   ├── performance-review/    # NEW
│   ├── database-architect/    # NEW
│   ├── infrastructure-scaffold/ # NEW
│   ├── project-bootstrap/
│   ├── e2e-testing/
│   ├── test-accounts/
│   ├── uat/
│   ├── compliance-architect/
│   ├── data-migration/
│   ├── feature-flags/
│   ├── release-management/
│   ├── observability/
│   ├── client-handoff/
│   ├── llmops/
│   ├── disaster-recovery/
│   ├── dora-metrics/
│   ├── design-system/
│   ├── client-communication/
│   ├── i18n/
│   ├── notification-architect/
│   ├── offline-first/
│   ├── chaos-engineering/
│   ├── edge-computing/
│   ├── finops/
│   ├── micro-frontends/
│   ├── growth-engineering/
│   ├── green-software/
│   ├── proposal-generator/
│   ├── api-gateway/
│   ├── ... (64 total)
│   └── legal-doc-scaffold/
├── agents/                   # 31 custom subagent definitions
│   ├── code-reviewer.md      # Security + quality review agent
│   ├── project-bootstrapper.md  # New project setup agent
│   ├── test-runner.md        # Execute test suites, report coverage
│   ├── pr-reviewer.md        # Automated PR diff review
│   ├── refactor-assistant.md # Safe refactoring with test validation
│   ├── ci-debugger.md        # Diagnose failed CI/CD runs
│   ├── release-coordinator.md # Version bump, changelog, deploy validation
│   ├── doc-generator.md      # API docs, ADRs, changelogs from code
│   ├── codebase-explainer.md # Onboarding — explain architecture, trace flows
│   ├── migration-validator.md # Database migration safety checks
│   ├── deployment-validator.md # Pre-deployment checklist validation
│   ├── dependency-auditor.md # Vulnerability and outdated package audit
│   ├── api-validator.md      # OpenAPI spec and contract validation
│   ├── product-analyst.md    # Feature adoption, analytics instrumentation
│   ├── ux-researcher.md      # Usability analysis, friction mapping
│   ├── roadmap-strategist.md # RICE scoring, dependency mapping, roadmaps
│   ├── competitive-intel.md  # Feature matrices, positioning, moat analysis
│   ├── content-strategist.md # Editorial calendars, SEO, content briefs
│   ├── campaign-analyst.md   # Attribution, funnel analysis, channel ROI
│   ├── brand-guardian.md     # Voice/tone, visual identity, microcopy audit
│   ├── growth-analyst.md     # Activation, retention, viral mechanics
│   ├── financial-analyst.md  # Revenue forecasts, unit economics, scenarios
│   ├── market-intelligence.md # TAM/SAM/SOM, trends, market timing
│   ├── investor-relations.md # Board updates, KPIs, fundraising narratives
│   ├── contract-reviewer.md  # SOW/contract risk, terms, IP review
│   ├── data-analyst.md       # Schema exploration, queries, data quality
│   ├── metrics-dashboard.md  # KPI definitions, SLOs, dashboard wireframes
│   ├── ab-test-analyst.md    # Experiment design, statistical analysis
│   ├── qa-engineer.md         # Test planning, edge cases, regression, quality gates
│   ├── accessibility-checker.md # WCAG 2.2 automated compliance
│   └── firebase-security-auditor.md # Firestore rules and Functions audit
├── hooks/                    # Multi-layer automated enforcement
│   └── hooks.json            # Command + Prompt + Agent hooks (12 event types)
├── rules/                    # 11 path-specific coding standards
│   ├── android.md             # Loads for *.kt files
│   ├── ios.md                 # Loads for *.swift files
│   ├── web.md                 # Loads for *.ts/*.tsx files
│   ├── firebase.md            # Loads for functions/**
│   ├── python.md              # Loads for *.py files
│   ├── go.md                  # Loads for *.go files
│   ├── rust.md                # Loads for *.rs files
│   ├── sql.md                 # Loads for *.sql, migrations/**
│   ├── docker.md              # Loads for Dockerfile, *.dockerfile
│   ├── terraform.md           # Loads for *.tf, *.tfvars
│   └── cicd.md                # Loads for .github/workflows/**
├── output-styles/            # 9 custom output formatting styles
│   ├── prd/                   # Product docs (PRDs, GTM, research)
│   ├── code-generation/       # Code scaffolds and implementations
│   ├── financial-analysis/    # Cost models, SaaS metrics
│   ├── audit-report/          # Audits, reviews, compliance
│   ├── api-specification/     # OpenAPI specs, endpoint docs
│   ├── architecture-decision/ # ADRs, RFCs, trade-off matrices
│   ├── runbook/               # Incident runbooks, DR procedures
│   ├── test-plan/             # Test plans, coverage reports
│   └── monitoring-alert/      # Alert definitions, thresholds
├── .mcp.json                 # MCP server configs (GitHub, Sentry, Firestore, PostgreSQL)
├── .lsp.json                 # LSP server configs (TypeScript, Python/Pyright)
├── marketplace.json          # Plugin marketplace manifest
├── settings.json             # Default permission rules
├── claude-commands/           # Legacy format (backwards compat, 64 files)
├── gemini skills/             # Google Gemini skills (.skill ZIP)
├── CLAUDE.md                  # Project instructions
├── AGENT-GUIDE.md             # How to structure prompts for agents & skills
├── setup.sh                  # Setup script for Antigravity & other projects
├── EVALUATION.md              # Full evaluation document
└── README.md
```

## Installation

### Via GitHub Package (Recommended)

Install the plugin as an npm package from GitHub Packages. This is the easiest way to keep all your projects up to date.

**1. Authenticate with GitHub Packages** (one-time setup):

```bash
# Create a Personal Access Token (PAT) with read:packages scope at
# https://github.com/settings/tokens, then:
npm login --scope=@cure-consulting-group --registry=https://npm.pkg.github.com
```

Or add to your project's `.npmrc`:
```
@cure-consulting-group:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

**2. Install in your project:**

```bash
npm install @cure-consulting-group/product-engineering-skills
```

The postinstall script automatically:
- Symlinks the package to `~/.claude/plugins/ProductEngineeringSkills`
- Registers the plugin in `~/.claude/settings.json`

All 64 skills, hooks, agents, rules, and output styles are immediately available.

**3. Enable auto-updates with Dependabot** (recommended):

Add `.github/dependabot.yml` to your project (or run `setup.sh` which does this automatically):

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    allow:
      - dependency-name: "@cure-consulting-group/product-engineering-skills"
    labels:
      - "dependencies"
      - "skills-update"
    commit-message:
      prefix: "chore"
      include: "scope"
```

Dependabot will open a PR in your project whenever a new version is published. Merge it and every agent on that project gets the updated skills.

**4. Manual update:**

```bash
npm update @cure-consulting-group/product-engineering-skills
```

### As a Claude Code Plugin (Manual)

```bash
# Load the plugin during a session
claude --plugin-dir /path/to/ProductEngineeringSkills

# Or for development/testing
claude --plugin-dir ./ProductEngineeringSkills
```

Once loaded, all skills are available as namespaced commands:
```
/cure-product-engineering:sdlc
/cure-product-engineering:feature-audit
/cure-product-engineering:android-feature-scaffold
/cure-product-engineering:incident-response
/cure-product-engineering:accessibility-audit
```

Hooks, agents, rules, output styles, and MCP servers are all included automatically.

### Setup Script (Antigravity & Other Projects)

The fastest way to onboard any project:

```bash
# From the target project directory
/path/to/ProductEngineeringSkills/setup.sh

# Or specify the project path
/path/to/ProductEngineeringSkills/setup.sh /path/to/antigravity-app

# Install globally for ALL projects
/path/to/ProductEngineeringSkills/setup.sh --global

# Legacy mode (just copy skills, no hooks/agents)
/path/to/ProductEngineeringSkills/setup.sh --legacy
```

The setup script will:
1. Clone/update the plugin to `~/.claude/plugins/`
2. Detect your project type (Android/iOS/Web/Firebase)
3. Install only the relevant path-specific rules
4. Create a project CLAUDE.md with skill references
5. Add `.claude/settings.local.json` to `.gitignore`

### Via Marketplace

```bash
# Add the Cure Consulting marketplace
claude marketplace add https://github.com/Cure-Consulting-Group/ProductEngineeringSkills/marketplace.json

# Install the plugin
claude plugin install cure-product-engineering
```

### Legacy Method (Copy Commands)

Copy the `claude-commands/` files into your project's `.claude/commands/` directory:

```bash
cp claude-commands/*.md /path/to/your/project/.claude/commands/
```

Then use them as slash commands:
```
/sdlc — Generate SDLC artifacts
/android-feature-scaffold — Scaffold an Android feature module
/feature-audit — Audit a completed feature
```

### Using with Google Gemini

Import the `.skill` files from `gemini skills/` into your Gemini workspace. Each `.skill` file is a ZIP archive containing:
- `SKILL.md` — The main skill definition
- `references/` — Supporting documents and templates

## Skill Inventory (64 Skills)

### Product & Strategy (7)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **product-manager** | OKRs, roadmaps, RICE prioritization, feature briefs | Yes |
| **product-design** | Apple HIG, Material Design 3, design tokens, accessibility-first | Yes |
| **market-research** | TAM/SAM/SOM, competitive analysis, ICP definition (read-only) | Yes |
| **go-to-market** | GTM plans, launch strategy, channel selection, growth playbooks | Yes |
| **product-marketing** | Brand strategy, messaging frameworks, campaigns | Yes |
| **customer-onboarding** | Activation flows, empty states, email sequences, retention | Yes |
| **seo-content-engine** | Technical SEO, structured data, content strategy | Yes |

### Engineering & Architecture (18)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **sdlc** | PRDs, ADRs, RFCs, Epics, Stories, Task specs — full SDLC | Yes |
| **android-feature-scaffold** | Clean Architecture Android scaffolding (MVI, Compose, Hilt) | Yes |
| **ios-architect** | Swift/SwiftUI Clean Architecture, MVVM, structured concurrency | Yes |
| **nextjs-feature-scaffold** | App Router, Server/Client components, Tailwind patterns | Yes |
| **firebase-architect** | Firestore schema, security rules, Cloud Functions | Yes |
| **api-architect** | REST/GraphQL design, versioning, auth, rate limiting | Yes |
| **api-gateway** | API gateway and BFF layers, rate limiting, GraphQL federation | Yes |
| **stripe-integration** | Stripe payments + subscriptions via Firebase Functions | Yes |
| **ai-feature-builder** | LLM integration, RAG pipelines, prompt engineering | Yes |
| **llmops** | LLM operationalization — prompt versioning, eval pipelines, cost optimization, guardrails | Yes |
| **database-architect** | Schema design, migrations, indexing for Firestore/PostgreSQL/SQLite | Yes |
| **data-migration** | ETL pipelines, zero-downtime cutover, validation, rollback strategies | Yes |
| **infrastructure-scaffold** | Cloud infra configs for Firebase, GCP, Vercel, Docker | Yes |
| **edge-computing** | Edge functions, CDN strategies, cache invalidation, edge middleware | Yes |
| **micro-frontends** | Module federation, monorepo management, independent deployments | Yes |
| **offline-first** | Offline-first architecture, sync strategies, conflict resolution, optimistic UI | Yes |
| **i18n** | Internationalization — string extraction, RTL, locale-aware formatting, translation workflows | Yes |
| **notification-architect** | Push (FCM/APNs), in-app messaging, email, preference management | Yes |

### Quality & Security (11)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **feature-audit** | 5-phase post-completion audit with scored gap report | Yes (read-only, forked) |
| **testing-strategy** | Testing pyramid, platform standards, coverage rules | Yes |
| **e2e-testing** | E2E test suites with page objects, visual regression, CI integration | Yes |
| **test-accounts** | Test user personas, seed data scripts, environment credentials | Yes |
| **uat** | UAT plans, acceptance criteria checklists, go/no-go release gates | Yes |
| **security-review** | OWASP checklist, auth/data/API/mobile/web security | Yes (read-only, forked) |
| **compliance-architect** | HIPAA, COPPA, GDPR, PCI compliance frameworks, consent flows, audit trails | Yes |
| **accessibility-audit** | WCAG 2.2 compliance, screen readers, inclusive design | Yes (read-only, forked) |
| **performance-review** | Performance budgets, load testing, optimization strategies | Yes |
| **chaos-engineering** | Resilience testing, failure injection, graceful degradation, game days | Yes |
| **green-software** | Sustainable software practices, carbon-aware computing, energy efficiency | Yes |

### Operations & Delivery (12)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **project-bootstrap** | Bootstrap repo with CLAUDE.md + STATE.md via codebase inspection and developer interview | Yes |
| **project-manager** | Sprint planning, RACI, risk registers, retrospectives | Yes |
| **ci-cd-pipeline** | GitHub Actions, build/test/deploy, environments, secrets | Yes |
| **release-management** | App store submissions, staged rollouts, versioning, ASO, changelogs | Yes |
| **feature-flags** | Progressive rollouts, A/B testing, kill switches, experimentation frameworks | Yes |
| **observability** | Structured logging, distributed tracing, alerting, SLO/SLI, dashboards | Yes |
| **dora-metrics** | DORA and SPACE metrics — deployment frequency, lead time, MTTR, developer experience | Yes |
| **analytics-implementation** | Event taxonomy, tracking plans, funnels, dashboards | Yes |
| **incident-response** | Runbooks, severity classification, post-mortems, escalation | Yes |
| **disaster-recovery** | DR and business continuity — RTO/RPO, backup strategies, failover, DR testing | Yes |
| **growth-engineering** | Activation funnels, referral programs, lifecycle automation, PLG patterns | Yes |
| **design-system** | Design tokens, component libraries, Storybook/Catalog, cross-platform consistency | Yes |

### Business & Finance (7)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **engineering-cost-model** | Project estimates, infrastructure costs, build vs buy | Yes (read-only) |
| **saas-financial-model** | Unit economics, MRR/ARR, pricing tiers, break-even | Yes (read-only) |
| **finops** | Cloud cost optimization, budget alerts, resource right-sizing, FinOps practices | Yes |
| **investor-reporting** | Investor updates, board decks, portfolio financials, cap table, runway modeling | Yes |
| **fundraising-materials** | Pitch decks, data rooms, investor updates, cap table scenarios, fundraising pipeline | Yes |
| **burn-rate-tracker** | Burn rates, runway scenarios, break-even analysis, cash flow projections | Yes |
| **legal-doc-scaffold** | ToS, Privacy Policy, SOW, NDA scaffolds | No (manual only) |

### Portfolio Management (2) — NEW
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **portfolio-registry** | Product portfolio registry — single source of truth for all products, stacks, teams, stages | Yes |
| **technology-radar** | ThoughtWorks-style technology radar — Adopt/Trial/Assess/Hold across the portfolio | Yes |

### Consulting Operations (3)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **client-handoff** | Handoff packages, runbooks, credential transfers, maintenance SLAs, knowledge transfer | Yes |
| **client-communication** | Sprint demo scripts, stakeholder updates, risk escalation, executive summaries | Yes |
| **proposal-generator** | Consulting proposals, SOWs, milestone pricing, engagement structure | No (manual only) |

### Platform Design (4)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **android-design-expert** | Material Design 3 — dynamic color, component tokens, adaptive layouts, motion, Compose patterns | Yes |
| **ios-design-expert** | Apple HIG — SF Symbols, Dynamic Type, navigation patterns, SwiftUI components | Yes |
| **web-design-expert** | Responsive design, CSS architecture, design tokens, container queries, accessibility-first, Tailwind | Yes |
| **stitch-design** | AI-native UI design via Stitch MCP — vibe design, mockups, screen generation, design tokens, component export | Yes |

## Hooks (Multi-Layer Automated Enforcement + Agent Auto-Triggering)

The plugin includes three types of hooks across **12 event types**: `SessionStart`, `PreCompact`, `PostCompact`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `PreToolUse`, `Notification`, `SubagentStart`, `SubagentStop`, `TaskCompleted`, `Stop`.

**New in v4.0**: Hooks now suggest and auto-trigger agents based on context. Every code edit, test run, deployment, and PR action recommends the most relevant agent(s).

### Command Hooks (Deterministic)
| Hook | Event | What It Does | Agent Integration |
|------|-------|--------------|-------------------|
| **Welcome + Agent roster** | SessionStart | Confirms plugin loaded, lists all 31 agents by domain | Displays full agent inventory |
| **Git status** | SessionStart | Reports current branch, uncommitted changes, last commit | — |
| **Dependency check** | SessionStart | Detects outdated packages | Suggests dependency-auditor |
| **Code edit advisor** | PostToolUse (Edit/Write) | Context-aware suggestions based on file type (.kt, .swift, .ts, .sql, .tf, etc.) | Suggests code-reviewer, test-runner, brand-guardian, migration-validator |
| **Command advisor** | PostToolUse (Bash) | Post-action guidance for tests, installs, deploys, PRs, releases | Suggests ci-debugger, dependency-auditor, pr-reviewer, release-coordinator |
| **Failure recovery** | PostToolUseFailure | Diagnoses failure type and suggests fix approach | Auto-suggests ci-debugger, deployment-validator, dependency-auditor |
| **Destructive prompt guard** | UserPromptSubmit | Detects destructive operations in prompts | Blocks and confirms |
| **Protected files** | PreToolUse (Edit/Write) | Blocks edits to .env, lock files, credentials, tfstate | — |
| **Dangerous commands** | PreToolUse (Bash) | Blocks force push, destructive rm, DROP TABLE, prod deploys | — |
| **Context re-injection** | PreCompact | Re-injects all 64 skills, 31 agents, and Cure standards | Full agent roster preserved |
| **Post-compact restore** | PostCompact | Confirms context restored with agent availability | — |
| **Subagent start banner** | SubagentStart | Announces agent with role, standards, and companion agents | Lists companion agents |
| **Subagent completion** | SubagentStop | Suggests follow-up agents (test-runner, code-reviewer, pr-reviewer) | Agent chaining |
| **Task quality check** | TaskCompleted | Validates tests, security, docs, brand consistency | Suggests test-runner, code-reviewer, doc-generator, brand-guardian |

### Prompt Hooks (LLM-Validated)
| Hook | Event | What It Does | Agent Integration |
|------|-------|--------------|-------------------|
| **Code quality gate** | PreToolUse (Edit/Write) | Haiku validates: no secrets, no debug logs, no disabled tests, no `any` types | — |
| **Deployment safety** | PreToolUse (Bash) | Haiku validates: blocks production deployments outside CI/CD | — |
| **Intent classifier** | UserPromptSubmit | Haiku classifies prompt intent and suggests the most relevant agent(s) from all 30 | Maps prompts → agents with confidence scores |

### Agent Hooks (Multi-Turn Verification)
| Hook | Event | What It Does | Agent Integration |
|------|-------|--------------|-------------------|
| **Completion validator** | Stop | Validates: tests for new code, security review for sensitive changes, rollback for migrations, docs for features, brand consistency for UI, analytics for events, API contracts | Suggests specific agents for each gap found |

## MCP Server Integrations

Pre-configured MCP servers in `.mcp.json`:

| Server | Type | What It Does |
|--------|------|--------------|
| **GitHub** | HTTP | PR management, issue tracking, code search |
| **Sentry** | HTTP | Error monitoring, issue tracking, release health |
| **Firestore** | stdio | Direct database queries, schema inspection |
| **PostgreSQL** | stdio | Database queries, schema inspection, migrations |

## LSP Server Integrations

Pre-configured LSP servers in `.lsp.json`:

| Server | Language | What It Provides |
|--------|----------|-----------------|
| **TypeScript** | `.ts`, `.tsx`, `.js` | Type checking, auto-imports, refactoring, go-to-definition |
| **Python (Pyright)** | `*.py` | Static type analysis, import resolution, error diagnostics |

## Output Styles

Custom output formatting for different artifact types:

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

## Custom Agents (30)

### Engineering Agents (14)

| Agent | Purpose | Tools | Auto-Triggered By |
|-------|---------|-------|--------------------|
| **code-reviewer** | Security + quality review against Cure standards | Read-only | Stop hook, SubagentStop |
| **project-bootstrapper** | Set up new projects with correct architecture | Full access | Manual |
| **test-runner** | Execute test suites and report coverage gaps | Read + Bash | PostToolUse (code edits) |
| **pr-reviewer** | Automated PR diff review — security, performance, test gaps | Read + Bash | PostToolUse (gh pr) |
| **refactor-assistant** | Safe refactoring with test validation before/after every change | Full access | Manual |
| **ci-debugger** | Diagnose failed CI/CD runs and suggest targeted fixes | Read + Bash | PostToolUseFailure (build/test) |
| **release-coordinator** | Version bump, changelog, tagging, deploy validation | Read + Edit + Bash | PostToolUse (git tag/gh release) |
| **doc-generator** | API docs, ADRs, changelogs, onboarding guides from code | Read + Bash | TaskCompleted |
| **codebase-explainer** | Onboarding — explains architecture, traces data flows | Read + Bash | Manual |
| **migration-validator** | Validate database migrations for safety and correctness | Read + Bash | PostToolUse (*.sql edits) |
| **deployment-validator** | Pre-deployment checklist and config validation | Read + Bash | PostToolUse (infra edits) |
| **dependency-auditor** | Audit dependencies for vulnerabilities and outdated packages | Read + Bash | PostToolUse (npm/pip install) |
| **api-validator** | OpenAPI spec validation, contract testing, breaking change detection | Read + Bash | Stop hook |
| **qa-engineer** | Test planning, edge case discovery, regression analysis, bug triage, quality gates | Read + Bash | Stop hook, pre-release |

### Product Agents (4)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **product-analyst** | Feature adoption, user journey mapping, analytics instrumentation audit | Read + Bash |
| **ux-researcher** | Usability analysis, friction mapping, form evaluation, cognitive load | Read-only |
| **roadmap-strategist** | RICE scoring, dependency mapping, capacity planning, quarterly roadmaps | Read + Bash |
| **competitive-intel** | Feature comparison matrices, positioning analysis, moat assessment | Read + Web |

### Marketing Agents (4)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **content-strategist** | Editorial calendars, content briefs, SEO strategy, distribution plans | Read + Web |
| **campaign-analyst** | Attribution tracking, funnel analysis, channel ROI, A/B test infra audit | Read + Bash |
| **brand-guardian** | Voice/tone consistency, visual identity, microcopy quality, cross-platform | Read-only |
| **growth-analyst** | Activation funnels, retention mechanics, viral coefficients, experiments | Read + Bash |

### Business & Finance Agents (4)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **financial-analyst** | Revenue forecasts, unit economics, cost structures, scenario analysis | Read + Bash |
| **market-intelligence** | TAM/SAM/SOM, Porter's Five Forces, trend analysis, market timing | Read + Web |
| **investor-relations** | Board updates, KPI dashboards, fundraising narratives, investor materials | Read + Bash |
| **contract-reviewer** | SOW/contract risk analysis, missing clauses, unfavorable terms, IP issues | Read-only |

### Data & Analytics Agents (3)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **data-analyst** | Schema exploration, query generation, data quality assessment, anomalies | Read + Bash |
| **metrics-dashboard** | KPI definitions, SLO/SLI targets, dashboard wireframes, alert thresholds | Read + Bash |
| **ab-test-analyst** | Experiment design, sample size calculation, statistical significance | Read + Bash |

### Security & Compliance Agents (2)

| Agent | Purpose | Tools | Auto-Triggered By |
|-------|---------|-------|--------------------|
| **accessibility-checker** | Automated WCAG 2.2 compliance checking | Read-only | Stop hook |
| **firebase-security-auditor** | Firestore rules and Cloud Functions security audit | Read + Bash | PostToolUse (Firebase edits) |

## Path-Specific Rules

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

## Tech Stack Defaults

These skills assume the following stack (override per-project as needed):

| Layer | Default |
|-------|---------|
| Android | Kotlin, Jetpack Compose, Hilt, MVI, Clean Architecture |
| iOS | Swift, SwiftUI, MVVM, structured concurrency |
| Web | Next.js, TypeScript, Tailwind CSS |
| Backend | Firebase (Firestore, Cloud Functions v2, Auth) |
| API | REST (OpenAPI 3.0), GraphQL where appropriate |
| Payments | Stripe (Android SDK + server-side via Firebase Functions) |
| AI | OpenAI, Gemini, Claude — production integrations with guardrails |
| Analytics | Firebase Analytics, Mixpanel, or PostHog |
| CI/CD | GitHub Actions, Firebase Deploy, Fastlane (mobile) |
| Testing | JUnit5/MockK (Android), XCTest (iOS), Vitest/Playwright (Web) |
| Design | 8pt grid, WCAG AA minimum, platform-native patterns |

## Contributing

When adding a new skill:
1. Create the skill in `skills/{name}/SKILL.md` with proper YAML frontmatter
2. Also create a legacy version in `claude-commands/{name}.md`
3. Create a Gemini version in `gemini skills/{name}.skill`
4. Follow the existing format: Step 1 (Classify), Step 2 (Gather Context), Step 3+ (Framework/Output)
5. Include opinionated defaults — these are standards, not suggestions
6. Cross-reference related skills where relevant
7. Bump the version in `.claude-plugin/plugin.json`
