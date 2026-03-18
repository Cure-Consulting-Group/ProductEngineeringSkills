---
name: technology-radar
description: "Generate and maintain a ThoughtWorks-style technology radar — track Adopt/Trial/Assess/Hold decisions across the portfolio with rationale and migration plans"
argument-hint: "[portfolio-or-domain]"
context: fork
---

# Technology Radar

Generate and maintain a ThoughtWorks-style technology radar for multi-product portfolios. Use when evaluating technology choices, conducting quarterly reviews, planning migrations away from deprecated technologies, or auditing technology debt across products. Designed for Cure Consulting Group's portfolio: Vendly, Autograph, The Initiated, Antigravity, and TwntyHoops.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Radar Task

| Type | When to Use | Output |
|------|------------|--------|
| Full Radar Generation | First-time setup, annual reset, new portfolio | Complete TECHNOLOGY_RADAR.md with all quadrants and rings |
| Single Technology Assessment | Evaluating one technology for adoption or retirement | Radar entry with rationale, affected products, migration plan if Hold |
| Quarterly Radar Review | First week of each quarter | Ring movement proposals, new entries, divergence report |
| Migration Planning | Moving from Hold technology to Adopt replacement | Migration plan with effort estimates, product-by-product timeline |
| Technology Debt Audit | Sprint planning, budget season, technical health check | Inventory of Hold technologies still in production with priority rankings |

## Automated Technology Discovery

Before building radar, scan all projects:
1. Glob for dependency files: `**/package.json`, `**/build.gradle*`, `**/Podfile`, `**/Cargo.toml`, `**/requirements.txt`, `**/go.mod`
2. Read each file and extract all dependencies with versions
3. Count usage across projects (e.g., "React: 5 projects, Vue: 1 project")
4. Use WebSearch to check: GitHub stars trends, npm download trends, security advisories
5. Auto-suggest ring placements based on adoption breadth and industry trends

## Artifact Generation (Required)

Generate using Write:
1. **Radar document**: `docs/technology-radar.md` — full radar with all four rings
2. **Migration tracker**: `docs/tech-migrations.md` — planned moves between rings with effort estimates

## Step 2: Gather Context

1. **Portfolio scope** -- which products are included in this radar (all five, a subset, a single product)?
2. **Dependency scan** -- read package.json, build.gradle.kts, Podfile, Gemfile, requirements.txt, go.mod, Cargo.toml, docker-compose.yml, and CI/CD configs across all repos to build an accurate inventory of what is actually in use.
3. **Technology satisfaction** -- for each major technology, what is the team's experience? Are there pain points, performance issues, hiring challenges, or maintenance burden?
4. **Recent evaluations** -- has the team recently trialed or assessed any new technologies? What were the results?
5. **Business constraints** -- are there budget, timeline, or staffing constraints that affect migration decisions?
6. **Prior radar** -- does a previous TECHNOLOGY_RADAR.md exist? If so, read it to track ring movements over time.

### Dependency Scanning Checklist

```
Scan these files in every product repo:

JavaScript/TypeScript:
  - package.json (dependencies + devDependencies)
  - package-lock.json / yarn.lock / pnpm-lock.yaml (exact versions)
  - tsconfig.json (TypeScript configuration)
  - next.config.js / next.config.ts (Next.js version and plugins)
  - tailwind.config.js (Tailwind version and plugins)
  - playwright.config.ts / vitest.config.ts / jest.config.ts (test framework)

Android:
  - build.gradle.kts (root + app + feature modules)
  - libs.versions.toml / gradle/libs.versions.toml (version catalog)
  - settings.gradle.kts (included modules)
  - gradle.properties (Kotlin/AGP versions)

iOS:
  - Package.swift (Swift Package Manager)
  - Podfile + Podfile.lock (CocoaPods)
  - .xcodeproj / .xcworkspace (Xcode version, deployment target)
  - project.pbxproj (Swift version, build settings)

Infrastructure:
  - firebase.json + .firebaserc (Firebase services)
  - docker-compose.yml / Dockerfile (container stack)
  - vercel.json (Vercel configuration)
  - .github/workflows/*.yml (CI/CD tools and versions)
  - terraform/*.tf / pulumi/*.ts (infrastructure as code)

General:
  - .tool-versions / .node-version / .ruby-version (runtime versions)
  - .env.example (service integrations — API keys reveal which services)
  - README.md (often lists tech stack)
```

