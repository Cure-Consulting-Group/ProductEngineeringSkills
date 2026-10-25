# ProductEngineeringSkills — Overview

_Auto-generated. Do not edit by hand. Regenerate with `python3 scripts/generate-overview.py`._

## 1. Summary

| Field | Value |
| --- | --- |
| Plugin | cure-product-engineering |
| Version | 7.13.0 |
| Skills | 106 |
| Agents | 41 |
| Personas | 4 |
| Hooks (entries) | 11 |
| Rules | 11 |
| Output Styles | 0 |
| MCP Servers | 4 |
| LSP Servers | 2 |


## 2. Skills


### Business (14)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| bid-decision | Makes the bid/no-bid call: kill criteria, weighted scorecard, win odds, bid cost. Use when deciding whether to commit to a proposal, or when a pursuit is drifting. | Read, Grep, Glob, Bash(ls:*), Bash(sed -n:*), Bash(date:*), Write, Edit, WebSearch |
| burn-rate-tracker | Models burn, runway scenarios, break-even, and cash-flow projections. Use when asking how long cash lasts, when to raise or cut, or planning a studio or product budget. | Read, Grep, Glob, WebSearch |
| buyer-intelligence | Builds a buyer, incumbent, and renewal-date database from declined bids and award notices. Use when a bid is declined, a sole source or award notice appears, or building a buyer dossier. | Read, Grep, Glob, Bash(ls:*), Bash(sed -n:*), Bash(date:*), Write, Edit, WebSearch, WebFetch |
| capture-management | Builds a public-sector pipeline: target profile, sourcing, pre-RFP positioning, teaming. Use when entering a government market, choosing which bids to chase, or building past performance. | Read, Grep, Glob, Bash(ls:*), Bash(sed -n:*), Write, Edit, WebSearch, WebFetch |
| engineering-cost-model | Estimates internal build cost: dev hours, cloud spend, maintenance, build-vs-buy. Use when asking what a feature or product will cost or take to build. | Read, Grep, Glob, WebSearch |
| finops | Optimizes Firebase and GCP cost: budgets, alerts, right-sizing, AI API spend. Use when a cloud bill spikes, budgeting a live bill, or cutting infra and LLM costs. | default |
| fundraising-materials | Builds pitch decks, the ask and use of funds, and the investor outreach pipeline. Use when preparing a seed or Series A raise: deck, intro blurb, target list, or process plan. | Read, Grep, Glob, WebSearch |
| investor-reporting | Drafts investor updates, board decks, portfolio P&L, data rooms, and cap-table/SAFE models. Use when writing the monthly investor update, a quarterly board deck, or diligence prep. | default |
| proposal-generator | Drafts consulting proposals and SOWs: scope, milestones, pricing, payment terms. Use when writing a client proposal, a statement of work, or a change order for Cure. | default |
| public-sector-contracting | Reviews public-sector contract terms: liability, IP, termination, non-appropriation. Use when reading a municipal, state, or federal contract form or its insurance terms, or choosing exceptions. | Read, Grep, Glob, Bash(ls:*), Bash(pdftotext:*), Write, Edit, WebSearch |
| rfp-evaluation | Extracts every RFP/RFQ requirement into a compliance matrix. Use when a solicitation has passed triage and you need what it requires and how its rubric maps to effort. | Read, Grep, Glob, Bash(ls:*), Bash(mkdir -p 00-source/extracted), Bash(pdftotext:*), Write, Edit, WebSearch |
| saas-financial-model | Models SaaS unit economics, MRR/ARR projections, and pricing tiers. Use when computing LTV, CAC, payback, or churn, projecting MRR, or setting subscription prices. | Read, Grep, Glob, WebSearch |
| solicitation-triage | Screens public-sector solicitations and portal alert batches to a verdict in under an hour. Use when a new RFP, RFQ, bid notice, or weekly bid-portal feed arrives. | Read, Grep, Glob, Bash(ls:*), Bash(sed -n:*), Bash(date:*), Bash(mkdir -p 00-source/extracted), Bash(pdftotext:*), Write, Edit, WebSearch |
| technical-estimation | Builds defensible software estimates with ranges: PERT, reference class, risk reserve. Use when an estimate will be bid on, contracted, or audited, e.g. an RFP cost volume. | Read, Grep, Glob, Bash(ls:*), Bash(git ls-files:*), Write, Edit, WebSearch |


