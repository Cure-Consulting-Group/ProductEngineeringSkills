# ProductEngineeringSkills — Overview

_Auto-generated. Do not edit by hand. Regenerate with `python3 scripts/generate-overview.py`._

## 1. Summary

| Field | Value |
| --- | --- |
| Plugin | cure-product-engineering |
| Version | 7.1.2 |
| Skills | 80 |
| Agents | 39 |
| Personas | 4 |
| Hooks (entries) | 20 |
| Rules | 11 |
| Output Styles | 9 |
| MCP Servers | 4 |
| LSP Servers | 2 |


## 2. Skills


### Business (7)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| burn-rate-tracker | Model burn rates, runway scenarios, break-even analysis, and cash flow projections for multi-product venture studios | Read, Grep, Glob, WebSearch |
| engineering-cost-model | Engineering cost estimation — developer hours, infrastructure spend (Firebase/GCP/AWS), build-vs-buy analysis, and project budgeting for internal planning | Read, Grep, Glob, WebSearch |
| finops | Optimize cloud costs — budget alerts, resource right-sizing, usage analysis, FinOps practices, and cost allocation for Firebase and GCP | default |
| fundraising-materials | Generate pitch decks, investor updates, data room checklists, cap table scenarios, and fundraising pipeline management for venture-backed startups | Read, Grep, Glob, WebSearch |
| investor-reporting | Generate investor updates, board decks, portfolio financial reports, cap table scenarios, runway modeling, and fundraising pipeline tracking | default |
| proposal-generator | Generate consulting proposals and SOWs — project scoping, milestone-based pricing, deliverable definitions, and engagement structure | default |
| saas-financial-model | Model unit economics, MRR/ARR projections, pricing tiers, runway, and break-even analysis | Read, Grep, Glob, WebSearch |


