# ProductEngineeringSkills — Overview

_Auto-generated. Do not edit by hand. Regenerate with `python3 scripts/generate-overview.py`._

## 1. Summary

| Field | Value |
| --- | --- |
| Plugin | cure-product-engineering |
| Version | 7.9.1 |
| Skills | 103 |
| Agents | 40 |
| Personas | 4 |
| Hooks (entries) | 17 |
| Rules | 11 |
| Output Styles | 9 |
| MCP Servers | 0 |
| LSP Servers | 0 |


## 2. Skills


### Business (14)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| bid-decision | Makes the bid/no-bid call on a solicitation: kill criteria, weighted scorecard, win odds, bid cost. Use when deciding whether to commit to a proposal or a pursuit is drifting. | Read, Grep, Glob, Bash, Write, Edit, WebSearch |
| burn-rate-tracker | Models burn, runway scenarios, break-even, and cash-flow projections. Use when asking how long cash lasts, when to raise or cut, or planning a studio or product budget. | Read, Grep, Glob, WebSearch |
| buyer-intelligence | Builds a buyer, incumbent, and renewal-date database from declined bids and award notices. Use when a bid is declined, a sole source or award notice appears, or building a buyer dossier. | Read, Grep, Glob, Bash, Write, Edit, WebSearch, WebFetch |
| capture-management | Builds a public-sector pipeline: target profile, sourcing, pre-RFP positioning, teaming. Use when entering a government market, choosing which bids to chase, or building past performance. | Read, Grep, Glob, Bash, Write, Edit, WebSearch, WebFetch |
| engineering-cost-model | Estimates internal build cost: developer hours, cloud and service spend, maintenance, build-vs-buy. Use when asking what a feature or product will cost or take to build. | Read, Grep, Glob, WebSearch |
| finops | Cloud cost optimization for Firebase and GCP: budgets, alerts, right-sizing, labels, AI API spend. Use when a cloud bill spikes, setting budgets, or cutting infra and LLM costs. | default |
| fundraising-materials | Builds pitch decks, the ask and use of funds, and the investor outreach pipeline. Use when preparing a seed or Series A raise: deck, intro blurb, target list, or process plan. | Read, Grep, Glob, WebSearch |
| investor-reporting | Drafts investor updates, board decks, portfolio P&L, data rooms, and cap-table/SAFE models. Use when writing the monthly investor update, a quarterly board deck, or diligence prep. | default |
| proposal-generator | Drafts consulting proposals and SOWs: scope, milestones, pricing, payment terms. Use when writing a client proposal, a statement of work, or a change order for Cure. | default |
| public-sector-contracting | Reviews government contract terms: liability, IP, termination, non-appropriation, insurance. Use when reading a municipal, state, or federal contract form or choosing exceptions. | Read, Grep, Glob, Bash, Write, Edit, WebSearch |
| rfp-evaluation | Extracts every requirement from an RFP/RFQ into a compliance matrix and maps the rubric to effort. Use when a solicitation has passed triage and you need what it requires. | Read, Grep, Glob, Bash, Write, Edit, WebSearch |
| saas-financial-model | Models SaaS unit economics, MRR/ARR projections, and pricing tiers. Use when computing LTV, CAC, payback, or churn, projecting MRR, or setting subscription prices. | Read, Grep, Glob, WebSearch |
| solicitation-triage | Screens public-sector solicitations and portal alert batches to a verdict in under an hour. Use when a new RFP, RFQ, bid notice, or weekly bid-portal feed arrives. | Read, Grep, Glob, Bash, Write, Edit, WebSearch |
| technical-estimation | Builds defensible software estimates with ranges: PERT, reference class, risk reserve. Use when an estimate will be bid on, contracted, or audited, e.g. an RFP cost volume. | Read, Grep, Glob, Bash, Write, Edit, WebSearch |