### Engineering (40)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| agent-designer | Designs LLM agent internals: tool schemas, memory, termination, evals, cost, failure modes. Use when an agent or multi-agent system is the chosen shape and needs a design. | default |
| agent-workflow-designer | Picks the shape of an LLM system: single call, workflow pattern, or autonomous agent. Use when deciding how to structure an AI feature, or when an agent is too slow, costly, or flaky. | default |
| ai-feature-builder | Builds user-facing LLM features: client wrapper, prompts, streaming UX, kill switch. Use when adding chat, summarization, extraction, or generation to an app, with fallbacks. | default |
| analytics-implementation | Designs analytics event taxonomies, tracking plans, funnels, and consent flows. Use when instrumenting product analytics (GA4/Firebase, Mixpanel, PostHog) or auditing events. | default |
| android-design-expert | Applies Material Design 3 to Android screens and components. Use when designing or reviewing Compose UI for dynamic color, adaptive layouts, navigation, motion, or M3 Expressive. | default |
| android-feature-scaffold | Scaffolds Android feature modules (Clean Architecture, MVI, Compose, Hilt). Use when creating a new Kotlin feature, screen, ViewModel, repository, or use case in an Android app. | default |
| api-architect | Designs REST/GraphQL API contracts: errors, auth, rate limits, versioning, OpenAPI. Use when designing endpoints or an API's error, auth, or deprecation policy. | default |
| api-gateway | Designs API gateway and BFF layers: middleware order, aggregation, auth, federation. Use when adding a gateway, a mobile/web BFF, or federating GraphQL subgraphs. | default |
| client-communication | Drafts client status emails, risk escalations, executive summaries, and demo scripts. Use when writing a weekly client update, escalating a blocker, or preparing a stakeholder demo or QBR. | default |
| client-handoff | Builds client handoff packages: architecture, runbooks, credential transfer, KT plan, SLA. Use when handing a project, phase, or support role to a client team or winding down an engagement. | default |
| cure-infra-bootstrap | Runs Cure's bootstrap CLI (init/apply/doctor/inventory). Use when setting up, upgrading, or drift-checking CLAUDE.md, .claude/, and rules in a project. | Read, Bash |
| data-migration | Plans and runs data migrations: ETL, backfills, dual-write, cutover, rollback. Use when moving or reshaping existing data across databases, Firestore, or legacy systems without downtime. | default |
| database-architect | Chooses databases and designs SQL/Room schemas, indexes, and query plans. Use when picking an engine, modeling relational data, adding indexes, or fixing slow queries. | default |
| e2e-testing | Writes E2E suites (Playwright, Compose, XCUITest) with page objects and CI wiring. Use when adding E2E, smoke, or visual regression tests for a user flow, or fixing flaky E2E tests. | default |
| env-secrets-manager | Audits .env files and secrets, read-only. Use when designing an .env schema, scanning for leaked keys, responding to a leak, planning rotation, or moving to a secret manager. | Read, Grep, Glob |
| firebase-architect | Designs Firestore data models, security rules, Cloud Functions v2, and App Check. Use when building a Firebase feature, writing rules or triggers, or wiring a Firestore data layer. | default |
| git-worktree-manager | Sets up git worktrees with isolated ports, env files, and databases. Use when running parallel features, a hotfix, or a PR review without stashing or switching the main checkout. | default |
| i18n | Internationalizes and localizes Android, iOS, and Next.js apps. Use when externalizing strings, adding a locale or RTL, fixing plurals or date/currency formats, or setting up translation. | default |
| interview-system-designer | Designs engineering interview loops: stages, rubrics, question banks, AI-use policy. Use when hiring engineers, setting debrief rules, or fixing a loop with poor pass or accept rates. | default |
| ios-architect | Scaffolds Swift/SwiftUI iOS features: Clean Architecture, MVVM, Swift 6 concurrency. Use when creating a new iOS feature, view model, repository, or StoreKit 2 flow. | default |
| ios-design-expert | Applies Apple HIG to iOS/iPadOS screens and components. Use when designing or reviewing SwiftUI UI for Liquid Glass, navigation, tab bars, Dynamic Type, SF Symbols, or widgets. | default |
| llmops | Runs LLM features in production: evals, prompt versions, cost, caching, routing. Use when an AI feature needs eval gates, spend control, or a model or prompt rollout. | default |
| mcp-server-builder | Designs and builds MCP servers: tool schemas, resources, transports, auth. Use when building a Model Context Protocol server, wrapping an API as MCP tools, or migrating to a new SDK/spec. | default |
| micro-frontends | Decides whether and how to split a web frontend into independent apps. Use when teams block each other's releases, or weighing Vercel microfrontends, multi-zones, or module federation. | default |
| monorepo-navigator | Speeds up and fixes monorepos (pnpm, Turborepo, Nx, Bazel). Use when CI is slow, caches miss, or dependencies drift, or when joining, creating, or extracting a package from one. | default |
| nextjs-feature-scaffold | Scaffolds Next.js 16 App Router features in TypeScript. Use when adding a page, route, Server Action, form, or CRUD feature to a Next.js app, with Server/Client split, caching, auth, and tests. | default |
| notification-architect | Designs push (FCM/APNs/web), in-app, email, and SMS notifications. Use when adding push, notification preferences, email deliverability, or multi-channel dispatch. | default |
| offline-first | Designs offline-first Android, iOS, and web apps: local storage, sync, conflicts. Use when an app must work without network, queue writes, resolve sync conflicts, or show optimistic UI. | default |
| parallel-agent-orchestration | Runs parallel agent sessions on one repo: decomposition, budget, locks, merge order. Use when splitting a wave of work across 2+ agents or subagents. | default |
| performance-review | Sets performance budgets and load-test plans for web, mobile, backend. Use when an app or page is slow, before a launch or scale event, or to set Core Web Vitals targets. | default |
| project-bootstrap | Writes a tailored CLAUDE.md and STATE.md for a repo by interview. Use when onboarding an existing or new repo to agent work by hand, without the Cure manifest CLI. | default |
| project-manager | Plans sprints and delivery: capacity, RACI, risk registers, dependencies, retros. Use when planning a sprint, sizing capacity, building a timeline, or tracking delivery risk. | default |
| rag-architect | Designs RAG pipelines: chunking, embeddings, vector store, reranking. Use when building or auditing retrieval over documents, a knowledge base, or semantic search with retrieval evals. | default |
| sdlc | Writes engineering specs: PRDs, ADRs, RFCs, epics, user stories, task and test specs. Use when asked to write a PRD or ADR, draft an RFC, spec a feature, or break work into stories. | default |
| self-improving-memory | Curates agent auto-memory (MEMORY.md plus user/feedback/project/reference entries). Use when seeding memory for a new engagement, auditing or consolidating it, or checking for stale entries. | default |
| stitch-design | Generates, syncs, and audits UI screens through Google Stitch MCP. Use when the user names Stitch or DESIGN.md, or the repo has a .stitch/ folder: screen generation, token export, design-drift audits. | default |
| stripe-integration | Adds Stripe payments via Firebase Cloud Functions, Cure's default stack. Use when adding checkout, subscriptions, a billing portal, saved cards, or payment webhooks synced to Firestore. | default |
| test-accounts | Sets up QA test accounts, personas, seed/reset scripts, and env-guarded credentials. Use when setting up test users, seed data, receivable QA email addresses, or test-account teardown. | default |
| testing-strategy | Defines test architecture: pyramid, frameworks, coverage gates, flaky-test policy. Use when setting up testing, setting test standards, or asking 'what tests do we need'. | default |
| web-design-expert | Guides web UI design: responsive layout, tokens, Tailwind v4, dark mode, motion. Use when designing or reviewing pages and components for layout, CSS architecture, or theming. | default |


