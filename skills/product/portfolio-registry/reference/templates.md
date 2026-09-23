# portfolio-registry: PORTFOLIO.md templates

> Read when writing or regenerating PORTFOLIO.md sections (Steps 3–6 of the `portfolio-registry` skill). Shared-infrastructure and dependency templates are in `details.md`.

## Contents
- Registry template (company + per-product)
- Technology Radar summary
- Team roster and allocation
- Portfolio health scorecard
- AI session context block
- Maintenance schedule

## Registry template (company + per-product)

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
| AI/ML | [Exact model IDs in use per provider, or N/A] |
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

## Technology Radar summary

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
| [e.g., a new speech-to-text model] | [Autograph] | [Transcription accuracy vs the current model] |

### Assess (researching, not in production)
| Technology | Interest | Rationale |
|-----------|----------|-----------|
| [e.g., Supabase] | [Alternative to Firebase for products needing PostgreSQL] | [Evaluating for The Initiated] |

### Hold (stop adopting, plan migration)
| Technology | Reason | Migration Plan |
|-----------|--------|----------------|
| [e.g., Firebase Realtime DB] | [Firestore is superior for our use cases] | [Migrate remaining reads by Q3] |
```

## Team roster and allocation

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

## Portfolio health scorecard

````markdown
---

## Portfolio Health Scorecard

> Scoring: G (Green) = healthy, Y (Yellow) = needs attention, R (Red) = at risk
> Review monthly. Trend arrows: [^] improving, [v] declining, [=] stable

| Product | Stage | Priority | MRR | Burn | Runway | Team | Tech Debt | Security | Compliance | Overall |
|---------|-------|----------|-----|------|--------|------|-----------|----------|------------|---------|
| Vendly | [stage] | P0 | [$X] | [$X/mo] | [Xmo] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] |
| Autograph | [stage] | P1 | [$X] | [$X/mo] | [Xmo] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] |
| The Initiated | [stage] | P1 | [$X] | [$X/mo] | [Xmo] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] | [G/Y/R] |
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
````

## AI session context block

Keep it under 500 tokens. Fill from the registry; the example shows the shape.

````markdown
---

## AI Session Context

> Copy this block into any AI session (Claude, Codex, Google Antigravity, Cursor, Copilot) for instant
> portfolio awareness. Keep it under 500 tokens for efficient context usage.

```
PORTFOLIO CONTEXT — Cure Consulting Group
==========================================
Type: Venture studio + consultancy (hybrid)
Products (6):
  - Vendly (P0, growth) — LATAM merchant OS. Android/iOS, Firebase, Stripe.
    Compliance: LATAM fintech. Locales: en, es-DO, es-MX, pt-BR.
  - Autograph (P1, beta) — AI medical scribe. Web, HIPAA-compliant.
    LLM: [model IDs]. Clinical workflow.
  - The Initiated (P1, MVP) — Women's basketball recruiting. Web, B2B+B2C.
    NCAA compliance. Events platform.
  - TwntyHoops (P2, growth) — Basketball media/events. Web, content + community.
  - Cure Consulting (P1, mature) — Consultancy. Client work + this skill library.

Shared infra: Firebase Auth (shared identity), GitHub Actions, shared design tokens.
Total burn: $[X]/mo | Runway: [X] months
Active priorities: [top 3 this month]
Hard constraints: HIPAA (Autograph), NCAA (The Initiated), LATAM fintech (Vendly)
Skill library: github.com/Cure-Consulting-Group/ProductEngineeringSkills
```
````

## Maintenance schedule

````markdown
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

When stale: run the portfolio-registry skill in "health check" mode to refresh.
```
````
