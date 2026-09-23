# investor-reporting: detailed reference

> Reference for the `investor-reporting` skill. Read the section you need: board deck, portfolio
> financial report, cap table, data room, or KPI definitions. Product names come from PORTFOLIO.md;
> `[Product A]`… below are placeholders.

## Contents
- Step 4: Quarterly Board Deck
- Step 5: Portfolio Financial Report
- Step 6: Cap Table Modeling
- Step 8: Data Room
- Step 9: KPI Definitions by Business Model

## Step 4: Quarterly Board Deck

12-15 slides maximum. Every slide has one message. If a slide needs a paragraph of explanation, it is a bad slide.

### Deck Structure

```
QUARTERLY BOARD DECK — Q[X] [YEAR]
Cure Consulting Group
[Date]

Slide 1: TITLE + AGENDA
  Cure Consulting Group — Q[X] [YEAR] Board Review
  Agenda: Portfolio Overview | Financials | Product Deep Dives | Decisions

Slide 2: EXECUTIVE SUMMARY
  3-5 bullet points covering the quarter. Same TL;DR energy as the
  monthly update, but for the full quarter.
  Traffic light status per product: Green / Yellow / Red

Slide 3: PORTFOLIO HEALTH SCORECARD
┌─────────────┬────────┬──────────┬──────────┬───────────┬───────┐
│ Product     │ Stage  │ Revenue  │ Growth   │ Health    │ Trend │
├─────────────┼────────┼──────────┼──────────┼───────────┼───────┤
│ [Product A] │ [X]    │ $XX,XXX  │ XX% QoQ  │ Green     │ Up    │
│ [Product B] │ [X]    │ $XX,XXX  │ XX% QoQ  │ Yellow    │ Flat  │
│ …one row per product in PORTFOLIO.md                            │
└─────────────┴────────┴──────────┴──────────┴───────────┴───────┘

  Health criteria:
    Green:  On track or ahead of plan
    Yellow: Behind plan but recoverable, or facing known risks
    Red:    Significantly behind, requires board-level discussion

Slide 4: CONSOLIDATED FINANCIALS
  - Total revenue (MRR breakdown by product)
  - Total burn (allocated by product + shared costs)
  - Cash position and runway
  - Quarter-over-quarter comparison
  - Use bar charts, not tables. One data story per chart.

Slide 5: REVENUE BREAKDOWN
  Stacked bar chart: revenue by product over last 4 quarters
  Show trajectory, not just this quarter's snapshot
  Include revenue mix % (which products are driving growth)

Slide 6: BURN & RUNWAY
  - Monthly burn trend line (last 6 months)
  - Burn by category: engineering, marketing, infrastructure, G&A
  - Runway at current burn rate
  - Runway if revenue hits target
  - Runway if revenue misses by 25%

Slides 7-10: PRODUCT DEEP DIVES (one per active product, 1 slide each)
  For each product:
    - Key metrics (3-4 max, with QoQ change)
    - Top milestone achieved this quarter
    - Top risk or blocker
    - Next quarter's #1 priority
    - 1 chart showing the metric that matters most

  Per-product focus: the 3–4 KPIs for that product's business model (Step 9 below).

Slide 11: STRATEGIC DECISIONS
  Frame 1-3 decisions the board needs to weigh in on.
  Format per decision:
    Context:       [Why this decision matters now]
    Options:       [Option A] vs [Option B] (vs [Option C])
    Recommendation:[What management recommends and why]
    Ask:           [Vote / Feedback / Approval needed]

  Example decisions:
    - Should we raise a bridge round or extend runway by cutting Product X?
    - Should we pursue enterprise vs SMB for [Product]?
    - Should we spin out [Product] as a separate entity?

Slide 12: NEXT QUARTER PRIORITIES
  Top 3 priorities for the studio. Tied to metrics.
    Priority 1: [Goal] — measured by [metric] — target: [number]
    Priority 2: [Goal] — measured by [metric] — target: [number]
    Priority 3: [Goal] — measured by [metric] — target: [number]

Slide 13: APPENDIX — DETAILED FINANCIALS
  Full P&L table, balance sheet summary, detailed burn breakdown.
  This is the "for the record" slide. Board members who want detail will ask.

Slide 14: APPENDIX — PRODUCT ROADMAPS
  High-level roadmap per product (next 2 quarters only, no 5-year fantasies)

Slide 15: APPENDIX — CAP TABLE SUMMARY (if relevant)
  Current ownership, option pool remaining, next round implications
```

