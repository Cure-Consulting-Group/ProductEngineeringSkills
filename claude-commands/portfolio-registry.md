# Portfolio Registry

The highest-leverage artifact in the skill library. A portfolio registry gives every AI assistant (Claude, Gemini, Cursor, Copilot) and every human full context on what exists, who owns it, how it connects, and where resources are allocated. Without this file, every session starts blind. With it, every skill in this library becomes dramatically smarter.

This skill generates and maintains `PORTFOLIO.md` -- the single source of truth for Cure Consulting Group's venture studio. It lives at `~/.claude/PORTFOLIO.md` (global) or at the project root (per-project subset). Every AI session should read this file before starting work.

## Why This Matters

```
Without PORTFOLIO.md:
  - AI suggests Firebase Auth setup when you already have shared auth across 4 products
  - Engineer builds a payment flow without knowing Vendly already solved it
  - New hire spends 2 weeks mapping what exists before contributing
  - Cost model ignores shared infrastructure savings
  - Security review misses cross-product data flows

With PORTFOLIO.md:
  - AI knows every product, stack, constraint, and dependency from token 1
  - Engineers reuse existing solutions across products
  - New hires onboard in hours, not weeks
  - Cost models account for shared infrastructure
  - Security reviews trace data flows across the full portfolio
  - Every other skill (/sdlc, /security-review, /engineering-cost-model) auto-inherits context
```

## Core Principle: Context Is the Multiplier

```
PORTFOLIO.md is read by:
  ├── /sdlc           → knows which products exist, their stacks, and constraints
  ├── /security-review → traces cross-product auth, data flows, compliance
  ├── /engineering-cost-model → accounts for shared infra, team allocation
  ├── /saas-financial-model   → knows revenue per product, burn rate, runway
  ├── /incident-response      → knows escalation paths per product
  ├── /project-bootstrap      → avoids duplicating existing infrastructure
  ├── /firebase-architect     → knows all Firebase project IDs and shared rules
  ├── /api-architect          → knows existing API contracts across products
  └── Every other skill       → has full portfolio awareness
```

## Step 1: Classify the Request

| Request Type | What to Do | Output |
|---|---|---|
| Full portfolio registry | Interview user about all products, generate complete PORTFOLIO.md | `~/.claude/PORTFOLIO.md` |
| Single product registration | Add one new product to existing registry | Append to PORTFOLIO.md |
| Product update | Update stage, priority, team, stack, or other fields for one product | Edit PORTFOLIO.md section |
| Product decommission | Move product to sunset stage, document migration/shutdown plan | Edit PORTFOLIO.md + archive note |
| Portfolio health check | Audit the registry for staleness, missing fields, risk flags | Health report + update recommendations |
| Auto-detect from machine | Scan local repos, package.json, build.gradle, Podfile to infer portfolio | Draft PORTFOLIO.md from detected projects |

If the user says "set up portfolio" or "register everything" -- do a full portfolio registry.
If the user names a specific product -- do single product registration or update.
If ambiguous, ask: "Full portfolio setup, or registering/updating a single product?"

## Step 2: Gather Context

### For Full Portfolio Registry

Interview the user. Ask these questions in order, but accept partial answers and infer the rest:

```
1. Company basics
   - Company name (default: Cure Consulting Group)
   - Operating model: venture studio / consultancy / hybrid
   - Total headcount (full-time + contractors)
   - Monthly burn rate and runway

2. For EACH product:
   - Product name and one-line description
   - Stage: idea / MVP / beta / growth / mature / sunset
   - Priority: P0 (existential) / P1 (strategic) / P2 (opportunistic) / P3 (maintenance)
   - Revenue model and current MRR/ARR
   - Team members and roles
   - Tech stack (platforms, languages, frameworks, infra)
   - GitHub repo URLs
   - Environment details (Firebase project IDs, domains)
   - Compliance requirements (HIPAA, NCAA, COPPA, GDPR, PCI, SOC2)
   - Supported languages/locales
   - Current sprint goal
   - Top 2-3 risks
   - Dependencies on other products or shared infra

3. Shared infrastructure
   - Shared auth provider and whether products share identity
   - Design token source and sharing model
   - Analytics platform and cross-product tracking
   - CI/CD provider and shared workflows
   - AI models in use and cost tracking approach
```