### Engineering (39)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| agent-designer | Design single-agent and multi-agent systems — tool schemas, memory, termination, evals, cost, and failure modes | default |
| agent-workflow-designer | Choose the right agentic workflow pattern — chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, or autonomous agent | default |
| ai-feature-builder | Build production AI features with LLM integration, RAG pipelines, prompt engineering, and guardrails | default |
| analytics-implementation | Design event taxonomy, tracking plans, funnels, dashboards, and privacy/consent flows | default |
| android-design-expert | Expert Android design guidance following Material Design 3 — dynamic color, component tokens, adaptive layouts, motion system, and Jetpack Compose implementation patterns | default |
| android-feature-scaffold | Scaffold Android features with Clean Architecture, MVI, Jetpack Compose, Hilt, and Kotlin | default |
| api-architect | Design REST/GraphQL APIs with versioning, auth, rate limiting, and error standards | default |
| api-gateway | Design API gateway and BFF layers — rate limiting, request transformation, auth middleware, GraphQL federation, and mobile-optimized backends | default |
| client-communication | Generate client-facing artifacts — sprint demo scripts, stakeholder updates, risk escalation reports, and executive status summaries | default |
| client-handoff | Generate client handoff packages — architecture docs, runbooks, credential transfers, maintenance SLAs, and knowledge transfer plans for consulting engagements | default |
| cure-infra-bootstrap | Provision Cure's standardized Claude development infrastructure into any project (greenfield or existing). Idempotently scaffolds CLAUDE.md, STATE.md, .claude/{settings.json,skills,agents,rules,hooks}, .cursorrules, .gemini/config.yaml. Manifest-driven, version-pinned, conflict-aware. | Read, Bash |
| data-migration | Plan and execute data migrations — ETL pipelines, zero-downtime cutover, validation, rollback strategies, and legacy system integration | default |
| database-architect | Design database schemas, plan migrations, optimize queries, define indexing strategies for Firestore, PostgreSQL, and SQLite | default |
| e2e-testing | Generate end-to-end test suites with page objects, CI integration, visual regression, and cross-platform test strategies | default |
| env-secrets-manager | .env hygiene, secret leak detection, rotation playbooks, and migration to managed secret stores — read-only audits and recommendations across local, CI, and production environments | Read, Grep, Glob, Bash |
| firebase-architect | Design Firestore schemas, security rules, Cloud Functions, and data layer architecture | default |
| git-worktree-manager | Use git worktrees for parallel work — multiple client features, hotfixes, or PR reviews simultaneously without stash/branch-switch overhead | default |
| i18n | Implement internationalization and localization — string extraction, RTL support, locale-aware formatting, translation workflows, and platform i18n patterns | default |
| interview-system-designer | Design calibrated, fair, predictive engineering interview loops for client hires — from phone screen to debrief, with stage rubrics, question banks, and evaluation metrics | default |
| ios-architect | Scaffold iOS features with Swift/SwiftUI, Clean Architecture, MVVM, and structured concurrency | default |
| ios-design-expert | Expert iOS design guidance following Apple Human Interface Guidelines (HIG) — SF Symbols, Dynamic Type, navigation patterns, SwiftUI components, and platform-native interactions | default |
| llmops | Operationalize LLM features — prompt versioning, evaluation pipelines, cost optimization, guardrails, RAG monitoring, and model lifecycle management | default |
| mcp-server-builder | Design and build MCP (Model Context Protocol) servers — the integration protocol Claude Code, Codex, and other agents use to call tools, expose resources, and consume prompts | default |
| micro-frontends | Architect micro-frontend systems — module federation, monorepo management, shared dependencies, independent deployments, and cross-team coordination | default |
| monorepo-navigator | Navigate, work in, and improve monorepos — pnpm workspaces, Turborepo, Nx, Lerna, Yarn workspaces, Bazel, or untangling a folder that thinks it's a monorepo | default |
| nextjs-feature-scaffold | Scaffold Next.js features with App Router, Server/Client components, Tailwind, and data fetching patterns | default |
| notification-architect | Design notification systems — push (FCM/APNs), in-app messaging, email transactional flows, preference management, and delivery optimization | default |
| offline-first | Architect offline-first mobile apps — local storage, sync strategies, conflict resolution, optimistic UI, and background sync patterns | default |
| performance-review | Define performance budgets, load testing plans, optimization strategies, and monitoring dashboards across mobile, web, and backend | default |
| project-bootstrap | Bootstrap any project repo with CLAUDE.md and STATE.md — interviews the developer, inspects the codebase, and generates agent coordination files | default |
| project-manager | Sprint execution and delivery management — sprint planning, RACI matrices, risk registers, retrospectives, and velocity tracking for engineering teams | default |
| rag-architect | Design production RAG pipelines — chunking, embedding model selection, vector store choice, hybrid retrieval, reranking, and eval — with explicit cost and latency budgets | default |
| sdlc | Generate structured engineering documents — PRDs, ADRs, RFCs, Epics, User Stories, Task specs, and test specs from a feature description | default |
| self-improving-memory | Curate Claude Code auto-memory (user / feedback / project / reference) for an engagement — bootstrap, audit, detect patterns, and run health checks on MEMORY.md | default |
| stitch-design | AI-native UI design and screen generation via Stitch MCP — vibe design, mockup creation, screen generation, UI prototyping, design system management, DESIGN.md authoring, component export, screen-to-code handoff, design token sync, visual consistency audits, Stitch canvas manipulation, and high-fidelity wireframe production | default |
| stripe-integration | Integrate Stripe payments and subscriptions via Firebase Cloud Functions with webhook handling | default |
| test-accounts | Generate test account strategies, seed data scripts, test user personas, and environment-scoped credentials for all platforms | default |
| testing-strategy | Define the overall testing architecture — pyramid ratios, platform-specific frameworks (JUnit5/MockK, XCTest, Vitest/Playwright), coverage thresholds, and CI integration for a project or feature | default |
| web-design-expert | Expert web design guidance — responsive design, CSS architecture, design tokens, container queries, accessibility-first patterns, dark mode, and Tailwind/CSS implementation | default |