### Slide Design Rules
```
ONE message per slide. If you can't summarize the slide in 8 words, split it.
Data visualization over tables. Bar charts > line charts > tables.
No walls of text. Max 6 bullet points per slide, max 10 words per bullet.
Consistent color coding. Green/Yellow/Red for health. Same color per product everywhere.
White space is your friend. Crowded slides signal unclear thinking.
Every number needs context. "$50K MRR" means nothing. "$50K MRR (up 30% QoQ)" tells a story.
```

## Step 5: Portfolio Financial Report

Consolidated financials across the full venture studio. This is the CFO's document.

```
CURE CONSULTING GROUP — PORTFOLIO FINANCIAL REPORT
Period: [Month/Quarter] [Year]
Prepared: [Date]

1. CONSOLIDATED P&L
┌──────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│                      │ [Prod A] │ [Prod B] │ [Prod C] │ [Prod D] │ [Prod E] │ TOTAL    │
├──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Revenue              │ $X,XXX   │ $X,XXX   │ $X,XXX   │ $X,XXX   │ $X,XXX   │ $XX,XXX  │
│ COGS                 │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($XX,XXX)│
│ Gross Profit         │ $X,XXX   │ $X,XXX   │ $X,XXX   │ $X,XXX   │ $X,XXX   │ $XX,XXX  │
│ Gross Margin         │ XX%      │ XX%      │ XX%      │ XX%      │ XX%      │ XX%      │
├──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Engineering          │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($XX,XXX)│
│ Marketing            │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($XX,XXX)│
│ Infrastructure       │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($XX,XXX)│
│ G&A (allocated)      │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($XX,XXX)│
├──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Net Income (Loss)    │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($X,XXX) │ ($XX,XXX)│
└──────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

2. SHARED COST ALLOCATION
  Studio-level costs must be allocated. Use this framework:
    Engineering shared services (DevOps, infra, code review): by engineering hours
    G&A (legal, accounting, office): equal split or by revenue share
    Marketing shared (brand, website): by attribution or equal split
    Leadership time: by hours logged per product

  Rule: Never let shared costs hide a product's true burn.
        Every dollar must be attributed to a product or to "Studio Overhead."

3. REVENUE DETAIL
  Per-product revenue build, by business model:
    Marketplace:   GMV $XXX,XXX × take rate X.X% = revenue $X,XXX
    B2B SaaS:      XX seats/providers × $XXX/mo = MRR $X,XXX
    Subscription:  XX subscriptions × $XX/mo + sponsorships = $X,XXX
    Freemium tool: XX paid users × $XX/mo (conversion X%) = $X,XXX
    Media/events:  events $X,XXX + sponsorships $X,XXX + media $X,XXX = $X,XXX

4. CASH POSITION & RUNWAY
  Opening cash balance:     $XXX,XXX
  + Revenue received:       $XX,XXX
  - Total expenses paid:    ($XX,XXX)
  - One-time costs:         ($X,XXX)
  = Closing cash balance:   $XXX,XXX

  Monthly burn rate:        $XX,XXX
  Runway at current burn:   XX months (status per burn-rate-tracker thresholds)
  Runway, conservative case: XX months

5. UNIT ECONOMICS PER PRODUCT
┌─────────────┬─────────┬─────────┬─────────┬─────────┬──────────┐
│ Metric      │ [Prod A]│ [Prod B]│ [Prod C]│ [Prod D]│ [Prod E] │
├─────────────┼─────────┼─────────┼─────────┼─────────┼──────────┤
│ CAC         │ $XXX    │ $X,XXX  │ $XX     │ $XX     │ N/A      │
│ LTV         │ $X,XXX  │ $XX,XXX │ $XXX    │ $XXX    │ N/A      │
│ LTV:CAC     │ X.Xx    │ X.Xx    │ X.Xx    │ X.Xx    │ N/A      │
│ Payback (mo)│ XX      │ XX      │ XX      │ XX      │ N/A      │
│ Gross Margin│ XX%     │ XX%     │ XX%     │ XX%     │ XX%      │
│ Churn (mo)  │ X.X%    │ X.X%   │ X.X%    │ X.X%    │ N/A      │
└─────────────┴─────────┴─────────┴─────────┴─────────┴──────────┘

  Event-based products use event economics, not SaaS metrics:
    Revenue per event, cost per event, margin per event, sponsorship yield

6. INFRASTRUCTURE COSTS BY PRODUCT
┌─────────────────┬─────────┬─────────┬─────────┬─────────┬──────────┐
│ Service         │ [Prod A]│ [Prod B]│ [Prod C]│ [Prod D]│ [Prod E] │
├─────────────────┼─────────┼─────────┼─────────┼─────────┼──────────┤
│ Firebase/GCP    │ $XXX    │ $XXX    │ $XXX    │ $XXX    │ $XXX     │
│ AI APIs         │ $XX     │ $X,XXX  │ $XX     │ $XXX    │ $XX      │
│ Stripe fees     │ $XXX    │ $XXX    │ $XX     │ $XX     │ $XX      │
│ Vercel/hosting  │ $XX     │ $XX     │ $XX     │ $XX     │ $XX      │
│ Other services  │ $XX     │ $XX     │ $XX     │ $XX     │ $XX      │
├─────────────────┼─────────┼─────────┼─────────┼─────────┼──────────┤
│ TOTAL           │ $XXX    │ $X,XXX  │ $XXX    │ $XXX    │ $XXX     │
└─────────────────┴─────────┴─────────┴─────────┴─────────┴──────────┘

  Flag any product where AI API costs > 20% of revenue.
  Flag any product where infra costs are growing faster than revenue.

7. SCENARIO MODELING
  What if we pause Product X?
    - Savings: $X,XXX/month (team reallocation, infra reduction)
    - Lost revenue: $X,XXX/month
    - Net impact on runway: +X months
    - Strategic cost: [what do we lose beyond revenue?]

  What if Product Y hits target?
    - Revenue increase: $X,XXX/month by Month X
    - Impact on runway: +X months
    - Required investment to hit target: $X,XXX
    - ROI: X:1 over 12 months
```