### Finance (4)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| comps-analysis | Values a company against trading peers with EV/Revenue, EV/EBITDA, and P/E multiples. Use when benchmarking valuation multiples or pricing a company off public comparables. | default |
| dcf-modeling | Builds DCF valuations: unlevered FCF, WACC, terminal value, equity bridge. Use when estimating intrinsic value or a per-share price from projected cash flows. | default |
| equity-research | Analyzes a public company from 10-K/10-Q filings and earnings calls. Use when digesting earnings, reading SEC filings, or drafting a buy/hold/sell thesis with catalysts. | default |
| merger-modeling | Models M&A accretion/dilution: pro-forma EPS, deal mix, purchase price allocation. Use when judging an acquisition's financial impact on the buyer, including synergies. | default |


### Legal (4)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| bar-benchmark | Scores legal competency on a NY bar-style bank (MBE, NYLE, MPRE, MEE essays). Use when baselining a model, gating legal skill changes, or measuring the legal skills' uplift live. | default |
| legal-doc-scaffold | Drafts first-pass ToS, privacy policy, SOW, NDA, DPA, EULA, and refund policy. Use when a product or engagement needs a starting draft for attorney review, from a required-clause checklist. | default |
| legal-doctrine | Explains black-letter law and NY practice with bar-exam traps. Use when analyzing a legal issue (contracts, CPLR, estates, privacy, NIL, IP, ethics) or a bar-style question. | default |
| legal-research | Researches law and verifies citations, New York first. Use when a legal question needs controlling authority, a memo's citations need checking, or a case or statute cite must be confirmed. | default |


