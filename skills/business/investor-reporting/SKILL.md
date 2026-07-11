---
name: investor-reporting
description: "Generate investor updates, board decks, portfolio financial reports, cap table scenarios, runway modeling, and fundraising pipeline tracking"
when_to_use: "Use when generating monthly investor updates, quarterly board decks, portfolio P&L, or runway modeling. NOT for pitch decks or fundraising (use fundraising-materials)."
argument-hint: "[product-or-portfolio]"
---

# Investor Reporting

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

Investor communications for a multi-product venture studio. Monthly updates, board decks, portfolio financials, cap table modeling, runway scenarios, and data room preparation. Optimized for Cure Consulting Group's portfolio: Vendly, Autograph, The Initiated, Antigravity, and TwntyHoops.

Investors remember two things: how honest you were when things were hard, and whether you delivered on what you said you would. This skill ensures both.

## Step 1: Classify the Reporting Need

| Need | Output | Audience |
|------|--------|----------|
| Monthly investor update | 1-page email with metrics, wins, losses, asks | Angels, pre-seed/seed investors |
| Quarterly board deck | 12-15 slide deck with portfolio health + decisions | Board members, lead investors |
| Portfolio financial report | Consolidated P&L, burn, runway, unit economics | CFO, board, institutional investors |
| Fundraising data room | Organized document checklist for due diligence | Prospective investors, VCs |
| Cap table modeling | Pre/post money, dilution, waterfall, SAFE conversion | Founders, legal, prospective investors |
| Runway & scenario modeling | Burn analysis, revenue scenarios, decision framework | Internal leadership, board |
| Ad-hoc investor request | Custom data pull or narrative for a specific investor | Individual investor or fund |

## Step 2: Gather Context

Before generating any investor artifact, collect:

1. **Scope** — single product or full portfolio report?
2. **Reporting period** — which month/quarter? Exact date range.
3. **Audience** — angels (want narrative + vision), institutional VCs (want metrics + comps), board (want decisions + risks)?
4. **Stage per product**:
   - Vendly: what stage? (pre-revenue, pilot, scaling)
   - Autograph: what stage? (pre-revenue, pilot, scaling)
   - The Initiated: what stage? (pre-revenue, pilot, scaling)
   - Antigravity: what stage? (pre-revenue, pilot, scaling)
   - TwntyHoops: what stage? (pre-revenue, pilot, scaling)
5. **Key metrics available** — MRR, users, GMV, burn, cash position, runway?
6. **Wins this period** — product launches, partnerships, hires, milestones hit?
7. **Losses this period** — missed targets, churn, departures, blockers?
8. **Cash position** — current bank balance, last funding event, next raise timeline?
9. **Specific asks** — what do you need from investors right now?

## Step 3: Monthly Investor Update

The single most important investor communication. Send it on the same day every month, no exceptions. Even — especially — when things are bad.

### Format Rules
```
Delivery:     Plain-text email (not a PDF, not a deck, not a Notion link)
Length:       Under 1 page, 5-minute read maximum
Frequency:    Monthly, same day each month (1st or 15th)
Tone:         Direct, honest, no spin. Bad news first if there is bad news.
Subject line: [Company] Monthly Update — [Month Year]
```

### Template Structure

