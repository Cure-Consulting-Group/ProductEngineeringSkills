# Analytics Implementation

**Outcome:** a tracking plan engineering can implement without questions — event names, triggers, typed properties, priorities — plus consent handling that is correct for the product's jurisdictions. Done when every P0 event maps to a decision someone will make with it, and no event fires before the consent state allows it.

Measure what drives decisions, not everything.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Stack: !`ls package.json build.gradle.kts Podfile Package.swift pubspec.yaml 2>/dev/null | head -5 || echo "(none detected)"`
- Existing tracking calls: !`grep -rhoE "(logEvent|trackEvent|analytics\.track|posthog\.capture|mixpanel\.track|gtag)\(\s*['\"][A-Za-z0-9_]+" --include=*.ts --include=*.tsx --include=*.js --include=*.kt --include=*.swift --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null | sort | uniq -c | sort -rn | head -10 || echo "(none)"`

If events exist, audit them against Step 3 before proposing new ones; report the count of unique event names and naming violations.

## Step 1: Classify the Need

| Need | Output |
|------|--------|
| Event taxonomy | Naming + property standards |
| Tracking plan | Full event spec (Step 4) |
| Funnel instrumentation | Funnel steps mapped to events; activation event named |
| Consent / privacy | Consent flow + SDK wiring (Step 6) |
| Attribution | UTM strategy + first-touch capture |
| Instrumentation audit | Findings on existing events (all of them, with severity) |

Experiment design and dashboards route to the `ab-test-analyst` and `metrics-dashboard` agents.

## Step 2: Gather Context

Ask only what's unknown: product and platforms; analytics tool(s); the 3–5 decisions this data must inform; greenfield or existing; jurisdictions and audiences (EEA/UK, California and other US states, children under 13).

## Step 3: Taxonomy Standards

- **Names:** `object_action`, snake_case, past tense — `account_created`, `item_added_to_cart`, `payment_completed`. Not `createAccount`, `click_button`.
- **Prefer GA4 recommended events** where they fit (`sign_up`, `login`, `purchase`, `add_to_cart`) when GA4/Firebase is the tool — they unlock built-in reports. Keep Cure naming for custom events.
- **Global properties on every event:** `user_id` (when authenticated), `platform`, `app_version`; timestamps and session IDs come from the SDK.
- **Property rules:** snake_case keys; lowercase enum values; numbers as numbers; no PII in properties (email, name, phone, precise location, free-text input).
- **GA4/Firebase hard limits** (verified 2026-09-23, support.google.com/analytics/answer/9267744): event and parameter names ≤40 chars; parameter values ≤100 chars; ≤25 parameters per event; 500 distinct event names per app user on app streams (unlimited on web); user properties ≤25 per property, names ≤24 chars, values ≤36 chars. Names starting with `firebase_`, `google_`, or `ga_` are reserved. Violations are dropped silently — lint for them.

## Step 4: Tracking Plan

```markdown
| Event | Trigger (exact moment) | Properties (type) | Decision it informs | Priority |
|-------|------------------------|-------------------|---------------------|----------|
| account_created | Server confirms signup | method (email/google/apple) | Signup channel mix | P0 |
| payment_completed | Payment provider success callback | value (number), currency (ISO 4217), plan_id | Revenue funnel | P0 |
```

P0 ships with the feature; P1 next sprint; P2 only if a named decision needs it. Fire conversion events from the server-confirmed moment, not the button tap. Name one **activation event** per product — the action that best predicts retention — and define funnels as ordered event sequences from it.

**UTMs:** require `utm_source`, `utm_medium`, `utm_campaign` on marketing links; capture on first visit (first-touch), persist, and attach to `account_created`.

## Step 5: Implementation Patterns

One wrapper per platform so call sites never import a vendor SDK directly; the wrapper checks consent and fans out to providers.

```kotlin
// Android — firebase-analytics (KTX modules were removed in BoM 34.0.0; APIs live in the main module)
Firebase.analytics.logEvent("payment_completed") {
    param("value", 29.99); param("currency", "USD"); param("plan_id", "pro_monthly")
}
```