## Step 6: Cap Table Modeling

Model ownership, dilution, and exit scenarios. Get this wrong and founders, employees, and investors all lose.

```
1. CURRENT CAP TABLE
┌────────────────────┬──────────┬────────┬─────────────┐
│ Shareholder        │ Shares   │ %      │ Type        │
├────────────────────┼──────────┼────────┼─────────────┤
│ Founder 1          │ X,XXX,XXX│ XX.X%  │ Common      │
│ Founder 2          │ X,XXX,XXX│ XX.X%  │ Common      │
│ Angel Investor A   │ XXX,XXX  │ X.X%   │ Preferred   │
│ Angel Investor B   │ XXX,XXX  │ X.X%   │ SAFE (conv) │
│ Employee Pool      │ XXX,XXX  │ XX.X%  │ Options     │
│   - Allocated      │ XXX,XXX  │ X.X%   │ Options     │
│   - Unallocated    │ XXX,XXX  │ X.X%   │ Options     │
├────────────────────┼──────────┼────────┼─────────────┤
│ TOTAL              │ X,XXX,XXX│ 100.0% │             │
└────────────────────┴──────────┴────────┴─────────────┘

2. PRE/POST MONEY VALUATION SCENARIOS
┌──────────────────────┬───────────┬───────────┬───────────┐
│                      │ Low       │ Base      │ High      │
├──────────────────────┼───────────┼───────────┼───────────┤
│ Pre-money valuation  │ $X.XM     │ $X.XM     │ $X.XM     │
│ Round size           │ $XXX K    │ $XXX K    │ $X.XM     │
│ Post-money valuation │ $X.XM     │ $X.XM     │ $XX.XM    │
│ New investor %       │ XX.X%     │ XX.X%     │ XX.X%     │
│ Founder dilution     │ XX.X%     │ XX.X%     │ XX.X%     │
│ Price per share      │ $X.XX     │ $X.XX     │ $X.XX     │
└──────────────────────┴───────────┴───────────┴───────────┘

3. OPTION POOL SIZING
  Standard: 10-20% of fully diluted shares
  Pre-seed/Seed: 10-15% (smaller team, fewer hires planned)
  Series A: 15-20% (investors will require refresh)

  Rule: Create or expand the pool BEFORE the round, not after.
        The dilution comes from existing shareholders, not new investors.
        Investors know this. You should too.

  Current pool: X,XXX,XXX shares (XX.X% of fully diluted)
  Allocated:    X,XXX,XXX shares
  Remaining:    X,XXX,XXX shares
  Recommended:  [Expand to XX% if raising, current is sufficient if not]

4. SAFE/CONVERTIBLE NOTE CONVERSION
  For each outstanding SAFE or note: amount, cap, discount, form (post- or pre-money SAFE),
  interest (notes). Confirm the form from the signed document before modeling.

  Round price = pre-money valuation / pre-money fully diluted shares (never post-money).
  A SAFE converts at the LOWER of the cap price and the discounted round price.
  POST-MONEY SAFE (YC standard since 2018): SAFE ownership = investment / post-money cap,
    measured on capitalization that INCLUDES the SAFE shares, before new money.
  PRE-MONEY SAFE (older form): cap price = cap / capitalization EXCLUDING SAFE shares.
  Convertible note: same mechanics; principal plus accrued interest
    (principal × rate × days elapsed / 365) converts.

  Worked example (post-money SAFE, no discount; 10,000,000 founder + pool shares):
    SAFE $500K at $8M post-money cap → 6.25% → 666,667 shares; cap price $0.75
    Round: $2M at $12M pre → $12M / 10,666,667 = $1.125; cap applies ($0.75 is lower)
    New investor 1,777,778 shares (14.29%); 12,444,444 × $1.125 = $14M post ✓; SAFE 5.36%
    Same SAFE as a pre-money SAFE: $8M / 10,000,000 = $0.80 → 625,000 shares.

5. DILUTION WATERFALL — PROPOSED ROUND
┌────────────────────┬───────────┬──────────┬───────────┬──────────┐
│ Shareholder        │ Pre-Round │ Pre %    │ Post-Round│ Post %   │
├────────────────────┼───────────┼──────────┼───────────┼──────────┤
│ Founder 1          │ X,XXX,XXX │ XX.X%    │ X,XXX,XXX │ XX.X%   │
│ Founder 2          │ X,XXX,XXX │ XX.X%    │ X,XXX,XXX │ XX.X%   │
│ Existing Investors │ XXX,XXX   │ X.X%     │ XXX,XXX   │ X.X%    │
│ SAFE Conversions   │ —         │ —        │ XXX,XXX   │ X.X%    │
│ New Option Pool    │ —         │ —        │ XXX,XXX   │ XX.X%   │
│ New Investors      │ —         │ —        │ X,XXX,XXX │ XX.X%   │
├────────────────────┼───────────┼──────────┼───────────┼──────────┤
│ TOTAL              │ X,XXX,XXX │ 100.0%   │ X,XXX,XXX │ 100.0%  │
└────────────────────┴───────────┴──────────┴───────────┴──────────┘

   Standard terms to hold: 1x non-participating liquidation preference; broad-based
   weighted-average anti-dilution. Push back on >1x, participating preferred, or full ratchet.

6. EXIT WATERFALL (WHO GETS WHAT)
  Model at 3 exit values: $5M, $20M, $50M (or use actual scenarios)

  Liquidation preferences matter:
    1x non-participating preferred: investor gets back their money OR converts (whichever is more)
    1x participating preferred: investor gets back their money AND their pro-rata share
    No preference (common): everyone splits pro-rata

┌────────────────────┬──────────┬──────────┬──────────┐
│ Shareholder        │ $5M Exit │ $20M Exit│ $50M Exit│
├────────────────────┼──────────┼──────────┼──────────┤
│ Founder 1          │ $X.XM    │ $X.XM    │ $XX.XM   │
│ Founder 2          │ $X.XM    │ $X.XM    │ $XX.XM   │
│ Investors (pref)   │ $X.XM    │ $X.XM    │ $X.XM    │
│ Employees (options)│ $XXX,XXX │ $X.XM    │ $X.XM    │
├────────────────────┼──────────┼──────────┼──────────┤
│ TOTAL              │ $5.0M    │ $20.0M   │ $50.0M   │
└────────────────────┴──────────┴──────────┴──────────┘

  Studio-specific consideration:
    If Cure holds equity in each product entity separately, model the waterfall
    per entity. If Cure is a single entity with product lines, model once.
    This distinction matters enormously at exit. Decide the structure early.
```

