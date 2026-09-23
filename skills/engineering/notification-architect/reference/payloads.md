# notification-architect: payloads and schemas

Read this file when generating push payloads, the device-token schema, or the preference model for the notification-architect skill.

## Contents
- FCM HTTP v1 payloads (Android, iOS via APNs, web)
- Device token schema
- Preference model
- Notification catalog template

## FCM HTTP v1 payloads

### Android
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
        "channel_id": "order_updates"
      }
    }
  }
}
```

Deep links travel in `data`; build the `PendingIntent` in your `FirebaseMessagingService` (data messages) or read `intent.extras` in the launcher activity (notification messages opened from the tray). `click_action` works only with a matching intent-filter and only for notification messages — avoid it for new code.

### iOS (APNs via FCM)
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

- `mutable-content: 1` enables a Notification Service Extension (rich media, decryption).
- `thread-id` groups; `category` enables actions; `interruption-level` (`passive`, `active`, `time-sensitive`) controls Focus breakthrough — `time-sensitive` needs the entitlement.

### Web (service worker)
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

## Device token schema
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

- Hash tokens for document IDs; delete tokens inactive 60+ days, on sign-out, and on `UNREGISTERED`/`INVALID_ARGUMENT` send errors.

## Preference model
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

## Notification catalog template
```
| Notification | Trigger | Channels | Category | Opt-Out? | Rate Limit |
|-------------|---------|----------|----------|----------|------------|
| Order shipped | order.status.shipped | push, email | orderUpdates | Yes | 1/order |
| Password reset | auth.passwordReset | email | security | No | 3/hour |
| New message | chat.message.created | push, in-app | messages | Yes | 5/day |
```