```
SUBJECT: Cure Consulting Group — [Month Year] Update

TL;DR (3 bullets max)
  - [Biggest win this month — be specific with numbers]
  - [Biggest challenge or miss — be honest]
  - [One-line cash/runway status]

HIGHLIGHTS
  List 3-5 wins. Each must be specific and measurable:
    Good:  "Vendly processed $47K GMV in March, up 32% MoM"
    Bad:   "Vendly is growing nicely"
    Good:  "Signed LOI with Baptist Health for Autograph pilot — 12 providers"
    Bad:   "Autograph had a good month for partnerships"

LOWLIGHTS
  List 2-3 challenges. Never bury bad news. Never spin.
    Good:  "Missed Vendly merchant acquisition target (got 8, target was 15).
            Root cause: onboarding flow too complex. Fix shipping next week."
    Bad:   "Merchant growth was slower than expected but we're optimistic"

  Rules:
    - Every lowlight must include: what happened, why, what you're doing about it
    - If you missed a target from last month's update, call it out explicitly
    - Investors respect honesty. They do not respect surprises at board meetings.

KEY METRICS
┌────────────────────┬──────────┬──────────┬──────────┬─────────┐
│ Metric             │ Vendly   │ Autograph│ Initiated│ Studio  │
├────────────────────┼──────────┼──────────┼──────────┼─────────┤
│ MRR / Revenue      │ $X,XXX   │ $X,XXX   │ $X,XXX   │ $XX,XXX │
│ MoM Growth         │ X%       │ X%       │ X%       │ X%      │
│ Users / Customers  │ XXX      │ XXX      │ XXX      │ —       │
│ Key Product Metric │ GMV: $XX │ Scribes: X│ Coaches: X│ —      │
│ Monthly Burn       │ $X,XXX   │ $X,XXX   │ $X,XXX   │ $XX,XXX │
├────────────────────┼──────────┴──────────┴──────────┼─────────┤
│ Cash Position      │                                │ $XXX,XXX│
│ Runway (months)    │                                │ XX      │
└────────────────────┴────────────────────────────────┴─────────┘

  Always include runway. Investors check this number first.
  If runway < 6 months, flag it explicitly and state your plan.

PRODUCT UPDATES (per product, 2-3 sentences each)
  Vendly:       [What shipped, what's next]
  Autograph:    [What shipped, what's next]
  The Initiated:[What shipped, what's next]
  Antigravity:  [What shipped, what's next]
  TwntyHoops:   [What shipped, what's next]

ASKS (always include at least one)
  Be specific. Investors want to help but need direction.
    Good:  "Looking for intros to LATAM fintech operators, specifically anyone
            who has scaled merchant onboarding in Mexico or Colombia"
    Bad:   "Let us know if you can help with anything"
    Good:  "Hiring a senior ML engineer for Autograph. Ideal: experience with
            medical NLP. If you know anyone, reply and I'll send the JD."
    Bad:   "We're hiring"

  Categories of asks:
    - Introductions (to customers, partners, hires, other investors)
    - Advice (specific strategic questions, not vague "what do you think")
    - Follow-on or bridge (only when appropriate, with clear terms)
```

### Monthly Update Anti-Patterns
```
NEVER DO THESE:
  - Skip a month because "nothing happened" (something always happened)
  - Send it late without acknowledging the delay
  - Use vanity metrics (total signups instead of active users)
  - Hide bad news in the middle of a long paragraph
  - Send a 3-page update (nobody reads past page 1)
  - Use jargon your angels won't understand
  - Forget the ask (you're leaving value on the table)
  - Report metrics differently than last month (consistency builds trust)
  - Round numbers up to make them look better
  - Promise things you can't deliver by next month's update
```

## Step 4: Quarterly Board Deck

See [reference/details.md](reference/details.md) (section “Step 4: Quarterly Board Deck”) for full detail.

## Step 5: Portfolio Financial Report

See [reference/details.md](reference/details.md) (section “Step 5: Portfolio Financial Report”) for full detail.

## Step 6: Cap Table Modeling

See [reference/details.md](reference/details.md) (section “Step 6: Cap Table Modeling”) for full detail.

## Step 7: Runway & Scenario Modeling

The most important financial exercise for an early-stage studio. Know exactly when you run out of money under every scenario.