## Step 3: Radar Structure -- Quadrants and Rings

### Four Quadrants (ThoughtWorks Model)

```
┌─────────────────────────────────┬─────────────────────────────────┐
│                                 │                                 │
│   LANGUAGES & FRAMEWORKS        │   TOOLS                         │
│                                 │                                 │
│   Programming languages,        │   Build tools, CI/CD, IDEs,     │
│   UI frameworks, server         │   testing frameworks, linters,  │
│   frameworks, SDKs              │   deployment tools, CLIs        │
│                                 │                                 │
├─────────────────────────────────┼─────────────────────────────────┤
│                                 │                                 │
│   PLATFORMS                     │   TECHNIQUES                    │
│                                 │                                 │
│   Cloud providers, BaaS,        │   Architecture patterns,        │
│   payment processors, AI APIs,  │   development practices,        │
│   databases, hosting            │   processes, methodologies      │
│                                 │                                 │
└─────────────────────────────────┴─────────────────────────────────┘
```

### Four Rings -- Decision Criteria

```
ADOPT (innermost ring):
  Definition:  Default choice for all new work. Team is proficient. Battle-tested
               in production across multiple products.
  Criteria:
    - Used in 2+ products successfully
    - Team has deep expertise (can debug, optimize, contribute upstream)
    - Strong ecosystem (docs, community, hiring pool)
    - No known blocking issues or planned deprecations
    - Performance characteristics are well understood
  Action:      Use without discussion. Include in project templates.

TRIAL (second ring):
  Definition:  Promising technology being evaluated in one product. Not yet proven
               at portfolio scale. Worth investing time to learn.
  Criteria:
    - Used in exactly 1 product or a dedicated proof-of-concept
    - Solves a real problem better than current Adopt alternative
    - Team has at least one champion with working knowledge
    - Acceptable risk profile for the trial product
    - Clear success criteria and timeline for promotion or demotion
  Action:      Use in designated trial product only. Report findings quarterly.

ASSESS (third ring):
  Definition:  Technology worth researching. Do NOT put in production. Track for
               next quarter to decide whether to trial.
  Criteria:
    - Industry buzz or strategic potential
    - No production usage yet
    - Assigned researcher to track developments
    - Will be re-evaluated next quarter for Trial or removal
  Action:      Read docs, attend talks, build throwaway prototypes. No production code.

HOLD (outermost ring):
  Definition:  Stop adopting this technology. Migrate existing usage when practical.
               Document why it was moved to Hold.
  Criteria:
    - Superseded by better Adopt/Trial alternative
    - Maintenance burden exceeds value
    - Security concerns, deprecation, or end-of-life
    - Hiring difficulty or shrinking community
    - Performance or scalability limits reached
  Action:      No new usage. Create migration plan. Prioritize migration in sprints.
```

## Step 4: Radar Entry Format

For each technology on the radar, generate an entry using this exact format:

```markdown
### [Technology Name]
- **Ring:** Adopt / Trial / Assess / Hold
- **Quadrant:** Languages & Frameworks / Tools / Platforms / Techniques
- **Products using:** [comma-separated list of products currently using this]
- **Since:** [YYYY-QX — when first adopted or moved to current ring]
- **Rationale:** [2-3 sentences explaining why this technology is in this ring.
  Be specific about benefits, risks, or problems. Reference actual experience.]
- **Migration plan:** [Only for Hold entries — what to migrate to, estimated effort
  per product (S/M/L/XL), target completion quarter]
- **Owner:** [Person or team who championed this decision]
```

### Entry Quality Rules

