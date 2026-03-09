# Product Engineering Skills

The complete skill library that Cure Consulting Group uses to build apps, platforms, and products. These skills encode our standards, frameworks, and processes — so every project ships with the same level of rigor.

## How It's Organized

```
ProductEngineeringSkills/
├── claude-commands/      # Claude Code custom commands (.md)
├── gemini skills/        # Google Gemini skills (.skill ZIP)
└── README.md
```

## Skill Inventory (24 Skills)

### Product & Strategy
| Skill | What It Does |
|-------|-------------|
| **product-manager** | OKRs, roadmaps, RICE prioritization, feature briefs, north star metrics |
| **product-design** | Apple HIG, Material Design 3, Web design specs, tokens, accessibility-first |
| **market-research** | TAM/SAM/SOM, competitive analysis, ICP definition, pricing research |
| **go-to-market** | GTM plans, launch strategy, channel selection, growth playbooks |
| **product-marketing** | Brand strategy, messaging frameworks, copy, campaigns, portfolio brand profiles |
| **customer-onboarding** | Activation flows, empty states, email sequences, retention metrics |
| **seo-content-engine** | Technical SEO, structured data, content strategy, keyword research |

### Engineering & Architecture
| Skill | What It Does |
|-------|-------------|
| **sdlc** | PRDs, ADRs, RFCs, Epics, Stories, Task specs, test specs — full SDLC artifacts |
| **android-feature-scaffold** | Clean Architecture Android scaffolding (MVI, Compose, Hilt, Kotlin) |
| **ios-architect** | Swift/SwiftUI Clean Architecture, MVVM, structured concurrency |
| **nextjs-feature-scaffold** | App Router, Server/Client components, data fetching, SEO, Tailwind patterns |
| **firebase-architect** | Firestore schema design, security rules, Cloud Functions, data layer |
| **api-architect** | REST/GraphQL design, versioning, auth, rate limiting, error standards |
| **stripe-integration** | Stripe payments + subscriptions via Firebase Cloud Functions, webhook handling |
| **ai-feature-builder** | LLM integration, RAG pipelines, prompt engineering, guardrails, cost management |

### Quality & Security
| Skill | What It Does |
|-------|-------------|
| **feature-audit** | 5-phase post-completion audit with scored gap report and test scaffolds |
| **testing-strategy** | Testing pyramid, platform standards, patterns, coverage rules, CI integration |
| **security-review** | OWASP checklist, auth/data/API/mobile/web security, supply chain, Firebase config |

### Operations & Delivery
| Skill | What It Does |
|-------|-------------|
| **project-manager** | Sprint planning, RACI, risk registers, retrospectives, velocity tracking |
| **ci-cd-pipeline** | GitHub Actions, build/test/deploy, environments, secrets, rollback procedures |
| **analytics-implementation** | Event taxonomy, tracking plans, funnels, dashboards, privacy/consent |

### Business & Finance
| Skill | What It Does |
|-------|-------------|
| **engineering-cost-model** | Project estimates, infrastructure costs, build vs buy, SOW pricing |
| **saas-financial-model** | Unit economics, MRR/ARR modeling, pricing tiers, runway, break-even |
| **legal-doc-scaffold** | Terms of Service, Privacy Policy, SOW, NDA scaffolds (with attorney disclaimer) |

## Using with Claude Code

Copy the `claude-commands/` files into your project's `.claude/commands/` directory:

```bash
cp claude-commands/*.md /path/to/your/project/.claude/commands/
```

Then use them as slash commands:
```
/sdlc — Generate SDLC artifacts
/android-feature-scaffold — Scaffold an Android feature module
/nextjs-feature-scaffold — Scaffold a Next.js feature
/ai-feature-builder — Build a production AI feature
/engineering-cost-model — Estimate project costs
/feature-audit — Audit a completed feature
```

## Using with Google Gemini

Import the `.skill` files from `gemini skills/` into your Gemini workspace. Each `.skill` file is a ZIP archive containing:
- `SKILL.md` — The main skill definition
- `references/` — Supporting documents and templates

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
1. Create both a Claude command (`.md`) and Gemini skill (`.skill`) version
2. Follow the existing format: Step 1 (Classify), Step 2 (Gather Context), Step 3+ (Framework/Output)
3. Include opinionated defaults — these are standards, not suggestions
4. Cross-reference related skills where relevant