### Engineering (40)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| agent-designer | Designs LLM agent internals: tool schemas, memory, termination, evals, cost, failure modes. Use when an agent or multi-agent system is the chosen shape and needs a design. | default |
| agent-workflow-designer | Picks the shape of an LLM system: single call, workflow pattern, or autonomous agent. Use when deciding how to structure an AI feature, or when an agent is too slow, costly, or flaky. | default |
| ai-feature-builder | Builds user-facing LLM features: client wrapper, prompts, streaming UX, fallbacks, kill switch. Use when adding chat, summarization, extraction, or generation to an app. | default |
| analytics-implementation | Designs analytics event taxonomies, tracking plans, funnels, and consent flows. Use when instrumenting product analytics (GA4/Firebase, Mixpanel, PostHog) or auditing events. | default |
| android-design-expert | Material Design 3 guidance for Android screens and components. Use when designing or reviewing Compose UI for dynamic color, adaptive layouts, navigation, motion, or M3 Expressive. | default |
| android-feature-scaffold | Scaffolds Android feature modules (Clean Architecture, MVI, Compose, Hilt). Use when creating a new Kotlin feature, screen, ViewModel, repository, or use case in an Android app. | default |
| api-architect | Designs REST/GraphQL API contracts: errors, auth, rate limits, versioning, OpenAPI. Use when designing endpoints or an API's error, auth, or deprecation policy. | default |
| api-gateway | Designs API gateway and BFF layers: middleware order, aggregation, auth, GraphQL federation. Use when adding a gateway, a mobile/web BFF, or federating GraphQL subgraphs. | default |
| client-communication | Drafts client-facing status emails, risk escalations, executive summaries, and sprint demo scripts. Use when writing a weekly client update, escalating a blocker, or preparing a stakeholder demo or QBR. | default |
| client-handoff | Builds client handoff packages: architecture, runbooks, credential transfer, KT plan, SLA. Use when handing a project, phase, or support role to a client team or winding down an engagement. | default |
| cure-infra-bootstrap | Runs Cure's manifest-driven bootstrap CLI (init/apply/doctor/inventory) for CLAUDE.md, .claude/, rules. Use when setting up, upgrading, or drift-checking Cure agent infra in a project. | Read, Bash |
| data-migration | Plans and runs data migrations: ETL, backfills, dual-write, zero-downtime cutover, rollback. Use when moving or reshaping existing data across databases, Firestore, or legacy systems. | default |
| database-architect | Designs schemas, indexes, and query plans for Firestore, PostgreSQL, SQLite/Room. Use when choosing a database, modeling data, adding indexes, or fixing slow queries. | default |
| e2e-testing | Writes E2E test suites (Playwright, Compose/Espresso, XCUITest) with page objects and CI wiring. Use when adding E2E, smoke, or visual regression tests for a user flow or fixing flaky E2E tests. | default |
| env-secrets-manager | Read-only .env and secrets audits. Use when designing an .env schema, scanning for leaked keys, responding to a leak, planning rotation, or moving to a secret manager. | Read, Grep, Glob, Bash |
| firebase-architect | Designs Firestore data models, security rules, Cloud Functions v2, and App Check. Use when building a Firebase feature, writing rules or triggers, or wiring a Firestore data layer. | default |
| git-worktree-manager | Sets up git worktrees with isolated ports, env files, and databases. Use when running parallel features, a hotfix, or a PR review without stashing or switching the main checkout. | default |
| i18n | Internationalization and localization for Android, iOS, and Next.js. Use when externalizing strings, adding a locale, supporting RTL, fixing plurals or date/currency formatting, or setting up a translation pipeline. | default |
| interview-system-designer | Designs engineering interview loops: stages, rubrics, question banks, AI-use policy, debrief rules. Use when hiring engineers or fixing a loop with poor pass or accept rates. | default |
| ios-architect | Scaffolds iOS features in Swift/SwiftUI with Clean Architecture, MVVM, and Swift 6 concurrency. Use when creating a new iOS feature, view model, repository, or StoreKit 2 flow. | default |
| ios-design-expert | Apple HIG design guidance for iOS/iPadOS screens and components. Use when designing or reviewing SwiftUI UI for Liquid Glass, navigation, tab bars, Dynamic Type, SF Symbols, or widgets. | default |
| llmops | Runs LLM features in production: evals, prompt versioning, cost, caching, model routing, monitoring. Use when an AI feature needs eval gates, spend control, or a model/prompt rollout. | default |
| mcp-server-builder | Designs and builds MCP (Model Context Protocol) servers: tool schemas, resources, transports, auth. Use when building an MCP server, wrapping an API as MCP tools, or migrating one to a new SDK/spec. | default |
| micro-frontends | Decides whether and how to split a web frontend into independently deployed apps. Use when teams block each other's releases, or when weighing Vercel microfrontends, multi-zones, or module federation. | default |
| monorepo-navigator | Diagnoses and speeds up JS/TS and polyglot monorepos (pnpm, Turborepo, Nx, Bazel). Use when joining, creating, or fixing a monorepo: slow CI, cache misses, dependency drift, package boundaries, or extracting a package. | default |
| nextjs-feature-scaffold | Scaffolds Next.js 16 App Router features in TypeScript. Use when adding a page, route, Server Action, form, or CRUD feature to a Next.js app, with Server/Client split, caching, auth, and tests. | default |
| notification-architect | Designs notification systems: push (FCM/APNs/web), in-app, transactional email, SMS, and preferences. Use when adding push notifications, notification preferences, email deliverability, or multi-channel dispatch. | default |
| offline-first | Offline-first design for Android, iOS, and web: local storage, sync, conflicts. Use when an app must work without network, queue writes, resolve sync conflicts, or show optimistic UI. | default |
| parallel-agent-orchestration | Operating model for running parallel agent sessions on one repo. Use when splitting a wave across 2+ agents or subagents: decomposition, budget, locks, merge order. | default |
| performance-review | Sets performance budgets and load-test plans for web, mobile, backend. Use when an app or page is slow, before a launch or scale event, or to set Core Web Vitals targets. | default |
| project-bootstrap | Writes a tailored CLAUDE.md and STATE.md for a repo by interview. Use when onboarding an existing or new repo to agent work by hand, without the Cure manifest CLI. | default |
| project-manager | Sprint and delivery management for engineering teams. Use when planning a sprint, sizing capacity, building a RACI, risk register, dependency map, timeline, or running a retro. | default |
| rag-architect | Designs RAG pipelines: chunking, embeddings, vector store, reranking. Use when building or auditing retrieval over documents, a knowledge base, or semantic search with retrieval evals. | default |
| sdlc | Writes engineering specs: PRDs, ADRs, RFCs, epics, user stories, task and test specs. Use when asked to write a PRD or ADR, draft an RFC, spec a feature, or break work into stories. | default |
| self-improving-memory | Curates agent auto-memory (MEMORY.md plus user/feedback/project/reference entries). Use when seeding memory for a new engagement, auditing or consolidating it, or checking for stale entries. | default |
| stitch-design | Generates, syncs, and audits UI screens through Google Stitch MCP. Use when the user names Stitch or DESIGN.md, or the repo has a .stitch/ folder: screen generation, token export, design-drift audits. | default |
| stripe-integration | Stripe payments and subscriptions through Firebase Cloud Functions. Use when adding checkout, subscriptions, billing portal, saved cards, or Stripe webhooks with Firestore sync to a mobile or web app. | default |
| test-accounts | QA test accounts: personas, receivable QA emails, seed/reset scripts, env-guarded credentials. Use when setting up test users, seed data, QA email addresses, or test-account teardown. | default |
| testing-strategy | Defines test architecture: pyramid, frameworks, coverage gates, flaky-test policy. Use when setting up testing, setting test standards, or asking 'what tests do we need'. | default |
| web-design-expert | Web UI design guidance: responsive layout, tokens, Tailwind v4, dark mode, motion. Use when designing or reviewing pages and components for layout, CSS architecture, theming, or Core Web Vitals impact. | default |


