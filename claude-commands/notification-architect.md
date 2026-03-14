
# Notification Architect

Designs production-grade notification systems across push, in-app, email, and SMS channels. Every output enforces user preference respect, delivery reliability, legal compliance, and measurable engagement. Notifications are a trust contract with the user — abuse it and they churn.

## Core Principle: Every Notification Must Earn Its Send

```
Push notification     →  Time-sensitive, actionable, personalized
In-app message        →  Contextual, non-interruptive, feature discovery
Transactional email   →  Expected, informative, legally required
SMS                   →  Critical only (2FA, account recovery, urgent alerts)
```

**Hard rules:**
- Never send a notification the user has not opted into — implicit or explicit
- Every notification channel has an unsubscribe/opt-out mechanism — no exceptions
- Push notifications must deep-link to relevant content — never to the app home screen
- Rate limit all channels — no user receives more than 5 push notifications per day by default
- All notification content is localized — see `/i18n` for string management
- Transactional emails (receipts, password resets) are separate from marketing — different sending infrastructure
- Never send PII in push notification payloads — the lock screen is public

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

## Step 3: Notification Architecture

### Channel Taxonomy

| Channel | Best For | Latency | User Tolerance | Cost |
|---------|----------|---------|----------------|------|
| Push | Time-sensitive actions, real-time updates | <1s | Low (3-5/day max) | Free (FCM) |
| In-app | Feature discovery, contextual tips, soft prompts | Immediate | Medium | Free |
| Email | Receipts, digests, onboarding sequences, reports | Minutes | Medium (1-2/day) | Low |
| SMS | 2FA, critical account alerts, delivery updates | <5s | Very low (rare) | High |

### Notification Service Architecture

```
Event Source (app, Cloud Function, cron)
    │
    ▼
Notification Service (centralized dispatch)
    ├── Preference Check    →  Does user want this, on this channel?
    ├── Rate Limiter        →  Has user hit daily/hourly cap?
    ├── Template Engine     →  Render content with user data + locale
    ├── Channel Router      →  Select best channel(s) for this notification
    │   ├── Push Adapter    →  FCM / APNs
    │   ├── Email Adapter   →  SendGrid / Postmark
    │   ├── SMS Adapter     →  Twilio / SNS
    │   └── In-App Adapter  →  Firestore / WebSocket
    └── Delivery Tracker    →  Log send/deliver/open/click events
```

### Payload Design per Platform

**Android (FCM):**
```json
{
  "message": {
    "token": "device_token",
    "data": {
      "type": "order_update",
      "orderId": "abc123",
      "deepLink": "myapp://orders/abc123"
    },
    "android": {
      "priority": "high",
      "notification": {
        "title": "Order Shipped",
        "body": "Your order #abc123 is on its way",
        "channel_id": "order_updates",
        "click_action": "OPEN_ORDER_DETAIL"
      }
    }
  }
}
```

- Use **data messages** for app-controlled display (preferred for most cases)
- Use **notification messages** only when background display with no custom logic is acceptable
- Always include `channel_id` — Android 8+ requires notification channels

**iOS (APNs via FCM):**
```json
{
  "message": {
    "token": "device_token",
    "apns": {
      "headers": {
        "apns-priority": "10",
        "apns-push-type": "alert"
      },
      "payload": {
        "aps": {
          "alert": {
            "title": "Order Shipped",
            "body": "Your order #abc123 is on its way"
          },
          "sound": "default",
          "badge": 1,
          "category": "ORDER_UPDATE",
          "thread-id": "orders",
          "mutable-content": 1
        },
        "deepLink": "myapp://orders/abc123"
      }
    }
  }
}
```

- Use `mutable-content: 1` for Notification Service Extensions (rich media, decryption)
- Group notifications with `thread-id`
- Use `category` for actionable notifications (reply, approve, dismiss)

**Web (Service Worker):**
```javascript
self.registration.showNotification('Order Shipped', {
  body: 'Your order #abc123 is on its way',
  icon: '/icons/notification-icon.png',
  badge: '/icons/badge-icon.png',
  data: { deepLink: '/orders/abc123' },
  actions: [
    { action: 'view', title: 'View Order' },
    { action: 'dismiss', title: 'Dismiss' }
  ],
  tag: 'order-abc123',  // Deduplication
  renotify: true
});
```

## Step 4: Push Notification Implementation

### FCM Setup (Android + Web)

1. Add Firebase to the project (see `/firebase-architect`)
2. Register for FCM token on app start — store token in `users/{uid}/devices/{tokenHash}`
3. Handle token refresh — update Firestore document on every `onNewToken` callback
4. Implement `FirebaseMessagingService` (Android) / service worker (web) for message handling
5. Create notification channels on Android (one per notification category)

### APNs Integration (iOS)

