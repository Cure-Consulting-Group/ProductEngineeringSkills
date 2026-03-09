# Analytics Implementation

Instrument event tracking, funnels, and dashboards across mobile and web. Measure what matters, not everything.

## Step 1: Classify the Analytics Need

| Need | Output |
|------|--------|
| Event taxonomy | Structured event naming + properties |
| Tracking plan | Full event spec for engineering implementation |
| Funnel analysis | Conversion funnel definition + instrumentation |
| Dashboard design | KPI dashboard layout + data sources |
| A/B test setup | Experiment design + tracking instrumentation |
| Attribution | Channel attribution model + UTM strategy |

## Step 2: Gather Context

1. **Product** — what app/platform are we instrumenting?
2. **Analytics tool** — Firebase Analytics, Mixpanel, Amplitude, PostHog, custom?
3. **Key business metrics** — what decisions will this data inform?
4. **Current state** — starting from zero or improving existing?
5. **Privacy requirements** — GDPR consent, CCPA opt-out, COPPA?

## Step 3: Event Taxonomy Standards

### Naming Convention
```
Format: object_action
Case:   snake_case
Tense:  past tense for completed actions

Examples:
  account_created        (not: create_account, userSignedUp)
  item_added_to_cart     (not: addToCart, cart_add)
  payment_completed      (not: pay, purchase_made)
  search_performed       (not: search, user_searched)
  screen_viewed          (not: pageView, open_screen)
```

### Event Categories
```
Lifecycle:    app_opened, session_started, app_backgrounded
Auth:         account_created, login_completed, logout_completed
Navigation:   screen_viewed, tab_selected, deep_link_opened
Engagement:   feature_used, item_viewed, content_shared
Conversion:   trial_started, subscription_created, payment_completed
Error:        error_occurred, crash_detected, api_error
```

### Property Standards
```
Every event includes:
  timestamp        — ISO 8601 (auto-captured by most SDKs)
  user_id          — authenticated user ID (if logged in)
  session_id       — auto-generated per session
  platform         — android / ios / web
  app_version      — semantic version

Event-specific properties:
  screen_viewed:    { screen_name: "home", previous_screen: "login" }
  item_viewed:      { item_id: "123", item_type: "product", source: "search" }
  payment_completed:{ amount: 29.99, currency: "USD", method: "card" }
  error_occurred:   { error_code: "AUTH_EXPIRED", screen: "checkout" }

Rules:
  - Property names: snake_case, no abbreviations
  - String values: lowercase (no "Home" vs "home" inconsistency)
  - Numbers: raw numbers, not strings ("amount": 29.99, not "29.99")
  - No PII in event properties (no email, name, phone, IP)
```

## Step 4: Tracking Plan Template

```markdown
## Tracking Plan — [Product Name]

| Event | Trigger | Properties | Priority |
|-------|---------|-----------|----------|
| screen_viewed | Every screen load | screen_name, previous_screen | P0 |
| account_created | After successful signup | method (email/google/apple) | P0 |
| feature_used | Core action completed | feature_name, duration_ms | P0 |
| payment_completed | Successful charge | amount, currency, plan_id | P0 |
| error_occurred | Unhandled error | error_code, screen, stack_hash | P0 |
| search_performed | Search submitted | query_length, results_count | P1 |
| item_shared | Share button tapped | item_id, share_method | P2 |

Priority: P0 = must ship with feature, P1 = next sprint, P2 = nice to have
```

## Step 5: Funnel Definitions

### Standard SaaS Funnel
```
1. Visitor         → screen_viewed (landing page)
2. Signed Up       → account_created
3. Activated       → [core_action]_completed (define per product)
4. Engaged         → session_started (day 2-7 return)
5. Converted       → subscription_created / payment_completed
6. Retained        → session_started (day 30+)
7. Referred        → referral_sent
```

### E-Commerce Funnel
```
1. Browse          → item_viewed
2. Add to Cart     → item_added_to_cart
3. Begin Checkout  → checkout_started
4. Payment         → payment_completed
5. Repeat          → second payment_completed (within 90 days)
```

Define activation metric per product — the single action that predicts retention.

## Step 6: Implementation Patterns

### Firebase Analytics (Mobile)
```kotlin
// Android
analytics.logEvent("payment_completed") {
    param("amount", 29.99)
    param("currency", "USD")
    param("plan_id", "pro_monthly")
}
```

```swift
// iOS
Analytics.logEvent("payment_completed", parameters: [
    "amount": 29.99,
    "currency": "USD",
    "plan_id": "pro_monthly"
])
```

### Web (Next.js)
```typescript
// Wrapper function — swap provider without changing call sites
export function trackEvent(name: string, properties?: Record<string, unknown>) {
  // Firebase Analytics
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', name, properties);
  }
  // Add other providers here (Mixpanel, Amplitude, etc.)
}
```

### UTM Tracking
```
Required UTM params for all marketing links:
  utm_source     — where traffic comes from (google, linkedin, email)
  utm_medium     — marketing medium (cpc, social, email, referral)
  utm_campaign   — campaign name (spring_launch, black_friday)

Capture UTMs on first visit, persist in cookie/localStorage, attach to account_created event.
```

## Step 7: Privacy & Consent

```
GDPR (EU users):
  - Show consent banner before any tracking
  - No analytics fired until consent given
  - Respect "decline all" — zero tracking, not degraded tracking
  - Provide data deletion on request

CCPA (California):
  - "Do Not Sell My Personal Information" link
  - Honor Global Privacy Control (GPC) signal

Implementation:
  - Consent state stored in cookie/localStorage
  - Analytics wrapper checks consent before firing
  - Firebase: Analytics.setAnalyticsCollectionEnabled(userConsented)
```

## Step 8: Dashboard Design

```
Executive Dashboard (weekly review):
  - Active users (DAU, WAU, MAU)
  - Activation rate (% of signups completing core action)
  - Conversion rate (% of active → paid)
  - Revenue (MRR, new MRR, churned MRR)
  - Retention curve (day 1, 7, 30)

Engineering Dashboard (daily monitoring):
  - Error rate by screen
  - API latency (p50, p95, p99)
  - Crash-free user rate
  - App load time
  - Feature adoption (% of users using new feature)
```