```
Every entry MUST have:
  - A clear, defensible rationale (not "it's popular" or "we like it")
  - Actual products listed (not aspirational — what is really in use today)
  - An accurate ring placement based on the criteria in Step 3
  - For Hold: a specific migration target and effort estimate
  - For Trial: success criteria and evaluation timeline
  - For Assess: assigned researcher and next review date

Common mistakes to avoid:
  - Placing a technology in Adopt when only one product uses it (that is Trial)
  - Placing a technology in Assess when it is already in production (that is Trial or Adopt)
  - Hold entries without a migration plan (every Hold needs an exit strategy)
  - Missing the "Products using" field (this is the most important field for portfolio view)
  - Confusing "we want to use this" with "we are using this"
```

## Step 5: Default Radar for Cure Consulting Group

Pre-populate based on the portfolio tech stack defined in CLAUDE.md and README.md.

### ADOPT

```
Kotlin + Jetpack Compose
  Ring: Adopt | Quadrant: Languages & Frameworks
  Products: Vendly (Android), Autograph (Android), TwntyHoops (Android)
  Since: 2023-Q1
  Rationale: Native Android stack with first-class Google support. Compose eliminates
  XML layouts and enables declarative UI. Team is highly proficient. Excellent hiring pool.
  Owner: Android Lead

Swift + SwiftUI
  Ring: Adopt | Quadrant: Languages & Frameworks
  Products: Vendly (iOS), Autograph (iOS), TwntyHoops (iOS)
  Since: 2023-Q1
  Rationale: Native iOS stack. SwiftUI provides declarative UI parity with Compose.
  Structured concurrency simplifies async code. Required for latest iOS APIs.
  Owner: iOS Lead

TypeScript + Next.js App Router
  Ring: Adopt | Quadrant: Languages & Frameworks
  Products: Vendly (Web), The Initiated (Web), Antigravity (Web)
  Since: 2023-Q2
  Rationale: App Router with Server Components reduces client bundle size and simplifies
  data fetching. TypeScript catches bugs at compile time. Largest web framework ecosystem.
  Owner: Frontend Lead

Tailwind CSS
  Ring: Adopt | Quadrant: Languages & Frameworks
  Products: Vendly (Web), The Initiated (Web), Antigravity (Web)
  Since: 2023-Q2
  Rationale: Utility-first CSS eliminates style drift across products. Consistent design
  tokens via tailwind.config. Smaller CSS bundles than component libraries. Fast iteration.
  Owner: Frontend Lead

Firebase (Firestore, Cloud Functions v2, Auth)
  Ring: Adopt | Quadrant: Platforms
  Products: All five products
  Since: 2022-Q4
  Rationale: Unified BaaS across the portfolio. Firestore scales without ops overhead.
  Cloud Functions v2 (Cloud Run-based) resolves cold start issues. Auth handles
  multi-provider login. Generous free tier for early-stage products.
  Owner: Platform Engineer

Stripe
  Ring: Adopt | Quadrant: Platforms
  Products: Vendly, Autograph, TwntyHoops
  Since: 2023-Q1
  Rationale: Industry-standard payments. Excellent SDK for Android and web. Subscriptions,
  invoicing, and Connect for marketplaces. Strong compliance (PCI DSS handled by Stripe).
  Owner: Backend Lead

GitHub Actions
  Ring: Adopt | Quadrant: Tools
  Products: All five products
  Since: 2022-Q4
  Rationale: CI/CD tightly integrated with GitHub repos. Matrix builds for multi-platform.
  Reusable workflows reduce duplication across products. Free tier sufficient for current scale.
  Owner: Platform Engineer

Playwright
  Ring: Adopt | Quadrant: Tools
  Products: Vendly (Web), The Initiated (Web), Antigravity (Web)
  Since: 2024-Q1
  Rationale: Cross-browser E2E testing with auto-waiting. Better reliability than Cypress.
  Native support for multiple browser contexts, network interception, and component testing.
  Owner: QA Lead

Clean Architecture
  Ring: Adopt | Quadrant: Techniques
  Products: All five products
  Since: 2022-Q4
  Rationale: Strict separation of domain/data/presentation layers. Enables testability,
  swappable data sources, and consistent onboarding across all products. Non-negotiable standard.
  Owner: Engineering Lead

MVI (Android)
  Ring: Adopt | Quadrant: Techniques
  Products: Vendly (Android), Autograph (Android), TwntyHoops (Android)
  Since: 2023-Q1
  Rationale: Unidirectional data flow eliminates state bugs. Single state object per screen
  simplifies debugging. Works naturally with Compose recomposition model.
  Owner: Android Lead

MVVM (iOS)
  Ring: Adopt | Quadrant: Techniques
  Products: Vendly (iOS), Autograph (iOS), TwntyHoops (iOS)
  Since: 2023-Q1
  Rationale: SwiftUI's @Observable and @State map directly to MVVM. Simpler than TCA for
  most screens. Well-understood pattern with strong community documentation.
  Owner: iOS Lead

Conventional Commits
  Ring: Adopt | Quadrant: Techniques
  Products: All five products
  Since: 2023-Q2
  Rationale: Structured commit messages enable automated changelogs, semantic versioning,
  and consistent git history. Enforced via commit hooks across the portfolio.
  Owner: Engineering Lead

Trunk-Based Development
  Ring: Adopt | Quadrant: Techniques
  Products: All five products
  Since: 2023-Q3
  Rationale: Short-lived branches (<1 day) reduce merge conflicts and enable continuous
  delivery. Feature flags decouple deploy from release. Proven to improve DORA metrics.
  Owner: Engineering Lead
```

