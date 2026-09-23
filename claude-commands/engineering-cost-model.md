# Engineering Cost Model

> **Advisory skill — writes reports only.** It may write the estimate file the user asks for; it
> never edits code, infrastructure, or financial records. `allowed-tools` only pre-approves tools
> and other runtimes ignore it, so this paragraph is the guardrail in every runtime.

**Outcome:** an internal cost estimate — hours by component, year-1 infrastructure and services,
monthly maintenance, and total year-1 cost — with assumptions and the prices' sources dated.
**Done when** every feature maps to an hours line, every vendor price was checked on its current
pricing page, and the top two cost risks are named. Match length to the need; no filler sections
or restated summaries.

## Step 1: Classify

| Need | Output |
|------|--------|
| Project estimate | Hours × rate + infrastructure + maintenance |
| Architecture comparison | Side-by-side cost of 2+ approaches |
| Infrastructure forecast | Monthly/annual cloud and service cost at scale bands |
| Build vs buy | Custom build vs SaaS over 3 years |
| Maintenance budget | Ongoing cost of a shipped product |

Client-facing pricing, milestones, and payment schedules go to `proposal-generator`, which owns
Cure's commercial terms; this skill supplies its cost basis. When the estimate will be bid
against or held under contract, use `technical-estimation` (three-point PERT, σ roll-up,
reference-class correction) and feed its hours back here.

## Step 2: Gather Context

What is being built (feature, MVP, product, migration); platforms; team model and rates; timeline
driver (deadline or scope); users at launch, 6, and 12 months; third-party services.

## Step 3: Engineering hours

Pick the column per task honestly. The columns already carry task complexity; add a component
multiplier only for risk the column can't see: integration-heavy 1.3×, real-time/AI/payments
1.6×, never-built-before R&D 2.0× (state which and why). For a range rather than a point, take hours from the Simple and Complex columns
as the optimistic and pessimistic bounds (method in `technical-estimation`).


```
MOBILE (Android or iOS — one platform)
┌─────────────────────────────────┬──────────┬──────────┬──────────┐
│ Task                            │ Simple   │ Moderate │ Complex  │
├─────────────────────────────────┼──────────┼──────────┼──────────┤
│ Screen (UI only)                │ 4-8      │ 8-16     │ 16-32   │
│ Screen + ViewModel/State        │ 8-16     │ 16-32    │ 32-48   │
│ API integration (per endpoint)  │ 4-8      │ 8-16     │ 16-24   │
│ Local persistence (per entity)  │ 4-8      │ 8-16     │ 16-24   │
│ Auth flow (login/signup)        │ 16-24    │ 24-40    │ 40-60   │
│ Push notifications              │ 8-16     │ 16-24    │ 24-40   │
│ Payment integration (Stripe)    │ 24-40    │ 40-60    │ 60-80   │
│ Camera/media capture            │ 8-16     │ 16-32    │ 32-48   │
│ Maps/location                   │ 8-16     │ 16-24    │ 24-40   │
│ App Store submission            │ 4-8      │ 8-12     │ 12-16   │
└─────────────────────────────────┴──────────┴──────────┴──────────┘

WEB (Next.js / React)
┌─────────────────────────────────┬──────────┬──────────┬──────────┐
│ Task                            │ Simple   │ Moderate │ Complex  │
├─────────────────────────────────┼──────────┼──────────┼──────────┤
│ Page (static/marketing)         │ 4-8      │ 8-16     │ 16-24   │
│ Page (dynamic + data fetching)  │ 8-16     │ 16-32    │ 32-48   │
│ Form (with validation)          │ 4-8      │ 8-16     │ 16-32   │
│ Dashboard / data table          │ 16-24    │ 24-40    │ 40-60   │
│ Auth (Firebase/NextAuth)        │ 12-20    │ 20-32    │ 32-48   │
│ Payment/checkout                │ 16-24    │ 24-40    │ 40-60   │
│ CMS/blog integration            │ 8-16     │ 16-24    │ 24-40   │
│ SEO + metadata + structured data│ 4-8      │ 8-12     │ 12-16   │
│ i18n (per additional language)  │ 8-16     │ 16-24    │ 24-32   │
└─────────────────────────────────┴──────────┴──────────┴──────────┘

BACKEND (Firebase / Node.js)
┌─────────────────────────────────┬──────────┬──────────┬──────────┐
│ Task                            │ Simple   │ Moderate │ Complex  │
├─────────────────────────────────┼──────────┼──────────┼──────────┤
│ CRUD API (per resource)         │ 4-8      │ 8-16     │ 16-24   │
│ Auth + security rules           │ 8-16     │ 16-24    │ 24-40   │
│ Webhook handler                 │ 4-8      │ 8-16     │ 16-24   │
│ Background job / scheduled fn   │ 4-8      │ 8-16     │ 16-32   │
│ Email/notification system       │ 8-16     │ 16-24    │ 24-40   │
│ File upload + storage           │ 4-8      │ 8-16     │ 16-24   │
│ Search implementation           │ 8-16     │ 16-32    │ 32-48   │
│ AI/LLM integration (per feature)│ 16-24    │ 24-48    │ 48-80   │
│ Data migration                  │ 8-16     │ 16-32    │ 32-60   │
└─────────────────────────────────┴──────────┴──────────┴──────────┘

CROSS-CUTTING
┌─────────────────────────────────┬──────────┬──────────┬──────────┐
│ Task                            │ Simple   │ Moderate │ Complex  │
├─────────────────────────────────┼──────────┼──────────┼──────────┤
│ CI/CD pipeline setup            │ 4-8      │ 8-16     │ 16-24   │
│ Analytics instrumentation       │ 4-8      │ 8-16     │ 16-24   │
│ Testing (per feature)           │ 8-16     │ 16-24    │ 24-40   │
│ Design system setup             │ 16-24    │ 24-40    │ 40-60   │
│ Project setup + boilerplate     │ 4-8      │ 8-16     │ 16-24   │
│ Code review + QA                │ 15-20% of total development hours       │
│ Project management              │ 10-15% of total development hours       │
└─────────────────────────────────┴──────────────────────────────────┘
```