### For Auto-Detect Mode

Scan the local machine for project signals:

```
Detection strategy:
  1. Check ~/Documents, ~/Projects, ~/Code, ~/dev for git repos
  2. For each repo, read:
     - package.json (name, dependencies → detect Next.js, React, Firebase, Stripe)
     - build.gradle / build.gradle.kts (detect Android, Kotlin, Hilt, Compose)
     - Podfile / Package.swift (detect iOS, SwiftUI, dependencies)
     - .firebaserc (Firebase project IDs and aliases)
     - .env* files (environment names, API endpoints — DO NOT store secrets)
     - docker-compose.yml (infrastructure shape)
     - .github/workflows/*.yml (CI/CD configuration)
     - README.md (project description)
  3. Cross-reference GitHub org repos if gh CLI is authenticated
  4. Present findings to user for confirmation before generating registry
```

### For Single Product Registration

Ask only about the specific product. Pre-fill defaults from existing PORTFOLIO.md if it exists.

## Step 3: Portfolio Registry Template

Generate `PORTFOLIO.md` with this exact structure. Every section is required. Use `[TBD]` for unknown fields -- never omit a section.

```markdown
# Portfolio Registry -- [Company Name]

> Last updated: [YYYY-MM-DD]. This file is the single source of truth for the
> product portfolio. Every AI session should read this file before starting work.
> Update at least monthly or when any product changes stage, priority, or team.

---

## Company Overview

| Field | Value |
|-------|-------|
| Company | [Name] |
| Model | [Venture studio / Consultancy / Hybrid] |
| Headcount | [X full-time, Y contractors] |
| Monthly burn | [$X/mo] |
| Runway | [X months at current burn] |
| Primary domain | [company.com] |
| GitHub org | [github.com/org-name] |
| Shared Slack | [workspace URL or name] |
| Fiscal year | [start month] |

---

## Products

### [Product Name]

| Field | Value |
|-------|-------|
| One-liner | [What it does in one sentence] |
| Stage | [idea / MVP / beta / growth / mature / sunset] |
| Priority | [P0 / P1 / P2 / P3] |
| Revenue model | [SaaS / marketplace / platform / media / consulting / pre-revenue] |
| MRR | [$X] |
| ARR | [$X] |
| Team | [Name (Role), Name (Role), ...] |
| Platforms | [Android / iOS / Web / API / CLI] |
| Languages | [Kotlin, Swift, TypeScript, Python, etc.] |
| Frameworks | [Compose, SwiftUI, Next.js, etc.] |
| Infrastructure | [Firebase, GCP, Vercel, AWS, etc.] |
| Database | [Firestore, PostgreSQL, SQLite, etc.] |
| Auth | [Firebase Auth, Auth0, custom, etc.] |
| Payments | [Stripe, local processor, N/A] |
| AI/ML | [Models used: GPT-4, Claude, Gemini, custom, N/A] |
| Repos | [github.com/org/repo-1, github.com/org/repo-2] |
| Environments | dev: [project-id-dev], staging: [project-id-staging], prod: [project-id-prod] |
| Domains | [app.product.com, api.product.com] |
| Compliance | [HIPAA / NCAA / COPPA / GDPR / PCI / SOC2 / none] |
| Locales | [en, es-DO, es-MX, pt-BR, etc.] |
| Active sprint goal | [One sentence describing current focus] |
| Key risks | 1. [Risk] 2. [Risk] 3. [Risk] |
| Dependencies | [Shared Firebase Auth, shared design tokens, etc.] |
| Key metrics | [DAU, conversion rate, churn, etc.] |
| Last deploy | [YYYY-MM-DD or "continuous"] |

#### Architecture Notes
[2-5 sentences on the architecture: layers, patterns, key technical decisions.
Reference ADRs if they exist.]

#### Known Tech Debt
- [ ] [Debt item 1 — severity: high/medium/low]
- [ ] [Debt item 2]
- [ ] [Debt item 3]

---

[REPEAT for each product]
```

