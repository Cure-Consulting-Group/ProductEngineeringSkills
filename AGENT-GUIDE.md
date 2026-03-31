# Agent & Skill Usage Guide

How to structure prompts to get maximum value from the 64 skills and 30 agents in the Cure Consulting Group plugin.

## How It Works

You don't need to memorize agents or skills. The intent classifier hook and agent descriptions handle routing automatically. But knowing the patterns makes you significantly more effective.

- **Skills** = templates, frameworks, structured outputs (PRDs, ADRs, test plans, scaffolds)
- **Agents** = execution against your actual code (review, test, diagnose, analyze)
- **Hooks** = automatic reminders that suggest the right agent after every action

## Core Workflow Patterns

### 1. Building a New Feature (Full Lifecycle)

Start broad, then narrow. One prompt can trigger a full chain:

```
Build a subscription management screen for our Android app.
Users need to view their plan, upgrade/downgrade, and cancel.
```

What happens automatically:
- Intent classifier suggests `android-feature-scaffold` skill
- Code edits trigger hooks that suggest `code-reviewer`, `test-runner`
- Stop hook validates tests, security review, docs

To get more out of it, layer in specific agents:

```
Build the subscription management screen for Android.

Before coding:
- Run @agent-product-analyst to check if we have analytics for subscription flows
- Run @agent-ux-researcher to evaluate our current upgrade flow for friction

Then scaffold with /android-feature-scaffold, including Stripe integration.

After coding:
- Run @agent-test-runner to verify coverage
- Run @agent-pr-reviewer when ready for merge
```

### 2. Fixing a Bug

Lead with the symptom, not the solution:

```
Users on Android are seeing a blank screen after upgrading their subscription.
The crash is in SubscriptionViewModel. Diagnose and fix.
```

If CI is also broken:

```
CI is failing on the payments module. Diagnose with @agent-ci-debugger,
fix the issue, then run @agent-test-runner to verify.
```

### 3. Refactoring Safely

```
The PaymentRepository has grown to 400+ lines. Refactor it using
@agent-refactor-assistant — ensure tests pass before and after every change.
```

### 4. Pre-Release Validation

```
We're cutting v2.3.0 this week. Run the full release checklist:
- @agent-release-coordinator for version bump and changelog
- @agent-deployment-validator for pre-deploy checks
- @agent-dependency-auditor for vulnerability scan
```

## Prompt Structures That Maximize Agent/Skill Usage

### Pattern A: "Audit Then Build"

```
First run /security-review on our auth module.
Then fix every Critical and High finding.
```

### Pattern B: "Multi-Agent Analysis"

```
I need a full product health check:
- @agent-product-analyst — analytics coverage
- @agent-growth-analyst — retention and activation
- @agent-metrics-dashboard — do we have the right KPIs tracked?
- @agent-ux-researcher — friction in our core flows

Synthesize findings into priorities.
```

### Pattern C: "Skill for Framework, Agent for Execution"

Skills give you the framework/template. Agents execute against your code.

```
Run /database-architect to design the schema for our new messaging feature.
Then @agent-migration-validator to verify the migrations are safe.
```

```
Run /testing-strategy to define our test plan.
Then @agent-test-runner to check current coverage against the plan.
```

### Pattern D: "Business Context First"

```
We're pitching Series A next month. Generate:
- @agent-financial-analyst — unit economics and 12-month forecast
- @agent-market-intelligence — TAM/SAM/SOM for our vertical
- @agent-investor-relations — board update with KPIs
- @agent-competitive-intel — feature matrix vs top 3 competitors
```

### Pattern E: "End-to-End Feature with Quality Gates"

The most powerful pattern — a single prompt that chains the full lifecycle:

```
Build [feature description].

Quality gates:
1. /sdlc — generate the PRD and ADR first, get my approval
2. /[platform]-feature-scaffold — scaffold the implementation
3. @agent-code-reviewer — review before I look at it
4. @agent-test-runner — verify 80%+ coverage
5. @agent-pr-reviewer — final check before PR
```

## Quick Reference: What to Invoke When