### Finance (4)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| comps-analysis | Performs Comparable Company Analysis (Comps) to value a company relative to peers. Use when you need to benchmark multiples (EV/EBITDA, P/E), analyze industry premiums, or calculate enterprise value. | default |
| dcf-modeling | Performs Discounted Cash Flow (DCF) valuation. Use when you need to calculate intrinsic value based on projected free cash flows, WACC, and terminal value. | default |
| equity-research | Conducts public equity research and investment analysis. Use when you need to analyze earnings calls, parse SEC filings (10-K, 10-Q), track catalysts, or draft investment theses. | default |
| merger-modeling | Performs Accretion/Dilution analysis for M&A transactions. Use when you need to model pro-forma financial impact, calculate synergy requirements, or analyze purchase price accounting. | default |


### Legal (1)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| legal-doc-scaffold | Generate Terms of Service, Privacy Policy, SOW, and NDA scaffolds with attorney disclaimer | default |


### Marketing (5)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| go-to-market | Pre-launch planning — positioning, channel strategy, pricing, launch timeline, and distribution playbooks for new products or major feature releases | default |
| growth-engineering | Build growth systems — activation funnels, referral programs, lifecycle automation, cohort analysis, and product-led growth patterns | default |
| product-marketing | Product voice and content marketing expert — generates platform-native content packages across Instagram, YouTube, LinkedIn, and X/Twitter for portfolio brands | default |
| seo-content-engine | Technical SEO and content strategy for web properties — meta tags, Open Graph, JSON-LD structured data, sitemap generation, keyword research, and content calendars | default |
| technical-blog-writer | Crafts high-impact technical blog posts modeled after Netflix/Uber engineering blogs, translated for business owners. Use when you need to explain complex engineering feats using the 'Famous Actor' simple-explanation tone with clear visual concepts. | default |


### Platform (10)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| chaos-engineering | Design resilience testing — failure injection, graceful degradation, game days, and fault tolerance verification for distributed systems | default |
| ci-cd-pipeline | Generate GitHub Actions workflows for build, test, deploy with environment configs and secrets management | default |
| disaster-recovery | Design disaster recovery and business continuity plans — RTO/RPO targets, backup strategies, failover architecture, and DR testing runbooks | default |
| dora-metrics | Implement DORA and SPACE metrics — deployment frequency, lead time, MTTR, change failure rate, and developer experience dashboards | default |
| edge-computing | Architect edge computing solutions — edge functions, CDN strategies, cache invalidation, edge middleware, and global latency optimization | default |
| green-software | Apply sustainable software practices — carbon-aware computing, energy-efficient architecture, resource optimization, and sustainability reporting | default |
| incident-response | Create incident runbooks, severity classification, on-call procedures, post-mortems, and escalation paths | default |
| infrastructure-scaffold | Generate cloud infrastructure configs for Firebase, GCP, Vercel, and Docker with IaC templates and environment management | default |
| observability | Set up observability stacks — structured logging, distributed tracing, alerting, SLO/SLI definition, and dashboards with Crashlytics, Sentry, or Datadog | default |
| release-management | Manage release workflows — app store submissions, staged rollouts, versioning strategy, changelogs, and ASO for Android and iOS | default |


### Product (10)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| customer-onboarding | Design user activation and first-run experiences — onboarding flows, empty states, welcome emails, tooltips, and time-to-value optimization for mobile (Android/iOS) and web apps | default |
| design-system | Build cross-platform design systems — design tokens, component libraries, Storybook/Catalog setup, theme architecture, and platform consistency | default |
| feature-audit | Post-ship quality gate — audits a completed feature for missing tests, security gaps, accessibility, analytics, and documentation across Android (.kt), iOS (.swift), Web (.ts/.tsx), and Firebase | Read, Grep, Glob |
| feature-flags | Implement feature flag systems — progressive rollouts, A/B testing, kill switches, and experimentation frameworks with Firebase Remote Config or LaunchDarkly | default |
| market-research | Conduct TAM/SAM/SOM analysis, competitive research, ICP definition, and pricing research | Read, Grep, Glob, WebSearch, WebFetch |
| portfolio-registry | Generate and maintain a structured product portfolio registry — the single source of truth for all products, stacks, teams, stages, and shared infrastructure across the venture studio | default |
| product-design | Create design specs following Apple HIG, Material Design 3, design tokens, and accessibility standards | default |
| product-manager | Product strategy and prioritization — OKRs, RICE-scored roadmaps, feature briefs, and outcome-driven planning for product leaders | default |
| technology-radar | Generate and maintain a ThoughtWorks-style technology radar — track Adopt/Trial/Assess/Hold decisions across the portfolio with rationale and migration plans | default |
| uat | Generate UAT plans, acceptance criteria checklists, stakeholder sign-off workflows, and go/no-go release gates | default |


