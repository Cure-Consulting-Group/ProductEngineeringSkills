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

See [reference/details.md](reference/details.md) (section “Step 5: Default Radar for Cure Consulting Group”) for full detail.

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

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: `/engagement-automation`).

- **Cadence:** quarterly
- **Unattended:** cloud routine — Quarterly radar refresh: ring movements, new adoptions, Hold items still in production. Recipes: docs/AUTOMATION.md in the plugin repo.
- **Budget:** ~150k tokens/run; cap at one run per quarterly period.
- **Guardrails:** read-only run; deliver updated TECHNOLOGY_RADAR.md + divergence report; report on failure rather than retrying.