| You're doing... | Use this |
|-----------------|----------|
| Starting a new feature | `/sdlc` then `/[platform]-feature-scaffold` |
| Reviewing code | `@agent-pr-reviewer` or `@agent-code-reviewer` |
| Tests failing | `@agent-ci-debugger` then `@agent-test-runner` |
| Preparing a release | `@agent-release-coordinator` |
| Analyzing product health | `@agent-product-analyst` + `@agent-growth-analyst` |
| Writing a proposal | `/proposal-generator` |
| Checking security | `/security-review` or `@agent-firebase-security-auditor` |
| Onboarding a new dev | `@agent-codebase-explainer` |
| Building a dashboard | `@agent-metrics-dashboard` |
| Designing an API | `/api-architect` then `@agent-api-validator` |
| Fundraising prep | `@agent-investor-relations` + `@agent-financial-analyst` |
| Content planning | `@agent-content-strategist` |
| Reviewing a contract | `@agent-contract-reviewer` |
| Refactoring safely | `@agent-refactor-assistant` |
| New database tables | `/database-architect` then `@agent-migration-validator` |
| QA before shipping | `@agent-qa-engineer` |
| Finding edge cases | `@agent-qa-engineer` |
| Running A/B tests | `@agent-ab-test-analyst` |
| Competitive analysis | `@agent-competitive-intel` + `@agent-market-intelligence` |
| Brand consistency | `@agent-brand-guardian` |
| Campaign performance | `@agent-campaign-analyst` |
| Roadmap planning | `@agent-roadmap-strategist` |
| UX friction audit | `@agent-ux-researcher` |
| Data exploration | `@agent-data-analyst` |
| Cost analysis | `@agent-financial-analyst` + `/finops` |
| Client handoff | `/client-handoff` + `@agent-doc-generator` |
| Incident response | `/incident-response` + `@agent-metrics-dashboard` |

## Agent Chaining Recipes

These are multi-agent sequences for common complex workflows.

### New Feature (Full Stack)

```
1. /sdlc — PRD, user stories, acceptance criteria
2. /database-architect — schema design
3. /api-architect — endpoint design
4. /[platform]-feature-scaffold — implementation
5. @agent-test-runner — coverage check
6. @agent-code-reviewer — quality review
7. @agent-pr-reviewer — merge readiness
```

### Production Incident

```
1. /incident-response — severity classification, runbook
2. @agent-ci-debugger — diagnose the failure
3. @agent-metrics-dashboard — verify monitoring gaps
4. @agent-doc-generator — post-mortem documentation
```

### Quarterly Planning

```
1. @agent-roadmap-strategist — RICE-scored backlog
2. @agent-product-analyst — feature adoption data
3. @agent-growth-analyst — retention and activation analysis
4. @agent-financial-analyst — cost and revenue projections
5. @agent-competitive-intel — market positioning check
```

### Pre-Launch Checklist

```
1. @agent-deployment-validator — environment and config readiness
2. @agent-dependency-auditor — vulnerability scan
3. /security-review — OWASP checklist
4. /accessibility-audit — WCAG compliance
5. /performance-review — load testing and budgets
6. @agent-brand-guardian — copy and visual consistency
7. @agent-release-coordinator — version, changelog, tag, deploy
```

### Investor Meeting Prep

```
1. @agent-financial-analyst — unit economics, scenarios
2. @agent-market-intelligence — TAM/SAM/SOM, trends
3. @agent-competitive-intel — positioning matrix
4. @agent-investor-relations — deck, KPIs, narrative
5. @agent-growth-analyst — traction metrics
```

### New Developer Onboarding

```
1. @agent-codebase-explainer — architecture overview, key flows
2. @agent-doc-generator — verify docs are current
3. @agent-metrics-dashboard — show what we monitor
4. /testing-strategy — explain our test approach
```

## Pro Tips

1. **Plain English works.** The intent classifier maps your prompt to agents automatically. You don't have to @-mention anything — just describe what you need.

2. **Chain agents when order matters.** "Run A, then B, then C" gives you predictable sequencing.

3. **Skills = templates. Agents = execution.** Use skills when you want a structured output. Use agents when you want something analyzed or validated against your actual code.

4. **Hooks do the reminding.** After every code edit, the PostToolUse hook tells you which agents are relevant. After every task completion, it checks quality. The system prompts you automatically.

5. **Combine domains for richer output.** The most powerful prompts cross domains: engineering + product, marketing + data, business + competitive. The agents are designed to complement each other.

6. **Be specific about quality gates.** When you tell Claude "run @agent-test-runner and only proceed if coverage is above 80%", it will enforce that gate.