### Finance (4)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| comps-analysis | Values a company against trading peers with EV/Revenue, EV/EBITDA, and P/E multiples. Use when benchmarking valuation multiples or pricing a company off public comparables. | default |
| dcf-modeling | Builds a discounted cash flow valuation: unlevered FCF, WACC, terminal value, equity bridge. Use when estimating intrinsic value or a per-share price from projected cash flows. | default |
| equity-research | Analyzes a public company from 10-K/10-Q filings and earnings calls into a thesis and catalysts. Use when digesting earnings, reading SEC filings, or drafting a buy/hold/sell view. | default |
| merger-modeling | Models M&A accretion/dilution: pro-forma EPS, deal mix, purchase price allocation, synergies. Use when judging an acquisition's financial impact on the buyer. | default |


### Legal (1)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| legal-doc-scaffold | Drafts first-pass ToS, privacy policy, SOW, NDA, DPA, EULA, and refund policy for attorney review. Use when a product or engagement needs a starting draft built from a required-clause checklist and compliance flags. | default |


### Marketing (6)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| go-to-market | Writes launch plans: positioning, messaging, channels, launch phases. Use when launching a product, entering a new market, or planning a major feature release. | default |
| growth-engineering | Builds growth systems past activation. Use when improving retention loops, referrals, lifecycle messaging, PLG paywalls and trials, or cohort retention. | default |
| instagram-publishing-setup | Sets up programmatic Instagram publishing: Meta app, tester role, token, media hosting, scheduler. Use when posting to Instagram from code or stuck on Insufficient Developer Role or a media_publish 400. | default |
| product-marketing | Writes platform-native social content for portfolio brands. Use when creating Reels, Shorts, LinkedIn or X posts, a campaign, a message house, or brand-voice copy. | default |
| seo-content-engine | Technical SEO and search content strategy for websites. Use when a site needs to rank, an SEO audit, metadata, JSON-LD, sitemaps, Core Web Vitals, or keyword clusters. | default |
| technical-blog-writer | Writes one engineering blog post for business readers, Netflix/Uber style. Use when turning a scaling, cost, or reliability win into a plain-language post with visuals. | default |