1. Enable Push Notifications capability in Xcode
2. Register for remote notifications in `AppDelegate` or via SwiftUI `.onAppear`
3. Use FCM as the intermediary — FCM handles APNs certificate/key management
4. Prefer key-based auth (`.p8` file) over certificate-based — keys don't expire annually
5. Handle notification tap in `UNUserNotificationCenterDelegate.didReceive`

### Token Management

```
users/{uid}/
  devices/
    {tokenHash}/
      token: string
      platform: "android" | "ios" | "web"
      createdAt: Timestamp
      lastActiveAt: Timestamp
      appVersion: string
```

- Hash tokens before using as document IDs (tokens can be very long)
- Clean up stale tokens — delete devices not active in 60+ days
- Handle multi-device: a user may have multiple tokens (phone + tablet + web)
- On sign-out, remove the device token document

### Topic-Based Targeting

- Use FCM topics for broadcast notifications (e.g., `announcements`, `deals-us`, `sport-scores`)
- Subscribe/unsubscribe on the client side — topics map to preference categories
- Max 2000 topics per app; avoid per-user topics (use token targeting instead)
- Topic messages have lower priority than token-targeted messages

### Rich Notifications

- **Android:** custom `NotificationCompat.Builder` with `BigPictureStyle`, `BigTextStyle`, action buttons
- **iOS:** `UNNotificationServiceExtension` for image download, `UNNotificationContentExtension` for custom UI
- **Web:** `image` field in notification options (limited browser support)
- Always provide a fallback — rich content may fail to load

### Silent / Background Notifications

- Use for data sync triggers — no user-visible notification
- **Android:** data-only FCM message, handled in `FirebaseMessagingService` even when app is killed
- **iOS:** `content-available: 1` in APNs payload; limited to ~2-3 per hour by iOS; not guaranteed
- **Web:** not reliably supported — use periodic background sync instead

## Step 5: Preference Management

### User Preference Model

```typescript
interface NotificationPreferences {
  global: boolean;                    // Master kill switch
  channels: {
    push: boolean;
    email: boolean;
    sms: boolean;
    inApp: boolean;
  };
  categories: {
    orderUpdates: { push: boolean; email: boolean };
    promotions: { push: boolean; email: boolean };
    messages: { push: boolean; email: boolean; inApp: boolean };
    security: { push: boolean; email: boolean; sms: boolean };  // Always enabled
    systemAlerts: { push: boolean; inApp: boolean };             // Always enabled
  };
  quietHours: {
    enabled: boolean;
    start: string;  // "22:00" in user's local time
    end: string;    // "08:00"
    timezone: string;
  };
}
```

### Preference UI Patterns

- **Onboarding:** ask for push permission with context ("Get order updates?") — never on first launch with no context
- **Settings screen:** grouped by category, with per-channel toggles
- **Inline controls:** "Mute this conversation" or "Unfollow this thread" in context
- **Re-engagement:** if user declines push, offer email as alternative; ask again after value demonstration (e.g., after first order)

### Server-Side Enforcement

- The notification service checks preferences BEFORE sending — client-side filtering is not sufficient
- Security and account notifications (2FA, password reset, login alerts) ignore user preferences — they always send
- Log every preference check result for audit trail
- Preference changes take effect immediately — no "next batch" delay

### Legal Requirements

- **CAN-SPAM:** unsubscribe link in every marketing email, honored within 10 business days (aim for instant)
- **GDPR:** explicit opt-in for marketing notifications, record consent timestamp and method
- **TCPA:** express written consent for SMS marketing, clear disclosure of message frequency
- **CASL:** implied consent expires after 2 years, express consent required for continued sending

## Step 6: Delivery Optimization

### Send-Time Optimization

- Store user's timezone (from device or IP geolocation)
- Default quiet hours: 10 PM - 8 AM in user's local timezone
- For non-urgent notifications, defer to user's optimal engagement window
- Track per-user open times to build individual send-time models (requires analytics data)

### Rate Limiting

```
Default limits (configurable per notification category):
  Push:   5 per user per day, max 2 per hour
  Email:  2 per user per day (excluding transactional)
  SMS:    1 per user per day (excluding 2FA)
  In-app: 3 per session
```

- Rate limits are per-user, not per-device
- Transactional notifications (receipts, 2FA) are exempt from rate limits
- When rate limit is hit, queue the notification for next available slot or drop (configurable per category)

### Deduplication

- Assign a unique `notificationId` derived from event type + entity ID + timestamp window
- If same `notificationId` sent within 5-minute window, suppress duplicate
- Example: 3 comments on your post in 2 minutes → 1 grouped notification, not 3

### Fallback Chains

```
Primary channel fails → try next channel in priority order:

Order updates:    push → in-app → email
Chat messages:    push → in-app
Promotions:       email → in-app
Security alerts:  push → sms → email (all channels, do not stop on success)
```

- Track delivery confirmation per channel before falling back
- Push "delivered" ≠ "seen" — use in-app as complement, not replacement
- For critical notifications (security), send on ALL channels simultaneously

