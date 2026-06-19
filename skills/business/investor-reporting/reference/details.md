# investor-reporting: detailed reference

> Reference material for the `investor-reporting` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 4: Quarterly Board Deck
- Step 5: Portfolio Financial Report
- Step 6: Cap Table Modeling

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
│ Vendly      │ [X]    │ $XX,XXX  │ XX% QoQ  │ Green     │ Up    │
│ Autograph   │ [X]    │ $XX,XXX  │ XX% QoQ  │ Yellow    │ Flat  │
│ Initiated   │ [X]    │ $XX,XXX  │ XX% QoQ  │ Green     │ Up    │
│ Antigravity │ [X]    │ $XX,XXX  │ XX% QoQ  │ Yellow    │ Up    │
│ TwntyHoops  │ [X]    │ $XX,XXX  │ XX% QoQ  │ Green     │ Up    │
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

  Per-product focus:
    Vendly:       GMV, merchant count, take rate, merchant retention
    Autograph:    Provider count, scribes completed, time saved per provider, pilot conversions
    The Initiated: Coach accounts, athlete profiles, matching rate, platform engagement
    Antigravity:  Downloads/signups, DAU, agents deployed, community activity
    TwntyHoops:   Events held, attendance, social reach, sponsorship revenue

Slide 11: STRATEGIC DECISIONS
  Frame 1-3 decisions the board needs to weigh in on.
  Format per decision:
    Context:       [Why this decision matters now]
    Options:       [Option A] vs [Option B] (vs [Option C])
    Recommendation:[What management recommends and why]
    Ask:           [Vote / Feedback / Approval needed]

  Example decisions:
    - Should we raise a bridge round or extend runway by cutting Product X?
    - Should we pursue enterprise vs SMB for Autograph?
    - Should we spin out Antigravity as a separate entity?

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
│                      │ Vendly   │ Autograph│ Initiated│ Antigrav │ TwntyH   │ TOTAL    │
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
  Per-product MRR/ARR breakdown:
    Vendly:       GMV $XXX,XXX × take rate X.X% = revenue $X,XXX
    Autograph:    XX providers × $XXX/mo = MRR $X,XXX
    The Initiated: XX subscriptions × $XX/mo + sponsorships = $X,XXX
    Antigravity:  XX users × $XX/mo (freemium conversion X%) = $X,XXX
    TwntyHoops:   Events $X,XXX + Sponsorships $X,XXX + Media $X,XXX = $X,XXX

4. CASH POSITION & RUNWAY
  Opening cash balance:     $XXX,XXX
  + Revenue received:       $XX,XXX
  - Total expenses paid:    ($XX,XXX)
  - One-time costs:         ($X,XXX)
  = Closing cash balance:   $XXX,XXX

  Monthly burn rate:        $XX,XXX
  Runway at current burn:   XX months
  Runway if revenue grows 10% MoM: XX months

5. UNIT ECONOMICS PER PRODUCT
┌─────────────┬─────────┬─────────┬─────────┬─────────┬──────────┐
│ Metric      │ Vendly  │ Autograph│ Initiated│ Antigrav│ TwntyH  │
├─────────────┼─────────┼─────────┼─────────┼─────────┼──────────┤
│ CAC         │ $XXX    │ $X,XXX  │ $XX     │ $XX     │ N/A      │
│ LTV         │ $X,XXX  │ $XX,XXX │ $XXX    │ $XXX    │ N/A      │
│ LTV:CAC     │ X.Xx    │ X.Xx    │ X.Xx    │ X.Xx    │ N/A      │
│ Payback (mo)│ XX      │ XX      │ XX      │ XX      │ N/A      │
│ Gross Margin│ XX%     │ XX%     │ XX%     │ XX%     │ XX%      │
│ Churn (mo)  │ X.X%    │ X.X%   │ X.X%    │ X.X%    │ N/A      │
└─────────────┴─────────┴─────────┴─────────┴─────────┴──────────┘

  TwntyHoops uses event-based economics, not SaaS metrics:
    Revenue per event, cost per event, margin per event, sponsorship yield

6. INFRASTRUCTURE COSTS BY PRODUCT
┌─────────────────┬─────────┬─────────┬─────────┬─────────┬──────────┐
│ Service         │ Vendly  │ Autograph│ Initiated│ Antigrav│ TwntyH  │
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
  For each outstanding SAFE or note:
┌────────────────────┬───────────┬────────────┬───────────┬───────────┐
│ Instrument         │ Amount    │ Val Cap    │ Discount  │ Converts  │
├────────────────────┼───────────┼────────────┼───────────┼───────────┤
│ SAFE — Investor A  │ $XXX,XXX  │ $X.XM      │ —         │ At next   │
│ SAFE — Investor B  │ $XXX,XXX  │ $X.XM      │ 20%       │ priced rnd│
│ Conv Note — Inv C  │ $XXX,XXX  │ $X.XM      │ 20%       │ + interest│
└────────────────────┴───────────┴────────────┴───────────┴───────────┘

  Conversion math:
    SAFE with cap:      shares = investment / (cap / fully diluted shares)
    SAFE with discount: shares = investment / (price × (1 - discount))
    Use whichever gives the investor MORE shares (investor-favorable)

    Convertible note:   same as SAFE, but add accrued interest to principal
    Interest:           principal × rate × (days elapsed / 365)

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
