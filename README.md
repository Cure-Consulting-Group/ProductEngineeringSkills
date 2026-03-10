# Product Engineering Skills

The complete skill library that Cure Consulting Group uses to build apps, platforms, and products. These skills encode our standards, frameworks, and processes — so every project ships with the same level of rigor.

**Now available as a Claude Code Plugin** — install once, get auto-updates across all projects.

## How It's Organized

```
ProductEngineeringSkills/
├── .claude-plugin/           # Plugin manifest
│   └── plugin.json
├── skills/                   # 24 skills (new SKILL.md format with frontmatter)
│   ├── sdlc/
│   ├── android-feature-scaffold/
│   ├── ios-architect/
│   ├── ... (24 total)
│   └── legal-doc-scaffold/
├── agents/                   # Custom subagent definitions
│   ├── code-reviewer.md      # Security + quality review agent
│   └── project-bootstrapper.md  # New project setup agent
├── hooks/                    # Automated enforcement
│   └── hooks.json
├── rules/                    # Path-specific coding standards
│   ├── android.md             # Loads for *.kt files
│   ├── ios.md                 # Loads for *.swift files
│   ├── web.md                 # Loads for *.ts/*.tsx files
│   └── firebase.md            # Loads for functions/**
├── settings.json             # Default permission rules
├── claude-commands/           # Legacy format (backwards compat)
├── gemini skills/             # Google Gemini skills (.skill ZIP)
├── CLAUDE.md                  # Project instructions
├── EVALUATION.md              # Full evaluation document
└── README.md
```

## Installation

### As a Claude Code Plugin (Recommended)

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
```

Hooks, agents, rules, and settings are all included automatically.

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

## Skill Inventory (24 Skills)

### Product & Strategy
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **product-manager** | OKRs, roadmaps, RICE prioritization, feature briefs | Yes |
| **product-design** | Apple HIG, Material Design 3, design tokens, accessibility-first | Yes |
| **market-research** | TAM/SAM/SOM, competitive analysis, ICP definition (read-only) | Yes |
| **go-to-market** | GTM plans, launch strategy, channel selection, growth playbooks | Yes |
| **product-marketing** | Brand strategy, messaging frameworks, campaigns | Yes |
| **customer-onboarding** | Activation flows, empty states, email sequences, retention | Yes |
| **seo-content-engine** | Technical SEO, structured data, content strategy | Yes |

### Engineering & Architecture
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

### Quality & Security
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **feature-audit** | 5-phase post-completion audit with scored gap report | Yes (read-only, forked context) |
| **testing-strategy** | Testing pyramid, platform standards, coverage rules | Yes |
| **security-review** | OWASP checklist, auth/data/API/mobile/web security | Yes (read-only, forked context) |

### Operations & Delivery
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **project-manager** | Sprint planning, RACI, risk registers, retrospectives | Yes |
| **ci-cd-pipeline** | GitHub Actions, build/test/deploy, environments, secrets | Yes |
| **analytics-implementation** | Event taxonomy, tracking plans, funnels, dashboards | Yes |

### Business & Finance
| Skill | What It Does | Auto-Invoked? |
|-------|-------------|---------------|
| **engineering-cost-model** | Project estimates, infrastructure costs, build vs buy | Yes (read-only) |
| **saas-financial-model** | Unit economics, MRR/ARR, pricing tiers, break-even | Yes (read-only) |
| **legal-doc-scaffold** | ToS, Privacy Policy, SOW, NDA scaffolds | No (manual only) |

## Hooks (Automated Enforcement)

The plugin includes hooks that run automatically:

| Hook | Event | What It Does |
|------|-------|--------------|
| **Welcome** | SessionStart | Confirms plugin loaded, lists available skills |
| **Platform reminder** | PostToolUse (Edit/Write) | After editing source files, reminds to run audit/testing |
| **Protected files** | PreToolUse (Edit/Write) | Blocks edits to .env and lock files |
| **Dangerous commands** | PreToolUse (Bash) | Blocks force push to main, destructive rm, DROP TABLE |

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