## Step 4: Infrastructure and services

Look up every unit price on the vendor's current pricing page and date it in the output; the
figures below are planning anchors, not quotes.

```
Firebase no-cost quotas (verified 2026-09-23, firebase.google.com/pricing):
  Firestore:  50K reads, 20K writes, 20K deletes per day; 1 GiB stored
  Functions:  2M invocations, 400K GB-seconds per month (Blaze plan required)
  Storage:    5 GB-months stored, 100 GB/month downloaded
  Hosting:    10 GB stored, 360 MB/day transfer
  Auth:       50K MAU; phone SMS billed per message

Cure planning bands for a Firebase app (validate against the calculator):
  0–1K users: \$0–25/mo | 1K–10K: \$25–150 | 10K–50K: \$150–500 | 50K–100K: \$500–2,000
  100K+: \$2,000+ (optimize reads, add caching — see finops)

Services to price explicitly:
  Stripe: 2.9% + 30¢ per successful US domestic card charge (verified 2026-09-23, stripe.com/pricing)
  Email: SendGrid retired its free plan in 2025 (60-day trial, then paid plans); Resend and
         Postmark have paid tiers — check current pricing
  LLM APIs: per-token prices by model tier — check each provider's pricing page; see finops Step 6
  Hosting (Vercel/Cloud Run), search, error monitoring, analytics, domains: check current tiers
```

## Step 5: Project cost templates (Cure reference points)

### MVP (one platform + backend)
```
Typical scope: 5-8 screens, auth, core feature, payments
Hours: 200-400 hours
At \$150/hr: \$30,000-60,000
At \$200/hr: \$40,000-80,000
Timeline: 6-10 weeks

Infrastructure (year 1): \$300-2,000
Third-party services (year 1): \$500-3,000
Total year 1: \$31,000-85,000
```

### Full Product (mobile + web + backend)
```
Typical scope: 15-25 screens per platform, admin dashboard, API
Hours: 800-1,500 hours
At \$150/hr: \$120,000-225,000
At \$200/hr: \$160,000-300,000
Timeline: 4-8 months

Infrastructure (year 1): \$1,200-12,000
Third-party services (year 1): \$2,000-10,000
Total year 1: \$125,000-322,000
```