### TRIAL

```
Claude API / Anthropic SDK
  Ring: Trial | Quadrant: Platforms
  Products: Antigravity
  Since: 2024-Q2
  Rationale: Strong reasoning capabilities for complex AI features. Evaluate against
  OpenAI and Gemini for cost, latency, and output quality. Trial in Antigravity's
  AI assistant feature before portfolio-wide decision.
  Success criteria: <2s p95 latency, <$0.01/request avg, user satisfaction >4.2/5
  Owner: AI Lead

Gemini API
  Ring: Trial | Quadrant: Platforms
  Products: The Initiated
  Since: 2024-Q3
  Rationale: Google-native AI with strong multimodal support. Evaluate for content
  generation features. Firebase integration is seamless. Compare pricing vs Claude/OpenAI.
  Success criteria: Multimodal accuracy >90%, cost <OpenAI equivalent, stable API
  Owner: AI Lead

OpenAI API
  Ring: Trial | Quadrant: Platforms
  Products: Vendly
  Since: 2024-Q1
  Rationale: Most mature AI API ecosystem. Evaluate GPT-4o for product description
  generation and search. Compare against Claude and Gemini on same tasks to make
  portfolio-wide AI provider decision by Q4.
  Success criteria: Output quality parity with Claude, function calling reliability >99%
  Owner: AI Lead

TCA — The Composable Architecture (iOS)
  Ring: Trial | Quadrant: Techniques
  Products: TwntyHoops (iOS)
  Since: 2024-Q3
  Rationale: Evaluate for complex state management screens where MVVM becomes unwieldy.
  TCA provides better testability for state machines and side effects. Trial in
  TwntyHoops live scoring feature (complex real-time state).
  Success criteria: Fewer state bugs than MVVM equivalent, team productivity after ramp-up
  Owner: iOS Lead

Turborepo
  Ring: Trial | Quadrant: Tools
  Products: The Initiated
  Since: 2024-Q4
  Rationale: Monorepo build orchestration with remote caching. Evaluate for shared
  component libraries across web products. Could reduce CI build times by 40-60%.
  Success criteria: CI build time reduction >40%, DX improvement (team survey)
  Owner: Platform Engineer
```

### ASSESS