```swift
// iOS
Analytics.logEvent("payment_completed", parameters: ["value": 29.99, "currency": "USD", "plan_id": "pro_monthly"])
```

```typescript
// Web — typed wrapper; EVENT_NAMES is the tracking-plan const
export function track<E extends EventName>(name: E, props: EventProps[E]) {
  if (!consent.analytics) return;
  window.gtag?.('event', name, props);   // add Mixpanel/PostHog fan-out here
}
```

## Step 6: Privacy & Consent

These are legal requirements, and getting them wrong exposes the client to regulators and ad-platform penalties.

**EEA/UK — Google Consent Mode v2** (verified 2026-09-23, developers.google.com/tag-platform/security/guides/consent; support.google.com/google-ads/answer/13695607)
- Send all four signals: `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`. The last two were added in v2 (Nov 2023) and are required for EEA traffic to keep Google Ads measurement and personalization.
- Default every signal to `denied` before any tag fires; update from the CMP (use a Google-certified CMP when running Google Ads).
- *Basic* mode blocks tags until consent; *advanced* mode loads tags with cookieless pings while denied (enables modeling). Cure default: basic, unless the client's counsel approves advanced.
- "Decline all" means no analytics storage — not degraded tracking.

**California — CPRA** (Cal. Civ. Code §1798.135)
- If the product sells *or shares* personal information (sharing includes cross-context behavioral advertising, e.g. ad pixels), provide a "Do Not Sell or Share My Personal Information" link — the old "Do Not Sell" wording is outdated.
- Honor Global Privacy Control (GPC) as an opt-out of sale/sharing. Other US state laws have similar opt-outs — confirm before use for each state in scope.

**Children:** under-13 audiences fall under COPPA — disable ad signals and advertising identifiers entirely; route to `compliance-architect`.

**SDK wiring (platform-correct):**

| Platform | Collection on/off | Consent signals | Default-denied config |
|----------|-------------------|-----------------|-----------------------|
| Android | `Firebase.analytics.setAnalyticsCollectionEnabled(bool)` | `Firebase.analytics.setConsent { analyticsStorage(...); adStorage(...); adUserData(...); adPersonalization(...) }` | Manifest `<meta-data>`: `google_analytics_default_allow_analytics_storage`, `_ad_storage`, `_ad_user_data`, `_ad_personalization_signals` = `false` |
| iOS | `Analytics.setAnalyticsCollectionEnabled(_:)` | `Analytics.setConsent([.analyticsStorage: .denied, ...])` | Info.plist `GOOGLE_ANALYTICS_DEFAULT_ALLOW_ANALYTICS_STORAGE`, `_AD_STORAGE`, `_AD_USER_DATA`, `_AD_PERSONALIZATION_SIGNALS` = `false` |
| Web | `setAnalyticsCollectionEnabled(analytics, bool)` (modular) | `setConsent({...})` from `firebase/analytics`, or `gtag('consent','update', {...})` | `setConsent` with all four `'denied'` before `getAnalytics()` — SDK consent defaults to `granted` |

Store the consent state once (CMP or first-party cookie) and have every platform wrapper read it before firing.

## Output

For a plan: the tracking-plan table, taxonomy rules applied, consent matrix per jurisdiction, and the activation event. For an audit: every finding (naming, PII, limit violations, missing consent gating, duplicate events) with severity and a fix. Match length to the need; no filler sections or restated summaries.

## Code/Artifact Generation

Applies when the user asks to implement instrumentation (not for a plan review or a question). Detect platforms and write only for those present:

1. Event name constants and typed property map (`src/analytics/events.ts` or platform equivalent)
2. Consent-aware tracker wrapper per platform
3. `docs/tracking-plan.md` from Step 4
4. A lint/test that fails on names or parameters over the GA4 limits

Extend an existing wrapper rather than adding a second one.
