---
name: fundraising-materials
version: "1.0.0"
description: "Generate pitch decks, investor updates, data room checklists, cap table scenarios, and fundraising pipeline management for venture-backed startups"
when_to_use: "Use when preparing pitch decks, data rooms, or fundraising pipeline management. NOT for ongoing investor updates (use investor-reporting)."
argument-hint: "[product-or-round]"
allowed-tools: ["Read", "Grep", "Glob", "WebSearch"]
---

# Fundraising Materials

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

Generate investor-ready materials for venture-backed startups. Pitch decks that close, investor updates that build trust, data rooms that survive diligence, and cap tables that don't surprise you. Built for the Cure Consulting Group portfolio: Vendly, Autograph, The Initiated, Antigravity, TwntyHoops.

## Step 1: Classify the Fundraising Need

| Need | Output |
|------|--------|
| Seed pitch deck | 12-15 slide deck for pre-seed or seed round, angel/institutional |
| Series A deck | Metrics-heavy deck proving product-market fit and scalable GTM |
| Investor update | Monthly email template with metrics, wins, asks |
| Data room prep | Organized folder structure with all diligence documents |
| Cap table modeling | Pre/post money, dilution, SAFE conversion, waterfall analysis |
| Fundraising pipeline | CRM structure, outreach sequence, follow-up cadence |

## Step 2: Gather Context

1. **Product** — which portfolio company? (Vendly, Autograph, The Initiated, Antigravity, TwntyHoops)
2. **Stage** — pre-seed, seed, Series A, bridge? First institutional raise or follow-on?
3. **Current metrics** — MRR, users, growth rate, retention, runway remaining?
4. **Target raise** — how much are you raising? What valuation expectations?
5. **Investor audience** — angels, micro-VCs, institutional VCs, strategics? Generalist or sector-specific?
6. **Timeline** — when do you need to close? How much runway remains?
7. **Prior raises** — existing SAFEs, convertible notes, priced rounds? Current cap table state?

## Step 3: Pitch Deck Structure (12-15 Slides)