## Step 7: Transactional Email

### Email Categories

| Type | Examples | Opt-Out? | Priority |
|------|----------|----------|----------|
| Transactional | Receipts, password resets, 2FA | No | Immediate |
| System | Account changes, TOS updates, security alerts | No | Immediate |
| Triggered | Welcome series, onboarding, re-engagement | Yes | Batched |
| Marketing | Promotions, newsletters, product updates | Yes | Scheduled |

### Sending Infrastructure

- **Transactional:** SendGrid or Postmark dedicated IP — separate from marketing sends
- **Marketing:** SendGrid or Mailchimp — separate IP pool, separate domain
- Authenticate with SPF, DKIM, and DMARC — all three, no exceptions
- Use a subdomain for sending (e.g., `mail.yourapp.com`) to protect root domain reputation

### Email Template System

- Use MJML or React Email for responsive templates
- Variables injected server-side — never trust client-provided template data
- Preview text (preheader) is mandatory — don't let email clients auto-generate from body
- Plain text alternative for every HTML email
- Test rendering across: Gmail, Apple Mail, Outlook, Yahoo (use Litmus or Email on Acid)

### Email Verification Flows

1. User signs up → send verification email with time-limited token (24h expiry)
2. Token is single-use, stored hashed in database
3. Verification link deep-links to app (Universal Links / App Links) with web fallback
4. Unverified users see limited functionality with persistent banner prompting verification
5. Resend throttle: max 3 verification emails per hour per address

## Step 8: Analytics and Monitoring

### Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Push delivery rate | >95% | <90% |
| Push open rate | >8% | <3% |
| Email delivery rate | >98% | <95% |
| Email open rate | >25% | <15% |
| Email click rate | >3% | <1% |
| Unsubscribe rate | <0.5% per send | >1% |
| SMS delivery rate | >97% | <93% |
| Bounce rate (email) | <2% | >5% |
| Spam complaint rate | <0.1% | >0.3% |

### Event Tracking

Log these events for every notification:
```
notification.created     — notification generated by the system
notification.filtered    — suppressed by preference/rate-limit/dedup
notification.sent        — handed to delivery provider (FCM/SendGrid/Twilio)
notification.delivered   — confirmed delivery to device/inbox
notification.opened      — user tapped/clicked the notification
notification.actioned    — user took the CTA action (deep link followed)
notification.dismissed   — user swiped away / marked as read
notification.bounced     — delivery failed (invalid token, email bounce)
notification.complained  — user reported as spam
```

### Monitoring and Alerting

- Dashboard: real-time delivery rates per channel, per notification type
- Alert on delivery rate drops (token expiry waves, provider outages)
- Alert on spam complaint rate increase (stop sending immediately if >0.5%)
- Weekly report: engagement trends, unsubscribe trends, deliverability health
- Monthly cleanup: remove bounced email addresses, expired push tokens, unsubscribed users

## Step 9: Output Templates

For every notification system design, deliver:

1. **Channel architecture diagram** — flow from event source to user device
2. **Preference model** — data schema with defaults and enforcement rules
3. **Notification catalog** — table of all notification types with channel, template, and trigger
4. **FCM/APNs configuration** — platform setup steps and payload examples
5. **Email template scaffolds** — MJML/React Email templates for transactional flows

### Notification Catalog Template
```
| Notification | Trigger | Channels | Category | Opt-Out? | Rate Limit |
|-------------|---------|----------|----------|----------|------------|
| Order shipped | order.status.shipped | push, email | orderUpdates | Yes | 1/order |
| Password reset | auth.passwordReset | email | security | No | 3/hour |
| New message | chat.message.created | push, in-app | messages | Yes | 5/day |
```

## Tech Stack Defaults

```yaml
push:
  android: Firebase Cloud Messaging (FCM) via firebase-messaging
  ios: APNs via FCM (key-based auth, .p8 file)
  web: FCM via firebase-messaging + service worker
email:
  transactional: Postmark or SendGrid (dedicated IP)
  marketing: SendGrid or Mailchimp (separate IP pool)
  templates: React Email or MJML
  authentication: SPF + DKIM + DMARC on sending subdomain
sms:
  provider: Twilio or AWS SNS
  use_case: 2FA and critical alerts only
in_app:
  storage: Firestore collection per user
  display: custom UI component (banner, modal, inbox)
analytics:
  events: Firebase Analytics + custom notification events
  dashboards: Mixpanel or PostHog notification funnels
```

## Cross-References

- `/analytics-implementation` — notification event tracking and funnel analysis
- `/firebase-architect` — Firestore schema for notification preferences and token storage
- `/i18n` — localize all notification content per user locale
- `/customer-onboarding` — onboarding notification sequences and activation emails
- `/security-review` — audit notification payloads for PII exposure
- `/compliance-architect` — GDPR/CAN-SPAM/TCPA compliance for notification channels