### Security (4)

| Skill | Description | Allowed Tools |
| --- | --- | --- |
| accessibility-audit | Audit apps and websites for WCAG 2.2 compliance, screen reader support, and inclusive design across Android, iOS, and Web | Read, Grep, Glob |
| compliance-architect | Architect compliance frameworks for HIPAA, COPPA, GDPR, CCPA, and PCI — consent flows, audit trails, data classification, and privacy-by-design | default |
| qsbs-compliance | Track and enforce IRC §1202 QSBS qualification — gross asset test (<$50M), active business test (>80% qualified), C-Corp status, holding period tracking, and disqualifying event detection | Read, Grep, Glob |
| security-review | OWASP Top 10 security audit for codebases — scans auth flows, API endpoints, data storage, secrets handling, and dependency supply chain across .kt, .swift, .ts, .py, .go, .rs, and infrastructure files | Read, Grep, Glob |


## 3. Agents


### Business (4)

| Agent | Purpose | Tools |
| --- | --- | --- |
| financial-analyst | Financial modeling agent that builds revenue forecasts, unit economics, scenario analyses, cost structures, and P&L projections from product data and business logic in code. Use when building a revenue forecast, unit-economics model, scenario analysis, or P&L projection. | Read, Grep, Glob, Bash |
| investor-relations | Generates investor-facing materials — board updates, quarterly reports, KPI dashboards, fundraising narratives, and cap table scenarios from product and financial data. Use when preparing board updates, investor reports, KPI dashboards, or fundraising materials. | Read, Grep, Glob, Bash |
| market-intelligence | Market intelligence agent for TAM/SAM/SOM analysis, industry trends, regulatory landscape, market timing, and investment thesis validation. | Read, Grep, Glob, Bash, WebSearch, WebFetch |
| ops-finance | Operational finance agent that assists with invoice generation, 1099 tracking, bookkeeping, tax compliance prep, and multi-entity consolidation for Cure Consulting Group. | Read, Grep, Glob, Bash |


### Data (3)

| Agent | Purpose | Tools |
| --- | --- | --- |
| ab-test-analyst | Designs and analyzes A/B tests — experiment design, sample size calculation, statistical significance testing, guardrail metrics, and result interpretation with actionable recommendations. Use when designing an experiment, sizing a test, or interpreting A/B results. | Read, Grep, Glob, Bash |
| data-analyst | Data analysis agent that explores schemas, writes queries, analyzes data patterns, identifies anomalies, and generates visualization recommendations from database and analytics code. Use when exploring a schema, writing analytical queries, or investigating data anomalies. | Read, Grep, Glob, Bash |
| metrics-dashboard | Designs KPI dashboards with metric definitions, alert thresholds, SLO/SLI targets, and visualization specs for engineering, product, and business stakeholders. | Read, Grep, Glob, Bash |


### Engineering (18)