### Cure Consulting Group Default Products

When generating for Cure Consulting Group, pre-populate these products and ask the user to confirm/update:

```
Products to register:
  1. Vendly         — LATAM merchant OS (Android/iOS, Firebase, Stripe, multi-language)
  2. Autograph      — AI medical scribe (HIPAA, LLM, clinical workflow)
  3. The Initiated  — Women's basketball recruiting (NCAA, B2B+B2C, events)
  4. Antigravity    — AI agent orchestration IDE (VS Code fork, open source)
  5. TwntyHoops     — Basketball media/events (content, community)
  6. Cure Consulting Group — The consultancy itself (client work, this skill library)
```

## Step 4: Shared Infrastructure Map

```markdown
---

## Shared Infrastructure

### Authentication
| Field | Value |
|-------|-------|
| Provider | [Firebase Auth / Auth0 / custom] |
| Shared identity | [Yes/No — do products share user accounts?] |
| SSO | [Yes/No — single sign-on across products?] |
| MFA | [Required / Optional / Not implemented] |
| Auth project ID | [Firebase project ID if shared] |
| Custom claims | [List any shared custom claims: role, org_id, etc.] |

### Design System
| Field | Value |
|-------|-------|
| Shared base | [Yes/No — spacing, type scale, 8pt grid] |
| Per-brand theming | [Color, typography, imagery per product] |
| Token source | [Style Dictionary / Figma Variables / Tailwind config / manual] |
| Token repo | [github.com/org/design-tokens or N/A] |
| Component library | [Shared UI lib or per-product] |
| Design tool | [Figma / Sketch / none] |

### Analytics
| Field | Value |
|-------|-------|
| Platform | [Firebase Analytics / Mixpanel / PostHog / Amplitude] |
| Cross-product user ID | [Yes/No — can you track a user across products?] |
| Event taxonomy | [Standardized / Per-product / None] |
| Portfolio dashboard | [URL or N/A] |
| Data warehouse | [BigQuery / Snowflake / N/A] |

### CI/CD
| Field | Value |
|-------|-------|
| Provider | [GitHub Actions / CircleCI / Bitrise] |
| Shared workflows | [List reusable workflow files] |
| Deployment strategy | [Per-product / Unified / Mixed] |
| Artifact registry | [GitHub Packages / GCP Artifact Registry / N/A] |
| Mobile distribution | [Firebase App Distribution / TestFlight / Google Play Internal] |

### AI Infrastructure
| Field | Value |
|-------|-------|
| Models in use | [GPT-4, Claude, Gemini — list which product uses which] |
| API key management | [Per-product keys (required) / Shared keys (fix this)] |
| Cost tracking | [Per-product / Shared / Not tracked (fix this)] |
| Monthly AI spend | [$X total, $X per product] |
| Rate limiting | [Implemented / Not implemented] |
| Prompt management | [Version controlled / Ad hoc] |

### Domains & DNS
| Field | Value |
|-------|-------|
| Registrar | [Cloudflare / GoDaddy / Google Domains / Namecheap] |
| DNS provider | [Cloudflare / Route53 / Cloud DNS] |
| SSL | [Auto via Cloudflare / Let's Encrypt / GCP-managed] |
| Domains | [List all domains across portfolio] |

### Secrets Management
| Field | Value |
|-------|-------|
| Secrets vault | [1Password / GCP Secret Manager / AWS Secrets Manager] |
| Rotation policy | [90 days / manual / none] |
| Environment injection | [dotenv / GCP Secret Manager / GitHub Secrets] |
```

