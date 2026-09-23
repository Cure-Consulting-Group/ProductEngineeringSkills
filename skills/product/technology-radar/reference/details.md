# technology-radar: detailed reference

> Read when generating a first radar for Cure Consulting Group (Step 5 of the `technology-radar` skill). It is a starting draft, not current truth: confirm every entry against the dependency scan, and replace the illustrative dates and targets with real ones.

## Contents
- Step 5: Default Radar for Cure Consulting Group

## Step 5: Default Radar for Cure Consulting Group

Pre-populate from PORTFOLIO.md and the dependency scan; drop any entry the scan doesn't confirm.

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
  Products: Vendly (Web), The Initiated (Web)
  Since: 2023-Q2
  Rationale: App Router with Server Components reduces client bundle size and simplifies
  data fetching. TypeScript catches bugs at compile time. Largest web framework ecosystem.
  Owner: Frontend Lead

Tailwind CSS
  Ring: Adopt | Quadrant: Languages & Frameworks
  Products: Vendly (Web), The Initiated (Web)
  Since: 2023-Q2
  Rationale: Utility-first CSS eliminates style drift across products. Tailwind v4 is
  CSS-first: design tokens map in via `@theme` in CSS (no tailwind.config). Fast iteration.
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
  Products: Vendly (Web), The Initiated (Web)
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

Claude API / Anthropic SDK
  Ring: Adopt | Quadrant: Platforms
  Products: Autograph and Cure's agent tooling
  Since: [quarter adopted]
  Rationale: Default LLM provider for agentic, coding, and long-document features; this
  skill library itself is Claude-first. Pin exact model IDs per feature and re-check
  them against Anthropic's current model list each quarter.
  Owner: AI Lead
```

### TRIAL

```
Gemini API
  Ring: Trial | Quadrant: Platforms
  Products: The Initiated
  Since: 2024-Q3
  Rationale: Google-native AI with strong multimodal support, reachable through Firebase
  AI Logic. Evaluate for content generation; compare cost and quality against Claude on
  the same eval set. Confirm current model IDs before use.
  Success criteria: Multimodal accuracy >90%, cost <OpenAI equivalent, stable API
  Owner: AI Lead

OpenAI API
  Ring: Trial | Quadrant: Platforms
  Products: Vendly
  Since: 2024-Q1
  Rationale: Evaluate OpenAI's current models for product-description generation and
  search, against Claude and Gemini on the same eval set. Confirm current model IDs
  and prices before use; don't carry model names over from old radars.
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

Server Actions for mutations (React 19)
  Ring: Trial | Quadrant: Techniques
  Products: [web product trialing it]
  Since: [quarter]
  Rationale: React 19 is stable and Server Components are already Adopt via the App
  Router. Trial Server Actions as the default for form mutations in place of API routes;
  success = less client code with auth and validation checked in every action.
  Owner: Frontend Lead
```

### ASSESS

```
React Native / Kotlin Multiplatform (KMP)
  Ring: Assess | Quadrant: Languages & Frameworks
  Products: None (research only)
  Since: 2025-Q1
  Rationale: Cross-platform could reduce development cost for new products. KMP shares
  business logic while keeping native UI. React Native shares UI; its New Architecture
  (bridgeless, default since 0.76) removed the old bridge overhead. Neither proven in our
  portfolio yet.
  Researcher: Mobile Lead | Next review: [next quarter]

Supabase
  Ring: Assess | Quadrant: Platforms
  Products: None (research only)
  Since: 2025-Q1
  Rationale: Open-source Firebase alternative with PostgreSQL. Better relational data
  support, row-level security, real-time subscriptions. Evaluate as alternative for
  products that outgrow Firestore's document model limitations.
  Researcher: Backend Lead | Next review: [next quarter]

Deno
  Ring: Assess | Quadrant: Platforms
  Products: None (research only)
  Since: 2025-Q1
  Rationale: Secure-by-default TypeScript runtime. Native TypeScript support without build
  step. Built-in test runner, linter, formatter. Evaluate as Node.js replacement for
  Cloud Functions or standalone services.
  Researcher: Platform Engineer | Next review: [next quarter]

Edge Functions (Vercel / Cloudflare Workers)
  Ring: Assess | Quadrant: Platforms
  Products: None (research only)
  Since: 2025-Q1
  Rationale: Global distribution for latency-sensitive routes (auth, personalization,
  geolocation). Vercel now defaults functions and proxy.ts to the Node.js runtime; the
  Edge runtime is limited (no full Node APIs, size limits). Confirm current platform
  guidance with the edge-computing skill before trialing.
  Researcher: Frontend Lead | Next review: [next quarter]

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
  Migration: Replace with StateFlow/SharedFlow. Effort: M (Vendly). Target: [quarter].
  Owner: Android Lead

UIKit (iOS)
  Ring: Hold | Quadrant: Languages & Frameworks
  Products: Vendly (iOS — legacy screens), Autograph (iOS — 3 screens)
  Since: 2024-Q1 (moved from Adopt)
  Rationale: SwiftUI is the Adopt standard. UIKit screens cannot use @Observable,
  previews, or navigation stack. Maintaining both UI frameworks doubles the mental model.
  Migration: Rewrite screens in SwiftUI. Effort: L (Vendly), S (Autograph). Target: [quarter].
  Owner: iOS Lead

Pages Router (Next.js)
  Ring: Hold | Quadrant: Languages & Frameworks
  Products: [any web product with routes still on pages/]
  Since: 2024-Q2 (moved from Adopt)
  Rationale: App Router is the Adopt standard. Pages Router cannot use Server Components,
  streaming, or parallel routes. Maintaining both routers complicates the codebase.
  Migration: Move remaining routes to app/. Effort: M per product. Target: [quarter].
  Owner: Frontend Lead

Jest
  Ring: Hold | Quadrant: Tools
  Products: The Initiated (Web — partial)
  Since: 2024-Q3 (moved from Adopt)
  Rationale: Vitest is faster (native ESM, Vite-powered), compatible with Jest API,
  and aligns with our Vite/Next.js toolchain. Jest's CJS-first architecture causes
  configuration headaches with ESM dependencies.
  Migration: Swap jest.config for vitest.config, update imports. Effort: S per product. Target: [quarter].
  Owner: Frontend Lead

Express.js
  Ring: Hold | Quadrant: Languages & Frameworks
  Products: Autograph (API — standalone service)
  Since: 2024-Q2 (moved from Adopt)
  Rationale: Cloud Functions v2 or Next.js API routes are the standard for new endpoints.
  Express adds an unnecessary abstraction layer when running inside Cloud Functions.
  Standalone Express servers require separate hosting and scaling.
  Migration: Move endpoints to Cloud Functions v2 or Next.js API routes. Effort: L (Autograph). Target: [quarter].
  Owner: Backend Lead

XML Layouts (Android)
  Ring: Hold | Quadrant: Techniques
  Products: Vendly (Android — 12 legacy screens)
  Since: 2023-Q3 (moved from Adopt)
  Rationale: Jetpack Compose is the Adopt standard. XML layouts cannot use Compose state
  management, previews, or animation APIs without interop bridges. Maintaining both
  layout systems slows feature development.
  Migration: Rewrite screens in Compose. Effort: L (Vendly). Target: [quarter].
  Owner: Android Lead
```
