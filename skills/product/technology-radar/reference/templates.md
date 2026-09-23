# technology-radar: scan checklist, divergence, and output templates

> Read when running the dependency scan (Step 2), the divergence check (Step 6), or writing TECHNOLOGY_RADAR.md (Step 7) in the `technology-radar` skill.

## Dependency scan checklist

```
Scan these files in every product repo:

JavaScript/TypeScript:
  - package.json (dependencies + devDependencies)
  - package-lock.json / yarn.lock / pnpm-lock.yaml (exact versions)
  - tsconfig.json (TypeScript configuration)
  - next.config.js / next.config.ts (Next.js version and plugins)
  - tailwind.config.js (v3) or the CSS file with `@import "tailwindcss"` / `@theme` (v4)
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

## Divergence check table

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

## Divergence report format

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

## Debt inventory, effort sizes, and ring-movement template

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

## TECHNOLOGY_RADAR.md skeleton

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
```
