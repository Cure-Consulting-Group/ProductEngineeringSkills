---
name: chaos-engineering
description: "Design resilience testing — failure injection, graceful degradation, game days, and fault tolerance verification for distributed systems"
argument-hint: "[service-or-project]"
---

# Chaos Engineering

Structured resilience testing framework for distributed systems. Use when verifying fault tolerance, planning game days, designing graceful degradation, or building automated chaos into CI/CD. Assumes Firebase + GCP infrastructure with mobile and web clients.

## Step 1: Classify the Resilience Need

| Type | When to Use | Output |
|------|------------|--------|
| Failure Mode Analysis | Before launch or after architecture changes — catalog what can break | Failure mode catalog with severity, likelihood, and mitigation |
| Game Day Planning | Quarterly or before major launches — structured team exercise | Game day runbook with scope, safety controls, rollback plan |
| Automated Chaos | Mature teams with solid monitoring — continuous resilience verification | CI-integrated fault injection with steady-state hypothesis checks |
| Graceful Degradation Audit | After incidents or during architecture review — verify fallbacks work | Degradation matrix showing behavior under each failure mode |

## Step 2: Gather Context

1. **Architecture** -- what services exist, how do they communicate, what are the critical paths (auth, payments, data sync)?
2. **Dependencies** -- external APIs (Stripe, SendGrid, OAuth providers), databases (Firestore, Cloud SQL), CDNs, third-party SDKs?
3. **Monitoring maturity** -- do you have dashboards, alerts, error tracking, distributed tracing? Chaos without observability is just breaking things.
4. **Team readiness** -- has the team run game days before? Is there an on-call rotation? Do runbooks exist for major failure modes?
5. **Blast radius tolerance** -- can you test in production, or only staging? What is the acceptable impact window?
6. **Recovery mechanisms** -- feature flags, rollback procedures, circuit breakers already in place?

## Step 3: Failure Mode Catalog

### Network Failures
```
Failure Mode         Likelihood  Impact   Detection
─────────────────────────────────────────────────────────────
Network partition    Medium      High     Health checks fail, timeout errors spike
DNS resolution       Low         Critical All services unreachable
TLS certificate      Low         Critical Browser warnings, API rejections
High latency (>5s)   High        Medium   User abandonment, timeout cascades
Packet loss (>10%)   Medium      Medium   Retries spike, throughput drops
```

### Service Failures
```
Failure Mode              Likelihood  Impact    Detection
─────────────────────────────────────────────────────────────────
Cloud Functions crash     High        High      Error rate spike in Cloud Monitoring
Cloud Functions timeout   High        Medium    Timeout errors, 504 responses
Cloud Run OOM kill        Medium      High      Instance restarts, 503 responses
Auth provider down        Low         Critical  Login failures, session refresh fails
Firestore unavailable     Low         Critical  All reads/writes fail
Firestore quota exceeded  Medium      High      RESOURCE_EXHAUSTED errors
```

### Infrastructure Failures
```
Failure Mode              Likelihood  Impact    Detection
─────────────────────────────────────────────────────────────────
Disk full                 Medium      High      Write failures, log loss
Memory exhaustion         Medium      High      OOM kills, service restarts
CPU saturation            Medium      Medium    Latency increase, queue buildup
Cold start storm          High        Medium    Latency spike after scale-to-zero
Config/secret unavail.    Low         Critical  Service fails to start or auth fails
```

### Third-Party Failures
```
Failure Mode              Likelihood  Impact    Detection
─────────────────────────────────────────────────────────────────
Stripe API down           Low         Critical  Payment failures
SendGrid/email down       Medium      Low       Delayed notifications
OAuth provider down       Low         High      New logins fail
CDN outage                Low         High      Static assets unavailable
Analytics ingestion down  Medium      None      Data gap (no user impact)
```

## Step 4: Graceful Degradation Patterns

### Circuit Breaker
```typescript
// Wrap every external dependency call in a circuit breaker.
// After N consecutive failures, stop calling the dependency for a cooldown period.

interface CircuitBreakerConfig {
  failureThreshold: number;    // failures before opening (default: 5)
  resetTimeoutMs: number;      // cooldown before half-open (default: 30000)
  monitorWindowMs: number;     // window for counting failures (default: 60000)
}

// States:
//   CLOSED  → normal operation, requests pass through
//   OPEN    → dependency is down, return fallback immediately
//   HALF-OPEN → allow one probe request to test recovery

// Use for: Stripe API, external OAuth, third-party APIs
// Do NOT use for: Firestore (Google handles retries), internal services on same VPC
```

