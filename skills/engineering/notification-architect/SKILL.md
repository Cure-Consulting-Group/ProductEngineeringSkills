---
name: notification-architect
description: "Designs notification systems: push (FCM/APNs/web), in-app, transactional email, SMS, and preferences. Use when adding push notifications, notification preferences, email deliverability, or multi-channel dispatch."
when_to_use: "NOT for lifecycle or growth campaigns and experiments (use growth-engineering) or onboarding sequence content (use customer-onboarding)."
argument-hint: "[notification-type-or-project]"
metadata:
  verified: 2026-09-23
---

# Notification Architect

Push, in-app, email, and SMS that respect user preferences, reach the device, stay legal, and are measurable. Notifications are a trust contract — abuse it and users churn.

**Done when:** every notification type in scope has a trigger, channel(s), category, opt-out rule, and rate limit (the catalog); preferences are enforced server-side; and platform setup covers permission, tokens, and deep links. For an audit, done is severity-ranked findings.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Existing notification code: !`grep -rlE "FirebaseMessaging|firebase-messaging|UNUserNotificationCenter|POST_NOTIFICATIONS|sendgrid|postmark|twilio|resend" --include=*.kt --include=*.swift --include=*.ts --include=*.js --include=*.xml --include=*.json . 2>/dev/null | grep -v node_modules | head -10 || echo "(none found)"`

## Invariants

- Send only what the user opted into; every non-transactional channel has a working opt-out (law, and the fastest route to spam folders).
- No PII in push payloads — the lock screen is public.
- Push deep-links to the relevant content, never the home screen.
- Transactional and marketing mail use separate sending subdomains/streams so a marketing complaint spike can't block password resets.
- Localize all content (the `i18n` skill owns string management).

## Step 1: Classify the Notification Need

| Request | Primary Output | Action |
|---------|---------------|--------|
| Push notification setup | FCM/APNs integration + token management | Configure push |
| Notification preferences | Preference model + UI + server enforcement | Design preferences |
| Transactional email | Template system + sending infrastructure | Build email pipeline |
| In-app messaging | Message display system + targeting rules | Implement in-app |
| Multi-channel orchestration | Channel router + fallback chains + dedup | Design orchestration |
| Notification audit | Delivery metrics + preference compliance review | Audit system |

## Step 2: Gather Context

Before generating, confirm:
1. **Platforms** — Android, iOS, web, or all three?
2. **Current stack** — existing notification infrastructure? (FCM, SendGrid, Twilio, etc.)
3. **Notification types** — what events trigger notifications? (orders, messages, promotions, system alerts)
4. **User segments** — different notification strategies per user cohort?
5. **Compliance requirements** — GDPR, CAN-SPAM, TCPA, CASL?
6. **Volume** — expected notifications per day? (hundreds, thousands, millions)
7. **Personalization needs** — user-specific content, send-time optimization?
8. **Deep linking** — existing deep link infrastructure?

## Step 3: Architecture

```
Event source (app, Cloud Function, queue)
  → Notification service: preference check → rate limit → dedup → template (locale) → channel router
      → push (FCM/APNs) | email (Postmark/SendGrid/Resend) | SMS (Twilio/SNS) | in-app (Firestore)
  → delivery tracker (created/filtered/sent/delivered/opened/actioned/bounced/complained)
```

Channel fit: push for time-sensitive actions (≤5/day default), in-app for contextual discovery, email for receipts/digests, SMS for 2FA and critical alerts only (cost and consent burden). Read [reference/payloads.md](reference/payloads.md) when writing payloads, the token schema, the preference model, or the catalog.

## Step 4: Push — Platform Gotchas

- **Android 13+ (API 33):** `POST_NOTIFICATIONS` is a runtime permission and notifications are off by default for new installs. Declare it, and request at a user-driven moment (tapping a bell, placing an order), not on first launch. Create one notification channel per category (Android 8+).
- **Force-stopped apps** (user force-stop, some OEM battery killers) receive nothing, data messages included, until the user reopens the app. Don't design critical flows on push alone.
- **Data vs notification messages:** data messages give the app control of display; notification messages are displayed by the system when backgrounded. Put the deep link in `data` either way.
- **iOS:** use a `.p8` APNs auth key through FCM (does not expire, unlike certificates). Background pushes (`content-available: 1`) are throttled and not guaranteed — a hint to sync, never a delivery channel.
- **Tokens:** store per device under `users/{uid}/devices/{tokenHash}`, refresh on `onNewToken`, delete on sign-out and on `UNREGISTERED` send errors, prune after 60 days inactive.
- **Topics:** an app instance can subscribe to at most 2,000 topics; subscription changes are capped at 3,000 QPS per project and 1,000 instances per batch request. Use topics for broadcast categories, token targeting for per-user messages.
- **Web push:** requires a user gesture for the permission prompt; iOS Safari supports web push only for home-screen-installed web apps.