## Step 5: Technology Radar Summary

Brief overview linking to full `/technology-radar` output if available.

```markdown
---

## Technology Radar (Summary)

> Full analysis available via `/technology-radar`. This is a snapshot.

### Adopt (use in all new projects)
| Technology | Rationale |
|-----------|-----------|
| [e.g., Kotlin + Compose] | [Standard Android stack, team expertise, ecosystem maturity] |
| [e.g., Firebase Auth] | [Cross-product identity, free tier covers needs, good SDK support] |
| [e.g., GitHub Actions] | [All repos on GitHub, reusable workflows, good Firebase integration] |

### Trial (using in one product, evaluating)
| Technology | Product | Rationale |
|-----------|---------|-----------|
| [e.g., Claude API] | [Autograph] | [Medical scribe accuracy, evaluating vs GPT-4] |

### Assess (researching, not in production)
| Technology | Interest | Rationale |
|-----------|----------|-----------|
| [e.g., Supabase] | [Alternative to Firebase for products needing PostgreSQL] | [Evaluating for The Initiated] |

### Hold (stop adopting, plan migration)
| Technology | Reason | Migration Plan |
|-----------|--------|----------------|
| [e.g., Firebase Realtime DB] | [Firestore is superior for our use cases] | [Migrate remaining reads by Q3] |
```

## Step 6: Team Roster and Allocation

```markdown
---

## Team Roster & Allocation

| Person | Role | Products | Allocation | Utilization | Key Person Risk | Notes |
|--------|------|----------|------------|-------------|-----------------|-------|
| [Name] | [Engineering Lead] | [Vendly (60%), Autograph (40%)] | [100%] | [Overloaded] | [HIGH — sole Android expert] | [Needs hire to derisk] |
| [Name] | [Designer] | [All products (20% each)] | [100%] | [Spread thin] | [MEDIUM] | [Design system would reduce load] |
| [Name] | [Founder/CEO] | [All] | [N/A] | [N/A] | [N/A] | [Product vision, fundraising, client work] |

### Allocation Rules
- No engineer should be split across more than 2 products in a sprint
- P0 products get first claim on shared resources
- Key person risk HIGH means: if this person leaves, the product stalls for >2 weeks
- Utilization above 85% is a red flag — no slack for incidents or innovation
- Contractors should not own critical path items without knowledge transfer plan

### Hiring Priorities (derived from allocation gaps)
1. [Role] for [Product] — [why this is urgent]
2. [Role] for [Product] — [why this matters]
3. [Role] for [Product] — [nice to have]
```

## Step 7: Portfolio Health Scorecard

```markdown
---

## Portfolio Health Scorecard

> Scoring: G (Green) = healthy, Y (Yellow) = needs attention, R (Red) = at risk
> Review monthly. Trend arrows: [^] improving, [v] declining, [=] stable

| Product | Stage | Priority | MRR | Burn | Runway | Team | Tech Debt | Security | Compliance | Overall |
|---------|-------|----------|-----|------|--------|------|-----------|----------|------------|---------|
| Vendly | [stage] | P0 | [$X] | [$X/mo] | [Xmo] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] |
| Autograph | [stage] | P1 | [$X] | [$X/mo] | [Xmo] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] |
| The Initiated | [stage] | P1 | [$X] | [$X/mo] | [Xmo] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] |
| Antigravity | [stage] | P2 | [$X] | [$X/mo] | [Xmo] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] |
| TwntyHoops | [stage] | P2 | [$X] | [$X/mo] | [Xmo] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] |
| Cure Consulting | [stage] | P1 | [$X] | [$X/mo] | [Xmo] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] |

### Scoring Criteria

```
Team Health:
  G: Fully staffed, no key person risk, <85% utilization
  Y: Minor gaps, one key person risk, 85-95% utilization
  R: Understaffed, critical key person risk, >95% utilization

