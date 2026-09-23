# Growth Engineering

**Outcome:** a growth system tied to one metric — the loop or mechanism, its trigger rules, the
events that measure it, and an experiment backlog with hypotheses. Done when the target metric,
baseline, and the first experiment's primary and guardrail metrics are written down. Match length to
the need; no filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Portfolio products: `grep -m6 -E '^#{2,3} ' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Analytics SDKs: `grep -m4 -ohE '"(firebase|@amplitude/[a-z-]+|mixpanel[a-z-]*|posthog-js|@segment/[a-z-]+)"' package.json 2>/dev/null | grep . || echo "(none in package.json)"`

## Step 1: Classify

| Need | Deliver |
|---|---|
| Retention | Engagement loop + at-risk re-engagement rules |
| Referral | Invite trigger, flow, reward, anti-fraud |
| Monetization / PLG | Limits, upgrade triggers, paywall, trial model |
| Lifecycle automation | Segments, behavioral triggers, message rules |
| Cohort analysis | Retention curves by cohort + the targeting/activation read |
| Experiment program | Backlog, cadence, log format (statistics → ab-test-analyst) |

Activation problems (signup → first value) go to customer-onboarding first — fix activation before
scaling acquisition or referrals.

## Step 2: Gather Context

Ask only for what is missing: product type (B2C, B2B, marketplace), current DAU/MAU, D1/D7/D30,
conversion, stage (pre-PMF / post-PMF / mature), analytics and flag tools, incentive budget, and
platform constraints (App Store and Play policies on referral rewards and external purchase links).

## Step 3: Cure Defaults

- **Trial:** no credit card required, reverse trial — full features for 14 days, then downgrade to free. Traditional card-upfront trials only when the client's sales motion needs high-intent leads.
- **Free tier:** genuinely useful; limits hit through engaged usage (projects, seats, storage), never arbitrary time bombs or punitive watermarks. Tier structure itself is owned by saas-financial-model.
- **Upgrade prompts:** at the moment of intent (user attempting the gated thing), never mid-flow; show a preview of the gated feature; offer monthly and annual.
- **Referral:** only after D30 retention flattens. Two-sided rewards in product value (credit, premium time) before cash. Reward only after the referee activates; cap per user per month; hold payout 7 days; flag duplicate devices.
- **Re-engagement ladder:** 2 days idle → push with specific content; 5 → email on what they're missing; 14 → personal founder note; 30 → win-back offer. Max two re-engagement pushes a week, none 9pm–9am local. Segment users as active / cooling / at-risk / dormant / churned; no generic blasts.
- **Streaks:** show them prominently, one-day grace, weekly cadence unless the product is truly daily, milestones at 7 / 30 / 100.

Working targets (Cure starting points, not industry benchmarks — replace with the product's own
baseline): activation within the first session for >60% of signups; D30 >20% consumer, >40% B2B;
LTV:CAC >3 with payback <12 months; referral K >0.3 counts as a meaningful assist (don't plan on K >1).

## Step 4: Build the Mechanism

- **Loops:** name the trigger → action → reward → stored investment, and the event that proves each step fired.
- **Lifecycle:** a daily scheduled job (Cloud Function or cron) reads `last_active_at`, assigns the segment, and hands delivery to notification-architect's channels.
- **Referral flow:** prompt after a success moment (never during onboarding or errors) → prefilled deep link via the native share sheet (`ShareLink` on iOS, `Intent.ACTION_SEND` chooser on Android, Web Share API with copy-link fallback) → personalized landing with one-tap signup carrying the referral code.
- **Cohorts:** by signup week by default; also by channel, platform, plan, and feature exposure. A curve that flattens after ~week 4 has found core users; one that never flattens is a PMF problem, not a growth problem. If paid cohorts retain far better than free, treat it as a targeting problem.

## Step 5: Experiments

Every experiment has a hypothesis, one primary metric, guardrails (activation, revenue per user,
support tickets, error rate), and a duration fixed before launch (minimum two weeks). Sample size and
the readout go to the ab-test-analyst agent; flag plumbing goes to feature-flags. Target 2–3
experiments a week once traffic allows; keep a log of name, hypothesis, result, and learning.

## Step 6: Code/Artifact Generation

Applies only when the user asks to build. Write what the classification needs, such as a cohort
retention query (BigQuery `events_*` with `UNNEST(event_params)`, or SQL for Postgres), a referral
schema with the anti-fraud fields, or the lifecycle segmentation job. Don't write a sample-size
calculator — that is the ab-test-analyst agent's job. Related: analytics-implementation (event
taxonomy), stripe-integration (subscription mechanics).