### Bulkhead Isolation
```
Isolate failure domains so one broken service doesn't take down everything.

Pattern                       Implementation
──────────────────────────────────────────────────────────────
Separate Cloud Functions      Each service = separate function with own memory/timeout
Connection pooling            Limit connections per downstream dependency
Queue-based decoupling        Pub/Sub between services — producer doesn't block on consumer
Separate Firebase projects    Critical services on dedicated projects (billing isolation)
Thread pool isolation         Cloud Run: separate containers per service domain
```

### Timeout + Retry with Backoff
```
Every network call MUST have:
  1. Timeout — never wait forever (Cloud Functions: 60s default, reduce for user-facing)
  2. Retry with exponential backoff — 1s, 2s, 4s, 8s, max 3 retries
  3. Jitter — add random 0-500ms to avoid thundering herd
  4. Idempotency — retried operations must be safe to repeat

// Firebase SDK handles retries for Firestore/Auth automatically.
// YOU must handle retries for: Stripe, SendGrid, custom APIs, webhooks.

Timeout defaults:
  User-facing API:       5 seconds (fail fast, show error)
  Background job:        30 seconds (retry on failure)
  Webhook processing:    10 seconds (acknowledge fast, process async)
  Database migration:    300 seconds (long-running, no retry)
```

### Fallback Responses
```
Every degraded state must have a defined fallback:

Service Down              Fallback Behavior
──────────────────────────────────────────────────────────────
Stripe API               Show "Payment temporarily unavailable, try again in a few minutes"
                         Queue the payment intent for retry via Cloud Tasks
Auth provider            Allow existing sessions to continue (cached tokens)
                         Disable new signups/logins with clear messaging
Firestore reads          Serve from local cache (Firebase SDK offline persistence)
                         Show stale data with "Last updated X ago" indicator
Firestore writes         Queue writes locally, sync when available
                         Show "Saved offline, will sync automatically"
Image/CDN               Serve placeholder images, lazy-load when available
Analytics                Drop events silently — never block user actions for analytics
Email/notifications      Queue for later delivery, no user-facing error
Search service           Fall back to basic Firestore queries (slower, less relevant)
```

### Feature Flag Kill Switches
```
Every major feature MUST have a Remote Config kill switch:

firebase.remoteConfig().defaultConfig = {
  enable_payments: true,
  enable_social_login: true,
  enable_push_notifications: true,
  enable_new_checkout_flow: true,
  maintenance_mode: false,
  force_update_version: "0.0.0",
};

Kill switch response time: < 1 minute (Remote Config fetch interval in crisis)
Test kill switches monthly — they are useless if untested.
```

## Step 5: Game Day Planning

### Pre-Game Day Checklist
```
1. SCOPE DEFINITION
   - Which failure modes are we testing? (pick 2-3 per game day)
   - Which environment? (staging first, production only for mature teams)
   - What is the blast radius? (specific service, specific region, percentage of traffic)
   - Duration: 1-2 hours maximum for the exercise

2. SAFETY CONTROLS
   - [ ] Kill switch to stop the experiment immediately
   - [ ] Rollback procedure documented and tested
   - [ ] On-call engineer designated and available
   - [ ] Customer support notified (if production)
   - [ ] Blast radius limited (percentage of traffic, single region)
   - [ ] Monitoring dashboards open and visible to all participants

3. PARTICIPANTS
   - Experiment lead: drives the chaos injection
   - Observer: watches dashboards, takes notes
   - On-call: ready to intervene if blast radius exceeds plan
   - Stakeholder: product/business person to assess user impact

4. STEADY-STATE DEFINITION
   - Define "normal" before you break things:
     - Error rate: < X%
     - P95 latency: < Xms
     - Throughput: > X req/s
     - Business metric: orders/min, signups/min
```