```
React Native / Kotlin Multiplatform (KMP)
  Ring: Assess | Quadrant: Languages & Frameworks
  Products: None (research only)
  Since: 2025-Q1
  Rationale: Cross-platform could reduce development cost for new products. KMP shares
  business logic while keeping native UI. React Native shares UI but has bridge overhead.
  Neither proven in our portfolio yet. Research for potential new product in 2026.
  Researcher: Mobile Lead | Next review: 2025-Q2

Supabase
  Ring: Assess | Quadrant: Platforms
  Products: None (research only)
  Since: 2025-Q1
  Rationale: Open-source Firebase alternative with PostgreSQL. Better relational data
  support, row-level security, real-time subscriptions. Evaluate as alternative for
  products that outgrow Firestore's document model limitations.
  Researcher: Backend Lead | Next review: 2025-Q2

Deno
  Ring: Assess | Quadrant: Platforms
  Products: None (research only)
  Since: 2025-Q1
  Rationale: Secure-by-default TypeScript runtime. Native TypeScript support without build
  step. Built-in test runner, linter, formatter. Evaluate as Node.js replacement for
  Cloud Functions or standalone services.
  Researcher: Platform Engineer | Next review: 2025-Q3

Edge Functions (Vercel / Cloudflare Workers)
  Ring: Assess | Quadrant: Platforms
  Products: None (research only)
  Since: 2025-Q1
  Rationale: Sub-10ms cold starts, global distribution, lower latency than Cloud Functions.
  Evaluate for latency-sensitive API routes (auth, personalization, geolocation).
  Limited runtime (no Node.js APIs, size limits) may constrain usage.
  Researcher: Frontend Lead | Next review: 2025-Q2

Server Components + Server Actions (React 19)
  Ring: Assess | Quadrant: Techniques
  Products: None (research only)
  Since: 2025-Q1
  Rationale: Server Actions could replace API routes for mutations. Streaming SSR improves
  perceived performance. Evaluate stability and DX as React 19 matures. Already partially
  used via Next.js App Router but not fully leveraging Server Actions.
  Researcher: Frontend Lead | Next review: 2025-Q2
```

### HOLD

```
LiveData (Android)
  Ring: Hold | Quadrant: Languages & Frameworks
  Products: Vendly (Android — legacy screens)
  Since: 2024-Q1 (moved from Adopt)
  Rationale: StateFlow + Compose is the modern standard. LiveData requires lifecycle
  observation boilerplate and doesn't compose well with coroutines. No new screens
  should use LiveData.
  Migration: Replace with StateFlow/SharedFlow. Effort: M (Vendly). Target: 2025-Q2.
  Owner: Android Lead

UIKit (iOS)
  Ring: Hold | Quadrant: Languages & Frameworks
  Products: Vendly (iOS — legacy screens), Autograph (iOS — 3 screens)
  Since: 2024-Q1 (moved from Adopt)
  Rationale: SwiftUI is the Adopt standard. UIKit screens cannot use @Observable,
  previews, or navigation stack. Maintaining both UI frameworks doubles the mental model.
  Migration: Rewrite screens in SwiftUI. Effort: L (Vendly), S (Autograph). Target: 2025-Q3.
  Owner: iOS Lead

Pages Router (Next.js)
  Ring: Hold | Quadrant: Languages & Frameworks
  Products: Antigravity (Web — 6 routes still on pages/)
  Since: 2024-Q2 (moved from Adopt)
  Rationale: App Router is the Adopt standard. Pages Router cannot use Server Components,
  streaming, or parallel routes. Maintaining both routers complicates the codebase.
  Migration: Move remaining routes to app/. Effort: M (Antigravity). Target: 2025-Q2.
  Owner: Frontend Lead

Jest
  Ring: Hold | Quadrant: Tools
  Products: Antigravity (Web), The Initiated (Web — partial)
  Since: 2024-Q3 (moved from Adopt)
  Rationale: Vitest is faster (native ESM, Vite-powered), compatible with Jest API,
  and aligns with our Vite/Next.js toolchain. Jest's CJS-first architecture causes
  configuration headaches with ESM dependencies.
  Migration: Swap jest.config for vitest.config, update imports. Effort: S per product. Target: 2025-Q2.
  Owner: Frontend Lead

Express.js
  Ring: Hold | Quadrant: Languages & Frameworks
  Products: Autograph (API — standalone service)
  Since: 2024-Q2 (moved from Adopt)
  Rationale: Cloud Functions v2 or Next.js API routes are the standard for new endpoints.
  Express adds an unnecessary abstraction layer when running inside Cloud Functions.
  Standalone Express servers require separate hosting and scaling.
  Migration: Move endpoints to Cloud Functions v2 or Next.js API routes. Effort: L (Autograph). Target: 2025-Q3.
  Owner: Backend Lead

XML Layouts (Android)
  Ring: Hold | Quadrant: Techniques
  Products: Vendly (Android — 12 legacy screens)
  Since: 2023-Q3 (moved from Adopt)
  Rationale: Jetpack Compose is the Adopt standard. XML layouts cannot use Compose state
  management, previews, or animation APIs without interop bridges. Maintaining both
  layout systems slows feature development.
  Migration: Rewrite screens in Compose. Effort: L (Vendly). Target: 2025-Q4.
  Owner: Android Lead
```