### Marketing (6)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| go-to-market | Writes launch plans: positioning, messaging, channels, launch phases. Use when launching a product, entering a new market, or planning a major feature release. | default |
| growth-engineering | Designs retention, referral, lifecycle, and trial/paywall systems. Use when improving retention, adding referrals, setting upgrade triggers, or reading cohort curves. | default |
| instagram-publishing-setup | Sets up programmatic Instagram publishing: Meta app, tester role, token, scheduler. Use when posting to Instagram from code, hosting its media, or stuck on Insufficient Developer Role or a media_publish 400. | default |
| product-marketing | Writes platform-native social content for portfolio brands. Use when creating Reels, Shorts, LinkedIn or X posts, a campaign, a message house, or brand-voice copy. | default |
| seo-content-engine | Plans technical SEO and search content for websites. Use when a site needs to rank: SEO audit, metadata, JSON-LD, sitemaps, or keyword clusters. | default |
| technical-blog-writer | Writes one engineering blog post for non-technical readers, with analogies and visuals. Use when turning a scaling, cost, or reliability win into a publishable post. | default |


### Platform (11)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| chaos-engineering | Designs resilience tests: failure-mode catalogs, game days, fault injection. Use when planning a game day, testing fallbacks, auditing degradation, or adding chaos tests to CI on Firebase/GCP. | default |
| ci-cd-pipeline | Generates GitHub Actions CI/CD workflows for web, mobile, and Firebase. Use when setting up build, test, and deploy pipelines, environment approvals, or keyless GCP auth for a repo. | default |
| disaster-recovery | Designs DR plans: RTO/RPO tiers, backups, failover, drills. Use when planning Firestore or Cloud SQL backups, multi-region failover, or a DR test before launch or an audit. | default |
| dora-metrics | Measures DORA and SPACE metrics from git, CI, and incident data. Use when baselining deploy frequency, lead time, change fail rate, recovery time, or reporting engineering health. | default |
| edge-computing | Designs CDN caching, invalidation, and Next.js proxy routing on Vercel/Firebase. Use when cutting TTFB, setting Cache-Control, geo-routing, edge auth, or rate limits. | default |
| engagement-automation | Picks and configures recurring automation: /loop, cloud or desktop tasks, CI cron, hooks. Use when putting engagement work on autopilot: weekly audits, monthly reports, maintenance loops, PR-triggered reviews. | default |
| green-software | Measures and cuts software carbon (SCI score, carbon-aware regions, ESG reports). Use when asked for a carbon footprint, sustainability audit, green architecture, or an SCI score. | default |
| incident-response | Guides live incidents; builds on-call runbooks, severity levels, and post-mortems. Use when something is down or degraded now, or when setting up on-call, escalation, or a post-mortem. | default |
| infrastructure-scaffold | Generates Firebase, GCP, Vercel, and Docker configs per environment. Use when setting up hosting, Cloud Run, Functions, environments, or a Dockerfile for a project. | default |
| observability | Sets up logs, traces, SLOs, and alerts (Sentry, Crashlytics, Datadog, GCP). Use when adding monitoring, defining SLOs, or fixing noisy or missing alerts. | default |
| release-management | Plans mobile and web releases: versions, staged rollouts, rollback, changelogs. Use when cutting a release, shipping to Play or the App Store, planning a rollout or rollback, or store listings (ASO). | default |