```
Every slide gets ONE message. If you need two messages, you need two slides.
Target: 3 minutes to pitch the full deck verbally. If it takes longer, cut.

SLIDE 1 — TITLE
  Company name
  One-line tagline (what you do, not your mission statement)
  Round + amount: "Raising $X Seed Round"
  Contact info
  Rule: no logos of investors you're pitching. No "confidential" stamps.

SLIDE 2 — PROBLEM
  The pain point, stated with data
  Who has this problem and how many of them
  What they do today (the bad alternative)
  Rule: use a quote from a real customer if you have one

  Vendly: "LATAM merchants lose 12% of revenue to fragmented payment infrastructure"
  Autograph: "Physicians spend 2+ hours daily on documentation instead of patients"
  The Initiated: "Women's basketball recruits have zero data-driven tools for college selection"
  Antigravity: "Enterprises spend $2M+/year on manual agent orchestration that fails at scale"
  TwntyHoops: "Basketball culture content is fragmented — no single platform owns the space"

SLIDE 3 — SOLUTION
  What your product does in one sentence
  Live product screenshot or demo GIF — never wireframes
  Show the product, not a diagram of the product
  Rule: if you can't show it, you're too early for this slide

SLIDE 4 — MARKET SIZE
  TAM → SAM → SOM with cited sources
  Bottom-up calculation preferred over top-down
  Show the wedge: what you capture first, then expand into
  Rule: if your TAM is under $1B, reframe the market. If over $100B, you're too broad.

  LATAM additions (Vendly):
    - Latin America digital payments TAM ($500B+ and growing 25% YoY)
    - Merchant OS opportunity within payment infrastructure
    - Country-specific entry strategy (Mexico first? Brazil? Colombia?)
    - Regulatory landscape (Banco de Mexico, PIX, local payment rails)

  Healthcare additions (Autograph):
    - Healthcare IT TAM ($300B+)
    - Clinical documentation sub-market ($5B+)
    - Regulatory pathway: FDA status (if applicable), HIPAA, BAA chain
    - Reimbursement impact: how documentation quality affects revenue cycle

SLIDE 5 — TRACTION
  Show metrics that matter for YOUR stage:

  Pre-seed: waitlist, LOIs, design partners, pilot commitments
  Seed: active users, revenue (even small), growth rate, retention
  Series A: MRR/ARR, MoM growth, net revenue retention, unit economics

  Rule: growth rate > absolute numbers at seed
  Rule: never show vanity metrics (downloads, page views, signups without activation)
  Rule: show the graph. If the graph doesn't go up and to the right, tell the story of why.

SLIDE 6 — BUSINESS MODEL
  How you make money — be specific
  Revenue per customer, pricing tiers, billing model
  Gross margins (actual or projected)
  Path to revenue if pre-revenue: what triggers first dollar?
  Rule: "we'll figure out monetization later" is not a business model

SLIDE 7 — PRODUCT
  Deeper dive into what the product does
  3-4 key features or workflows
  Architecture overview ONLY if it's a technical differentiator (Antigravity: agent orchestration)
  Rule: this is the "show, don't tell" slide

  AI startup additions (Antigravity, Autograph):
    - Model strategy: build vs. fine-tune vs. API
    - Data moat: what proprietary data do you have or will you accumulate?
    - AI safety approach: guardrails, human-in-the-loop, evaluation framework

SLIDE 8 — COMPETITIVE LANDSCAPE
  2x2 positioning matrix (NOT a feature checklist)
  Axes should highlight YOUR advantage
  Include incumbents, direct competitors, and adjacent players
  Rule: "we have no competitors" is a red flag, not a flex
  Rule: never trash competitors — show why you win on the axes that matter

SLIDE 9 — GO-TO-MARKET
  How you acquire customers today
  Distribution strategy: direct sales, PLG, partnerships, marketplace?
  CAC and payback period (if known)
  Channel-specific strategy

  Vendly: merchant aggregator partnerships, payment processor integrations
  Autograph: health system pilot → department → enterprise expansion
  The Initiated: D1 program partnerships, recruit/family direct acquisition
  Antigravity: developer community, enterprise sales, integration partnerships
  TwntyHoops: content-first audience building, event partnerships, creator network

SLIDE 10 — TEAM
  Why THIS team wins in THIS market
  Founder-market fit: what unique experience/access do you have?
  Key hires: who's on board, who's the first hire with this raise?
  Advisors only if they're actively contributing or their name opens doors
  Rule: no stock photos. No "we're looking for a CTO" on your pitch deck.

SLIDE 11 — FINANCIALS
  18-month projection, not 5 years of hockey sticks
  Revenue, costs, net burn, key assumptions
  Unit economics: CAC, LTV, LTV:CAC ratio, payback period
  Current burn rate and runway
  Rule: show your assumptions explicitly — investors will challenge them
  Rule: conservative > optimistic. Beating projections builds trust.

SLIDE 12 — THE ASK
  Amount raising and instrument (SAFE, priced round, convertible note)
  Valuation cap or pre-money (if priced)
  Use of funds — 3-4 categories, specific percentages
  Milestones this capital unlocks (next fundraise trigger)

  Example:
    Raising: $2M Seed (SAFE, $10M cap)
    Use of funds:
      50% — Engineering (hire 3 engineers, ship v2)
      25% — Go-to-market (first sales hire, initial marketing)
      15% — Operations (legal, compliance, infrastructure)
      10% — Buffer (always have buffer)
    Milestones: $50K MRR, 500 active merchants, Series A ready in 18 months

OPTIONAL SLIDES (use 1-2 max):
  - Product roadmap (next 6-12 months, not longer)
  - Case study (one customer success story with metrics)
  - Technical architecture (only if it IS the moat — Antigravity)
  - Regulatory pathway (Autograph — FDA/HIPAA timeline)
```

### Pitch Deck Rules

