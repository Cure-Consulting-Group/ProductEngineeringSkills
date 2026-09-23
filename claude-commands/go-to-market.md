# Go-to-Market Plan

**Outcome:** a launch plan a small studio team can execute — one positioning statement, a messaging
hierarchy, at most three priority channels, phased launch with success criteria, and a kill list of
what we deliberately won't do. Done when every phase has a measurable exit criterion and every
channel has an owner and a CAC estimate. Match length to the need; no filler sections or restated
summaries.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Portfolio products: !`grep -m6 -E '^#{2,3} ' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Prior research: !`ls docs/market-research.md docs/icp.md docs/competitive-analysis.md 2>/dev/null | grep . || echo "(no market research docs)"`

Read any listed research docs and the product's PORTFOLIO.md section before planning.

## Step 1: Classify

| Request | Deliver |
|---|---|
| New product launch | Full plan (Step 3) |
| New market / segment | Positioning, ICP targeting, channels, phases 1–2 |
| Major feature release | Messaging, existing-user channels, launch checklist |
| Positioning only | Statement, one-liner, messaging hierarchy |

## Step 2: Gather Context

Ask only for what is missing: product and problem, ICP (from market-research if it exists), stage
(pre-launch / beta / public / expansion), launch date and whether it's hard, team and paid budget,
current traction (waitlist, beta users, revenue).

## Step 3: Cure GTM Defaults

These are the opinionated calls; deviate only with a stated reason.

- **Channels:** pick at most three for launch. Default for a small studio with no paid budget: founder-led direct outreach + one community where the ICP already gathers + one owned channel (email list or SEO). Paid acquisition only after month-1 retention is proven.
- **Kill list** (write it down): launching on every social platform at once, PR agencies pre-traction, paid ads before a retention signal, conferences without a pipeline target, "brand awareness" goals without a number.
- **Pricing:** tier structure, prices, and margins come from the saas-financial-model skill; this plan covers how tiers are messaged and the upgrade trigger. Growth default: no credit card to start, reverse trial (growth-engineering).
- **Launch sequence:** Phase 0 pre-launch (warm list, message tests) → Phase 1 beta (first paying customers, retention check) → Phase 2 public launch (awareness spike) → Phase 3 growth (repeatable acquisition, LTV/CAC). Don't enter Phase 2 until Phase 1's retention exit criterion is met.
- **Metrics:** one north star, a funnel with month-1 and month-3 targets, activation rate, trial→paid, month-1 retention, LTV/CAC.

## Step 4: Plan Sections

1. **Positioning** — "For [ICP] who [need], [product] is the [category] that [benefit]; unlike [alternative], we [differentiator]." Plus a one-liner and a 30-second pitch.
2. **Messaging** — primary message, three value props with proof, objection table.
3. **ICP targeting** — where they gather, trigger events.
4. **Pricing messaging** — tiers as defined in saas-financial-model, annual framing, upgrade trigger.
5. **Launch phases** — goal, activities, channels, exit criterion per phase.
6. **Channel plan** — channel, priority, estimated CAC, timeline, owner.
7. **Metrics** — Step 3 set with targets.
8. **Launch checklist** — technical, marketing, operations.
9. **90 days post-launch** — stabilize → learn → iterate → scale, with the decision point for scaling or pivoting.
10. **Kill list.**

If a web tool is available, check competitor positioning, pricing, and recent launches against
current, dated sources; otherwise mark competitor claims unverified.

## Step 5: Artifact Generation

Applies when the user wants documents written. Write only what the classification needs:
`docs/gtm-plan.md` (the plan), `docs/launch-checklist.md` (checkbox list), and
`docs/competitive-battlecard.md` (for new-product or new-market launches).