### Product (11)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| customer-onboarding | Designs onboarding and activation for mobile and web apps. Use when designing a first-run flow, empty states, welcome emails, or tooltips, or when day-1/day-7 retention or time-to-value is weak. | default |
| design-studio | Designs whole products: brand, UX flows, multi-screen designs, tokens, assets. Use when designing a new app, product, or flow, or redesigning from a PRD, sketch, or existing app. | default |
| design-system | Builds and governs component libraries from design-studio tokens. Use when setting up Storybook, Showkase, a SwiftUI catalog, token builds, or DS contribution rules. | default |
| feature-audit | Audits one shipped feature for completeness. Use after finishing a feature or before marking a PR ready, to find missing tests, wiring, error handling, a11y, and analytics. | Read, Grep, Glob, Bash(git log:*), Bash(ls:*) |
| feature-flags | Implements feature flags with Firebase Remote Config or LaunchDarkly. Use when adding a flag, kill switch, staged rollout, or experiment flag, or cleaning up stale flags. | default |
| market-research | Researches markets with sources: TAM/SAM/SOM, competitors, ICP, pricing, go/no-go. Use when sizing a market, profiling competitors or buyers, or deciding whether to enter. | Read, Grep, Glob, WebSearch, WebFetch |
| portfolio-registry | Creates and maintains PORTFOLIO.md, the registry of every product, stack, team, and stage. Use when setting up the portfolio, registering or updating a product, or health-checking a stale registry. | default |
| product-design | Specs one screen or component, or reviews existing UI against HIG, M3, and WCAG. Use when a developer needs states, a11y, and handoff notes, not full design work. | default |
| product-manager | Prioritizes and sets product direction: RICE, OKRs, roadmaps, feature briefs. Use when asked to prioritize a backlog, write OKRs, build a roadmap, or write a one-page brief. | default |
| technology-radar | Builds a portfolio technology radar (Adopt/Trial/Assess/Hold). Use when choosing or retiring a technology, running a quarterly tech review, or planning a migration off Hold tech. | default |
| uat | Plans and runs user acceptance testing with a go/no-go gate. Use when a feature or release candidate reaches staging and needs stakeholder sign-off before production. | default |


