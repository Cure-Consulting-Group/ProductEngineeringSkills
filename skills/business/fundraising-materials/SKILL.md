---
name: fundraising-materials
description: "Builds pitch decks, the ask and use of funds, and the investor outreach pipeline. Use when preparing a seed or Series A raise: deck, intro blurb, target list, or process plan."
when_to_use: "NOT for investor updates, board decks, data rooms, or cap-table and SAFE math (use investor-reporting), or runway and raise timing (use burn-rate-tracker)."
argument-hint: "[product-or-round]"
allowed-tools: ["Read", "Grep", "Glob", "WebSearch"]
metadata:
  verified: 2026-09-23
---

# Fundraising Materials

> **Advisory skill — drafts only.** It may write the draft files listed under Artifact
> Generation; it never sends outreach, shares a deck, or edits financial records. Nothing enforces
> this (`allowed-tools` only pre-approves tools and other runtimes ignore it), so this paragraph is
> the guardrail in every runtime. A human sends everything.

**Outcome:** a slide-by-slide deck outline with the real numbers filled in (or visibly marked
missing), a specific ask with use of funds and milestones, and — when asked — a target-investor
pipeline and process plan. **Done when** every slide has one message backed by a sourced number or
a labeled placeholder, and nothing on a slide is an unsourced statistic. Match length to the need;
no filler sections or restated summaries.

**Ownership:** investor-reporting owns investor updates, board decks, the data-room checklist,
cap-table modeling, and SAFE conversion math — link to it rather than restating. burn-rate-tracker
owns runway thresholds (when to start the raise).

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Portfolio: `sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`

Take the product, stage, market, and metrics from PORTFOLIO.md and the user. Don't reuse another
product's problem statements or market sizes.

## Step 1: Classify

| Need | Output |
|------|--------|
| Seed deck | 12–15 slides; traction can be pilots, LOIs, early revenue |
| Series A deck | Metrics-heavy: MRR/ARR, growth, NRR, unit economics, repeatable GTM |
| The ask | Amount, instrument, cap or pre-money, use of funds, milestones |
| Outreach pipeline | Target list, CRM fields, intro blurb, meeting cadence |
| Investor update / data room / cap table | Hand off to `investor-reporting` |

## Step 2: Gather Context

Stage and round (first institutional or follow-on); current metrics with dates; target amount
and valuation expectation; investor audience (angels, micro-VC, institutional, strategic; sector
focus); close-by date; existing SAFEs/notes (hand the math to investor-reporting).

## Step 3: Deck (12–15 slides, one message each)

| # | Slide | Cure rule |
|---|---|---|
| 1 | Title | One-line "what we do," round and amount |
| 2 | Problem | Who hurts, how many, what they do today — a customer quote beats a statistic |
| 3 | Solution | Live product screenshot or demo GIF, never wireframes |
| 4 | Market | Bottom-up TAM/SAM/SOM with cited, dated sources (`market-research`); show the wedge |
| 5 | Traction | Stage-appropriate: pre-seed = LOIs/pilots/waitlist; seed = active users, early revenue, growth; A = MRR, NRR, unit economics. Growth rate beats absolute numbers at seed. No vanity metrics |
| 6 | Business model | Price, billing, gross margin; the trigger for the first dollar if pre-revenue |
| 7 | Product | 3–4 workflows; architecture only if it is the moat. AI products: model strategy, data moat, safety/human-in-the-loop |
| 8 | Competition | 2×2 on axes where you win; include incumbents and adjacent players; never "no competitors" |
| 9 | Go-to-market | Channels in use today, CAC and payback if known |
| 10 | Team | Founder–market fit; first hires this round funds; active advisors only |
| 11 | Financials | 18-month projection, not 5-year; assumptions explicit; unit economics from `saas-financial-model`, runway from `burn-rate-tracker` |
| 12 | The ask | See Step 4 |

Optional (1–2 max): roadmap (6–12 months), one case study, regulatory pathway (health, fintech).
Appendix slides hold diligence depth; don't present them.

**Every number on a slide needs a source and an as-of date, or it is marked `[PLACEHOLDER —
needs source]`.** Invented market statistics in a deck become misrepresentations the moment it is
sent.

Deck rules: ≤ 30 words per slide excluding charts; a 3-minute verbal run-through; bar or line
charts only; one font family; send as PDF with view tracking.

## Step 4: The ask

State amount, instrument (post-money SAFE, priced round, note), cap or pre-money, 3–4 use-of-funds
lines with percentages (keep ~10% buffer), and the milestones the money reaches — the metrics
that make the next round possible, with a month. Size the round to reach those milestones plus
runway to raise again (burn-rate-tracker's MONITOR band, 9–12 months, at the milestone).

Validate valuation expectations against current comparable rounds: search the web for recent
rounds in the same sector, stage, and region, and cite the date of each comparable. Dilution
and SAFE conversion: model in `investor-reporting`.

## Step 5: Pipeline and process

CRM fields: investor, firm, stage and check size, sector focus, status (cold / warm intro / first
meeting / partner meeting / diligence / term sheet / closed / passed), intro source, last contact,
next step with date, priority (A/B/C).

Process:
1. Warm, double-opt-in intros with a 3-sentence forwardable blurb (company, traction, why this
   investor).
2. Batch first meetings into a 2–3 week window to create momentum; send the deck and requested
   data within 24 hours.
3. Partner meeting, then diligence — open the data room (built with investor-reporting).
4. Term sheet: counsel reviews; don't sign the same day.

Funnel planning numbers for a seed round: 50–80 targets → 20–30 first meetings → 5–10 serious
conversations → 1–3 term sheets; 6–8 weeks from first meeting to close is a tight process.
Follow-ups carry news (a metric, a customer), never "just checking in"; after three unanswered,
move the investor to passive.

## Artifact Generation

Applies to the outputs classified in Step 1. A question gets an answer inline.

1. `docs/pitch-deck-outline.md` — slide-by-slide, talking points, sources and placeholders
2. `docs/fundraising-pipeline.md` — CRM table, blurb, process calendar (only if asked)

## Output

```
FUNDRAISING MATERIALS — [COMPANY] — [ROUND] — [DATE]
Ask: $[X] on [instrument] at [cap / pre-money]; milestones [metric by month]
Deck: [N] slides | placeholders still open: [list]
Comparable rounds checked: [company, round, date, source]
Next: [owner → action → date]
```

Related: `investor-reporting` (updates, data room, cap table), `burn-rate-tracker` (runway),
`saas-financial-model` (unit economics), `market-research` (market sizing),
`legal-doc-scaffold` (ToS, privacy policy for diligence).