### Platform (11)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| chaos-engineering | Designs resilience tests: failure-mode catalogs, game days, fault injection, degradation audits. Use when planning a game day, testing fallbacks, or adding chaos tests to CI on Firebase/GCP. | default |
| ci-cd-pipeline | Generates GitHub Actions CI/CD workflows for web, mobile, and Firebase. Use when setting up build, test, and deploy pipelines, environment approvals, or keyless GCP auth for a repo. | default |
| disaster-recovery | Designs disaster recovery plans: RTO/RPO tiers, Firestore and Cloud SQL backups, failover, DR drills. Use when planning backups, multi-region failover, or a DR test before launch or an audit. | default |
| dora-metrics | Measures DORA delivery metrics and SPACE developer experience from git, CI, and incident data. Use when baselining deploy frequency, lead time, change fail rate, recovery time, or reporting engineering health. | default |
| edge-computing | Designs CDN caching, invalidation, and Next.js proxy routing on Vercel/Firebase. Use when cutting TTFB, setting Cache-Control, geo-routing, edge auth, or rate limits. | default |
| engagement-automation | Picks and configures recurring automation: /loop, cloud routines, CI cron, or hooks. Use when putting engagement work on autopilot: weekly audits, monthly reports, maintenance loops, PR-triggered reviews. | default |
| green-software | Measures and cuts software carbon (SCI score, carbon-aware regions, ESG reports). Use when asked for a carbon footprint, sustainability audit, green architecture, or an SCI score. | default |
| incident-response | Guides live production incidents; builds on-call runbooks, severity levels, and post-mortems. Use when something is down or degraded now, or when setting up on-call, escalation, or a post-mortem. | default |
| infrastructure-scaffold | Generates Firebase, GCP, Vercel, and Docker configs with dev/staging/prod separation and cost guards. Use when setting up hosting, Cloud Run, Functions, secrets, environments, or budgets for a project. | default |
| observability | Sets up logging, tracing, SLOs, burn-rate alerts, and dashboards (Crashlytics, Sentry, Datadog, GCP). Use when adding monitoring to a service, defining SLOs, or fixing noisy or missing alerts. | default |
| release-management | Plans mobile and web releases: versions, staged rollouts, rollback, changelogs. Use when cutting a release, shipping to Play or the App Store, planning a rollout or rollback, or store listings (ASO). | default |


### Product (11)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| customer-onboarding | Designs onboarding and activation for mobile and web apps. Use when designing a first-run flow, empty states, welcome emails, or tooltips, or when day-1/day-7 retention or time-to-value is weak. | default |
| design-studio | Full design studio: brand, UX architecture, screens, design systems, assets. Use for any design assignment, from idea, sketch, PRD, or existing app to screens and hand-off. | default |
| design-system | Builds and governs component libraries from design-studio tokens. Use when setting up Storybook, Showkase, a SwiftUI catalog, token builds, or DS contribution rules. | default |
| feature-audit | Post-ship completeness audit of one feature. Use after finishing a feature or before marking a PR ready, to find missing tests, wiring, error handling, a11y, and analytics. | Read, Grep, Glob |
| feature-flags | Implements feature flags with Firebase Remote Config or LaunchDarkly. Use when adding a flag, kill switch, staged rollout, or experiment flag, or cleaning up stale flags. | default |
| market-research | Sourced market research: TAM/SAM/SOM, competitors, ICP, pricing, go/no-go. Use when sizing a market, profiling competitors or buyers, or deciding whether to enter. | Read, Grep, Glob, WebSearch, WebFetch |
| portfolio-registry | Creates and maintains PORTFOLIO.md, the registry of every product, stack, team, and stage. Use when setting up the portfolio, registering or updating a product, or health-checking a stale registry. | default |
| product-design | Quick spec for one screen or component, or a review of existing UI against HIG, M3, and WCAG. Use when a developer needs states, a11y, and handoff notes, not full design work. | default |
| product-manager | Product strategy and prioritization. Use when asked to prioritize features, score a backlog with RICE, write OKRs, build a Now/Next/Later roadmap, or write a feature brief. | default |
| technology-radar | Builds and maintains a portfolio technology radar (Adopt/Trial/Assess/Hold) with migration plans. Use when choosing or retiring a technology, running a quarterly tech review, or planning a migration off Hold tech. | default |
| uat | Plans and runs user acceptance testing with a go/no-go gate. Use when a feature or release candidate reaches staging and needs stakeholder sign-off before production. | default |