```
1. CURRENT BURN ANALYSIS
  Fixed costs (don't change with revenue):
    Salaries & contractors:   $XX,XXX/month
    Office / coworking:       $X,XXX/month
    Tools & subscriptions:    $X,XXX/month
    Legal & accounting:       $X,XXX/month
    Insurance:                $XXX/month
    Total fixed:              $XX,XXX/month

  Variable costs (scale with usage/customers):
    Infrastructure (Firebase, GCP):  $X,XXX/month
    AI API costs (OpenAI, etc.):     $X,XXX/month
    Payment processing (Stripe):     $XXX/month
    Marketing spend:                 $X,XXX/month
    Total variable:                  $X,XXX/month

  Total monthly burn:         $XX,XXX
  Monthly revenue:            $XX,XXX
  Net burn:                   $XX,XXX
  Cash position:              $XXX,XXX
  Runway at current net burn: XX months

2. REVENUE TRAJECTORY SCENARIOS (12-month projection)
┌───────┬───────────────┬───────────────┬───────────────┐
│ Month │ Conservative  │ Base          │ Optimistic    │
├───────┼───────────────┼───────────────┼───────────────┤
│ 1     │ $XX,XXX       │ $XX,XXX       │ $XX,XXX       │
│ 3     │ $XX,XXX       │ $XX,XXX       │ $XX,XXX       │
│ 6     │ $XX,XXX       │ $XX,XXX       │ $XX,XXX       │
│ 9     │ $XX,XXX       │ $XX,XXX       │ $XX,XXX       │
│ 12    │ $XX,XXX       │ $XX,XXX       │ $XX,XXX       │
├───────┼───────────────┼───────────────┼───────────────┤
│ Runway│ XX months     │ XX months     │ XX months     │
└───────┴───────────────┴───────────────┴───────────────┘

  Conservative: current growth continues, no new products launch
  Base: planned launches hit, moderate growth
  Optimistic: all targets hit, viral growth or enterprise deal closes

3. SENSITIVITY TABLE — WHAT MOVES THE NEEDLE
┌─────────────────────────────┬───────────────┬───────────────┐
│ Change                      │ Monthly Impact │ Runway Impact │
├─────────────────────────────┼───────────────┼───────────────┤
│ Cut 1 engineer              │ -$X,XXX burn  │ +X months     │
│ Pause TwntyHoops            │ -$X,XXX burn  │ +X months     │
│ Vendly hits 50 merchants    │ +$X,XXX rev   │ +X months     │
│ Autograph closes enterprise │ +$XX,XXX rev  │ +X months     │
│ Raise $250K bridge          │ +$250K cash   │ +X months     │
│ Cut marketing 50%           │ -$X,XXX burn  │ +X months     │
│ Move to cheaper infra       │ -$X,XXX burn  │ +X months     │
└─────────────────────────────┴───────────────┴───────────────┘

4. BREAK-EVEN ANALYSIS PER PRODUCT
  For each product, answer: what does it take to cover its own costs?

  Vendly:       XXX merchants at $XX avg monthly revenue = break-even
  Autograph:    XX providers at $XXX/month = break-even
  The Initiated: X,XXX subscribers at $XX/month = break-even
  Antigravity:  X,XXX users at $XX/month = break-even
  TwntyHoops:   XX events/year at $X,XXX avg net per event = break-even

5. DECISION FRAMEWORK
  When to RAISE:
    - Runway < 6 months and metrics trending up
    - Clear use of funds (hire X, launch Y, scale Z)
    - Favorable market conditions for your stage
    - Never raise out of desperation. Investors smell it.

  When to CUT:
    - Runway < 4 months with no raise in progress
    - A product's metrics have been flat for 3+ months despite investment
    - Cost to acquire next customer is rising, not falling
    - Cut fast. Cut once. Then focus.

  When to DOUBLE DOWN:
    - Product shows clear PMF signals (organic growth, low churn, NPS > 50)
    - Unit economics are improving month over month
    - Marginal cost of growth is decreasing
    - Capital deployed here has higher ROI than other products in portfolio
```

## Step 8: Fundraising Data Room Checklist

Investors will request these documents during due diligence. Have them ready before you start fundraising, not after the first meeting.

