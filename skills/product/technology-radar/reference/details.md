# technology-radar: detailed reference

> Reference material for the `technology-radar` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 5: Default Radar for Cure Consulting Group

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