### Security (4)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| accessibility-audit | Audits Android, iOS, and web UI against WCAG 2.2 AA, findings ranked by severity. Use when checking accessibility, screen readers, touch targets, or contrast before a release or after a complaint. | Read, Grep, Glob |
| compliance-architect | Designs HIPAA, COPPA, GDPR, CCPA, and PCI compliance: consent, audit trails. Use when an app handles health, kids', EU, California, or card data, or needs a BAA or DPA. | default |
| qsbs-compliance | Checks IRC §1202 QSBS qualification for C-corps under both OBBBA regimes. Use when an equity event, entity change, asset growth, or revenue mix could affect QSBS, or for an annual QSBS health check. | Read, Grep, Glob |
| security-review | Finds OWASP vulnerabilities in code, APIs, mobile apps, LLM features, and Firebase config. Use when asked to check security, before launch, or after adding auth, payments, or PII. | Read, Grep, Glob |


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
| code-reviewer | Reviews named files or uncommitted work against Cure standards. Use when checking work in progress before a commit; every finding with severity and confidence, no merge verdict. NOT for a branch before merge (pr-reviewer agent) or a bug-only pass (/code-review). | Read, Grep, Glob |
| codebase-explainer | Explains a codebase with file:line citations. Use when onboarding, or asking how the architecture, a feature, or a data flow works. | Read, Grep, Glob, Bash |
| dependency-auditor | Audits dependencies for CVEs, staleness, licenses, and supply-chain risk. Use after adding or upgrading packages, or before a release. | Read, Grep, Glob, Bash |
| deployment-validator | Pre-deploy gate: env vars, secrets, flags, build, tests, rollback readiness. Use before deploying to staging or production; returns GO/NO-GO with findings. | Read, Grep, Glob, Bash |
| doc-generator | Generates docs from source: API docs, ADRs, changelogs, onboarding guides. Use when documentation is missing or has drifted from the code. | Read, Grep, Glob, Bash |
| equity-analyst | Public-equity research: filings, earnings, catalysts, valuation thesis. Use when researching a listed company or updating a thesis after earnings. | Read, Grep, Glob, Bash, WebFetch |
| investment-banker | M&A and capital-markets analysis: comps, DCF, LBO, accretion/dilution. Use when valuing a company for a deal or drafting a teaser, CIM, or buyer list. | Read, Grep, Glob, Bash |
| migration-validator | Reviews DB migrations for rollback safety, locking, and zero-downtime fit. Use before applying migrations to staging or production; reports every finding. | Read, Grep, Glob, Bash |
| pr-reviewer | Reviews a branch against its base for bugs, security, performance, tests, standards. Use before merging a PR; every finding with severity and confidence, plus a merge verdict. NOT for uncommitted work or a file set (code-reviewer agent). | Read, Grep, Glob, Bash |
| private-equity-analyst | Private-markets analysis: screening, diligence, LBO returns, IC memos. Use when sourcing or diligencing a private deal or monitoring a portfolio company. | Read, Grep, Glob, Bash |
| project-bootstrapper | Scaffolds a new Android, iOS, Next.js, or Firebase project to Cure standards. Use when starting a repo from scratch, not when adding features to an existing one. | Read, Grep, Glob, Bash, Edit, Write |
| qa-engineer | Adversarial QA: test plans, edge cases, regression scope, bug triage. Use when a change needs a QA pass beyond running tests; gives a QA ship recommendation that feeds deployment-validator's GO/NO-GO, never the deploy call itself. | Read, Grep, Glob, Bash |
| refactor-assistant | Behavior-preserving refactors with tests run before and after each step. Use when restructuring code that must not change behavior; stops on a red baseline. | Read, Grep, Glob, Bash, Edit, Write |
| release-coordinator | Runs a release: version bump, changelog, validation, tag, rollback plan. Use when cutting a web, mobile, or backend release; confirms before tagging or publishing. | Read, Grep, Glob, Bash, Edit |
| system-architect | Architecture reviews, RFCs, and ADRs with explicit trade-offs. Use when choosing a technology, drawing service boundaries, or reviewing a system design. | Read, Grep, Glob, Bash |
| test-runner | Runs the test suite, checks coverage, and flags skipped or flaky tests. Use after writing code or before a commit; reports results and doesn't fix code. | Read, Grep, Glob, Bash |


### Legal (3)