```
DATA ROOM STRUCTURE
Organize in a shared drive (Google Drive or DocSend). Number folders for order.

01 — CORPORATE
  [ ] Certificate of Incorporation / Articles of Organization
  [ ] Bylaws / Operating Agreement
  [ ] Board meeting minutes (all)
  [ ] Board consent resolutions
  [ ] Stockholder/member agreements
  [ ] Cap table (current, fully diluted, with all SAFEs/notes)
  [ ] 409A valuation (if applicable)
  [ ] State registrations / qualifications

02 — FINANCIALS
  [ ] Profit & loss statement (trailing 12 months, monthly)
  [ ] Balance sheet (current)
  [ ] Cash flow statement (trailing 12 months)
  [ ] Bank statements (last 6 months)
  [ ] Financial projections (12-24 months, with assumptions documented)
  [ ] Revenue breakdown by product
  [ ] Burn breakdown by product
  [ ] Accounts receivable / payable aging

03 — FUNDRAISING
  [ ] Pitch deck (current version)
  [ ] Executive summary / one-pager
  [ ] Previous term sheets (if any)
  [ ] Outstanding SAFEs / convertible notes (copies)
  [ ] Use of funds plan (this round)
  [ ] Prior investors list with amounts and terms

04 — PRODUCT
  [ ] Product demos (recorded or live links)
  [ ] Architecture overview (1-2 pages, not a novel)
  [ ] Product roadmap (next 6-12 months)
  [ ] User/customer testimonials or case studies
  [ ] Screenshots / UI walkthroughs
  [ ] App Store / Play Store links (if live)

05 — METRICS
  [ ] Cohort retention analysis (by month, by product)
  [ ] Growth charts (users, revenue, GMV — trailing 12 months)
  [ ] Unit economics summary (CAC, LTV, LTV:CAC per product)
  [ ] Funnel metrics (signup to activation to payment)
  [ ] NPS or satisfaction scores (if collected)
  [ ] Churn analysis with reasons

06 — TEAM
  [ ] Org chart
  [ ] Founder bios / LinkedIn profiles
  [ ] Key hire profiles
  [ ] Hiring plan (next 12 months)
  [ ] Employee stock option grants (summary, not individual)
  [ ] Advisory board (if any)

07 — LEGAL
  [ ] IP assignment agreements (all founders and contractors)
  [ ] Employee/contractor agreements (template)
  [ ] Material contracts (customers, vendors, partners)
  [ ] Pending or threatened litigation (disclose or confirm none)
  [ ] Insurance policies (D&O, E&O, general liability)

08 — COMPLIANCE (product-specific)
  [ ] HIPAA BAA and compliance documentation (Autograph)
  [ ] Privacy policies (all products)
  [ ] Terms of Service (all products)
  [ ] Data processing agreements (if handling EU data)
  [ ] SOC 2 status or roadmap (if applicable)
  [ ] COPPA compliance (if applicable, The Initiated — if minors)

09 — TECHNICAL
  [ ] Security review summary (see /security-review skill)
  [ ] Infrastructure overview (cloud providers, architecture diagram)
  [ ] Uptime / reliability metrics (if tracked)
  [ ] Open source license compliance
  [ ] Data backup and disaster recovery plan

READINESS RULES:
  - All documents must be current (within 30 days)
  - Label every document with date and version
  - Redact sensitive PII where possible
  - Use view-only links with tracking (DocSend preferred over raw Google Drive)
  - Have a "data room ready" date on your fundraising timeline
  - Budget 2-3 weeks to assemble from scratch, 2-3 days to refresh
```

## Step 9: KPI Dashboard Definitions

Define exactly what to measure per product. No vanity metrics. Every KPI must be actionable — if it moves, you know what to do.