### Security (4)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| accessibility-audit | WCAG 2.2 AA audit of Android, iOS, and web UI with severity-ranked findings. Use when checking accessibility, a11y, screen reader support, touch targets, or contrast before a release or after a complaint. | Read, Grep, Glob |
| compliance-architect | Designs HIPAA, COPPA, GDPR, CCPA, and PCI compliance: consent, audit trails, data classification. Use when an app handles health, kids', EU, California, or card data, or needs a BAA/DPA check. | default |
| qsbs-compliance | Checks IRC §1202 QSBS qualification for C-corps under both OBBBA regimes. Use when an equity event, entity change, asset growth, or revenue mix could affect QSBS, or for an annual QSBS health check. | Read, Grep, Glob |
| security-review | Security audit of code, APIs, mobile apps, LLM features, and Firebase/cloud config, mapped to OWASP. Use when asked to check security, find vulnerabilities, or review before launch or after adding auth, payments, or PII. | Read, Grep, Glob |


### Tax (12)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| audit-risk-substantiation | Rates audit and penalty risk on tax positions and builds the defense file. Use when judging a position's risk, deciding Form 8275 disclosure, or answering an IRS notice. | default |
| cpa-benchmark | Scores tax competency on a CPA-exam-grade question bank. Use when baselining, gating a filing season, or regression-testing a tax engine or tax skills after changes. Runner needs Node. | default |
| cpa-standards | Applies Circular 230, AICPA SSTS, and §7216 to tax work. Use when deciding if a position can be taken or must be disclosed, or on preparer duties, workpapers, conflicts, or confidentiality. | default |
| deductions-and-credits | Qualifies deductions, credits, and exclusions against IRC tests. Use when asked whether something is deductible, which credits apply, or what a return is leaving unclaimed. | default |
| estimated-tax-compliance | Computes quarterly estimated tax, safe harbors, and withholding. Use when sizing or timing 1040-ES or corporate estimates, avoiding an underpayment penalty, or changing a W-4. | default |
| irc-lookup | Finds and cites controlling Internal Revenue Code authority. Use when a tax position needs a statutory cite, a citation needs checking, or a pre-2025 rule may have changed under OBBBA. | default |
| nonprofit-dissolution | Winds down a New York nonprofit and its exempt-org filings. Use when dissolving a not-for-profit: final Form 990 with Schedule N, NY AG approval, Certificate of Dissolution, payroll closeout. | default |
| return-review | Reviews a computed tax return before handoff. Use when a return is done and needs a second pass: tie-outs, cross-form checks, prior-year variances, diagnostics, and missed opportunities. | default |
| software-dev-tax | Determines tax treatment of software development costs. Use when accounting for engineering spend under §174A, claiming a §41 R&D credit, sizing QREs, or allocating costs by repo. | default |
| tax-preparation | Prepares a tax return and CPA handoff package. Use when preparing a 1040, 1120, 1120-S, 1065 or Schedule C, gathering tax documents, reconciling 1099s, or filing information returns. | default |
| tax-recommendations | Turns tax analysis into a ranked, dated action plan. Use when a client asks what to do, wants a year-end tax plan, or needs a client-facing deliverable with quantified savings. | default |
| tax-strategies | Designs legal tax-reduction strategies. Use when asked how to pay less tax, choose an entity (S corp vs C corp), plan a sale or exit, or use QSBS, timing, or retirement stacking. | default |


## 3. Agents


### Business (5)