## Step 5: Preferences

- Model: global switch, per-channel, per-category × channel, and quiet hours in the user's timezone. Security/account notices (2FA, password reset, login alerts) ignore preferences.
- Enforce on the server before send; client filtering is not enforcement. Changes apply immediately. Log each suppression reason.
- Ask for push permission with context; if declined, offer email and re-ask only after demonstrated value.
- **Legal:** CAN-SPAM (unsubscribe in every marketing email, honor within 10 business days), GDPR (explicit opt-in, record timestamp + method), TCPA (prior express written consent for marketing SMS), CASL (implied consent lapses after 2 years). Route formal compliance design to the `compliance-architect` skill.

## Step 6: Delivery Rules

Defaults (configurable per category): push 5/user/day and 2/hour; email 2/day excluding transactional; SMS 1/day excluding 2FA; in-app 3/session. Limits are per user, not per device; transactional is exempt. Dedup on `eventType + entityId + window` (5 min) and group bursts ("3 new comments"). Default quiet hours 22:00–08:00 local.

Fallback chains: order updates push → in-app → email; chat push → in-app; security alerts on all channels at once.

## Step 7: Email Deliverability

- **Gmail/Yahoo sender rules (since Feb 2024):** all senders need SPF or DKIM, valid PTR, and TLS. Bulk senders (>5,000/day to Gmail) need SPF **and** DKIM, DMARC with From-domain alignment, and RFC 8058 one-click unsubscribe (`List-Unsubscribe` + `List-Unsubscribe-Post`) on marketing mail. Keep Postmaster spam rate under 0.1%; at 0.3% delivery degrades.
- Send from subdomains (`notify.` transactional, `news.` marketing). Use the provider's shared pool at low volume; a dedicated IP needs sustained volume and warm-up (provider thresholds vary — confirm before use), or it hurts deliverability.
- Templates: React Email or MJML, server-rendered, with preheader and plain-text part.
- Verification links: single-use hashed token, 24 h expiry, Universal/App Links with web fallback, resend throttled to 3/hour.

## Step 8: Metrics

| Metric | Target | Alert |
|--------|--------|-------|
| Push delivery (sent → delivered) | >95% | <90% |
| Push open | >8% | <3% |
| Email delivery | >98% | <95% |
| Email click | >3% | <1% |
| Unsubscribe per send | <0.5% | >1% |
| Bounce | <2% | >5% |
| Spam complaints | <0.1% | ≥0.3% — pause marketing sends |

Email open rate is inflated by Apple Mail Privacy Protection (auto-fetched pixels); use clicks and conversions for decisions, and treat opens as a trend at best.

## Step 9: Output

Deliver what the classification needs: architecture diagram, notification catalog, preference model with enforcement rules, platform setup (permission, tokens, payloads), and email authentication plan. Match length to the need; no filler sections.

## Code/Artifact Generation

Applies when Step 1 calls for building. Grep existing notification code first and extend it. Generate only for platforms in scope:

1. `FirebaseMessagingService` subclass (Android) with token sync, channels, and permission request helper
2. `UNUserNotificationCenterDelegate` setup (iOS)
3. `public/firebase-messaging-sw.js` (web)
4. `functions/src/notifications/send.ts` — dispatcher with preference check, rate limit, dedup
5. Email templates (React Email or MJML) for the transactional flows in scope
6. Preference document schema + security rules

## Cross-References

`analytics-implementation` (event tracking), `firebase-architect` (schema, rules), `i18n`, `customer-onboarding` (sequence content), `growth-engineering` (lifecycle experiments), `security-review` (payload PII), `compliance-architect` (GDPR/CAN-SPAM/TCPA), `offline-first` (silent-push sync triggers).