```
Non-negotiable:
  - One message per slide
  - Data beats narrative — show numbers, not adjectives
  - 30 words maximum per slide (excluding charts/tables)
  - 3-minute verbal pitch test: if you can't present in 3 minutes, cut slides
  - No more than 15 slides total (12 ideal)
  - Send as PDF, never PowerPoint/Keynote (formatting breaks)
  - Include appendix slides for deep-dive questions (don't present them)

Design rules:
  - White or dark background, high contrast
  - One font family, two weights maximum
  - Charts: bar or line only — no pie charts, no 3D, no gradients
  - Brand colors consistent throughout
  - No clip art, no stock photos of "diverse teams in an office"
```

## Step 4: Investor Update Template (Monthly Email)

```
SUBJECT: [Company Name] — [Month Year] Update

TL;DR (3 bullets maximum)
  - [Biggest win — be specific with numbers]
  - [Key challenge — be honest]
  - [One ask — make it actionable]

HIGHLIGHTS
  1. [Win with metric] — e.g., "Hit $12K MRR, up 34% MoM"
  2. [Win with context] — e.g., "Signed first enterprise pilot with [Hospital Name]"
  3. [Win with milestone] — e.g., "Shipped v2.0 with AI scribe, 95% accuracy in testing"

LOWLIGHTS
  1. [Challenge with context and plan] — e.g., "Churn increased to 8% — root cause: onboarding friction. Shipping guided setup flow this sprint."
  Rule: NEVER hide bad news. Investors find out eventually. Early transparency builds trust.

KEY METRICS
| Metric | This Month | Last Month | MoM Change |
|--------|-----------|------------|------------|
| MRR | $X | $X | +X% |
| Active Users | X | X | +X% |
| Burn Rate | $X | $X | +/-X% |
| Runway | X months | X months | — |
| [Product KPI] | X | X | +X% |

ASKS (always include — make it easy for investors to help)
  - Intros: "Looking to meet [specific person/role] at [specific company/fund]"
  - Hiring: "Recruiting [specific role] — job description here: [link]"
  - Advice: "Evaluating [specific decision] — would value your perspective"
  Rule: max 3 asks. Be specific. "Help us with sales" is useless. "Intro to VP Ops at HCA Healthcare" is actionable.

RULES:
  - Under 500 words total (investors skim, they don't read)
  - Send on the same day each month (1st or 15th)
  - Always include runway — even when it's uncomfortable
  - Send to ALL investors, not just leads
  - BCC investor list, use a mail merge tool
  - Include a "reply to help" CTA at the bottom
```

## Step 5: Data Room Checklist

```
Organize in a shared drive (Google Drive or Notion) with these folders:

01 — CORPORATE
  [ ] Certificate of incorporation (current, with all amendments)
  [ ] Bylaws (current version)
  [ ] Cap table (Carta or spreadsheet, fully diluted)
  [ ] Board minutes (all meetings to date)
  [ ] Stockholder agreements (if any)
  [ ] Investor rights agreement (if prior priced round)
  [ ] SAFE/convertible note agreements (all outstanding)
  [ ] 83(b) election filings (for all founders)
  [ ] State registrations / qualifications

02 — FINANCIAL
  [ ] Profit & loss statement (inception to date, monthly)
  [ ] Balance sheet (current)
  [ ] Cash flow statement (last 12 months, monthly)
  [ ] Bank statements (last 6 months)
  [ ] 18-month financial projection with assumptions
  [ ] Burn rate analysis
  [ ] Revenue breakdown by customer/product
  [ ] AR/AP aging (if applicable)

03 — PRODUCT
  [ ] Product demo video (2-3 minutes, current version)
  [ ] Architecture overview (one-page diagram)
  [ ] Product roadmap (6-12 months)
  [ ] IP assignments (all founders and employees)
  [ ] Open source audit (licenses used, compliance)
  [ ] Technical due diligence prep doc

04 — TEAM & HR
  [ ] Org chart (current + planned hires)
  [ ] Employee agreements (template + executed)
  [ ] Contractor agreements (all active)
  [ ] Option plan (equity incentive plan document)
  [ ] Option grant ledger
  [ ] Key person bios / LinkedIn links
  [ ] Offer letters (key hires)

05 — LEGAL
  [ ] Material contracts (customers, vendors, partners)
  [ ] Terms of service (current)
  [ ] Privacy policy (current)
  [ ] IP filings (patents, trademarks — if any)
  [ ] Litigation summary (or confirmation of no pending litigation)
  [ ] Insurance policies (D&O, E&O, general liability)

06 — COMPLIANCE (industry-specific)
  Autograph / Healthcare:
    [ ] HIPAA compliance documentation
    [ ] BAA chain (all vendors handling PHI)
    [ ] Security audit / SOC 2 status
    [ ] Clinical validation data
    [ ] FDA regulatory strategy (if applicable)

  Vendly / Fintech:
    [ ] Money transmission licenses or exemptions
    [ ] PCI DSS compliance status
    [ ] AML/KYC policy documentation
    [ ] Country-specific regulatory filings

07 — METRICS & ANALYTICS
  [ ] Cohort analysis (monthly cohorts, retention over time)
  [ ] Retention curves (by segment if possible)
  [ ] Growth charts (MRR, users, key product metric)
  [ ] Funnel conversion rates (acquisition → activation → revenue)
  [ ] NPS or satisfaction data (if collected)
  [ ] Competitive win/loss analysis

RULES:
  - Every document dated and version-labeled
  - Update data room weekly during active raise
  - Track who accesses what (Google Drive shows this)
  - Never include passwords, API keys, or production credentials
  - Keep a "data room ready" checklist in your project management tool
```

