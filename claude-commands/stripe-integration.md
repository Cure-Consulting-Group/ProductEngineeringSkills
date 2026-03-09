# Stripe Integration

Full Stripe integration: Android SDK → Firebase Functions → Stripe API → Firestore sync. Secret keys never touch the Android client. All payment operations are server-side.

## Integration Architecture

```
Android App
  └── StripeDataSource (Android SDK + PaymentSheet)
        ↓ Firebase Callable Function
  Cloud Functions
    ├── createPaymentIntent / createSubscription
    ├── createSetupIntent (save card)
    ├── stripeWebhook (HTTP — Stripe → Firebase)
    └── createPortalSession (manage subscription)
          ↓ Stripe API (secret key, server-side only)
  Stripe
    └── Events → stripeWebhook → Firestore sync
```

## Step 1: Classify the Integration Type

| Need | Primary Function |
|------|-----------------|
| Subscriptions (recurring) | `createSubscription` |
| One-time payment | `createPaymentIntent` |
| Save payment method | `createSetupIntent` |
| Manage subscription | `createPortalSession` |
| Webhook handling | `stripeWebhook` |
| Android UI (PaymentSheet) | PaymentSheet SDK |
| Full paywall screen | All of above |

## Step 2: Gather Context

1. **Payment type** — subscription / one-time / both?
2. **Plan tiers** — names, prices, billing intervals
3. **Trial period** — yes/no, how many days?
4. **Free tier** — yes/no?
5. **Payment UI** — use Stripe PaymentSheet (recommended) or custom UI?
6. **Existing Stripe account** — test mode / live mode setup?

## Step 3: Security Rules (Always Apply)

**Client (Android) can:**
- Call Firebase Callable Functions (authenticated)
- Use Stripe Android SDK for UI (PaymentSheet, CardElement)
- Read own subscription status from Firestore

**Client CANNOT:**
- Hold or use Stripe secret key
- Create/modify subscriptions directly via Stripe API
- Write to subscription documents in Firestore (Cloud Functions only)
- Access other users' payment data

## Stripe Config & Keys

```
Publishable Key → Android app (safe to expose)
Secret Key      → Firebase Secret Manager only (never in client)
Webhook Secret  → Firebase Secret Manager only
Price IDs       → Firebase Remote Config (safe to expose)
```

## Price ID Management

Store price IDs in Firebase Remote Config so they can be updated without app release:

```kotlin
// Android — fetch from Remote Config
val priceIds = mapOf(
    "starter_monthly" to remoteConfig.getString("stripe_price_starter_monthly"),
    "pro_monthly" to remoteConfig.getString("stripe_price_pro_monthly"),
    "pro_annual" to remoteConfig.getString("stripe_price_pro_annual")
)
```

## Webhook Events to Handle

Always implement idempotent handlers for:

```typescript
// Critical — must handle
'checkout.session.completed'        // Initial subscription
'customer.subscription.updated'     // Plan changes, renewals
'customer.subscription.deleted'     // Cancellation
'invoice.payment_succeeded'         // Successful payment
'invoice.payment_failed'            // Failed payment

// Recommended
'customer.subscription.trial_will_end'  // 3 days before trial ends
'payment_method.attached'               // New payment method saved
```

## Firestore Subscription Document Shape

```typescript
interface UserSubscription {
  stripeCustomerId: string;
  subscriptionId: string;
  status: 'active' | 'trialing' | 'past_due' | 'canceled' | 'unpaid';
  planId: string;
  priceId: string;
  currentPeriodStart: Timestamp;
  currentPeriodEnd: Timestamp;
  cancelAtPeriodEnd: boolean;
  trialEnd: Timestamp | null;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}
```

## Test Cards

```
Success:          4242 4242 4242 4242
Decline:          4000 0000 0000 0002
Requires auth:    4000 0025 0000 3155
Insufficient:     4000 0000 0000 9995
```

## Tech Stack

```yaml
android: Stripe Android SDK (PaymentSheet)
backend: Firebase Cloud Functions v2 (TypeScript)
stripe_sdk: stripe@14.x (Node.js)
firestore: subscription status sync
remote_config: price IDs
secret_manager: Stripe secret key + webhook secret
```