| Agent | Purpose | Tools |
| --- | --- | --- |
| api-validator | Validates API implementations match OpenAPI/GraphQL schemas. Checks endpoint coverage, request/response contracts, error handling consistency, and documentation completeness. Use when validating an API against its OpenAPI/GraphQL schema, checking contract coverage, or reviewing breaking changes. | Read, Grep, Glob, Bash |
| ci-debugger | Diagnoses failed CI/CD pipeline runs by analyzing logs, identifying root causes, and suggesting targeted fixes. Supports GitHub Actions, Firebase Deploy, Fastlane, and Docker builds. Use when a CI/CD run fails and you need root-cause analysis and a targeted fix. | Read, Grep, Glob, Bash |
| code-reviewer | Security and quality code review agent that audits code against Cure Consulting Group standards. Use when reviewing a diff or pull request for security, quality, and adherence to Cure standards. | Read, Grep, Glob |
| codebase-explainer | Onboarding agent that answers questions about the codebase, explains architecture, traces data flows, and helps new developers understand how things work. Use when onboarding to an unfamiliar codebase or asking how the architecture or a data flow works. | Read, Grep, Glob, Bash |
| dependency-auditor | Audits project dependencies for security vulnerabilities, outdated packages, license compliance, and supply chain risks. Use after installing or updating packages. | Read, Grep, Glob, Bash |
| deployment-validator | Pre-deployment checklist validator. Verifies environment variables, secrets management, feature flags, smoke tests, and rollback readiness before any deployment. Use before a deployment to validate env vars, secrets, feature flags, smoke tests, and rollback readiness. | Read, Grep, Glob, Bash |
| doc-generator | Generates and maintains technical documentation from code — API docs, architecture decision records, changelogs, onboarding guides, and inline documentation. Use when generating or updating API docs, ADRs, changelogs, or onboarding guides from code. | Read, Grep, Glob, Bash |
| equity-analyst | Public markets research specialist. Analyzes SEC filings, earnings transcripts, and market news to develop investment theses, track catalysts, and update valuation models. Use when researching a public company — analyzing filings or earnings and building or updating a valuation thesis. | Read, Grep, Glob, Bash, WebFetch |
| investment-banker | Specialized M&A and capital markets agent. Builds valuation models (Comps, DCF, LBO), drafts deal materials (CIMs, teasers), and analyzes pro-forma transaction impact. Use when building M&A valuation models (Comps/DCF/LBO) or drafting deal materials. | Read, Grep, Glob, Bash |
| migration-validator | Validates database migrations for correctness, rollback safety, naming conventions, and zero-downtime compatibility. Use before applying migrations to staging or production. | Read, Grep, Glob, Bash |
| pr-reviewer | Automated pull request reviewer that analyzes diffs for quality, security, performance, and adherence to Cure standards. Suggests improvements and flags blockers before merge. | Read, Grep, Glob, Bash |
| private-equity-analyst | Private markets specialist focused on deal sourcing, commercial due diligence, and portfolio monitoring. Analyzes unit economics, builds LBO models, and drafts IC memos. Use when sourcing or diligencing a private deal, building an LBO, or drafting an IC memo. | Read, Grep, Glob, Bash |
| project-bootstrapper | Sets up new projects with correct architecture, configuration, and Cure Consulting Group standards. Use when starting a new project that needs correct architecture, configuration, and Cure standards. | Read, Grep, Glob, Bash, Edit, Write |
| qa-engineer | QA engineer agent that performs comprehensive quality assurance — test plan generation, edge case discovery, regression analysis, exploratory testing checklists, bug triage, and quality gate enforcement across all platforms. Use when planning tests, discovering edge cases, triaging bugs, or enforcing a quality gate. | Read, Grep, Glob, Bash |
| refactor-assistant | Safe refactoring agent that restructures code while maintaining behavior. Runs tests before and after every change to ensure nothing breaks. Use when restructuring code that must preserve behavior, with tests run before and after each change. | Read, Grep, Glob, Bash, Edit, Write |
| release-coordinator | Orchestrates the full release process — version bump, changelog generation, tagging, deploy validation, and rollback readiness. Coordinates across mobile, web, and backend releases. Use when cutting a release — version bump, changelog, tag, deploy validation, and rollback readiness. | Read, Grep, Glob, Bash, Edit |
| system-architect | System architecture agent that generates RFCs, reviews system design, evaluates architectural trade-offs, and creates architecture decision records for Cure Consulting Group projects. | Read, Grep, Glob, Bash |
| test-runner | Validates test suite health, runs tests, checks coverage thresholds, and flags flaky tests. Use after writing new code or before commits. | Read, Grep, Glob, Bash |


### Legal (2)