| Agent | Purpose | Tools |
| --- | --- | --- |
| financial-analyst | Builds forecasts, unit economics, and scenarios from pricing and cost code. Use when you need a revenue forecast, unit-economics model, or P&L projection. | Read, Grep, Glob, Bash |
| investor-relations | Drafts board updates, investor reports, KPI packs, and raise narratives. Use when preparing investor-facing materials from product and financial data. | Read, Grep, Glob, Bash |
| market-intelligence | Market sizing (TAM/SAM/SOM), industry structure, trends, and timing. Use when validating a market, sizing an opportunity, or testing an investment thesis. | Read, Grep, Glob, Bash, WebSearch, WebFetch |
| ops-finance | Operational finance: invoices, 1099 tracking, month-end close, filing inventory. Use for Cure bookkeeping and multi-entity ops; tax positions go to tax-analyst. | Read, Grep, Glob, Bash |
| tax-analyst | Drafts tax workpapers, reviews, estimates, and plans for CPA review. Use when preparing or reviewing a return, planning estimates, scoring audit risk, or treating dev costs. | Read, Grep, Glob, Bash |


### Data (3)

| Agent | Purpose | Tools |
| --- | --- | --- |
| ab-test-analyst | Designs and analyzes A/B tests: sample size, significance, guardrails. Use when designing an experiment, sizing a test, or interpreting A/B results. | Read, Grep, Glob, Bash |
| data-analyst | Explores schemas, writes analytical queries, and checks data quality. Use when mapping a data model, answering a data question, or investigating anomalies. | Read, Grep, Glob, Bash |
| metrics-dashboard | Specifies KPIs, SLOs/SLIs, alert thresholds, and dashboard layouts. Use when designing dashboards or alerting for engineering, product, or business metrics. | Read, Grep, Glob, Bash |


### Engineering (18)

| Agent | Purpose | Tools |
| --- | --- | --- |
| api-validator | Checks API code against its OpenAPI or GraphQL spec. Use when validating contract coverage, error consistency, or breaking changes before merge or release. | Read, Grep, Glob, Bash |
| ci-debugger | Diagnoses failed CI/CD runs from logs and proposes the minimal fix. Use when a GitHub Actions, Firebase, Fastlane, or Docker build fails. | Read, Grep, Glob, Bash |
| code-reviewer | Reviews code against Cure standards: security, architecture, tests. Use when reviewing a diff, file set, or PR; reports every finding with severity and confidence. | Read, Grep, Glob |
| codebase-explainer | Explains a codebase with file:line citations. Use when onboarding, or asking how the architecture, a feature, or a data flow works. | Read, Grep, Glob, Bash |
| dependency-auditor | Audits dependencies for CVEs, staleness, licenses, and supply-chain risk. Use after adding or upgrading packages, or before a release. | Read, Grep, Glob, Bash |
| deployment-validator | Pre-deploy gate: env vars, secrets, flags, build, tests, rollback readiness. Use before deploying to staging or production; returns GO/NO-GO with findings. | Read, Grep, Glob, Bash |
| doc-generator | Generates docs from source: API docs, ADRs, changelogs, onboarding guides. Use when documentation is missing or has drifted from the code. | Read, Grep, Glob, Bash |
| equity-analyst | Public-equity research: filings, earnings, catalysts, valuation thesis. Use when researching a listed company or updating a thesis after earnings. | Read, Grep, Glob, Bash, WebFetch |
| investment-banker | M&A and capital-markets analysis: comps, DCF, LBO, accretion/dilution. Use when valuing a company for a deal or drafting a teaser, CIM, or buyer list. | Read, Grep, Glob, Bash |
| migration-validator | Reviews DB migrations for rollback safety, locking, and zero-downtime fit. Use before applying migrations to staging or production; reports every finding. | Read, Grep, Glob, Bash |
| pr-reviewer | Reviews a branch diff for bugs, security, performance, tests, standards. Use before merging a PR; returns every finding with severity, confidence, and a verdict. | Read, Grep, Glob, Bash |
| private-equity-analyst | Private-markets analysis: screening, diligence, LBO returns, IC memos. Use when sourcing or diligencing a private deal or monitoring a portfolio company. | Read, Grep, Glob, Bash |
| project-bootstrapper | Scaffolds a new Android, iOS, Next.js, or Firebase project to Cure standards. Use when starting a repo from scratch, not when adding features to an existing one. | Read, Grep, Glob, Bash, Edit, Write |
| qa-engineer | Adversarial QA: test plans, edge cases, regression scope, bug triage, ship gate. Use when a change needs a QA pass or a ship/no-ship call beyond running tests. | Read, Grep, Glob, Bash |
| refactor-assistant | Behavior-preserving refactors with tests run before and after each step. Use when restructuring code that must not change behavior; stops on a red baseline. | Read, Grep, Glob, Bash, Edit, Write |
| release-coordinator | Runs a release: version bump, changelog, validation, tag, rollback plan. Use when cutting a web, mobile, or backend release; confirms before tagging or publishing. | Read, Grep, Glob, Bash, Edit |
| system-architect | Architecture reviews, RFCs, and ADRs with explicit trade-offs. Use when choosing a technology, drawing service boundaries, or reviewing a system design. | Read, Grep, Glob, Bash |
| test-runner | Runs the test suite, checks coverage, and flags skipped or flaky tests. Use after writing code or before a commit; reports results and doesn't fix code. | Read, Grep, Glob, Bash |