### Game Day Execution Template
```
TIME    ACTION
─────────────────────────────────────────────────────────
T-30    Verify monitoring dashboards, confirm steady state
T-15    Brief all participants, confirm safety controls
T-5     Final go/no-go decision
T+0     Inject failure (see failure injection methods below)
T+1     Observe: did alerts fire? Did fallbacks activate?
T+5     Assess: is blast radius within bounds? Continue or abort?
T+15    Extend or escalate the failure (if safe)
T+30    Remove failure injection
T+35    Verify full recovery to steady state
T+45    Debrief: what worked, what didn't, action items

ABORT CRITERIA (stop immediately if any):
  - Blast radius exceeds plan (more users affected than expected)
  - No rollback mechanism is working
  - Real incident occurs unrelated to game day
  - Any data loss or data corruption detected
```

### Failure Injection Methods
```
Firebase / GCP:
  - Cloud Functions: deploy a version that returns 500 for X% of requests
  - Firestore: modify security rules to deny reads on specific collection
  - Auth: revoke service account tokens, disable OAuth provider in console
  - Hosting: deploy a maintenance page to a percentage of traffic
  - Cloud Run: set maxInstances=0 to simulate service unavailability

Network:
  - Vercel/Cloudflare: add latency rules in edge config
  - Cloud Armor: block traffic from specific regions
  - DNS: lower TTL before game day, point to wrong IP during test

Mobile:
  - Remote Config: enable maintenance_mode flag
  - Force update: set force_update_version to current version
  - Kill switch: disable specific feature via feature flag

Application:
  - Environment variable: set CHAOS_MODE=true to activate fault injection
  - Feature flag: enable chaos-specific flags that inject delays/errors
  - Dependency override: swap real client with failing mock via DI
```

## Step 6: Platform-Specific Resilience

### Android
```
Failure Scenario                 Required Handling
──────────────────────────────────────────────────────────────
No network                       Offline-first with Room/Firestore cache
                                 Show cached data with "Offline" indicator
                                 Queue mutations for sync on reconnect
Slow network (2G simulation)     Timeout after 10s, show loading skeleton
                                 Progressive image loading (thumbnails first)
Background process killed        Save state in onSaveInstanceState / ViewModel
                                 Resume gracefully, re-fetch if state is stale
Low memory                       Release caches in onTrimMemory()
                                 Avoid holding references to large bitmaps
Disk full                        Catch IOException on write, show storage warning
                                 Degrade gracefully (skip caching, continue operation)

Testing tools:
  - Android Studio Network Profiler (throttle to 2G/3G)
  - Firebase Test Lab (test on low-end devices)
  - StrictMode (detect disk/network on main thread)
  - LeakCanary (memory leak detection)
```

### iOS
```
Failure Scenario                 Required Handling
──────────────────────────────────────────────────────────────
No network                       NWPathMonitor for connectivity state
                                 Offline queue with Core Data or Firestore cache
Background termination           Save state in applicationDidEnterBackground
                                 BGTaskScheduler for deferred work
Memory pressure                  Respond to didReceiveMemoryWarning
                                 Release image caches, cancel non-essential tasks
App Transport Security           All connections HTTPS (enforced by default)
                                 Certificate pinning for sensitive endpoints
Push notification failure        Fallback to in-app polling for critical updates
                                 Silent push for background data refresh

Testing tools:
  - Network Link Conditioner (simulate poor network)
  - Xcode Memory Graph Debugger
  - Instruments (Leaks, Time Profiler, Network)
  - XCTest with simulated network conditions
```

### Firebase / Cloud Functions
```
Failure Scenario                 Required Handling
──────────────────────────────────────────────────────────────
Cold start latency               minInstances=1 for critical functions
                                 Lazy initialization of heavy dependencies
Timeout (default 60s)            Set explicit timeouts per function type
                                 User-facing: 30s, Background: 300s
Memory limit exceeded            Monitor memory usage, right-size per function
                                 Stream large payloads instead of buffering
Firestore contention             Avoid hotspots (distributed counters)
                                 Use batched writes, avoid document-level contention
Emulator-based testing           Run chaos scenarios against emulator suite
                                 Simulate auth failures, permission denials

Emulator chaos testing:
  firebase emulators:start
  # Then: modify security rules live to test denial scenarios
  # Then: stop Firestore emulator to test offline handling
  # Then: inject latency in function code with CHAOS_MODE env var
```

## Step 7: Automated Chaos in CI/CD