```
VENDLY — LATAM MERCHANT OS (Marketplace Model)
┌──────────────────────┬──────────────────────────────────────────────┬───────────┐
│ KPI                  │ Formula                                      │ Target    │
├──────────────────────┼──────────────────────────────────────────────┼───────────┤
│ GMV                  │ Total transaction volume processed            │ $XXX K/mo │
│ Take Rate            │ Revenue / GMV                                 │ 2-5%      │
│ Active Merchants     │ Merchants with 1+ transaction in last 30 days│ XXX       │
│ Merchant Retention   │ Merchants active this month / active last mo  │ > 85%     │
│ Avg Revenue/Merchant │ Revenue / active merchants                    │ $XX/mo    │
│ TPV Growth (MoM)     │ (This month GMV - last month GMV) / last mo  │ > 15%     │
│ Merchant CAC         │ Sales + marketing spend / new merchants       │ < $XXX    │
│ Merchant LTV         │ Avg revenue/merchant / monthly churn rate     │ > $X,XXX  │
│ Onboarding Time      │ Median days from signup to first transaction  │ < 7 days  │
│ Support Tickets/Merch│ Monthly support tickets / active merchants    │ < 1.0     │
└──────────────────────┴──────────────────────────────────────────────┴───────────┘

AUTOGRAPH — AI MEDICAL SCRIBE (SaaS / Healthcare)
┌──────────────────────┬──────────────────────────────────────────────┬───────────┐
│ KPI                  │ Formula                                      │ Target    │
├──────────────────────┼──────────────────────────────────────────────┼───────────┤
│ MRR                  │ Active providers × price per provider         │ $XX K/mo  │
│ Active Providers     │ Providers who completed 1+ scribe this month │ XXX       │
│ Scribes Completed    │ Total AI scribes generated this month         │ X,XXX/mo  │
│ Time Saved/Provider  │ Avg minutes saved per provider per day        │ > 60 min  │
│ Accuracy Rate        │ Scribes accepted without major edits / total  │ > 95%     │
│ Pilot Conversion     │ Pilots converted to paid / total pilots ended │ > 60%     │
│ Provider NPS         │ Net Promoter Score from provider surveys      │ > 50      │
│ Churn (monthly)      │ Providers lost / providers at start of month  │ < 3%      │
│ NRR                  │ (Start MRR + expansion - churn) / Start MRR  │ > 110%    │
│ HIPAA Incidents      │ Security/privacy incidents in period          │ 0         │
│ AI Cost/Scribe       │ LLM API cost per scribe generated             │ < $0.50   │
└──────────────────────┴──────────────────────────────────────────────┴───────────┘

THE INITIATED — WOMEN'S BASKETBALL RECRUITING PLATFORM
┌──────────────────────┬──────────────────────────────────────────────┬───────────┐
│ KPI                  │ Formula                                      │ Target    │
├──────────────────────┼──────────────────────────────────────────────┼───────────┤
│ Coach Accounts       │ Verified college coach accounts on platform   │ XXX       │
│ Athlete Profiles     │ Complete athlete profiles (video + stats)     │ X,XXX     │
│ DAU / MAU            │ Daily active / monthly active users           │ > 25%     │
│ Matching Rate        │ Athletes contacted by coaches / total athletes│ > XX%     │
│ Coach Engagement     │ Avg profiles viewed per coach per session     │ > 10      │
│ Platform Stickiness  │ DAU / MAU ratio                               │ > 20%     │
│ Athlete Completion   │ Profiles with video + stats + GPA / total     │ > 70%     │
│ Subscription Revenue │ Paid subscriptions × price                    │ $X,XXX/mo │
│ Recruiting Outcomes  │ Offers/commits attributed to platform          │ XX/season │
│ Coach Retention (Q)  │ Coaches active this quarter / last quarter    │ > 80%     │
└──────────────────────┴──────────────────────────────────────────────┴───────────┘

ANTIGRAVITY — AI AGENT ORCHESTRATION IDE (Dev Tools)
┌──────────────────────┬──────────────────────────────────────────────┬───────────┐
│ KPI                  │ Formula                                      │ Target    │
├──────────────────────┼──────────────────────────────────────────────┼───────────┤
│ Total Signups        │ Cumulative accounts created                   │ X,XXX     │
│ DAU                  │ Users who opened IDE in last 24 hours         │ XXX       │
│ Weekly Active        │ Users active 3+ days in last 7                │ XXX       │
│ Agents Deployed      │ Total agent workflows deployed to production  │ X,XXX     │
│ Retention (D7)       │ Users active on day 7 / users signed up 7d ago│ > 40%    │
│ Retention (D30)      │ Users active on day 30 / signed up 30d ago   │ > 20%     │
│ Freemium Conversion  │ Paid users / total active users              │ > 5%      │
│ MRR                  │ Paid users × avg price                        │ $X,XXX/mo │
│ Community PRs        │ Open source contributions per month           │ XX/mo     │
│ NPS                  │ Net Promoter Score from user surveys          │ > 40      │
│ Avg Session Duration │ Median minutes per IDE session                │ > 20 min  │
└──────────────────────┴──────────────────────────────────────────────┴───────────┘

TWNTYHOOPS — BASKETBALL MEDIA & EVENTS
┌──────────────────────┬──────────────────────────────────────────────┬───────────┐
│ KPI                  │ Formula                                      │ Target    │
├──────────────────────┼──────────────────────────────────────────────┼───────────┤
│ Events Held          │ Total events this period                      │ XX/quarter│
│ Avg Attendance       │ Total attendees / events held                 │ XXX/event │
│ Revenue per Event    │ (Tickets + sponsorships + merch) / events     │ $X,XXX    │
│ Cost per Event       │ Total event costs / events held               │ $X,XXX    │
│ Margin per Event     │ (Revenue - cost) / revenue per event          │ > 40%     │
│ Social Reach         │ Total followers across platforms              │ XX,XXX    │
│ Engagement Rate      │ (Likes + comments + shares) / impressions    │ > 3%      │
│ Sponsorship Revenue  │ Total sponsorship deals closed this period    │ $XX,XXX/Q │
│ Sponsor Retention    │ Returning sponsors / total sponsors last period│ > 70%    │
│ Content Pieces       │ Videos, articles, posts published             │ XX/week   │
│ Email List Size      │ Total newsletter subscribers                  │ X,XXX     │
│ Email Open Rate      │ Opens / emails sent                           │ > 30%     │
└──────────────────────┴──────────────────────────────────────────────┴───────────┘

DASHBOARD RULES:
  - Update every KPI weekly, report monthly (at minimum)
  - Every KPI needs a target. A number without a target is just a number.
  - Show trailing 3-month trend, not just current value
  - Red/yellow/green status based on % of target achieved
  - If a KPI has been red for 3 months, escalate to board or kill the initiative
  - Never add a KPI without removing one. Dashboard bloat kills focus.
  - Source of truth: one spreadsheet or dashboard tool, not scattered across Notion/Sheets/Slack
```

