# Go-to-Market Plan Generator

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

Structured GTM planning. Covers positioning through post-launch growth. Opinionated — cuts low-leverage activities, focuses on what actually moves the needle at early stage.

## GTM Framework

```
1. POSITION  → Who is this for, what does it do, why us?
2. PACKAGE   → Pricing, tiers, trial strategy
3. PLACE     → Where do we find buyers?
4. PROMOTE   → How do we reach and convert them?
5. PROVE     → Metrics, signals, when to scale vs. pivot
```

## Step 1: Gather Context

Before generating, confirm:
1. **Product** — what is it, what problem does it solve?
2. **ICP** — who is the primary buyer? (from market research if available)
3. **Stage** — pre-launch / beta / public launch / expansion?
4. **Timeline** — when is launch? Hard deadline?
5. **Resources** — solo founder? Small team? Budget for paid acquisition?
6. **Existing traction** — waitlist size, beta users, revenue?

## Output Template

Generate a GTM document with these sections:

### 1. Positioning Statement
> For [ICP], [Product Name] is the [category] that [primary benefit],
> unlike [main alternative] which [key differentiation].

Include one-liner (for social/word-of-mouth) and elevator pitch (30 seconds).

### 2. Messaging Hierarchy
- Primary message (the ONE thing to remember)
- 3 supporting value props with proof points
- Objection handling table

### 3. ICP & Targeting
- Where they are (communities, platforms, events, content, search terms)
- Trigger events (when they're most receptive)

### 4. Pricing & Packaging
Tier structure table: Free / Starter / Pro / Elite with prices, billing, features, target.
Include annual discount, trial strategy, upgrade trigger.

### 5. Launch Phases
- **Phase 0: Pre-Launch** — Build warm audience, validate messaging
- **Phase 1: Soft Launch / Beta** — First paying customers, validate retention
- **Phase 2: Public Launch** — Drive awareness spike, establish category
- **Phase 3: Growth** — Repeatable acquisition engine, improve LTV/CAC

Each phase includes: goal, activities checklist, channels, tactics, success criteria.

### 6. Channel Plan
Table with: Channel, Priority, Estimated CAC, Timeline, Owner

### 7. Analytics & Success Metrics
- North Star Metric
- Acquisition funnel with targets (Month 1 and Month 3)
- Key ratios: activation rate, trial→paid conversion, month-1 retention, LTV/CAC

### 8. Launch Checklist
Technical, Marketing, and Operations checklists.

### 9. 90-Day Post-Launch Plan
Week-by-week focus areas: Stabilize → Learn → Iterate → Scale

## Artifact Generation (Required)

Generate actual GTM documents using Write:

1. **GTM Plan**: `docs/gtm-plan.md` with:
   - Positioning statement (template: For [target] who [need], [product] is a [category] that [benefit]. Unlike [competitor], we [differentiator].)
   - Messaging matrix (persona × pain point × message × proof point)
   - Channel plan with budget allocation
   - Launch timeline with milestones
2. **Launch checklist**: `docs/launch-checklist.md` — GitHub issue-style checkboxes
3. **Competitive battlecard**: `docs/competitive-battlecard.md` — feature comparison table

Use WebSearch to research competitor positioning, pricing, and recent launches in the space.
