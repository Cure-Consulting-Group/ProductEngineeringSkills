---
name: bid-decision
description: "Make a disciplined go/no-go call on a solicitation — kill criteria, weighted scorecard, win probability, and pursuit economics"
when_to_use: "Use before committing resources to a proposal, or when a pursuit is drifting. NOT for parsing requirements (use rfp-evaluation). NOT for sourcing opportunities (use capture-management)."
argument-hint: "[solicitation-number]"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write", "Edit", "WebSearch"]
---

# Bid Decision

Decide whether to pursue a solicitation, using criteria set **before** you fall in love with the opportunity.

The core discipline: **proposal effort is real, unrecoverable cost, and buyers explicitly disclaim it.** A consulting firm that bids everything wins a low percentage of a lot of expensive attempts and starves its delivery work. The purpose of this skill is to make no-bid a respectable, frequent, early outcome.

## Pre-Processing (Auto-Context)

- Evaluation artifacts: !`ls 01-analysis/*.md 2>/dev/null || echo "(run rfp-evaluation first)"`
- Bid pipeline: !`sed -n '1,30p' ../../PIPELINE.md 2>/dev/null || echo "(no PIPELINE.md)"`
- Days remaining: !`date +%Y-%m-%d`
- Past pursuits: !`ls -d ../../archive/*/ 2>/dev/null | head -20 || echo "(no archive)"`

## Step 1: Kill criteria — before any scoring

These are procurement **facts**, not judgment calls. Any unresolvable "no" ends the pursuit regardless of how attractive the work looks. Answer them first because none can be fixed by writing.

| # | Question | Blocking? |
|---|---|---|
| K1 | Can we meet every **mandatory** qualification — references, certifications, licenses, registrations? | 🔴 |
| K2 | Can we obtain the required **insurance** at the stated limits and endorsements? | 🔴 |
| K3 | Can we **field the team** without abandoning existing client commitments? | 🔴 |
| K4 | Can we carry the **receivables float** through the payment cycle? | 🔴 |
| K5 | Are we **registered** on the portal and able to submit? | 🟡 usually days |
| K6 | Are we free of **debarment, arrears, or prior-performance bars** with this buyer? | 🔴 |
| K7 | Can we produce a **compliant** package in the time remaining, alongside current work? | 🔴 |
| K8 | Are the **contract terms** ones we would actually sign? | 🔴 |

### On mandatory qualifications

Read the operative verb. "Must provide three public-sector references" is a bar; "should demonstrate relevant experience" is a preference. When it is a bar and you cannot clear it, the honest options are:

1. **Team with a partner** who clears it — but subcontractors usually must be **named in the proposal** with qualifications and credit references, so this must be arranged in days, not weeks
2. **Bid anyway** and accept rejection risk — legitimate only when you have priced the effort as marketing spend and said so out loud
3. **No-bid** and spend the window closing the gap permanently

Option 3 is undervalued. Reference and insurance gaps block *every* future pursuit in that market; closing them once converts the next solicitation from a scramble into a writing exercise.

### On insurance

Public-sector limits routinely exceed commercial norms, and some endorsements are genuinely hard to obtain — naming a municipality as additional insured on a **cyber** policy is a common sticking point many carriers refuse. Get **written indications**, not a broker's verbal reassurance, before the go decision. "We can probably get that" is not a cleared kill criterion.

## Step 2: Assess win probability honestly

| Signal | Reading |
|---|---|
| Named incumbent with a renewal option | Win probability collapses; often a compliance exercise for the buyer |
| Requirements matching a specific product's feature list | Wired. Someone else wrote this scope |
| You participated in the RFI or pre-solicitation | Meaningfully positive — you shaped it |
| **RFI window closed before you saw it** | Negative. You are bidding blind on every ambiguity |
| Deadline extended, addenda pending | Positive — buyer is still shaping, field may be thin |
| Multiple awards permitted | Positive — not a single-slot fight |
| Rubric weights technical quality over size and price | Positive for a specialist |
| Rubric weights past performance and price | Negative for a small firm |
| Budget undisclosed against a very large scope | High risk — you may be bidding into a fraction of the need |

**Compute the rubric ratio.** If technical/governance/methodology criteria outweigh company size and past performance, a small firm competes on writing quality — a fair fight. If qualifications and price dominate, scale and incumbency win.

## Step 3: Score it

Weighted scorecard, 1–5 per factor. Score against evidence, not enthusiasm.

| Factor | Weight | Score | Weighted | Basis |
|---|---:|---:|---:|---|
| Win probability | 25 | | | Incumbency, positioning, rubric fit, field size |
| Scope fit to demonstrated capability | 20 | | | What we have actually shipped |
| Delivery capacity at the required timeline | 15 | | | Real availability, not aspirational |
| Contract & risk terms acceptability | 15 | | | Liability, IP, termination, payment |
| Economics — margin, payment terms, price-fixing exposure | 15 | | | Multi-year and escalation effects |
| Strategic value — reference, market entry, follow-on | 10 | | | Be honest; most work is not strategic |
| **Total** | **100** | | **/500** | |