## Artifact Generation (Required)

Generate using Write:
1. **Monthly update**: `docs/investor-updates/{YYYY-MM}.md` — populated template
2. **Board deck outline**: `docs/board-deck-outline.md` — slide-by-slide structure
3. **KPI dashboard config**: `monitoring/investor-kpi.json` — dashboard template
4. **Metric collection queries**: `analytics/investor-metrics.sql` — queries for each KPI

## Cross-References

Related skills for investor reporting workflows:
- `/saas-financial-model` — Deep unit economics and pricing analysis
- `/engineering-cost-model` — Build costs and infrastructure forecasting
- `/sdlc` — Product roadmap artifacts for board decks
- `/analytics-implementation` — Event tracking to feed KPI dashboards
- `/security-review` — Security posture for data room
- `/legal-doc-scaffold` — Legal docs for data room compliance section

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: `/engagement-automation`).

- **Cadence:** monthly
- **Session loop:** `/loop 4w /cure-product-engineering:investor-reporting`
- **Unattended:** cloud routine — Monthly draft of the investor update from repo/metrics state. Draft only: never auto-send. Recipes: docs/AUTOMATION.md in the plugin repo.
- **Budget:** ~120k tokens/run; cap at one run per monthly period.
- **Guardrails:** read-only run; deliver draft update as a report file — a human always reviews before anything is sent; report on failure rather than retrying.