Tech Debt:
  G: Manageable, addressed in sprint, no blockers
  Y: Accumulating, 1-2 items blocking new features
  R: Severe, blocking releases, requires dedicated sprint to address

Security:
  G: Last audit <3 months ago, no open critical/high findings
  Y: Audit >3 months ago OR 1-2 open high findings
  R: No audit in 6+ months OR open critical findings OR compliance gap

Compliance:
  G: All requirements met, documentation current
  Y: Minor gaps, documentation stale, audit due soon
  R: Compliance violation risk, missing required controls, audit overdue
```
```

## Step 8: Cross-Product Dependencies

```markdown
---

## Cross-Product Dependencies

### Dependency Matrix

| From | To | Type | What | Risk if Broken | Mitigation |
|------|----|------|------|----------------|------------|
| Vendly | Shared Firebase | Infrastructure | Auth, Firestore, Cloud Functions | All auth fails, data inaccessible | Multi-region, failover config |
| Autograph | OpenAI API | External vendor | GPT-4 for medical transcription | Core feature unusable | Fallback to Claude, queue system |
| The Initiated | Vendly design tokens | Design | Shared spacing, grid, type scale | Inconsistent UI | Tokens versioned, pinned |
| Antigravity | VS Code upstream | Open source | Fork base, extension API | Feature divergence, security patches | Weekly upstream sync, patch process |
| All products | GitHub Actions | CI/CD | Build, test, deploy pipelines | No deploys, no PR checks | Local build fallback documented |
| All products | Firebase Auth | Identity | User authentication | Complete auth failure | Status page monitoring, cached tokens |

### Dependency Rules
- Every external dependency must have a documented fallback or degradation strategy
- Shared infrastructure changes require notification to ALL dependent product teams
- Breaking changes to shared services require 2-week migration window minimum
- Vendor dependencies must be evaluated quarterly for cost, reliability, and alternatives
- Cross-product data flows must be documented in security review scope

### Circular Dependency Check
[List any circular dependencies — these are architectural red flags that need resolution]
- [None / List if found]
```

## Step 9: AI Session Context Block

The most-used section. This is the copy-paste block that gives any AI assistant instant portfolio awareness.

```markdown
---

## AI Session Context

> Copy this block into any AI session (Claude, Gemini, Cursor, Copilot) for instant
> portfolio awareness. Keep it under 500 tokens for efficient context usage.

```
PORTFOLIO CONTEXT — Cure Consulting Group
==========================================
Type: Venture studio + consultancy (hybrid)
Products (6):
  - Vendly (P0, growth) — LATAM merchant OS. Android/iOS, Firebase, Stripe.
    Compliance: LATAM fintech. Locales: en, es-DO, es-MX, pt-BR.
  - Autograph (P1, beta) — AI medical scribe. Web, HIPAA-compliant.
    LLM: GPT-4 + Claude. Clinical workflow.
  - The Initiated (P1, MVP) — Women's basketball recruiting. Web, B2B+B2C.
    NCAA compliance. Events platform.
  - Antigravity (P2, alpha) — AI agent orchestration IDE. VS Code fork.
    Open source. TypeScript + Electron.
  - TwntyHoops (P2, growth) — Basketball media/events. Web, content + community.
  - Cure Consulting (P1, mature) — Consultancy. Client work + this skill library.

Shared infra: Firebase Auth (shared identity), GitHub Actions, shared design tokens.
Total burn: $[X]/mo | Runway: [X] months
Active priorities: [top 3 this month]
Hard constraints: HIPAA (Autograph), NCAA (The Initiated), LATAM fintech (Vendly)
Skill library: github.com/Cure-Consulting-Group/ProductEngineeringSkills (29+ skills)
```
```

## Step 10: Maintenance Rules and Lifecycle