## Step 6: Cap Table Scenarios

```
PRE-MONEY / POST-MONEY CALCULATION
  Pre-money valuation = Post-money - Investment amount
  Post-money valuation = Pre-money + Investment amount
  Investor ownership = Investment / Post-money

  Example:
    Raising $2M on $10M pre-money
    Post-money = $12M
    Investor ownership = $2M / $12M = 16.67%

SAFE CONVERSION
  SAFEs convert at the LOWER of:
    1. Valuation cap / fully diluted shares = price per share at cap
    2. Discount rate applied to priced round price

  Example:
    SAFE: $500K at $8M cap
    Priced round: $2M at $12M pre-money ($14M post)
    Price per share at round: $14M / 10M shares = $1.40
    Price per share at cap: $8M / 10M shares = $0.80 ← lower, this applies
    SAFE converts to: $500K / $0.80 = 625,000 shares

DILUTION MODELING
  For each scenario, model:
    Founder ownership after round
    Employee option pool (typically 10-15% pre-money at seed, 15-20% at Series A)
    Prior investor ownership after dilution
    New investor ownership

  Table format:
  | Stakeholder | Pre-Round % | Post-Round % | Shares | Value at Post-Money |
  |-------------|-------------|-------------|--------|---------------------|
  | Founder 1 | X% | X% | X | $X |
  | Founder 2 | X% | X% | X | $X |
  | Option Pool | X% | X% | X | $X |
  | SAFE Holders | — | X% | X | $X |
  | New Investors | — | X% | X | $X |

OPTION POOL
  Standard sizes by stage:
    Pre-seed: 10% (or none — allocate at seed)
    Seed: 10-15% (pre-money, investors will insist)
    Series A: 15-20% (refresh + new hires)

  Rule: negotiate pool size based on actual hiring plan for next 18 months
  Rule: over-allocating option pool dilutes founders — push back with data

WATERFALL ANALYSIS
  Model returns at different exit values:
  | Exit Value | Preferred Return | Common Shares | Founder Payout | Investor Payout |
  |------------|-----------------|---------------|----------------|-----------------|
  | $10M | $X | $X | $X | $X |
  | $25M | $X | $X | $X | $X |
  | $50M | $X | $X | $X | $X |
  | $100M | $X | $X | $X | $X |

  Key terms that affect waterfall:
    - Liquidation preference (1x non-participating is standard — reject >1x or participating)
    - Participation rights (full participation = double-dip — resist this)
    - Anti-dilution (broad-based weighted average is standard — reject full ratchet)
```

## Step 7: Fundraising Pipeline