| Agent | Purpose | Tools |
| --- | --- | --- |
| contract-reviewer | Reviews contracts, SOWs, NDAs, and legal documents for risk, scope gaps, unfavorable terms, IP issues, and liability exposure. Flags items requiring legal counsel. | Read, Grep, Glob |
| legal-compliance | Legal compliance agent that monitors QSBS qualification, NCAA ECAG rules, FERPA data handling, trademark strategy, and entity compliance across the Cure Consulting Group venture portfolio. Use when checking QSBS, FERPA, NCAA ECAG, trademark, or entity-compliance questions across the portfolio. | Read, Grep, Glob |


### Marketing (5)

| Agent | Purpose | Tools |
| --- | --- | --- |
| brand-guardian | Enforces brand consistency across the product — validates voice/tone, visual identity, naming conventions, microcopy, and style guide adherence in UI code and content. Use when reviewing UI copy, microcopy, naming, or visual identity for brand and style-guide consistency. | Read, Grep, Glob |
| campaign-analyst | Analyzes marketing campaign performance — attribution, conversion funnels, A/B test results, CAC/LTV, channel ROI, and campaign optimization recommendations. Use when analyzing campaign performance, attribution, conversion funnels, or channel ROI. | Read, Grep, Glob, Bash |
| content-strategist | Plans and generates content strategy — editorial calendars, blog posts, social media plans, SEO content, email sequences, and content audits aligned with product and growth goals. Use when planning an editorial calendar, content brief, SEO plan, or distribution strategy. | Read, Grep, Glob, Bash, WebSearch |
| growth-analyst | Analyzes growth metrics — activation funnels, retention cohorts, viral coefficients, revenue attribution, and identifies growth levers from product data and code. Use when analyzing activation, retention, or virality and identifying growth levers. | Read, Grep, Glob, Bash |
| technical-content-strategist | High-level technical marketing agent that translates complex engineering feats into simple, accessible blog posts and visuals. Uses the Netflix/Uber/Pinterest/Square style of engineering authority, but with the 'Famous Actor' simple-explanation tone for business owners. | Read, Grep, Glob, WebFetch, WebSearch, NanoBanana |


### Product (4)

| Agent | Purpose | Tools |
| --- | --- | --- |
| competitive-intel | Competitive intelligence agent that analyzes market positioning, feature gaps, pricing strategies, and differentiation opportunities by examining product code and public data. Use when comparing the product to competitors, mapping feature gaps, or assessing positioning. | Read, Grep, Glob, Bash, WebSearch, WebFetch |
| product-analyst | Analyzes product usage patterns, feature adoption, user journeys, and product-market fit signals from analytics data, code instrumentation, and user feedback. Use when analyzing feature adoption, user journeys, or product-market-fit signals from analytics. | Read, Grep, Glob, Bash |
| roadmap-strategist | Builds and validates product roadmaps using RICE scoring, dependency mapping, capacity planning, and strategic alignment. Generates quarterly plans and milestone tracking. Use when prioritizing a roadmap with RICE, mapping dependencies, or planning a quarter. | Read, Grep, Glob, Bash |
| ux-researcher | Synthesizes UX research — analyzes UI code for usability issues, maps user flows for friction points, evaluates information architecture, and generates research plans. | Read, Grep, Glob |


### Security (3)

| Agent | Purpose | Tools |
| --- | --- | --- |
| accessibility-checker | Automated WCAG 2.2 accessibility validation for UI changes. Checks semantic HTML, ARIA labels, color contrast, keyboard navigation, and screen reader compatibility. | Read, Grep, Glob |
| firebase-security-auditor | Audits Firestore security rules for overly permissive access, missing validations, and data model mismatches. Use after modifying security rules or Firestore schema. | Read, Grep, Glob, Bash |
| skill-security-auditor | Static security audit for skill, agent, and persona files before they enter the repo. Scans for command injection, code execution, exfiltration, prompt injection, supply chain, privilege escalation, and secret leakage. Read-only. | Read, Grep, Glob |


## 4. Personas