| Weighted total | Action |
|---|---|
| ≥ 375 | Bid — commit full resources |
| 300–374 | Bid only with a credible plan to close a specific gap |
| 250–299 | Bid only for strategic reasons, at reduced effort |
| < 250 | No-bid |

**Set the thresholds before scoring.** Adjusting the band after seeing the total is how firms rationalize pursuits they have already emotionally committed to.

## Step 4: Pursuit economics

Bid cost is real. Compute it.

```markdown
| Line | Hours | Cost |
|---|---:|---:|
| Proposal writing | | |
| Compliance, forms, notarization | | |
| Estimation and pricing | | |
| Reference collection, insurance procurement | | |
| Oral presentation prep (assume it happens) | | |
| **Total bid cost** | | |
```

Then: **Expected value = (win probability × contract margin) − bid cost**

A 15% chance at \$400K of margin against a \$60K bid cost is EV-positive (\$0K... marginally). A 15% chance at \$200K margin against the same cost is clearly negative. Run the arithmetic rather than trusting instinct — instinct is reliably optimistic about win probability.

Also weigh **opportunity cost**: what does this team do instead for three weeks? For a small firm, a bid is usually funded by deferring delivery or business development, both of which have returns.

## Step 5: Make the call and record it

Four legitimate outcomes:

| Outcome | When |
|---|---|
| **Go** | Kill criteria cleared, score in band, EV positive |
| **Conditional go** | Score is defensible but 2–3 kill criteria are unverified. **Set a hard decision date** |
| **No-bid** | Any kill criterion fails unresolvably, or score is below band |
| **No-bid, invest instead** | Use the window to close the gaps that block every future pursuit in this market |

Conditional go is the honest answer when facts are genuinely pending — but it requires a **date**, an **owner per criterion**, and a **default of no-bid** if the date passes unanswered. Without those it is not a decision, it is a deferral, and the pursuit will drift into a rushed bid by inertia.

Record in `01-analysis/bid-no-bid.md`:

```markdown
**Decision:** <GO / CONDITIONAL GO / NO-BID>
**Decided by:** <name>
**Date:** <YYYY-MM-DD>
**Rationale:** <2–3 sentences>
**Conditions (if conditional):** <criterion → owner → date>
**Revisit if:** <what new information would change this>
```

## Step 6: Define the fallback

A no-bid is only wasted if you learn nothing. Convert the window into durable capability:

- Stand up the insurance program at market-standard public-sector limits
- Complete corporate disclosure questionnaires once and keep them current
- Register on the relevant portals with saved commodity codes and alerts
- Build reusable boilerplate — company profile, past performance, security architecture, accessibility approach, governance narratives
- Begin any certification with a long lead time (SOC 2 Type II runs 6–12 months)
- Pursue a smaller solicitation in the same market to create a first reference

These convert the *next* pursuit from a scramble into a writing exercise. For a firm entering a new market, this is frequently higher-value than the bid itself.

## Step 7: Track the decision against the outcome

Record every decision in the pipeline, including no-bids, and revisit quarterly.

| Metric | Why it matters |
|---|---|
| Win rate by pursuit type | Tells you which solicitations you should actually chase |
| Win rate vs. predicted probability | Calibrates your win-probability judgment |
| No-bid rate | Below ~50% in a new market usually means insufficient discipline |
| Bid cost per win | The real cost of business development |
| Bids lost on compliance vs. content | Compliance losses are unforced and fixable |

**Request a debrief on every loss.** Most public agencies must provide one. For a firm's first bids, the debrief is worth more than the contract.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Scoring before checking kill criteria | You will talk yourself past a hard bar |
| "We'll figure out the insurance later" | Some endorsements simply cannot be obtained |
| Adjusting thresholds after seeing the score | Rationalizing a decision already made emotionally |
| Conditional go with no date | Drifts into a rushed bid by default |
| Ignoring bid cost | It is real, unrecoverable, and explicitly disclaimed by the buyer |
| Treating strategic value as a trump card | Most work is not strategic; a loss is worth nothing |
| Never no-bidding | Signals no qualification discipline; dilutes every pursuit |
| Not tracking outcomes | You never learn which pursuits to chase |

## Handoff

- Requirements and compliance → `rfp-evaluation`
- Contract terms driving the risk score → `public-sector-contracting`
- Cost and effort driving the economics score → `technical-estimation`
- Pipeline and opportunity sourcing → `capture-management`
- If go → `proposal-generator`