### Legal (2)

| Agent | Purpose | Tools |
| --- | --- | --- |
| contract-reviewer | Business-risk review of SOWs, MSAs, NDAs, and contracts. Use when checking terms for scope, payment, IP, liability, or termination risk. Not legal advice. | Read, Grep, Glob |
| legal-compliance | Flags QSBS, FERPA, NCAA, trademark, and entity-compliance risk. Use when checking a portfolio company or codebase against those regimes. Not legal advice. | Read, Grep, Glob |


### Marketing (5)

| Agent | Purpose | Tools |
| --- | --- | --- |
| brand-guardian | Audits voice, terminology, microcopy, and visual tokens for consistency. Use when reviewing UI copy, naming, or visual identity against a brand or style guide. | Read, Grep, Glob |
| campaign-analyst | Analyzes marketing attribution, funnels, CAC/LTV, and channel ROI. Use when evaluating campaign performance or auditing UTM and conversion tracking. | Read, Grep, Glob, Bash |
| content-strategist | Content strategy: editorial calendars, briefs, SEO pillars, distribution. Use when planning content or auditing existing content against growth goals. | Read, Grep, Glob, Bash, WebSearch |
| growth-analyst | Analyzes activation, retention, virality, and monetization. Use when looking for growth levers or diagnosing a funnel or retention drop from code and data. | Read, Grep, Glob, Bash |
| technical-content-strategist | Turns engineering work into plain-language posts and visuals. Use when writing a technical story for business readers, with analogies and ROI framing. | Read, Grep, Glob, WebFetch, WebSearch |


### Product (4)

| Agent | Purpose | Tools |
| --- | --- | --- |
| competitive-intel | Competitive analysis: feature matrices, positioning, pricing, moats. Use when comparing the product to competitors or looking for differentiation gaps. | Read, Grep, Glob, Bash, WebSearch, WebFetch |
| product-analyst | Analyzes feature adoption, user journeys, and PMF signals. Use when auditing analytics coverage or asking how users move through the product. | Read, Grep, Glob, Bash |
| roadmap-strategist | Builds roadmaps with RICE scoring, dependencies, and capacity. Use when prioritizing a backlog, sequencing work, or planning the next quarter. | Read, Grep, Glob, Bash |
| ux-researcher | Usability review from UI code: IA, flows, forms, feedback, cognitive load. Use when auditing a product's UX or planning user research. | Read, Grep, Glob |


### Security (3)

| Agent | Purpose | Tools |
| --- | --- | --- |
| accessibility-checker | WCAG 2.2 AA check of web, Android, and iOS UI code. Use when UI changes need an accessibility pass; reports every finding with severity and confidence. | Read, Grep, Glob |
| firebase-security-auditor | Audits Firestore, Storage, and RTDB security rules against the data model. Use after changing rules or Firestore schema, or before a Firebase deploy. | Read, Grep, Glob, Bash |
| skill-security-auditor | Static security audit of skill, agent, and persona files. Use before merging changes under skills/, agents/, or personas/; returns PASS/WARN/FAIL and every finding. | Read, Grep, Glob |


## 4. Personas

| Persona | Description | Skills referenced |
| --- | --- | --- |
| cure-engagement-pm | Engagement PM persona: sprint cadence, scope, burn, client comms, handoff. Use when running delivery on a Cure client engagement. | 13 |
| cure-product-lead | Product lead persona: discovery, roadmap, metrics, stakeholders. Use when deciding what to build and why on a Cure client engagement. | 17 |
| cure-solo-consultant | Solo consultant persona covering tech, product, and PM. Use on small or early-stage engagements where one person ships the smallest viable thing. | 20 |
| cure-tech-lead | Engineering lead persona: architecture, quality bar, reviews, mentoring. Use when making technical decisions or reviews on a Cure client engagement. | 24 |