| Persona | Description | Skills referenced |
| --- | --- | --- |
| cure-engagement-pm | Project/program manager for a Cure client engagement — sprint cadence, scope/budget tracking, client comms, handoff | 14 |
| cure-product-lead | Product lead on a Cure client engagement — discovery, roadmap, stakeholder management, outcome-driven planning | 19 |
| cure-solo-consultant | Single consultant on a small or early-stage Cure engagement — wears all hats, picks the smallest viable thing | 21 |
| cure-tech-lead | Engineering lead on a Cure client engagement — architectural judgment, code quality enforcement, mentors junior consultants | 24 |


## 5. Hooks

| Event | Matcher | Type | What it does |
| --- | --- | --- | --- |
| SessionStart | startup | command | echo 'Cure Consulting Group ProductEngineeringSkills plugin loaded (v7.1.2). 80 skills (domain-organized), 39… |
| SessionStart | startup | command | echo "Git branch: $(git branch --show-current 2>/dev/null \|\| echo 'not a git repo'). Uncommitted changes: $(g… |
| SessionStart | startup | command | if [ -f package.json ]; then OUTDATED=$(npm outdated --json 2>/dev/null \| python3 -c "import sys,json; d=json… |
| SessionStart | startup | command | echo '\nAvailable Agents (39):\n  Engineering: code-reviewer, test-runner, pr-reviewer, refactor-assistant, c… |
| PreCompact | auto\|manual | command | echo 'CONTEXT RE-INJECTION AFTER COMPACTION:\n\nCure Consulting Group Standards (always apply):\n- Clean Arch… |
| PostCompact | auto\|manual | command | echo 'Context compacted. Cure Consulting Group plugin active — 80 skills, 39 agents, 4 personas available. Us… |
| PostToolUse | Edit\|Write | command | FILE=$(echo $CLAUDE_TOOL_INPUT \| python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path'… |
| PostToolUse | Bash | command | CMD=$(echo $CLAUDE_TOOL_INPUT \| python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''… |
| PostToolUseFailure | Bash | command | CMD=$(echo $CLAUDE_TOOL_INPUT \| python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''… |
| UserPromptSubmit |  | command | PROMPT=$(echo $CLAUDE_TOOL_INPUT \| python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('prompt',… |
| UserPromptSubmit |  | prompt | You are an intent classifier for Cure Consulting Group. Analyze the user's prompt and suggest the most releva… |
| UserPromptSubmit |  | prompt | You are a prompt coach for Cure Consulting Group. The user just submitted a prompt to a Claude Code agent. Yo… |
| PreToolUse | Edit\|Write | command | FILE=$(echo $CLAUDE_TOOL_INPUT \| python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path'… |
| PreToolUse | Bash | command | CMD=$(echo $CLAUDE_TOOL_INPUT \| python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''… |
| PreToolUse | Edit\|Write | prompt | You are a code quality validator for Cure Consulting Group. Check if the code change follows these rules: |
| PreToolUse | Bash | prompt | You are a deployment safety validator. Check if this bash command involves deploying to production or a share… |
| PreToolUse | Edit\|Write | prompt | You are the skill-security-auditor for Cure Consulting Group. This file is being written into the plugin (ski… |
| Notification |  | command | echo '{"notification_logged": true}' |
| SubagentStart |  | command | AGENT=$(echo $CLAUDE_TOOL_INPUT \| python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('name', d.… |
| SubagentStop |  | command | echo "Expert task complete. Final quality check checklist:\n- Tests added? \u2192 test-runner agent\n- Lint/T… |


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

| Server | Type | Transport / URL / Command | Note |
| --- | --- | --- | --- |
| firebase-firestore | stdio | npx | Firestore — direct database queries, schema inspection, document management |
| github | http | https://api.githubcopilot.com/mcp/ | GitHub API — PR management, issue tracking, code search, repository operations |
| postgres | stdio | npx | PostgreSQL — database queries, schema inspection, migration support |
| sentry | http | https://mcp.sentry.dev/sse | Sentry — error monitoring, issue tracking, release health |


## 9. LSP Servers

| Server | Extensions | Command |
| --- | --- | --- |
| python | .py, .pyi | npx pyright-langserver --stdio |
| typescript | .js, .jsx, .ts, .tsx | npx typescript-language-server --stdio |


---

_Regenerate with `python3 scripts/generate-overview.py`._
