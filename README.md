# Product Engineering Skills

The complete skill library that Cure Consulting Group uses to build apps, platforms, and products. These skills encode our standards, frameworks, and processes — so every project ships with the same level of rigor.

**Now available as a Claude Code Plugin** — install once, get auto-updates across all projects.

## How It's Organized

```
ProductEngineeringSkills/
├── .claude-plugin/           # Plugin manifest
│   └── plugin.json
├── skills/                   # 36 skills (new SKILL.md format with frontmatter)
│   ├── sdlc/
│   ├── android-feature-scaffold/
│   ├── incident-response/     # NEW
│   ├── accessibility-audit/   # NEW
│   ├── performance-review/    # NEW
│   ├── database-architect/    # NEW
│   ├── infrastructure-scaffold/ # NEW
│   ├── project-bootstrap/     # NEW
│   ├── e2e-testing/           # NEW
│   ├── test-accounts/         # NEW
│   ├── uat/                   # NEW
│   ├── ... (36 total)
│   └── legal-doc-scaffold/
├── agents/                   # Custom subagent definitions
│   ├── code-reviewer.md      # Security + quality review agent
│   └── project-bootstrapper.md  # New project setup agent
├── hooks/                    # Multi-layer automated enforcement
│   └── hooks.json            # Command + Prompt + Agent hooks
├── rules/                    # Path-specific coding standards
│   ├── android.md             # Loads for *.kt files
│   ├── ios.md                 # Loads for *.swift files
│   ├── web.md                 # Loads for *.ts/*.tsx files
│   └── firebase.md            # Loads for functions/**
├── output-styles/            # Custom output formatting
│   ├── prd/                   # Product docs (PRDs, GTM, research)
│   ├── code-generation/       # Code scaffolds and implementations
│   ├── financial-analysis/    # Cost models, SaaS metrics
│   └── audit-report/          # Audits, reviews, compliance
├── .mcp.json                 # MCP server configs (GitHub, Sentry, Firestore, Postgres)
├── marketplace.json          # Plugin marketplace manifest
├── settings.json             # Default permission rules
├── claude-commands/           # Legacy format (backwards compat, 29 files)
├── gemini skills/             # Google Gemini skills (.skill ZIP)
├── CLAUDE.md                  # Project instructions
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

All 36 skills, hooks, agents, rules, and output styles are immediately available.

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

## Skill Inventory (36 Skills)

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

### Engineering & Architecture (10)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **sdlc** | PRDs, ADRs, RFCs, Epics, Stories, Task specs — full SDLC | Yes |
| **android-feature-scaffold** | Clean Architecture Android scaffolding (MVI, Compose, Hilt) | Yes |
| **ios-architect** | Swift/SwiftUI Clean Architecture, MVVM, structured concurrency | Yes |
| **nextjs-feature-scaffold** | App Router, Server/Client components, Tailwind patterns | Yes |
| **firebase-architect** | Firestore schema, security rules, Cloud Functions | Yes |
| **api-architect** | REST/GraphQL design, versioning, auth, rate limiting | Yes |
| **stripe-integration** | Stripe payments + subscriptions via Firebase Functions | Yes |
| **ai-feature-builder** | LLM integration, RAG pipelines, prompt engineering | Yes |
| **database-architect** | Schema design, migrations, indexing for Firestore/PostgreSQL/SQLite | Yes |
| **infrastructure-scaffold** | Cloud infra configs for Firebase, GCP, Vercel, Docker | Yes |

### Quality & Security (8)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **feature-audit** | 5-phase post-completion audit with scored gap report | Yes (read-only, forked) |
| **testing-strategy** | Testing pyramid, platform standards, coverage rules | Yes |
| **e2e-testing** | E2E test suites with page objects, visual regression, CI integration | Yes |
| **test-accounts** | Test user personas, seed data scripts, environment credentials | Yes |
| **uat** | UAT plans, acceptance criteria checklists, go/no-go release gates | Yes |
| **security-review** | OWASP checklist, auth/data/API/mobile/web security | Yes (read-only, forked) |
| **accessibility-audit** | WCAG 2.2 compliance, screen readers, inclusive design | Yes (read-only, forked) |
| **performance-review** | Performance budgets, load testing, optimization strategies | Yes |

### Operations & Delivery (5)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **project-bootstrap** | Bootstrap repo with CLAUDE.md + STATE.md via codebase inspection and developer interview | Yes |
| **project-manager** | Sprint planning, RACI, risk registers, retrospectives | Yes |
| **ci-cd-pipeline** | GitHub Actions, build/test/deploy, environments, secrets | Yes |
| **analytics-implementation** | Event taxonomy, tracking plans, funnels, dashboards | Yes |
| **incident-response** | Runbooks, severity classification, post-mortems, escalation | Yes |

### Business & Finance (3)
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **engineering-cost-model** | Project estimates, infrastructure costs, build vs buy | Yes (read-only) |
| **saas-financial-model** | Unit economics, MRR/ARR, pricing tiers, break-even | Yes (read-only) |
| **legal-doc-scaffold** | ToS, Privacy Policy, SOW, NDA scaffolds | No (manual only) |

## Hooks (Multi-Layer Automated Enforcement)

The plugin includes three types of hooks:

### Command Hooks (Deterministic)
| Hook | Event | What It Does |
|------|-------|--------------|
| **Welcome** | SessionStart | Confirms plugin loaded, lists available skills |
| **Git status** | SessionStart | Reports current branch, uncommitted changes, last commit |
| **Platform reminder** | PostToolUse (Edit/Write) | After editing source files, reminds to run audit/testing |
| **Protected files** | PreToolUse (Edit/Write) | Blocks edits to .env, lock files, and credential files |
| **Dangerous commands** | PreToolUse (Bash) | Blocks force push to main, destructive rm, DROP TABLE, prod deploys |
| **Context re-injection** | PreCompact | Re-injects Cure standards and skill list after context compaction |

### Prompt Hooks (LLM-Validated)
| Hook | Event | What It Does |
|------|-------|--------------|
| **Code quality gate** | PreToolUse (Edit/Write) | Haiku validates: no hardcoded secrets, no debug logs, no disabled tests, no `any` types |
| **Deployment safety** | PreToolUse (Bash) | Haiku validates: blocks production deployments outside CI/CD |

### Agent Hooks (Multi-Turn Verification)
| Hook | Event | What It Does |
|------|-------|--------------|
| **Completion validator** | Stop | Agent checks if tests were written for new code and security reviews were run for sensitive changes |

## MCP Server Integrations

Pre-configured MCP servers in `.mcp.json`:

| Server | Type | What It Does |
|--------|------|--------------|
| **GitHub** | HTTP | PR management, issue tracking, code search |
| **Sentry** | HTTP | Error monitoring, issue tracking, release health |
| **Firestore** | stdio | Direct database queries, schema inspection |
| **PostgreSQL** | stdio | Database queries, schema inspection, migrations |

## Output Styles

Custom output formatting for different artifact types:

| Style | Used By | Key Rules |
|-------|---------|-----------|
| **prd** | Product skills (PRDs, GTM, research) | Numbered sections, decision matrices, executive summaries |
| **code-generation** | Engineering skills (scaffolds) | File tree first, dependency order, complete runnable code |
| **financial-analysis** | Business skills (costs, models) | ASCII tables, explicit assumptions, sensitivity analysis |
| **audit-report** | Quality skills (audits, reviews) | Severity scoring, checklists, remediation with effort estimates |

## Custom Agents

| Agent | Purpose | Tools |
|-------|---------|-------|
| **code-reviewer** | Security + quality review against Cure standards | Read-only |
| **project-bootstrapper** | Set up new projects with correct architecture | Full access |

## Path-Specific Rules

Rules load automatically when editing matching files:

| Rule | Triggers On | Standards |
|------|------------|-----------|
| `android.md` | `*.kt`, `*.java` | Clean Architecture, MVI, Compose, Hilt |
| `ios.md` | `*.swift` | MVVM/TCA, SwiftUI, structured concurrency |
| `web.md` | `*.ts`, `*.tsx`, `*.js` | Next.js App Router, Server Components, Tailwind |
| `firebase.md` | `functions/**`, `*.rules` | Cloud Functions v2, security rules, typed collections |

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