## Step 6: Quarterly Review Process

### Schedule

```
When:     First week of each quarter (January, April, July, October)
Duration: 2 hours (1 hour prep + 1 hour review meeting)
Attendees: Engineering Lead, Tech Leads (Android, iOS, Web, Platform), Product Lead
Output:   Updated TECHNOLOGY_RADAR.md, ring movement announcements, action items
```

### Pre-Meeting Preparation (Automated)

```
1. Dependency scan
   Run across all product repos. Diff against previous quarter's scan.
   Flag: new dependencies, removed dependencies, major version bumps.

2. Usage analysis
   For each technology on the radar, verify:
     - Is it still in use? (check imports, configs, build files)
     - Has usage expanded to new products?
     - Has usage shrunk (dead code, unused dependencies)?

3. Industry check
   For each Assess technology:
     - Any major releases or milestones?
     - Community momentum (GitHub stars trend, npm downloads, conference talks)
     - Any concerning signals (maintainer departures, funding issues, forks)?

4. Pain point survey
   Async survey to all engineers (1-5 scale + comments):
     - "Rate your satisfaction with [technology] for [purpose]"
     - "What technology do you wish we used instead?"
     - "What technology is causing you the most friction?"
```

### Review Meeting Agenda

```
1. Ring movements (30 minutes)
   For each proposed movement:
     - [Technology] from [Old Ring] → [New Ring]
     - Evidence: [data supporting the movement]
     - Impact: [which products are affected]
     - Decision: Approve / Defer / Need more data

2. New entries (15 minutes)
   Technologies discovered in dependency scan or survey that aren't on the radar.
   Assign initial ring placement.

3. Divergence report (10 minutes)
   Review technologies where products have diverged (see Step 8).
   Decide: converge or accept divergence.

4. Technology debt status (5 minutes)
   Review Hold migration progress. Reprioritize if needed.
```

### Ring Movement Template

```
RING MOVEMENT: [Technology Name]
Direction:  [Old Ring] → [New Ring]
Date:       [YYYY-QX]
Decision:   [Approved / Deferred]

Evidence:
  - [Bullet 1: usage data, performance metrics, team feedback]
  - [Bullet 2: industry trends, ecosystem health]
  - [Bullet 3: cost or risk analysis]

Impact:
  - Products affected: [list]
  - Action required: [what teams need to do]
  - Timeline: [when actions should be completed]

Decided by: [Names of decision makers]
```

## Step 7: Technology Debt Tracking

### Debt Inventory Format

```
TECHNOLOGY DEBT INVENTORY
Last updated: [YYYY-MM-DD]

┌────┬──────────────────┬──────────────┬───────────────────┬────────┬──────────┬──────────┐
│ #  │ Hold Technology   │ Products     │ Replace With      │ Effort │ Priority │ Status   │
├────┼──────────────────┼──────────────┼───────────────────┼────────┼──────────┼──────────┤
│ 1  │ [Technology]      │ [Products]   │ [Adopt target]    │ S/M/L/ │ P0-P3    │ Planned/ │
│    │                  │              │                   │ XL     │          │ Active/  │
│    │                  │              │                   │        │          │ Done     │
└────┴──────────────────┴──────────────┴───────────────────┴────────┴──────────┴──────────┘
```

### Effort Estimation Guide