```markdown
---

## Maintenance Schedule

### Update Triggers (update PORTFOLIO.md immediately when any of these occur)
- Product changes stage (e.g., MVP → beta)
- Product changes priority (e.g., P2 → P1)
- Team member joins, leaves, or changes allocation
- New product added or product sunset
- Fundraise closes (runway changes)
- Compliance requirement changes
- Shared infrastructure changes
- New repo created or repo archived

### Scheduled Reviews
| Cadence | What to Review | Who |
|---------|---------------|-----|
| Weekly | Active sprint goals, key risks | Product leads |
| Monthly | Full health scorecard, team allocation, tech debt status | Engineering lead |
| Quarterly | Technology radar, dependency audit, compliance status | CTO / Technical advisor |
| Annually | Full portfolio strategy, product lifecycle decisions | Leadership team |

### Versioning
- Keep a changelog at the bottom of PORTFOLIO.md
- Archive previous versions: `PORTFOLIO-[YYYY-MM-DD].md`
- Git-track the file if possible (it contains no secrets)
- Diff previous versions to spot trends

### Staleness Detection
```
A PORTFOLIO.md is STALE if:
  - Last updated date is >30 days ago
  - Any product's "active sprint goal" references a completed sprint
  - Team roster doesn't match current GitHub org members
  - MRR/ARR numbers are from >1 quarter ago
  - Any field still says [TBD] after 2 weeks

When stale: run /portfolio-registry with "health check" mode to refresh.
```
```

## Output Delivery

### File Placement
```
Full portfolio:        ~/.claude/PORTFOLIO.md (global — all sessions read this)
Per-project subset:    ./PORTFOLIO.md (project root — product-specific context)
Archive:               ~/.claude/portfolio-archive/PORTFOLIO-[YYYY-MM-DD].md
```

### Output Rules
- Always generate the complete file, even if only updating one product
- Use `[TBD]` for unknown fields -- never omit sections or leave them blank without marking
- Include the AI Session Context block at the end -- this is the most frequently used section
- After generating, remind the user: "Add `@PORTFOLIO.md` to your CLAUDE.md so every session reads it automatically"
- Offer to also run: `/engineering-cost-model`, `/security-review`, `/saas-financial-model` using the new portfolio context

### Validation Checklist
After generating PORTFOLIO.md, verify:
- [ ] Every product has all required fields filled or marked [TBD]
- [ ] Stage and priority are consistent (no P0 product at "idea" stage)
- [ ] Team allocation sums to ~100% per person (not >120%)
- [ ] Shared infrastructure section matches what products reference
- [ ] Cross-product dependencies are bidirectional (if A depends on B, B lists A as dependent)
- [ ] AI Session Context block is under 500 tokens
- [ ] No secrets, API keys, or passwords in the file
- [ ] Compliance fields are filled for regulated products (HIPAA, NCAA, PCI)

## Cross-References

This skill connects to every other skill in the library. Key relationships:

| Skill | How It Uses PORTFOLIO.md |
|-------|-------------------------|
| `/sdlc` | Knows product stack, constraints, and existing architecture |
| `/project-bootstrap` | Avoids recreating existing shared infra |
| `/security-review` | Traces cross-product data flows, compliance requirements |
| `/engineering-cost-model` | Uses team allocation, shared infra, burn rate |
| `/saas-financial-model` | Uses MRR/ARR, revenue models, unit economics per product |
| `/incident-response` | Knows escalation paths, system owners, dependencies |
| `/firebase-architect` | Knows all Firebase project IDs and shared configurations |
| `/api-architect` | Knows existing API contracts across products |
| `/testing-strategy` | Knows platform-specific test tooling per product |
| `/ci-cd-pipeline` | Knows shared workflows and deployment strategies |
| `/feature-audit` | Audits against product-specific constraints and compliance |
| `/accessibility-audit` | Knows locale and platform requirements per product |
| `/performance-review` | Knows infrastructure and scale requirements per product |
| `/database-architect` | Knows database choices and shared data models |
| `/go-to-market` | Knows market, revenue model, and competitive position per product |
