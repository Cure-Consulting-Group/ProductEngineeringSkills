# client-handoff: detailed reference

> Reference material for the `client-handoff` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 4: Runbook Generation

## Step 4: Runbook Generation

### 4.1 Deployment Runbook

```
DEPLOYMENT RUNBOOK — [PROJECT_NAME]

WEB DEPLOYMENT (Vercel / Firebase Hosting)
  Prerequisites:
    - GitHub access to repository
    - Vercel account access (or Firebase CLI authenticated)
    - Environment variables configured per environment

  Standard deploy (staging → production):
    1. Merge feature branch to main
    2. GitHub Actions runs: lint → test → build → deploy to staging
    3. Verify staging at https://staging.app.com
    4. Create release branch: git checkout -b release/vX.Y.Z
    5. Push and create PR to production branch
    6. Approve GitHub Actions deploy workflow
    7. Verify production at https://app.com
    8. Tag release: git tag vX.Y.Z && git push --tags

  Rollback:
    - Vercel: vercel rollback (reverts to previous deployment)
    - Firebase: firebase hosting:clone project-prod:previous project-prod:live

MOBILE DEPLOYMENT (iOS)
  Prerequisites:
    - Xcode with signing certificates
    - App Store Connect access
    - Fastlane configured

  Steps:
    1. Bump version in Xcode project
    2. Run: fastlane ios release
    3. Monitor TestFlight for beta feedback
    4. Promote to App Store from App Store Connect
    5. Monitor Crashlytics for 24 hours post-release

MOBILE DEPLOYMENT (Android)
  Prerequisites:
    - Android Studio with signing keystore
    - Google Play Console access
    - Fastlane configured

  Steps:
    1. Bump versionCode and versionName
    2. Run: fastlane android release
    3. Upload to internal testing track
    4. Promote to production (staged rollout: 10% → 50% → 100%)
    5. Monitor Crashlytics and Play Console vitals for 48 hours

CLOUD FUNCTIONS DEPLOYMENT
  Steps:
    1. Run tests: cd functions && npm test
    2. Deploy: firebase deploy --only functions --project production
    3. Verify: check Cloud Functions logs for errors
    4. Rollback: redeploy previous version from git tag
```

### 4.2 Incident Response Runbook

```
INCIDENT RESPONSE — [PROJECT_NAME]

First Responder Checklist:
  1. Check status dashboards: [DASHBOARD_URL]
  2. Check Crashlytics: [CRASHLYTICS_URL]
  3. Check Sentry: [SENTRY_URL]
  4. Check Firebase Console: [FIREBASE_URL]
  5. Check Cloud Functions logs: [LOGS_URL]

Common Issues and Fixes:

  Issue: App crashes on startup
  Likely cause: Firebase config mismatch or API key expired
  Fix: Check google-services.json / GoogleService-Info.plist match current project
  Escalate to: [NAME/TEAM]

  Issue: Payments failing
  Likely cause: Stripe webhook secret rotated, or Stripe API key expired
  Fix: Check Stripe Dashboard → Webhooks → verify endpoint status
  Escalate to: [NAME/TEAM]

  Issue: Cloud Functions timing out
  Likely cause: Cold start under load, or downstream service slow
  Fix: Check function logs, increase timeout/memory if needed, check downstream
  Escalate to: [NAME/TEAM]

  Issue: Authentication failures
  Likely cause: Firebase Auth config change, OAuth provider issue
  Fix: Check Firebase Console → Authentication → Settings
  Escalate to: [NAME/TEAM]

  Issue: Database slow / rate limited
  Likely cause: Missing Firestore indexes, or hot partition
  Fix: Check Firestore Console → Usage tab, add composite indexes
  Escalate to: [NAME/TEAM]

Escalation:
  - Cure Consulting support (if under maintenance SLA): [CONTACT]
  - Firebase support: https://firebase.google.com/support
  - Stripe support: https://support.stripe.com
```

### 4.3 Common Troubleshooting Guide

```
TOP 10 TROUBLESHOOTING SCENARIOS

1. "Build fails in CI"
   → Check GitHub Actions logs → usually dependency version mismatch
   → Fix: delete node_modules and package-lock.json, run npm install

2. "Emulators won't start"
   → Port conflict. Kill processes on ports 4000, 5001, 8080, 9099
   → Fix: lsof -ti:8080 | xargs kill -9

3. "Firestore security rules reject my request"
   → Test in Firebase Console → Rules Playground
   → Check authentication state and document path

4. "Push notifications not delivered"
   → Check APNs certificate expiry (iOS) or FCM server key (Android)
   → Verify device token is registered and not stale

5. "Stripe webhook returns 400"
   → Webhook secret mismatch between Stripe Dashboard and env vars
   → Use Stripe CLI to test locally: stripe listen --forward-to localhost:5001

6. "Next.js build fails with type errors"
   → Run: npx tsc --noEmit to see all type errors
   → Common: missing type for new API response shape

7. "Mobile app can't connect to staging/production"
   → Check API base URL in build config
   → Verify Firebase project ID matches environment

8. "Deployment hangs or times out"
   → Check GitHub Actions runner status
   → If Firebase deploy: check firebase-debug.log for details

9. "Images/files not loading"
   → Check Cloud Storage CORS configuration
   → Verify storage rules allow read access for the path

10. "Analytics events not appearing"
    → Firebase Analytics has 24-hour delay for non-real-time events
    → Use DebugView in Firebase Console for immediate verification
```

### 4.4 Monitoring Runbook

```
MONITORING RUNBOOK

Dashboards to Check Daily:
  - Service health: [URL]
  - Error tracking: [URL]
  - Business metrics: [URL]

What the Alerts Mean:
┌─────────────────────────────┬──────────────────────────────────────────┐
│ Alert Name                  │ What It Means / What to Do               │
├─────────────────────────────┼──────────────────────────────────────────┤
│ High Error Rate             │ >5% of requests failing. Check logs.     │
│ Latency Spike               │ p95 >2s. Check DB queries, cold starts.  │
│ Crash Rate Elevated         │ >1% crash rate. Check Crashlytics.       │
│ Payment Failures            │ Stripe errors. Check webhook + API keys. │
│ Budget Alert                │ Cloud spend approaching limit. Review.   │
│ Certificate Expiring        │ SSL/APNs cert needs renewal.             │
│ Function Timeout            │ Cloud Function hitting timeout limit.     │
└─────────────────────────────┴──────────────────────────────────────────┘
```