```
S (Small) — < 1 sprint (2 weeks)
  Examples: Swap test runner config, update import paths, replace one utility library
  Typical: 1-2 engineers, no user-facing changes, low risk

M (Medium) — 1-2 sprints (2-4 weeks)
  Examples: Migrate 5-10 screens from old UI framework, swap state management on
  one feature, move API routes from Express to Cloud Functions
  Typical: 1-2 engineers, some user-facing changes, moderate risk

L (Large) — 1-2 months
  Examples: Rewrite significant portion of UI framework (UIKit → SwiftUI),
  migrate database (Firestore → PostgreSQL for one service), replace auth provider
  Typical: 2-3 engineers, significant user-facing changes, high risk, needs testing plan

XL (Extra Large) — 1+ quarters
  Examples: Rewrite entire product in different framework, migrate cloud provider,
  replace payment processor
  Typical: Full team, phased rollout required, very high risk, needs dedicated project plan
```

### Priority Matrix

```
                    High Business Impact          Low Business Impact
                ┌───────────────────────────┬───────────────────────────┐
High Risk       │ P0 — Migrate immediately  │ P1 — Migrate this quarter │
(security,      │ Security vulnerabilities, │ Deprecated with no        │
 deprecation)   │ EOL runtimes, compliance  │ security risk but         │
                │ requirements              │ increasing maintenance    │
                ├───────────────────────────┼───────────────────────────┤
Low Risk        │ P2 — Migrate next quarter │ P3 — Migrate when         │
(inconvenience, │ Developer friction,       │ convenient                │
 maintenance)   │ slowing feature velocity  │ Cosmetic, low friction,   │
                │ on revenue features       │ can live with it          │
                └───────────────────────────┴───────────────────────────┘
```

### ADR Linkage

```
Every P0 or P1 migration MUST have an Architecture Decision Record (ADR):

ADR Template (use /sdlc skill to generate):
  - Title: "Migrate from [Hold tech] to [Adopt tech]"
  - Status: Proposed / Accepted / Completed
  - Context: Why the technology is on Hold
  - Decision: What we are migrating to and why
  - Consequences: Effort, risk, timeline, affected products
  - Link to TECHNOLOGY_RADAR.md entry
```

## Step 8: Divergence Detection

### What Is Divergence?

```
Divergence: Two or more products use DIFFERENT technologies for the SAME purpose.

Unnecessary divergence (reduce):
  - Product A uses Vitest, Product B uses Jest → both do unit testing, should converge
  - Product A uses Zustand, Product B uses Redux → both do state management, should converge
  - Product A uses Axios, Product B uses fetch → both do HTTP requests, should converge

Acceptable divergence (keep):
  - Android uses Kotlin, iOS uses Swift → platform-specific, expected
  - Web uses Playwright, Android uses Espresso → platform-specific test tools
  - Vendly uses Stripe Connect, TwntyHoops uses Stripe Subscriptions → different Stripe
    products for different business models
```

### Divergence Detection Process

```
For each technology purpose, check across all products:

┌─────────────────────────┬───────────────────────────────────────────────────┐
│ Purpose                 │ Check For                                         │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ Unit testing            │ Jest vs Vitest vs Mocha                           │
│ E2E testing             │ Playwright vs Cypress vs Detox (mobile OK)        │
│ State management (Web)  │ Redux vs Zustand vs Jotai vs Context              │
│ HTTP client             │ Axios vs fetch vs ky vs got                       │
│ CSS approach            │ Tailwind vs CSS Modules vs styled-components      │
│ Form handling           │ React Hook Form vs Formik vs native               │
│ Date handling           │ date-fns vs dayjs vs Luxon vs moment (Hold!)      │
│ Animation (Web)         │ Framer Motion vs React Spring vs CSS              │
│ Linting                 │ ESLint vs Biome (consistent config across repos?) │
│ Formatting              │ Prettier vs Biome vs dprint                       │
│ Package manager         │ npm vs yarn vs pnpm                               │
│ Node version            │ Same major version across all products?           │
└─────────────────────────┴───────────────────────────────────────────────────┘

For mobile, check:
│ DI (Android)            │ Hilt vs Koin vs Manual                            │
│ Networking (Android)    │ Retrofit vs Ktor                                  │
│ Image loading (Android) │ Coil vs Glide                                     │
│ Navigation (iOS)        │ NavigationStack vs Coordinator vs Router          │
│ Networking (iOS)        │ URLSession vs Alamofire                           │
│ Image loading (iOS)     │ AsyncImage vs Kingfisher vs SDWebImage            │
```