### CI-Integrated Fault Injection
```yaml
# .github/workflows/chaos.yml
name: Chaos Tests
on:
  schedule:
    - cron: '0 3 * * 1'  # Weekly Monday 3 AM
  workflow_dispatch:       # Manual trigger

jobs:
  chaos-test:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging
        run: firebase deploy --only functions --project staging

      - name: Define steady state
        run: |
          # Record baseline metrics
          curl -s https://staging.example.com/health | jq '.status' | grep -q "ok"
          # Record baseline error rate and latency

      - name: Inject failure — Cloud Functions timeout
        run: |
          # Deploy chaos version with 50% artificial timeout
          CHAOS_MODE=timeout_50pct firebase deploy --only functions --project staging

      - name: Verify graceful degradation
        run: |
          # Run integration tests — they should pass with degraded behavior
          npm run test:chaos
          # Verify: error rate < 10%, fallbacks activated, no data loss

      - name: Remove failure
        run: |
          firebase deploy --only functions --project staging

      - name: Verify recovery
        run: |
          sleep 30
          curl -s https://staging.example.com/health | jq '.status' | grep -q "ok"
          npm run test:integration
```

### Steady-State Hypothesis Verification
```
Before every chaos experiment, define what "normal" looks like:

Hypothesis Template:
  "When [failure is injected], the system should [expected behavior]
   with [acceptable degradation] and recover within [time limit]."

Examples:
  "When Cloud Functions return 500 for 50% of requests,
   the mobile app should show cached data for read operations
   and queue write operations for retry,
   with full recovery within 60 seconds of failure removal."

  "When Stripe API is unreachable,
   the checkout flow should show a clear error message
   and offer to notify the user when payments are restored,
   with no duplicate charges after recovery."

  "When Firestore is unavailable for 5 minutes,
   the web app should serve stale data from the browser cache
   with a visible 'offline' indicator,
   and automatically sync pending writes within 30 seconds of recovery."
```

### Chaos Maturity Model
```
Level 0 — Ad Hoc
  No resilience testing. Hope things work. Fix after incidents.
  → Start here: catalog failure modes, add basic health checks

Level 1 — Manual Game Days
  Quarterly game days in staging. Manual failure injection.
  → Add: circuit breakers, timeouts, fallback responses

Level 2 — Automated Staging Chaos
  Weekly automated chaos in staging. Steady-state verification.
  → Add: CI-integrated fault injection, automated recovery checks

Level 3 — Production Chaos
  Controlled chaos in production with traffic percentage limits.
  → Add: canary analysis, automated rollback, per-request fault injection

Level 4 — Continuous Verification
  Every deploy includes resilience verification. Chaos is part of CI/CD.
  → Add: pre-deploy chaos gates, SLO-based experiment abort
```

## Step 8: Output

```
CHAOS ENGINEERING REPORT
System: [NAME]
Date: [TODAY]
Prepared by: [NAME]

RESILIENCE SUMMARY
┌──────────────────────────┬────────────────────────────────────┐
│ Field                    │ Value                              │
├──────────────────────────┼────────────────────────────────────┤
│ Chaos Maturity Level     │ [0-4 from maturity model]          │
│ Failure Modes Cataloged  │ [Count]                            │
│ Degradation Patterns     │ [Circuit breaker, bulkhead, etc.]  │
│ Game Days Conducted      │ [Count, last date]                 │
│ Automated Chaos          │ [Yes/No, frequency]                │
│ Recovery Time Target     │ [Seconds/minutes]                  │
│ Kill Switches Deployed   │ [Count, last tested]               │
└──────────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Failure mode catalog with severity and likelihood
  - [ ] Graceful degradation matrix (failure → fallback behavior)
  - [ ] Circuit breaker and retry configuration
  - [ ] Feature flag kill switches for critical features
  - [ ] Game day runbook with safety controls
  - [ ] Platform-specific resilience patterns (Android/iOS/Firebase)
  - [ ] CI-integrated chaos test workflow
  - [ ] Steady-state hypotheses for each failure mode
  - [ ] Chaos maturity assessment with next-level recommendations

RELATED SKILLS:
  - /incident-response — when chaos reveals real problems
  - /testing-strategy — unit and integration tests complement chaos tests
  - /infrastructure-scaffold — infra configs that enable resilience
  - /performance-review — performance under failure conditions
```