## Step 8: Data Room

Numbered folders in a shared drive with view tracking (DocSend or equivalent). Budget 2–3 weeks
to assemble from scratch and 2–3 days to refresh; every document dated and versioned; refresh
weekly during an active raise.

```
01 — CORPORATE    Charter + amendments, bylaws/operating agreement, board minutes and consents,
                  stockholder agreements, cap table (fully diluted, all SAFEs/notes), 409A,
                  83(b) filings for founders, state registrations
02 — FINANCIALS   Monthly P&L (trailing 12 or inception), balance sheet, cash flow, 6 months of
                  bank statements, 12–24 month projection with assumptions, revenue and burn
                  by product, AR/AP aging
03 — FUNDRAISING  Current deck, one-pager, prior term sheets, SAFEs/notes, use of funds,
                  prior investors with amounts and terms
04 — PRODUCT      Demo video (2–3 min), architecture overview (1–2 pages), 6–12 month roadmap,
                  case studies, store links
05 — METRICS      Cohort retention by product, growth charts, unit economics, funnel,
                  NPS, churn reasons, win/loss
06 — TEAM         Org chart, bios, hiring plan, option plan + grant ledger (summary), advisors
07 — LEGAL        IP assignments (all founders, employees, contractors), employee/contractor
                  agreement templates, material contracts, litigation (or confirmation of
                  none), insurance (D&O, E&O, GL, cyber), trademarks/patents
08 — COMPLIANCE   Privacy policy and ToS per product; DPAs if EU data; SOC 2 status.
                  Health: HIPAA documentation, BAA chain for every vendor touching PHI,
                  clinical validation, FDA pathway if applicable.
                  Fintech: money-transmission licenses or exemptions, PCI DSS status,
                  AML/KYC policy, country filings.
                  Minors' data: COPPA posture where any user may be under 13.
09 — TECHNICAL    Security review summary, infra overview, uptime, open-source license audit,
                  backup and DR plan
```