| Agent | Purpose | Tools |
| --- | --- | --- |
| contract-reviewer | Business-risk review of SOWs, MSAs, NDAs, and contracts. Use when checking terms for scope, payment, IP, liability, or termination risk. Not legal advice. | Read, Grep, Glob |
| legal-analyst | Drafts NY-first legal research memos with every citation verified, for attorney review. Use when a legal question needs an IRAC answer with authority, or a draft's citations need checking. | Read, Grep, Glob, Bash |
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
| SessionStart | startup | command | echo 'Cure Consulting Group ProductEngineeringSkills plugin loaded (v7.13.0). 106 skills (domain-organized), … |
| SessionStart | startup | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" session-start |
| SessionStart | compact | command | printf '%b\n' 'STANDARDS RE-INJECTED AFTER COMPACTION — Cure Consulting Group standards (always apply):\n- Cl… |
| UserPromptSubmit |  | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" prompt |
| PreToolUse | Edit\|Write\|MultiEdit\|NotebookEdit | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" edit |
| PreToolUse | Edit\|Write\|MultiEdit\|NotebookEdit | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" skill-content |
| PreToolUse | Bash | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" bash |
| PreToolUse | Skill | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" telemetry |
| PostToolUse | Agent\|Task | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" agent-done |
| PostToolUseFailure |  | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" failure |
| Stop |  | command | python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" stop |


## 6. Rules

| Rule | Globs | Summary |
| --- | --- | --- |
| android.md | **/*.kt, **/*.kts, **/*.java, **/libs.versions.toml | - Clean Architecture: domain (pure Kotlin), data (DTOs + repositories), presentation (ViewModels + Compose) |
| cicd.md | .github/workflows/**, **/.github/workflows/**, **/.github/actions/** | When editing GitHub Actions workflows, follow these standards: |
| docker.md | **/Dockerfile*, **/*.dockerfile, **/compose*.{yaml,yml}, **/docker-compose*, **/.dockerignore | When editing Docker files, follow these standards: |
| firebase.md | **/functions/**, **/firestore*, **/*.rules, **/firebase.json | - Cloud Functions v2 (onCall, onRequest, scheduled, Firestore triggers) on the Node.js 22 runtime (`"engines": {"node": |
| go.md | **/*.go, **/go.mod | When editing Go files, follow these standards: |
| ios.md | **/*.swift | - Swift 6 language mode, complete strict concurrency — never `@unchecked Sendable`, `DispatchQueue` or completion handle |
| python.md | **/*.py, **/pyproject.toml | When editing Python files, follow these standards: |
| rust.md | **/*.rs, **/Cargo.toml | When editing Rust files, follow these standards: |
| sql.md | **/*.sql, **/migrations/** | When editing SQL files or migrations, follow these standards: |
| terraform.md | **/*.tf, **/*.tfvars, **/terraform/**, **/.terraform.lock.hcl | When editing Terraform or infrastructure-as-code files, follow these standards: |
| web.md | **/*.tsx, **/*.jsx, **/app/**/*.{ts,js}, **/components/**/*.{ts,js}, **/lib/**/*.{ts,js}, **/proxy.ts, **/middleware.ts, **/next.config.* | - Next.js 16 App Router — Server Components by default; `'use client'` only at interactive leaves |


## 7. Output Styles

_n/a_


## 8. MCP Servers

| Server | Type | Transport / URL / Command | Note |
| --- | --- | --- | --- |
| firebase | stdio | npx |  |
| github | http | https://api.githubcopilot.com/mcp/ |  |
| postgres | stdio | npx |  |
| sentry | http | https://mcp.sentry.dev/mcp |  |


## 9. LSP Servers

| Server | Extensions | Command |
| --- | --- | --- |
| python | .py, .pyi | npx -y --package=pyright@1.1.414 pyright-langserver --stdio |
| typescript | .js, .jsx, .ts, .tsx | npx -y typescript-language-server@6.0.2 --stdio |


---

_Regenerate with `python3 scripts/generate-overview.py`._
