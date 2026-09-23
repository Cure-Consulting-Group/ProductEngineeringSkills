# Investor Reporting

**Outcome:** an investor-ready draft — monthly update, board deck outline, portfolio financial
report, data-room index, or cap-table model — with every number sourced and dated and bad news
stated plainly. **Done when** the draft has the period's metrics against last period and target,
runway with its status from burn-rate-tracker, at least one specific ask, and nothing sent: a
human reviews and sends every investor communication. Match length to the need; no filler
sections or restated summaries.

This skill **owns** investor updates, board decks, the data-room checklist, cap-table modeling,
and SAFE conversion math. fundraising-materials links here. Runway thresholds come from
burn-rate-tracker.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`

Products, stages, and business models come from PORTFOLIO.md (maintained by
`portfolio-registry`). Report on the products listed there; don't carry a product list in this
skill. If the file is absent, ask which products are in scope.

## Step 1: Classify

| Need | Output | Audience |
|------|--------|----------|
| Monthly investor update | One-page email: metrics, wins, lowlights, asks | Angels, seed investors |
| Quarterly board deck | 12–15 slides: portfolio health and decisions | Board, lead investors |
| Portfolio financial report | Consolidated P&L, allocation, unit economics | CFO, board |
| Data room | Diligence folder index with status | Prospective investors |
| Cap table / SAFE model | Ownership, dilution, conversion, exit waterfall | Founders, counsel |
| Ad-hoc investor request | Specific data pull or narrative | One investor |

## Step 2: Gather Context

Scope (one product or portfolio) and exact period; audience; per product: stage, the one metric
that matters, revenue, burn; wins and misses (including any target promised last period); cash,
last funding event, raise timeline; the asks. Mark each number actual vs. estimate.

## Step 3: Monthly investor update

Same day every month, including — especially — bad months. Plain-text email, under one page.

```
SUBJECT: [Company] Monthly Update — [Month Year]

TL;DR (3 bullets): biggest win (with a number) · biggest miss · cash and runway status

HIGHLIGHTS (3–5, each specific and measurable)
  Good: "[Product] processed \$47K GMV in March, up 32% MoM"
  Bad:  "[Product] is growing nicely"
  Good: "Signed LOI with [health system] for a 12-provider pilot"

LOWLIGHTS (2–3): what happened, why, what we're doing. Call out any target missed from last
month's update by name.

KEY METRICS: per product, this month vs last month vs target — revenue, growth, customers,
the product's key metric, burn. Studio total: cash, net burn, runway (months) and status.

PRODUCT UPDATES: 2–3 sentences per active product — shipped, next.

ASKS (1–3, specific): "Intros to LATAM fintech operators who scaled merchant onboarding in
Mexico" — not "let us know if you can help."
```

Rules: metrics defined the same way every month; never round up; runway always included, with
the status and plan from `burn-rate-tracker` when it is DANGER or worse; don't promise what next
month's update can't show.

## Step 4: Quarterly board deck

Read the board-deck section of `reference/details.md` when building a board deck — it has the
slide order, portfolio health scorecard, and decision-slide format. Board decks frame 1–3
decisions with options and a recommendation; they are not status reports.

## Step 5: Portfolio financial report

Read the portfolio-financial-report section of `reference/details.md` when producing a
consolidated P&L — it has the allocation rules, per-product P&L layout, and infra cost flags
(AI API cost > 20% of a product's revenue; infra growing faster than revenue).

## Step 6: Cap table and SAFE conversion

Read the cap-table section of `reference/details.md` for any dilution, SAFE, note, option-pool,
or exit-waterfall question. Gotchas that most often produce wrong answers:

- The priced-round price is **pre-money valuation ÷ pre-money fully diluted shares**, never
  post-money.
- **Post-money SAFEs** (the YC standard since 2018) convert on capitalization that *includes*
  the SAFE shares; pre-money SAFEs exclude them. Confirm which form was signed before modeling.
- An option-pool increase negotiated "pre-money" dilutes existing holders, not the new investor.
- The model is for planning; counsel and the cap-table system of record are authoritative.

## Step 7: Runway in investor materials

Take runway, scenarios, and status from `burn-rate-tracker` — it owns the thresholds (start the
raise at 9 months on the conservative case; cut below 6 with no term sheet). In investor
materials, show runway at current net burn, the conservative-case runway, and the plan if the
status is DANGER or worse. Don't restate or re-derive the thresholds here.

## Step 8: Data room

Read the data-room section of `reference/details.md` when preparing diligence — it has the
numbered folder structure, industry-specific compliance folders (health, fintech, minors'
data), and readiness rules. Never put passwords, API keys, or production credentials in a data
room.

## Step 9: KPI definitions

Read the KPI section of `reference/details.md` when defining or auditing a product's dashboard —
it has KPI sets by business model (marketplace, B2B SaaS, clinical SaaS, two-sided community,
developer tool, media/events). Every KPI needs a formula, a target, and a trailing 3-month trend;
never add one without removing one.

## Artifact Generation

Applies to the draft types classified in Step 1. A question gets an answer inline.

1. `docs/investor-updates/{YYYY-MM}.md` — monthly update draft
2. `docs/board-deck-outline.md` — slide-by-slide outline
3. `docs/data-room-index.md` — folder index with status per document
4. `docs/cap-table-model.md` — scenarios with the conversion math shown
5. `monitoring/investor-kpi.json`, `analytics/investor-metrics.sql` — only when asked to wire a
   dashboard

## Cross-References

- `burn-rate-tracker` — runway, scenarios, raise/cut thresholds
- `fundraising-materials` — pitch deck, the ask, outreach pipeline
- `saas-financial-model` — unit economics per product
- `analytics-implementation` — event tracking behind the KPIs
- `security-review`, `legal-doc-scaffold` — data-room security and legal documents

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: `/engagement-automation`).

- **Cadence:** monthly
- **Session loop:** none — session loops expire after 7 days, so a monthly cadence never fires in-session; it belongs in the cloud routine below.
- **Unattended:** cloud routine — Monthly draft of the investor update from repo/metrics state. Draft only: never auto-send. Recipes: docs/AUTOMATION.md in the plugin repo.
- **Budget:** ~120k tokens/run; cap at one run per monthly period.
- **Guardrails:** writes only the draft update file (advisory — recurring-mode doctrine per AUTOMATION.md, not harness-enforced); a human always reviews before anything is sent; report on failure rather than retrying.
