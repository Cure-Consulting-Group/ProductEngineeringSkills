---
name: engineering-cost-model
description: "Estimate project costs, infrastructure spend, build vs buy decisions, and SOW pricing"
argument-hint: "[project-name]"
allowed-tools: ["Read", "Grep", "Glob", "WebSearch"]
---

# Engineering Cost Model

Estimate the true cost of building, running, and maintaining software architectures. Use this before scoping projects, pricing engagements, or choosing between build vs buy.

## Step 1: Classify the Cost Analysis Type

| Need | Output |
|------|--------|
| Project estimate | Total build cost (hours × rate + infrastructure) |
| Architecture comparison | Side-by-side cost of 2+ approaches |
| Infrastructure forecast | Monthly/annual cloud + service costs at scale |
| Build vs buy | Custom development vs SaaS/off-the-shelf comparison |
| Maintenance budget | Ongoing cost to keep a shipped product running |
| Client proposal | SOW-ready cost breakdown for consulting engagement |

## Step 2: Gather Context

1. **What's being built** — feature, MVP, full product, migration?
2. **Platforms** — Android, iOS, Web, backend, or combination?
3. **Team** — in-house, contractors, agency (rate per hour)?
4. **Timeline** — deadline-driven or scope-driven?
5. **Scale expectations** — users at launch, 6 months, 12 months?
6. **Third-party services** — Stripe, Firebase, AI APIs, CDN?

## Step 3: Engineering Hour Estimates

### Estimation Framework
```
Break every feature into tasks. Estimate each task in hours.
Always use three-point estimation:

  Optimistic (O):  everything goes right, no unknowns
  Likely (L):      normal development with typical blockers
  Pessimistic (P): significant unknowns, dependencies, or complexity

  Estimate = (O + 4L + P) / 6

Then apply the complexity multiplier:
  Simple (CRUD, standard UI):          1.0x
  Moderate (custom logic, integrations): 1.3x
  Complex (real-time, AI, payments):    1.6x
  Novel (never done before, R&D):      2.0x
```

### Standard Task Estimates (hours)

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

## Step 4: Infrastructure Cost Estimation

### Firebase (pay-as-you-go after free tier)
```
Free tier covers:
  Firestore: 50K reads, 20K writes, 20K deletes per day
  Auth: 10K verifications/month (phone), unlimited email
  Storage: 5GB stored, 1GB/day download
  Functions: 2M invocations, 400K GB-seconds
  Hosting: 10GB stored, 360MB/day transfer

Typical monthly cost by scale:
  0-1K users:     $0-25/month (free tier covers most)
  1K-10K users:   $25-150/month
  10K-50K users:  $150-500/month
  50K-100K users: $500-2,000/month
  100K+ users:    $2,000+/month (optimize reads, use caching)
```

### Third-Party Services
```
Stripe:          2.9% + $0.30 per transaction (no monthly fee)
SendGrid/Resend: $0-20/month (up to 100 emails/day free)
OpenAI API:      $0.50-15 per 1M tokens (model dependent)
Gemini API:      $0-7 per 1M tokens (model dependent)
Vercel:          $0-20/month (hobby/pro), usage-based beyond
Algolia/Search:  $0-50/month (up to 10K records free)
Sentry:          $0-26/month (error monitoring)
Analytics:       $0 (Firebase Analytics), $0-25/month (Mixpanel/PostHog)
Domain + DNS:    $12-20/year
```

## Step 5: Project Cost Templates

### MVP (one platform + backend)
```
Typical scope: 5-8 screens, auth, core feature, payments
Hours: 200-400 hours
At $150/hr: $30,000-60,000
At $200/hr: $40,000-80,000
Timeline: 6-10 weeks

Infrastructure (year 1): $300-2,000
Third-party services (year 1): $500-3,000
Total year 1: $31,000-85,000
```

### Full Product (mobile + web + backend)
```
Typical scope: 15-25 screens per platform, admin dashboard, API
Hours: 800-1,500 hours
At $150/hr: $120,000-225,000
At $200/hr: $160,000-300,000
Timeline: 4-8 months

Infrastructure (year 1): $1,200-12,000
Third-party services (year 1): $2,000-10,000
Total year 1: $125,000-322,000
```

### Maintenance (ongoing after launch)
```
Bug fixes + minor updates: 10-20 hours/month
OS/dependency updates:     5-10 hours/quarter
Feature additions:         scope per feature
Infrastructure monitoring: 2-5 hours/month

Monthly maintenance cost:
  At $150/hr: $2,250-4,500/month
  At $200/hr: $3,000-6,000/month
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

## Step 7: Cost Estimate Output

```
ENGINEERING COST ESTIMATE
Project: [NAME]
Date: [TODAY]
Prepared for: [CLIENT]

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

PAYMENT STRUCTURE (RECOMMENDED)
  30% — Project kickoff
  30% — Midpoint milestone (working prototype)
  30% — Delivery and launch
  10% — 30 days post-launch (bug fix period)
```