## 5. Hooks

| Event | Matcher | Type | What it does |
| --- | --- | --- | --- |
| SessionStart | startup | command | echo 'Cure Consulting Group ProductEngineeringSkills plugin loaded (v7.9.1). 103 skills (domain-organized), 4… |
| SessionStart | startup | command | python3 -c " |
| SessionStart | startup | command | echo "Git branch: $(git branch --show-current 2>/dev/null \|\| echo 'not a git repo'). Uncommitted changes: $(g… |
| SessionStart | startup | command | if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && { [ -d .claude ] \|\| [ -d .git ]; }; then PROVISIONED=''; if [ ! -f .cl… |
| PreCompact | auto\|manual | command | echo 'CONTEXT RE-INJECTION AFTER COMPACTION — Cure Consulting Group standards (always apply):\n- Clean Archit… |
| PostCompact | auto\|manual | command | echo 'Context compacted. Cure Consulting Group plugin active — 103 skills, 40 agents, 4 personas. Use /cure-p… |
| ConfigChange | skills | command | if [ -f scripts/audit-library.py ]; then python3 scripts/audit-library.py --fail-under 8 >/dev/null 2>&1 \|\| e… |
| PostToolUseFailure | Bash | prompt | A Bash command failed. Tool input and error output: $ARGUMENTS |
| PostToolUseFailure |  | command | python3 -c " |
| UserPromptSubmit |  | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" prompt |
| PreToolUse | Edit\|Write | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" edit |
| PreToolUse | Edit\|Write | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" skill-content |
| PreToolUse | Bash | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" bash |
| PreToolUse | Skill | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" telemetry |
| Stop |  | prompt | You are a quality gate reviewing the end of a Claude Code turn. Context: $ARGUMENTS |
| Stop |  | command | python3 -c " |
| SubagentStop | refactor-assistant\|project-bootstrapper\|release-coordinator | command | echo "Write-capable agent finished. Quality checklist:\n- Tests added/passing? → test-runner agent\n- Lint/ty… |


## 6. Rules

| Rule | Globs | Summary |
| --- | --- | --- |
| android.md | **/*.kt, **/*.java | - Use Clean Architecture: domain (pure Kotlin), data (DTOs + repos), presentation (ViewModels + Compose) |
| cicd.md | .github/workflows/**,**/.github/workflows/** | When editing GitHub Actions workflows, follow these standards: |
| docker.md | **/Dockerfile*,**/docker-compose*,**/.dockerignore | When editing Docker files, follow these standards: |
| firebase.md | **/functions/**, **/firestore*, **/*.rules, **/firebase.json | - Cloud Functions v2 (onCall, onRequest, scheduled, Firestore triggers) |
| go.md | **/*.go | When editing Go files, follow these standards: |
| ios.md | **/*.swift | - Use Clean Architecture: Domain (protocols + models), Data (implementations), Presentation (ViewModels + Views) |
| python.md | **/*.py | When editing Python files, follow these standards: |
| rust.md | **/*.rs | When editing Rust files, follow these standards: |
| sql.md | **/*.sql,**/migrations/** | When editing SQL files or migrations, follow these standards: |
| terraform.md | **/*.tf,**/*.tfvars,**/terraform/** | When editing Terraform or infrastructure-as-code files, follow these standards: |
| web.md | **/*.ts, **/*.tsx, **/*.js, **/*.jsx | - Next.js App Router — Server Components by default, Client Components only for interactivity |


## 7. Output Styles

| Style | Description |
| --- | --- |
| api-specification | Output style for API documentation — OpenAPI endpoints, request/response schemas, error formats, and authentication flows. |
| architecture-decision | Output style for Architecture Decision Records (ADRs) — context, decision, consequences, alternatives considered. |
| audit-report | Audit Report Style |
| code-generation | Code Generation Style |
| financial-analysis | Financial Analysis Style |
| monitoring-alert | Output style for monitoring and alerting configurations — SLO/SLI definitions, alert rules, dashboard layouts, and escalation policies. |
| prd | PRD & Strategy Document Style |
| runbook | Output style for operational runbooks — step-by-step procedures, troubleshooting guides, escalation paths, and recovery procedures. |
| test-plan | Output style for test plans — objectives, scope, test cases, data requirements, coverage metrics, and success criteria. |


## 8. MCP Servers

_n/a_


## 9. LSP Servers

_n/a_


---

_Regenerate with `python3 scripts/generate-overview.py`._
