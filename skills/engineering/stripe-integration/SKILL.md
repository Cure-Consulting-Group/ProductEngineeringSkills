---
name: stripe-integration
description: "Stripe payments and subscriptions through Firebase Cloud Functions. Use when adding checkout, subscriptions, billing portal, saved cards, or Stripe webhooks with Firestore sync to a mobile or web app."
when_to_use: "NOT for pricing or plan design (use saas-financial-model) or Stripe Connect marketplaces (no Cure skill covers Connect)."
argument-hint: "[payment-feature]"
metadata:
  verified: 2026-09-23
---

# Stripe Integration

Client (Android / iOS / web) → Firebase Callable Functions v2 → Stripe API → webhook → Firestore. Secret keys never reach a client; every money-moving call is server-side.

**Done when:** the requested flow works end-to-end in a Stripe sandbox (test card or test clock), the webhook handler is idempotent and signature-verified, and the client reads entitlement from Firestore only. Deliver the requested flow; don't add unrequested billing features.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Stripe SDK in use: !`grep -h '"stripe"\|com.stripe\|stripe-ios\|@stripe/' functions/package.json package.json app/build.gradle.kts Package.resolved 2>/dev/null | head -8 || echo "(no Stripe dependency found)"`
- Existing Stripe code: !`grep -rlE "stripe|Stripe" functions/src src app 2>/dev/null | grep -v node_modules | head -10 || echo "(none)"`

## Step 1: Classify the Integration

| Need | Server function | Client |
|------|-----------------|--------|
| Subscription | `createCheckoutSession` or `createSubscription` | Checkout (web) / PaymentSheet (mobile) |
| One-time payment | `createPaymentIntent` | PaymentSheet / Payment Element |
| Save a card | `createSetupIntent` | PaymentSheet in setup mode |
| Self-serve management | `createPortalSession` | open returned URL |
| Webhook sync only | `stripeWebhook` (HTTP) | — |
| Full paywall | all of the above | — |

A question or review gets an answer or findings; generate code only when Step 1 calls for building.

## Step 2: Gather Context

Payment type (subscription / one-time / both), plan tiers and intervals, trial length, free tier, platforms in scope, and whether the Stripe account already has products/prices and a pinned API version.

## Step 3: Security Rules (Always Apply)

These protect money and entitlement, so they are not negotiable:

- Clients may call authenticated Callable Functions, use Stripe client SDKs with the **publishable** key, and read their own subscription doc.
- Clients may not hold the secret key, call the Stripe API directly, write subscription docs (Functions-only in `firestore.rules`), or read other users' payment data.
- Secret key and webhook signing secret live in Secret Manager (`defineSecret`), never in env files or Remote Config. Price IDs may live in Remote Config so they change without a release.

## Step 4: Cure Decisions and Gotchas

- **Pin the API version** in the server SDK (`new Stripe(key, { apiVersion })`) and on the webhook endpoint. Current: stripe-node 22.x, which pins `2026-08-26.dahlia`; monthly releases under a major name are backward-compatible, majors are not.
- **Billing periods live on subscription items** since `2025-03-31.basil`: read `subscription.items.data[0].current_period_start/end`, not `subscription.current_period_*` (removed). Older tutorials are wrong here.
- **Webhook signature needs the raw body.** In Cloud Functions use `req.rawBody` with `stripe.webhooks.constructEvent(req.rawBody, sig, secret)`; a parsed JSON body always fails verification. This is the most common production bug.
- **Idempotency:** store processed `event.id`s (e.g., `stripe_events/{eventId}`) and skip repeats; Stripe retries and may deliver out of order, so re-fetch the subscription from Stripe on each subscription event instead of trusting event order.
- **Events to handle:** `checkout.session.completed` (provision), `customer.subscription.created|updated|deleted` (sync status/plan/period), `invoice.paid` (extend access — prefer it over `invoice.payment_succeeded`, which misses out-of-band payments), `invoice.payment_failed` (notify, grace period), `customer.subscription.trial_will_end` (3 days before), `charge.refunded` if refunds change entitlement. Ignore unknown event types gracefully.
- **Mobile UI:** PaymentSheet on Android and iOS; don't build custom card fields (`CardInputWidget` is legacy and widens PCI scope). Web: Checkout or Payment Element.
- **Accounts v2 "customer-configured Accounts"** are in public preview for non-Connect users; stay on v1 `Customer` unless the client opts in (confirm before use).

### Firestore subscription document (`users/{uid}/subscription/current`)

```typescript
interface UserSubscription {
  stripeCustomerId: string;
  subscriptionId: string;
  status: 'active' | 'trialing' | 'past_due' | 'canceled' | 'unpaid' | 'incomplete' | 'incomplete_expired' | 'paused';
  priceId: string;
  currentPeriodStart: Timestamp; // from items.data[0].current_period_start
  currentPeriodEnd: Timestamp;   // from items.data[0].current_period_end
  cancelAtPeriodEnd: boolean;
  trialEnd: Timestamp | null;
  updatedAt: Timestamp;
}
```

### Testing

Test cards: `4242 4242 4242 4242` success, `4000 0000 0000 0002` decline, `4000 0025 0000 3155` requires 3DS, `4000 0000 0000 9995` insufficient funds. Use `stripe listen --forward-to` for local webhooks and test clocks for renewals and trials (up to 3 customers per clock, 3 subscriptions per customer; clocks auto-delete after 30 days). Coverage targets come from the `testing-strategy` skill.

## Code/Artifact Generation

Applies when Step 1 calls for building. Grep existing Stripe code first and extend it. Generate only the pieces the classified flow needs, for the platforms in scope:

1. `functions/src/stripe/webhook.ts` — signature-verified, idempotent handler for the events above
2. `functions/src/stripe/checkout.ts` / `payment-intent.ts` / `portal.ts` — callable functions
3. `functions/src/stripe/sync.ts` — Stripe → Firestore mapping (item-level periods)
4. `firestore.rules` additions — subscription docs read-own, write-none
5. Client repository per platform in scope (`SubscriptionRepository.kt`, `SubscriptionRepository.swift`, or a web hook) that reads Firestore entitlement