### Divergence Report Format

```
DIVERGENCE REPORT
Date: [YYYY-MM-DD]

UNNECESSARY DIVERGENCE (action required):
┌────┬──────────────────┬─────────────────────────────┬──────────────────┬──────────┐
│ #  │ Purpose          │ Current State               │ Converge To      │ Effort   │
├────┼──────────────────┼─────────────────────────────┼──────────────────┼──────────┤
│ 1  │ [Purpose]        │ [Product A: X, Product B: Y]│ [Target tech]    │ S/M/L/XL │
└────┴──────────────────┴─────────────────────────────┴──────────────────┴──────────┘

ACCEPTABLE DIVERGENCE (no action):
┌────┬──────────────────┬─────────────────────────────┬──────────────────────────────┐
│ #  │ Purpose          │ Current State               │ Why Acceptable               │
├────┼──────────────────┼─────────────────────────────┼──────────────────────────────┤
│ 1  │ [Purpose]        │ [Product A: X, Product B: Y]│ [Platform-specific / etc.]   │
└────┴──────────────────┴─────────────────────────────┴──────────────────────────────┘
```

## Step 9: Output Format

Generate a complete TECHNOLOGY_RADAR.md file using this structure:

```
TECHNOLOGY RADAR — [COMPANY NAME]
Last updated: [YYYY-MM-DD]
Review cadence: Quarterly (next review: [YYYY-QX])
Prepared by: [Name/Team]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
┌──────────┬───────┬────────────────────────────────────────────────────┐
│ Ring     │ Count │ Key Changes This Quarter                          │
├──────────┼───────┼────────────────────────────────────────────────────┤
│ Adopt    │ [X]   │ [Notable additions or confirmations]              │
│ Trial    │ [X]   │ [What is being evaluated and where]               │
│ Assess   │ [X]   │ [What is on the horizon]                          │
│ Hold     │ [X]   │ [What is being phased out]                        │
└──────────┴───────┴────────────────────────────────────────────────────┘

Ring movements this quarter:
  [+] [Tech] → Adopt (promoted from Trial)
  [~] [Tech] → Trial (promoted from Assess)
  [-] [Tech] → Hold (demoted from Adopt/Trial)
  [NEW] [Tech] added to [Ring]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADOPT
[Entries grouped by quadrant, using Step 4 format]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRIAL
[Entries grouped by quadrant, using Step 4 format]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ASSESS
[Entries grouped by quadrant, using Step 4 format]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOLD
[Entries grouped by quadrant, using Step 4 format.
 Every Hold entry MUST include a migration plan.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIVERGENCE REPORT
[Output from Step 8]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TECHNOLOGY DEBT
[Output from Step 7 — Hold items still in production, prioritized]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUARTERLY REVIEW LOG
[Date] — [Summary of changes made]
[Date] — [Summary of changes made]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLES GENERATED:
  - [ ] TECHNOLOGY_RADAR.md created / updated
  - [ ] All entries have complete fields (ring, quadrant, products, rationale)
  - [ ] All Hold entries have migration plans with effort estimates
  - [ ] Divergence report generated
  - [ ] Technology debt inventory updated and prioritized
  - [ ] Ring movements documented with evidence
  - [ ] ADRs created for P0/P1 migrations
  - [ ] Next quarterly review scheduled
```

Cross-reference: `/sdlc` for ADRs and architecture decisions, `/infrastructure-scaffold` for platform choices, `/ci-cd-pipeline` for tooling decisions, `/database-architect` for data layer technologies, `/project-bootstrap` for new project technology selection.