```
CRM STRUCTURE (use Notion, Airtable, or spreadsheet)

| Field | Description |
|-------|------------|
| Investor Name | Full name of partner/angel |
| Fund / Firm | Fund name, vintage if known |
| Stage | Fundraise stage they invest in |
| Check Size | Typical investment amount |
| Sector Focus | Relevant verticals (fintech, healthtech, sports, AI) |
| Status | Cold / Warm Intro / First Meeting / Partner Meeting / Diligence / Term Sheet / Closed |
| Warm Intro Source | Who makes the introduction |
| Last Contact | Date of last interaction |
| Next Step | Specific next action |
| Notes | Meeting notes, feedback received |
| Priority | A (strong fit) / B (good fit) / C (backup) |

OUTREACH SEQUENCE
  1. Warm intro request (Day 0)
     — Ask mutual connection for a double opt-in intro
     — Provide a forwardable blurb: 3 sentences on company + why this investor
  2. First meeting (Day 3-7)
     — 30 minutes. Tell your story. Show traction. Gauge interest.
     — End with: "What would you need to see to move forward?"
  3. Follow-up materials (Day 7-8)
     — Send deck + any requested data within 24 hours of meeting
  4. Partner meeting (Day 14-21)
     — Deeper dive. Bring metrics, product demo, customer references.
  5. Diligence (Day 21-35)
     — Open data room. Introduce to customers. Technical review.
  6. Term sheet (Day 35-45)
     — Review with lawyer. Negotiate key terms. Don't sign same day.

FOLLOW-UP CADENCE
  During active raise:
    - Never more than 5 business days between touches
    - Always have a reason to follow up (new metric, new customer, press mention)
    - "Just checking in" is not a follow-up — share something new
    - If no response after 3 follow-ups, move to "passive" — revisit next round

PIPELINE RULES
  - Target 50-80 investors in initial list for seed round
  - Expect 20-30 first meetings from 50 outreach attempts
  - Expect 5-10 serious conversations from 20 first meetings
  - Expect 1-3 term sheets from 5 serious conversations
  - Run a tight process: 6-8 weeks from first meeting to close
  - Create urgency: batch meetings into 2-3 week windows
  - Never give an exploding term sheet — but do set timeline expectations
```

## Artifact Generation (Required)

Generate using Write:
1. **Pitch deck outline**: `docs/pitch-deck-outline.md` — slide-by-slide structure with talking points
2. **Investor update**: `docs/investor-updates/{YYYY-MM}.md` — monthly email template populated with current metrics
3. **Data room index**: `docs/data-room-index.md` — checklist of all required documents with status
4. **Cap table model**: `docs/cap-table-model.md` — pre/post money scenarios and SAFE conversion math
5. **Fundraising pipeline**: `docs/fundraising-pipeline.md` — CRM template with outreach sequence

Use WebSearch to research comparable rounds: "[sector] startup seed round 2025 [region]" to validate valuation expectations.

## Step 8: Output Template

```
FUNDRAISING MATERIALS — [COMPANY NAME]
Round: [ROUND TYPE]
Target: $[AMOUNT]
Date: [TODAY]

DELIVERABLES GENERATED:
  - [ ] Pitch deck ([X] slides, PDF format)
  - [ ] Investor update template (monthly email)
  - [ ] Data room structure (with checklist)
  - [ ] Cap table model (pre/post money, dilution scenarios)
  - [ ] Fundraising pipeline CRM template
  - [ ] Outreach blurb (forwardable intro text)

KEY METRICS FOR DECK:
  MRR: $[X] (growing [X]% MoM)
  Users: [X] active
  Runway: [X] months at current burn
  LTV:CAC: [X]:1

VALUATION CONTEXT:
  Target pre-money: $[X]M
  Post-money: $[X]M
  Investor ownership: [X]%
  Founder dilution: [X]% → [X]%

RELATED SKILLS:
  - /saas-financial-model — unit economics and projections for the deck
  - /engineering-cost-model — infrastructure cost modeling for financial slides
  - /market-research — TAM/SAM/SOM analysis for market size slide
  - /legal-doc-scaffold — ToS, privacy policy for data room
  - /burn-rate-tracker — runway scenarios for financial slides
```
