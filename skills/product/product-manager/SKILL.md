---
name: product-manager
description: "Product strategy and prioritization. Use when asked to prioritize features, score a backlog with RICE, write OKRs, build a Now/Next/Later roadmap, or write a feature brief."
when_to_use: "NOT for PRDs or stories (sdlc), sprint execution (project-manager), market sizing (market-research), or capacity audits (roadmap-strategist)."
argument-hint: "[product-or-feature-name]"
---

# Product Manager

**Outcome:** a decision-ready PM artifact — the decision or recommendation, success and guardrail
metrics, explicit non-goals, assumptions, and open questions with owners. Done when a stakeholder
could approve or reject it without a meeting. Match length to the need; no filler sections or restated
summaries.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Portfolio products: !`grep -m6 -E '^#{2,3} ' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Existing roadmap/briefs: !`ls docs/roadmap.md docs/briefs/ 2>/dev/null | head -5 | grep . || echo "(none)"`

Read the matching PORTFOLIO.md section for stage, priority, and metrics when the product is in it.

## Step 1: Classify

| Request | Output |
|---|---|
| Strategy / vision | Strategy doc: where we play, how we win, what we won't do |
| OKRs | 1–3 objectives × 3–5 KRs, each "metric from baseline to target by date" |
| Prioritization | RICE-scored backlog table, sorted, with the cut line and why items fell below it |
| Roadmap | Now / Next / Later with RICE scores and the outcome each item serves |
| Feature brief | One page: problem, user, outcome metric, guardrail, scope, non-goals |
| Metrics | North star + 3–5 input metrics + the decision each informs |
| Pricing / positioning | Recommendation; pair with market-research for evidence |

## Step 2: Gather Context

Minimum per type — ask only for what's missing:
- Strategy/OKRs: product, stage, traction, top 1–3 business goals.
- Prioritization: candidate list, horizon, binding constraint (people, date, money).
- Roadmap: milestones, capacity, hard deadlines.
- Brief: problem, target user, what success looks like.

## Step 3: Cure PM Rules

- Outcomes over outputs: "raise activation from 22% to 30%", not "add onboarding screen".
- Every feature ships with one primary (leading) metric and one guardrail; vanity counts (page views, total users) are never primary. Metrics must be readable within the release window.
- Say no in writing: every deferred item gets a one-line reason.
- Smallest bet first: name the cheapest test that could kill the idea before full build.
- Unknown numbers are stated as explicit assumptions, not guessed silently.

## Step 4: RICE (the one Cure definition)

**Score = Reach × Impact × Confidence ÷ Effort**

| Factor | Unit |
|---|---|
| Reach | Users (or accounts) affected per quarter |
| Impact | 3 massive · 2 high · 1 medium · 0.5 low · 0.25 minimal |
| Confidence | 100% · 80% · 50% (below 50% → run discovery, don't score) |
| Effort | **Person-weeks** (always — scores are only comparable in one unit) |

Show inputs next to each score so the ranking can be challenged.

## Step 5: Artifact Generation

Applies when the user wants a document written (not for a quick prioritization answer in chat).
Write only the artifact the classification calls for:

- Feature brief → `docs/briefs/{feature}.md`
- Roadmap → `docs/roadmap.md` (Now/Next/Later, RICE-scored)
- OKRs / strategy → `docs/okrs/{quarter}.md` or `docs/strategy.md`

A full PRD, epics, and stories are sdlc's output — hand the brief to sdlc rather than writing a PRD
here. If a web tool is available, check market or competitor assumptions against current, dated
sources; otherwise mark them unverified. Related: market-research (evidence), analytics-implementation
(instrumenting the success metrics).
