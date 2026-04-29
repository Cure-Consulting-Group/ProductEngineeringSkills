---
name: customer-onboarding
version: "1.0.0"
description: "Design user activation and first-run experiences — onboarding flows, empty states, welcome emails, tooltips, and time-to-value optimization for mobile (Android/iOS) and web apps"
when_to_use: "Use when designing first-time user experience, reducing churn in first 7 days, or asked to 'improve onboarding' or 'design the empty state'. NOT for growth funnels beyond onboarding (use growth-engineering). NOT for email marketing campaigns (use product-marketing)."
argument-hint: "[product-name]"
---

# Customer Onboarding

Design onboarding flows that drive activation and retention. The first 5 minutes determine whether a user stays or churns.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Onboarding Type

| Product Type | Onboarding Pattern |
|-------------|-------------------|
| Mobile app (consumer) | Progressive disclosure + value-first demo |
| SaaS web app (B2B) | Setup wizard + guided tour + email sequence |
| Marketplace / platform | Role-based paths (buyer vs seller, coach vs player) |
| E-commerce | Browse-first, account optional until checkout |
| Freemium with trial | Value-first → paywall at activation moment |
| Enterprise / complex | White-glove onboarding + dedicated support |

## Step 2: Gather Context

1. **Product** — what app/platform are we onboarding for?
2. **User segments** — different personas need different paths?
3. **Core action** — what must a user do to "get it"? (activation event)
4. **Current metrics** — signup-to-activation rate? Day 1/7 retention?
5. **Friction points** — where do users currently drop off?
6. **Auth required?** — can users see value before creating an account?

## Step 3: Onboarding Principles

```
1. VALUE BEFORE SIGNUP — show what the product does before asking for an account
2. PROGRESSIVE DISCLOSURE — don't dump every feature on day one
3. ONE GOAL PER SCREEN — never two asks on the same screen
4. SKIP IS ALWAYS AN OPTION — forced onboarding = churn
5. CELEBRATE COMPLETION — micro-wins build momentum
6. MEASURE EVERYTHING — every step in the flow is a funnel stage
```

## Step 4: Activation Metric Definition

```
The activation metric is the single action that predicts long-term retention.

How to find it:
  1. List all actions a user can take in first 7 days
  2. Correlate each action with 30-day retention
  3. The action with highest correlation = your activation metric

Examples:
  Slack:       Sent 2,000 messages (team level)
  Dropbox:     Uploaded first file
  Facebook:    Added 7 friends in 10 days
  Vendly:      Created first product listing
  SpedUp:      Completed first reading mission
```

## Step 5: Onboarding Flow Design

### Mobile App Pattern
```
Screen 1: Value Proposition (3 swipeable cards showing key benefits)
           → "Get Started" CTA
Screen 2: Quick Auth (Google/Apple sign-in, email as fallback)
           → Skip option if possible
Screen 3: Personalization (1-2 questions that customize the experience)
           → "What brings you here?" / role selection
Screen 4: Core Action Prompt (guide to activation event)
           → "Create your first [X]" with guided UI
Screen 5: Success State (celebration + next step suggestion)
           → Confetti, encouragement, "Here's what to try next"
```

### SaaS Web App Pattern
```
Step 1: Signup (name, email, password — nothing else)
Step 2: Welcome + goal selection ("What do you want to accomplish?")
Step 3: Setup wizard (3-5 steps to configure the core feature)
        → Progress bar, save and continue later
Step 4: Guided first action (interactive walkthrough of core feature)
        → Tooltips pointing to key UI elements
Step 5: Dashboard with checklist ("Complete your setup: 2/5 done")
        → Gamification via progress indicator
```

### Marketplace Pattern
```
Buyer path:   Browse → discover value → sign up when ready to transact
Seller path:  Sign up → create first listing (guided) → share/promote
              Split at signup: "I want to [buy/sell]"
```

## Step 6: Empty States

```
Every screen that could be empty needs a designed empty state:

Components of a good empty state:
  1. Illustration or icon (warm, not a generic error)
  2. Headline explaining what will appear here
  3. One-sentence description of value
  4. Single CTA to create the first item

Example:
  [illustration of inbox]
  "No messages yet"
  "When customers reach out, their messages will appear here."
  [Send Your First Message →]

Never show:
  - Blank white space
  - "No data" or "0 results"
  - A disabled or greyed-out interface
```

## Step 7: Email Onboarding Sequence

```
Email 1 (Immediate): Welcome + single CTA to complete core action
  Subject: "Welcome to [Product] — here's your first step"

Email 2 (Day 1): Quick win tutorial
  Subject: "Do this in 2 minutes to [specific benefit]"
  Send only if: user hasn't completed activation

Email 3 (Day 3): Social proof + feature highlight
  Subject: "[Customer name] just [achieved result] with [Product]"
  Send only if: user hasn't completed activation

Email 4 (Day 5): Direct help offer
  Subject: "Need help getting started? I'm here."
  From: founder/real person, not "noreply"

Email 5 (Day 7): Last chance / value reminder
  Subject: "Your [free trial/setup] expires in [X] days"
  Send only if: user inactive

Rules:
  - Stop the sequence when user activates
  - Every email has exactly ONE CTA
  - Plain text or minimal HTML (not a newsletter)
  - Reply-to goes to a real person
```

## Step 8: Measuring Onboarding Success

```
Funnel metrics (measure drop-off at each step):
  Signup started → Signup completed → Step 1 → Step 2 → ... → Activated

Key rates:
  Signup completion rate:     completed / started (target: >70%)
  Onboarding completion rate: finished flow / signed up (target: >50%)
  Time to activation:         median time from signup to core action
  Day 1 retention:            returned day after signup (target: >40%)
  Day 7 retention:            returned within 7 days (target: >25%)

Segmentation:
  - By acquisition channel (organic vs paid vs referral)
  - By platform (iOS vs Android vs Web)
  - By persona/role (if applicable)
  - By cohort (week-over-week improvement)
```

## Code Generation (Required)

Generate onboarding infrastructure using Write:

1. **Onboarding screens** (React): `src/onboarding/steps/` — Step1Welcome.tsx, Step2Setup.tsx, Step3Complete.tsx
2. **Onboarding state**: `src/onboarding/use-onboarding.ts` — hook managing onboarding progress
3. **Analytics events**: Add onboarding_started, onboarding_step_completed, onboarding_completed events
4. **Email sequence**: `docs/onboarding-emails.md` — Day 1, Day 3, Day 7 email templates
5. **Empty states**: `src/components/EmptyState.tsx` — reusable empty state with CTA

Reference `/analytics-implementation` for event taxonomy integration.

## Step 9: Onboarding Checklist Before Ship

- [ ] Value visible before account creation
- [ ] Signup requires minimum fields (name + email + password, or social auth)
- [ ] Every onboarding screen has a skip/later option
- [ ] Core action is reachable within 3 taps/clicks of signup
- [ ] Empty states designed for every screen
- [ ] Error states are helpful (not just "something went wrong")
- [ ] Analytics events fire at every onboarding step
- [ ] Activation metric defined and tracked
- [ ] Email sequence configured and tested
- [ ] Loading states present (no blank screens during setup)
- [ ] Accessibility: screen reader compatible, sufficient contrast
- [ ] Tested on slow connection (3G simulation)
