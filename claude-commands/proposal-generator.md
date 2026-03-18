# Proposal Generator

Generate professional consulting proposals and Statements of Work. Every proposal should be clear enough that a non-technical decision-maker can say yes, and specific enough that scope creep has no room to hide.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Engagement Type

| Type | Structure | Pricing Model |
|------|-----------|--------------|
| New client proposal | Full proposal + SOW | Fixed-price or hybrid |
| Expansion proposal | Addendum to existing SOW | T&M or fixed-price |
| Maintenance SOW | Ongoing support agreement | Retainer |
| Fixed-price project | Milestone-based delivery | Fixed-price |
| Time-and-materials | Estimated hours with cap | T&M with weekly cap |
| Emergency/expedited | Accelerated timeline | Premium rate (1.5x) |

## Step 2: Gather Context

1. **Client** — company name, industry, size, decision makers?
2. **Problem** — what pain are they trying to solve? (in their words)
3. **Scope** — what needs to be built/fixed/improved?
4. **Timeline** — hard deadline? Preferred launch date?
5. **Budget** — stated budget range? Previous vendor spend?
6. **Decision process** — who signs? Procurement involved? Legal review?
7. **Existing systems** — what does the current tech stack look like?
8. **Competition** — are they evaluating other vendors?

## Scope Validation

Before generating proposal:
1. Glob for similar past projects in the workspace to benchmark estimates
2. Reference `/engineering-cost-model` for accurate cost basis
3. Use WebSearch to validate market rates for the proposed services

## Artifact Generation (Required)

Generate using Write:
1. **Proposal document**: `docs/proposals/{client}-proposal.md` — complete proposal
2. **SOW**: `docs/proposals/{client}-sow.md` — statement of work with milestones
3. **Pricing breakdown**: `docs/proposals/{client}-pricing.md` — cost structure with assumptions

## Step 3: Proposal Structure

```markdown
# Proposal: [Project Name]
## Prepared for [Client Name] by Cure Consulting Group
### [Date]

---

## 1. Executive Summary (one page max)

[Client] needs [concise problem statement — 1-2 sentences].

We propose [solution summary — 1-2 sentences] delivered over [timeline]
for [price range or fixed price].

Why Cure:
- [Relevant experience — specific similar project or domain expertise]
- [Technical differentiator — architecture approach, team composition]
- [De-risk factor — methodology, guarantee, or IP advantage]

---

## 2. Scope Definition

### In Scope
| # | Deliverable | Description |
|---|------------|-------------|
| 1 | [Feature/Module] | [What it includes, in plain language] |
| 2 | [Feature/Module] | [What it includes] |
| 3 | [Feature/Module] | [What it includes] |

### Out of Scope
- [Explicitly list things the client might assume are included]
- [Common: ongoing maintenance, content creation, third-party integrations beyond X]
- [Common: legacy system migration, training beyond initial handoff]

### Assumptions
- Client provides [access to systems, brand assets, content, API keys] by [date]
- Client designates a single point of contact with authority to approve deliverables
- Feedback turnaround: 2 business days per review cycle
- Maximum [N] rounds of revision per deliverable

### Dependencies
- [Third-party API availability]
- [Client infrastructure readiness]
- [App store review timelines]

---

## 3. Technical Approach

### Architecture Overview
[High-level architecture description — 3-5 sentences]
[Include a text-based architecture diagram if helpful]

### Platform & Technology Choices
| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | [e.g., Next.js, SwiftUI] | [Why this choice] |
| Backend | [e.g., Firebase, Node.js] | [Why this choice] |
| Database | [e.g., Firestore, PostgreSQL] | [Why this choice] |
| Hosting | [e.g., Vercel, Cloud Run] | [Why this choice] |

### Methodology
- Agile delivery in 2-week sprints
- Weekly status meetings with stakeholder demo
- Continuous deployment to staging environment
- User acceptance testing before each milestone sign-off
```

## Step 4: Pricing Models

```
Choose the model that matches project clarity and client preference:

FIXED-PRICE (best when scope is well-defined)
  Structure:
    Milestone 1: Discovery & Design      — $XX,XXX (due on signing)
    Milestone 2: Core Development         — $XX,XXX (due on approval of M1)
    Milestone 3: Integration & Testing    — $XX,XXX (due on approval of M2)
    Milestone 4: Launch & Handoff         — $XX,XXX (due on go-live)

  Rules:
    - Never 100% upfront — milestone payments protect both parties
    - First milestone payment due on contract signing (covers discovery risk)
    - Final 20% due on go-live (incentive to ship)
    - Change requests: documented, priced, signed before work begins
    - Scope protection: out-of-scope requests go through change order process

TIME-AND-MATERIALS (best when scope is uncertain or evolving)
  Structure:
    Rate card:
      Senior Engineer    — $XXX/hour
      Staff Engineer     — $XXX/hour
      Designer           — $XXX/hour
      Project Manager    — $XXX/hour

    Estimated total: $XX,XXX - $XX,XXX (range based on assumptions)
    Weekly cap: $X,XXX (client can pause or adjust any week)
    Billing: weekly invoices with detailed time logs

  Rules:
    - Provide honest estimate range (not a meaningless "it depends")
    - Weekly caps give client control over burn rate
    - Detailed time tracking shared transparently (Harvest, Toggl)
    - Re-estimate monthly as scope becomes clearer

RETAINER (best for ongoing maintenance/support)
  Structure:
    Monthly hours: [X] hours/month
    Rate: $XXX/hour (discounted from T&M rate)
    Rollover: unused hours roll over 1 month (max 1.5x monthly allocation)
    SLA tiers:
      Critical (P0): 2-hour response, 8-hour resolution
      High (P1):     4-hour response, 24-hour resolution
      Normal (P2):   1 business day response, 1-week resolution

HYBRID (recommended for most projects)
  Fixed-price for defined scope (core features)
  + T&M for discovery phase (first 2-4 weeks)
  + T&M budget for change requests and enhancements
  Best of both worlds: predictable cost for core, flexibility for unknowns
```