## All 31 Agents by Domain

### Engineering (14)
| Agent | What It Does |
|-------|-------------|
| `code-reviewer` | Security + quality review against Cure standards |
| `project-bootstrapper` | Set up new projects with correct architecture |
| `test-runner` | Execute test suites and report coverage gaps |
| `pr-reviewer` | Automated PR diff review — security, performance, tests |
| `refactor-assistant` | Safe refactoring with test validation loop |
| `ci-debugger` | Diagnose failed CI/CD runs, suggest fixes |
| `release-coordinator` | Version bump, changelog, tag, deploy validation |
| `doc-generator` | API docs, ADRs, changelogs from code |
| `codebase-explainer` | Onboarding — explain architecture, trace flows |
| `migration-validator` | Database migration safety and rollback checks |
| `deployment-validator` | Pre-deployment checklist and config validation |
| `dependency-auditor` | Vulnerability, license, and outdated package audit |
| `api-validator` | OpenAPI spec validation and contract testing |
| `qa-engineer` | Test planning, edge cases, regression, bug triage, quality gates |

### Product (4)
| Agent | What It Does |
|-------|-------------|
| `product-analyst` | Feature adoption, analytics instrumentation audit |
| `ux-researcher` | Usability analysis, friction mapping, form evaluation |
| `roadmap-strategist` | RICE scoring, dependency mapping, capacity planning |
| `competitive-intel` | Feature matrices, positioning, moat assessment |

### Marketing (4)
| Agent | What It Does |
|-------|-------------|
| `content-strategist` | Editorial calendars, content briefs, SEO strategy |
| `campaign-analyst` | Attribution, funnel analysis, channel ROI |
| `brand-guardian` | Voice/tone, visual identity, microcopy consistency |
| `growth-analyst` | Activation, retention, viral mechanics, experiments |

### Business & Finance (4)
| Agent | What It Does |
|-------|-------------|
| `financial-analyst` | Revenue forecasts, unit economics, scenarios |
| `market-intelligence` | TAM/SAM/SOM, Porter's Five Forces, trends |
| `investor-relations` | Board updates, KPIs, fundraising narratives |
| `contract-reviewer` | SOW/contract risk, terms, IP review |

### Data & Analytics (3)
| Agent | What It Does |
|-------|-------------|
| `data-analyst` | Schema exploration, queries, data quality |
| `metrics-dashboard` | KPI definitions, SLOs, dashboard wireframes |
| `ab-test-analyst` | Experiment design, statistical significance |

### Security & Compliance (2)
| Agent | What It Does |
|-------|-------------|
| `accessibility-checker` | WCAG 2.2 automated compliance |
| `firebase-security-auditor` | Firestore rules and Functions security |

## All 64 Skills by Domain

### Product & Strategy (7)
`product-manager` · `product-design` · `market-research` · `go-to-market` · `product-marketing` · `customer-onboarding` · `seo-content-engine`

### Engineering & Architecture (18)
`sdlc` · `android-feature-scaffold` · `ios-architect` · `nextjs-feature-scaffold` · `firebase-architect` · `api-architect` · `api-gateway` · `stripe-integration` · `ai-feature-builder` · `llmops` · `database-architect` · `data-migration` · `infrastructure-scaffold` · `edge-computing` · `micro-frontends` · `offline-first` · `i18n` · `notification-architect`

### Quality & Security (11)
`feature-audit` · `testing-strategy` · `e2e-testing` · `test-accounts` · `uat` · `security-review` · `compliance-architect` · `accessibility-audit` · `performance-review` · `chaos-engineering` · `green-software`

### Operations & Delivery (12)
`project-bootstrap` · `project-manager` · `ci-cd-pipeline` · `release-management` · `feature-flags` · `observability` · `dora-metrics` · `analytics-implementation` · `incident-response` · `disaster-recovery` · `growth-engineering` · `design-system`

### Business & Finance (7)
`engineering-cost-model` · `saas-financial-model` · `finops` · `investor-reporting` · `fundraising-materials` · `burn-rate-tracker` · `legal-doc-scaffold`

### Portfolio Management (2)
`portfolio-registry` · `technology-radar`

### Consulting Operations (3)
`client-handoff` · `client-communication` · `proposal-generator`

### Platform Design (4)
`android-design-expert` · `ios-design-expert` · `web-design-expert` · `stitch-design`