Readiness: documents current within 30 days; PII redacted where possible; no credentials
anywhere in the room.

## Step 9: KPI Definitions by Business Model

Pick the set matching the product's model in PORTFOLIO.md. Targets are set per product; the
defaults below are Cure starting points, not benchmarks.

```
MARKETPLACE / MERCHANT PLATFORM
  GMV · take rate (revenue/GMV, 2–5%) · active merchants (1+ txn in 30d) · merchant retention
  (> 85%/mo) · GMV growth (> 15% MoM early) · merchant CAC · median days signup→first txn (< 7)
  · support tickets per merchant (< 1.0/mo)

B2B / CLINICAL SAAS (per-provider or per-seat)
  MRR · active seats (1+ core action this month) · core actions per seat · time saved per user
  · accepted-without-major-edit rate for AI output (> 95%) · pilot→paid conversion (> 60%)
  · monthly churn (< 3%) · NRR (> 110%) · security/privacy incidents (0) · AI cost per core
  action

TWO-SIDED COMMUNITY / RECRUITING PLATFORM
  Verified accounts per side · profile completion (> 70%) · DAU/MAU (> 20%) · match or contact
  rate · engagement per session · subscription revenue · outcomes attributed to the platform
  · quarterly retention of the paying side (> 80%)

DEVELOPER TOOL (freemium)
  Signups · weekly active (3+ days in 7) · D7 (> 40%) and D30 (> 20%) retention · free→paid
  conversion (> 5%) · MRR · core objects shipped (e.g. workflows deployed) · community
  contributions · NPS (> 40)

MEDIA / EVENTS
  Events held · average attendance · revenue, cost, and margin per event (> 40%) · sponsorship
  revenue and sponsor retention (> 70%) · audience reach · engagement rate (> 3%) · email list
  and open rate (> 30%)
```

Dashboard rules: update weekly, report monthly; every KPI has a formula, target, and trailing
3-month trend; red/yellow/green by % of target; red for 3 months → escalate or kill the
initiative; one source of truth, not scattered spreadsheets.