## Step 5: Timeline and Milestones

```markdown
## Project Timeline

| Phase | Duration | Key Deliverables | Milestone Payment |
|-------|----------|-----------------|-------------------|
| Discovery | 2 weeks | Requirements doc, architecture, designs | M1: $XX,XXX |
| Sprint 1-2 | 4 weeks | Core features, staging environment | — |
| Sprint 3-4 | 4 weeks | Secondary features, integrations | M2: $XX,XXX |
| Sprint 5 | 2 weeks | QA, performance, security review | M3: $XX,XXX |
| Launch | 1 week | Deployment, monitoring, handoff | M4: $XX,XXX |
| Support | 2 weeks | Post-launch bug fixes (included) | — |

Total duration: ~15 weeks
Go-live target: [Date]

Buffer allocation:
  - Add 20% buffer to all engineering estimates
  - Add 1 week buffer before hard launch dates
  - Client review delays extend timeline day-for-day

Dependencies:
  [Gantt-style dependency list]
  Discovery → Design approval → Development start
  API integration → requires client API access (Week 3)
  App Store submission → requires 2 weeks for review (Week 12)
```

## Step 6: Team Composition

```markdown
## Team

| Role | Person | Allocation | Weekly Rate |
|------|--------|-----------|-------------|
| Tech Lead | [Name] | 100% | $X,XXX |
| Senior Engineer | [Name] | 100% | $X,XXX |
| Engineer | [Name] | 50% | $X,XXX |
| Designer | [Name] | 50% (first 6 weeks) | $X,XXX |
| Project Manager | [Name] | 25% | $X,XXX |

Total team cost: $XX,XXX/week at full allocation

Substitution policy:
  - Cure may substitute team members of equal or greater seniority
  - Client will be notified 1 week in advance
  - No substitution of Tech Lead without client approval
  - Knowledge transfer documentation required for any transition

Key person risk:
  - All code is in shared repository with documentation
  - At least 2 team members have context on every module
  - No single point of failure by design
```

## Step 7: Terms and Conditions

```
IP Ownership:
  - All custom code becomes client property upon final payment
  - Cure retains right to use general methodologies and frameworks
  - Open-source components remain under their respective licenses
  - Pre-existing Cure IP (if any) is licensed, not transferred — listed in exhibit

Warranty:
  - 30-day warranty period after go-live
  - Covers defects against agreed requirements (not new features)
  - Bug fixes during warranty: included at no additional cost
  - Extended warranty available via retainer agreement

Liability:
  - Liability capped at total contract value
  - No liability for third-party service outages (cloud providers, APIs)
  - No consequential damages (lost revenue, lost data beyond direct contract value)

Confidentiality:
  - Mutual NDA in effect for duration of engagement + 2 years
  - Client data never shared, used for training, or retained after engagement
  - Cure may list client name in portfolio (unless client opts out)

Termination:
  - Either party may terminate with 14 days written notice
  - Client pays for all work completed through termination date
  - Cure delivers all work-in-progress and documentation upon termination
  - No kill fees for remaining milestones

Payment terms:
  - Net 15 from invoice date
  - Late payment: 1.5%/month after 30 days
  - Work pauses if payment is 30+ days overdue
```

## Step 8: SOW Template Generation

```markdown
# Statement of Work

**Project:** [Project Name]
**Client:** [Client Company]
**Vendor:** Cure Consulting Group
**Effective Date:** [Date]
**SOW Number:** [CURE-YYYY-NNN]

## 1. Overview
[2-3 sentence project description]

## 2. Scope of Work
[Copy from Section 2 of proposal — In Scope, Out of Scope, Assumptions]

## 3. Deliverables
| # | Deliverable | Acceptance Criteria | Due Date |
|---|------------|-------------------|----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

## 4. Timeline
[Copy from Section 5 — phases, durations, milestone dates]

## 5. Pricing and Payment Schedule
| Milestone | Amount | Due |
|-----------|--------|-----|
| M1: Signing | $XX,XXX | On execution |
| M2: [Phase] complete | $XX,XXX | On acceptance |
| M3: [Phase] complete | $XX,XXX | On acceptance |
| M4: Go-live | $XX,XXX | On deployment |
| **Total** | **$XXX,XXX** | |

## 6. Team and Responsibilities
### Cure Responsibilities
[Team composition, deliverables, communication cadence]

### Client Responsibilities
- Designate point of contact: [Name, Email]
- Provide access to: [systems, accounts, assets]
- Review and approve deliverables within [N] business days
- Attend weekly status meetings

## 7. Change Management
Changes to scope require a written Change Order signed by both parties.
Change Orders will include: description, impact to timeline, impact to cost.

## 8. Terms
[Reference Master Services Agreement or include inline terms from Section 7]

---

**Agreed and accepted:**

Cure Consulting Group               [Client Company]
By: _________________________       By: _________________________
Name:                                Name:
Title:                               Title:
Date:                                Date:
```

## Cross-References

- `/legal-doc-scaffold` — terms of service, NDA, and privacy policy templates
- `/engineering-cost-model` — detailed cost estimation for pricing proposals
- `/project-manager` — sprint planning and delivery methodology
- `/client-communication` — stakeholder communication during engagement
- `/sdlc` — SDLC artifacts referenced in technical approach section
