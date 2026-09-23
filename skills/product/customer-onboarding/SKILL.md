---
name: customer-onboarding
description: "Designs onboarding and activation for mobile and web apps. Use when designing a first-run flow, empty states, welcome emails, or tooltips, or when day-1/day-7 retention or time-to-value is weak."
when_to_use: "NOT for funnels past activation, referrals, or lifecycle (use growth-engineering) or marketing email campaigns (use product-marketing)."
argument-hint: "[product-name]"
---

# Customer Onboarding

**Outcome:** an onboarding design tied to one named activation event — flow per platform, empty
states, a behavior-triggered email sequence, and the funnel events that measure it. Done when every
step maps to a funnel event and the ship checklist (Step 7) passes. Match length to the need; no
filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Portfolio products: `grep -m6 -E '^#{2,3} ' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Platforms present: `ls package.json build.gradle.kts Podfile Package.swift 2>/dev/null | head -4 || echo "(none detected)"`

Use the platforms present to pick the screen implementation (Compose, SwiftUI, React) in Step 6.

## Step 1: Classify

| Request | Deliver |
|---|---|
| New flow design | Activation event, flow per platform, empty states, emails, events |
| Diagnose weak activation/retention | Funnel read + ranked friction fixes; no new flow unless asked |
| Single piece (empty state, email sequence, tooltip) | That piece only |
| Build it | The design plus code (Step 6) |

| Product type | Cure default pattern |
|---|---|
| Consumer mobile | Value-first demo, auth deferred until the first save |
| B2B SaaS web | Setup wizard (≤5 steps) + checklist + email sequence |
| Marketplace / two-sided | Split at signup by role (buyer/seller, coach/player); seller path goes straight to first listing |
| Freemium / trial | Reverse trial; paywall at the activation moment, never before it |
| Enterprise | White-glove kickoff + in-app checklist; don't build a self-serve wizard |

## Step 2: Gather Context

Ask only for what is missing: the product, personas (do they need separate paths?), the candidate
activation event, current signup→activation and D1/D7 numbers, known drop-off points, and whether
value can be shown before account creation.

## Step 3: Define the Activation Event

One action that predicts 30-day retention. Find it by correlating each first-week action with D30
retention and picking the strongest predictor that happens early. Portfolio defaults (confirm against
PORTFOLIO.md):

| Product | Activation event |
|---|---|
| Vendly | First product listing created |
| SpedUp | First reading mission completed |

If there is no data yet, pick the action closest to the core value, instrument it, and revisit after
four weeks of cohorts.

## Step 4: Flow Design Rules (Cure positions)

- Value before signup; social auth (Apple/Google) first, email as fallback.
- One ask per screen, a skip/later on every non-essential screen — forced tours raise churn.
- Personalization: at most two questions, and only if the answer changes what the user sees next.
- Core action reachable within three taps/clicks of signup; celebrate its completion and suggest the next step.
- Empty states on every list/feed screen: what will appear, why it matters, one CTA to create the first item. Never "No data" or a disabled UI.
- iOS and Android flows follow platform conventions (ios-design-expert, android-design-expert); visual design belongs to design-studio.

## Step 5: Email Sequence

Behavior-triggered, stops on activation, one CTA each, plain text, reply-to a real person.

| Send | Content | Condition |
|---|---|---|
| Immediate | Welcome + the single next step | Always |
| Day 1 | Two-minute quick win | Not activated |
| Day 3 | Customer result + one feature | Not activated |
| Day 5 | Personal help offer from a founder | Not activated |
| Day 7 | Trial/setup reminder | Inactive |

## Step 6: Code/Artifact Generation

Applies only when Step 1 is "Build it". Write, in the platform(s) detected:

1. Onboarding steps as screens/components in the project's feature layout, with a skip path.
2. Onboarding progress state (persisted, resumable).
3. Funnel events `onboarding_started`, `onboarding_step_completed` (with `step`), `onboarding_completed`, and the activation event — named per the analytics-implementation taxonomy.
4. A reusable empty-state component.
5. `docs/onboarding-emails.md` with the Step 5 sequence.

Deliver the requested artifacts; don't refactor adjacent code.

## Step 7: Measure and Ship Checklist

Targets (Cure starting benchmarks — replace with the product's own baseline once it has one):
signup completion >70%, onboarding completion >50%, D1 >40%, D7 >25%, plus median time-to-activation.
Segment by channel, platform, persona, and weekly cohort.

- [ ] Value visible before account creation; signup asks only for what auth needs
- [ ] Skip/later on every non-essential screen; core action ≤3 taps from signup
- [ ] Empty, loading, and error states designed for every screen in the flow
- [ ] Every step fires a funnel event; activation event tracked
- [ ] Email sequence stops on activation
- [ ] Screen reader and contrast pass; tested on a throttled connection