### Maintenance (ongoing after launch)
```
Bug fixes + minor updates: 10-20 hours/month
OS/dependency updates:     5-10 hours/quarter
Feature additions:         scope per feature
Infrastructure monitoring: 2-5 hours/month

Monthly maintenance cost:
  At \$150/hr: \$2,250-4,500/month
  At \$200/hr: \$3,000-6,000/month
  Or retainer: flat monthly fee (typically 15-20% of build cost annually)
```

## Step 6: Build vs Buy Analysis

```
DECISION FRAMEWORK

Build custom when:
  ✅ Core differentiator (this IS your product)
  ✅ No off-the-shelf solution fits >80% of requirements
  ✅ Data ownership/privacy is critical
  ✅ Long-term cost of SaaS licenses exceeds build cost
  ✅ You need deep integration with existing systems

Buy/use SaaS when:
  ✅ Not a core differentiator (auth, email, analytics, payments)
  ✅ Off-the-shelf fits >80% of requirements
  ✅ Speed to market matters more than customization
  ✅ Team doesn't have expertise to build + maintain
  ✅ Build cost > 3 years of SaaS subscription

Common build vs buy decisions:
  Auth:       BUY (Firebase Auth, Auth0) — never build your own
  Payments:   BUY (Stripe) — never build your own
  Email:      BUY (SendGrid, Resend) — commodity
  Analytics:  BUY (Firebase, Mixpanel) — commodity
  Search:     BUILD if simple, BUY if complex (Algolia, Typesense)
  CMS:        BUY if content-only, BUILD if integrated with app logic
  AI features: BUILD (custom integration with LLM APIs)
  Core logic:  ALWAYS BUILD — this is your product
```

## Live pricing

Search the web for the current pricing page of every detected service (e.g. "Firebase pricing",
"Vercel pricing", "<provider> API pricing per token") and flag any assumption that differs from
the published price. Don't put a year in the query; read the page date instead.

## Scripts

`cure-cost-estimator` (on PATH while the plugin is enabled; otherwise
`python3 <plugin-root>/skills/business/engineering-cost-model/scripts/cost_estimator.py`) totals
hours × rate + PM/QA overhead + infra + optional contingency. Stdlib only; `--help` lists flags.

```bash
cure-cost-estimator --hours 400 --rate 175 --infra-monthly 250 --duration-months 6 \
  --pm-pct 10 --qa-pct 15 --contingency-pct 15 --json
```

## Step 7: Cost Estimate Output

```
ENGINEERING COST ESTIMATE
Project: [NAME]
Date: [TODAY]
Prepared for: [INTERNAL / CLIENT PLANNING]

SCOPE SUMMARY
  Platforms: [Android / iOS / Web / Backend]
  Features: [list key features]
  Timeline: [X weeks/months]

DEVELOPMENT COST
┌────────────────────────┬───────┬────────────┐
│ Component              │ Hours │ Cost       │
├────────────────────────┼───────┼────────────┤
│ [Feature 1]            │ XX    │ $X,XXX     │
│ [Feature 2]            │ XX    │ $X,XXX     │
│ [Feature N]            │ XX    │ $X,XXX     │
├────────────────────────┼───────┼────────────┤
│ Testing & QA (15%)     │ XX    │ $X,XXX     │
│ Project Management (10%)│ XX   │ $X,XXX     │
├────────────────────────┼───────┼────────────┤
│ TOTAL DEVELOPMENT      │ XXX   │ $XX,XXX    │
└────────────────────────┴───────┴────────────┘

INFRASTRUCTURE (YEAR 1)
┌────────────────────────┬────────────┐
│ Service                │ Annual Cost│
├────────────────────────┼────────────┤
│ Firebase / Cloud       │ $X,XXX     │
│ Third-party APIs       │ $X,XXX     │
│ Domain + DNS           │ $XX        │
├────────────────────────┼────────────┤
│ TOTAL INFRASTRUCTURE   │ $X,XXX     │
└────────────────────────┴────────────┘

ONGOING MAINTENANCE
  Monthly: $X,XXX (XX hours/month)
  Annual:  $XX,XXX

TOTAL YEAR 1: $XXX,XXX
  Development:    $XX,XXX
  Infrastructure: $X,XXX
  Maintenance:    $XX,XXX

ASSUMPTIONS & RISKS
  - [Assumption 1]
  - [Risk 1 — impact on cost if realized]
  Prices checked: [vendor page, date]
```

Payment schedule and client terms: hand the totals to `proposal-generator`.
