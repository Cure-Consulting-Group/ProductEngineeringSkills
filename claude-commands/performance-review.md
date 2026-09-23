# Performance Review

**Outcome:** measured current numbers against explicit budgets, a ranked fix list with expected gain and effort, and (when asked) a load-test plan. Done when every budget that matters for the platform has a current value or a stated way to measure it, and every recommendation names the metric it moves. Every target is a number, never "make it faster." Match length to the need; no filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Stack: `ls package.json next.config.* build.gradle.kts Package.swift Podfile firebase.json 2>/dev/null | head -6 || echo "(none detected)"`
- Existing perf configs: `ls lighthouserc* .lighthouserc* k6* artillery* 2>/dev/null | head -5 || echo "(none)"`
- Existing build stats: `ls .next/analyze .next/build-manifest.json 2>/dev/null | head -3 || echo "(no build output)"`

## Baseline (read-only)

Measure from what exists; don't run builds or deploys unless the user asks (a build writes `.next/`, takes minutes, and the Recurring Mode run is read-only).
- Bundle: existing build output or analyzer report; otherwise ask the user to run `next build` (Turbopack prints per-route sizes) or open the analyzer.
- Field data beats lab data: CrUX/Search Console, Vercel Speed Insights or other RUM, Play Console Android vitals, Xcode Organizer/MetricKit.
- Code smells worth grepping: images >500 KB in the repo, raw `<img>` in Next.js pages, `SELECT *`, queries inside loops, unbounded list endpoints, Firestore list queries without `.limit()`.
- For industry benchmarks, search the web for current sources and date them.

## Step 1: Classify the Performance Review Type

| Type | When to Use | Primary Output |
|------|------------|----------------|
| Initial Audit | New project or first performance pass | Baseline metrics + budget definition |
| Optimization | Known performance issues or budget violations | Prioritized fix list with expected impact |
| Load Testing Plan | Pre-launch, scaling event, or new infrastructure | Test scenarios, scripts, success criteria |
| Regression guards | Post-launch, no perf checks in CI | Step 6 CI guards (dashboards/SLOs → `observability`) |
| Regression Check | After major release or dependency update | Before/after comparison, regression report |

## Step 2: Gather Context

```
Before any analysis, collect:

1. Platform(s):        Web / Android / iOS / Backend / Firebase
2. Current metrics:    What's measured today? (load time, crash rate, latency)
3. User scale:         DAU, peak concurrent users, geographic distribution
4. Infrastructure:     Cloud provider, CDN, database type, serverless vs. containers
5. Pain points:        What feels slow? User complaints? Drop-off points?
6. Deployment cadence: How often do you ship? CI/CD pipeline details?
7. Budget constraints: Hosting cost limits, CDN budget, third-party service caps
```

## Step 3: Performance Budgets by Platform

### Web (Next.js / React)

```
Core Web Vitals, p75 of field data (web.dev "Good" / Cure target):
  LCP  (Largest Contentful Paint):   ≤ 2.5s  / < 1.8s
  INP  (Interaction to Next Paint):  ≤ 200ms / < 150ms
  CLS  (Cumulative Layout Shift):    ≤ 0.1   / < 0.05
  (INP replaced FID as a Core Web Vital in March 2024 — don't report FID.)

Loading diagnostics:
  TTFB:                              ≤ 800ms good / Cure < 600ms (target < 200ms at the edge)
  First Contentful Paint:            ≤ 1.8s
  Total Blocking Time (lab proxy for INP): < 200ms
  (TTI was removed in Lighthouse 10 — don't budget it.)

Bundle size:
  Initial JS bundle:                 < 150 KB gzipped
  Per-route chunk:                   < 50 KB gzipped
  Total JS (all routes):             < 500 KB gzipped
  CSS:                               < 50 KB gzipped

Images:
  Hero/above-fold images:            < 200 KB each (WebP/AVIF)
  Thumbnails:                        < 30 KB each
  Total page weight:                 < 1.5 MB on initial load

Fonts:
  Custom fonts:                      < 100 KB total (WOFF2)
  Font display:                      swap or optional (no FOIT)
```

### Android (Kotlin)

```
Startup:
  Cold start:                        < 1s to first frame
  Warm start:                        < 500ms
  Hot start:                         < 200ms
  Splash → interactive:              < 2s

Rendering:
  Frame rendering:                   < 16ms per frame (60fps)
  Janky frames:                      < 5% of total frames
  Frozen frames (>700ms):            0 in normal flows

Memory:
  Baseline memory (idle):            < 80 MB
  Peak memory (active use):          < 200 MB
  Memory leak tolerance:             0 (strict — use LeakCanary)

Size:
  APK size (arm64):                  < 30 MB
  App Bundle download size:          < 15 MB (Play Store estimate)

Network:
  API response handling:             < 200ms to UI update after response
  Offline capability:                Core features work without network
```

### iOS (Swift)

```
Startup:
  Launch time (cold):                < 1s to first frame (< 400ms pre-main)
  Launch time (warm):                < 500ms
  Pre-main:                          prefer static linking / mergeable libraries over many
                                     dynamic frameworks; measure with the App Launch template

Rendering:
  Scrolling:                         60fps (120fps on ProMotion devices)
  Hitch ratio:                       < 5ms per second
  Off-screen rendering:              0 in scroll paths

Memory:
  Baseline memory:                   < 60 MB
  Peak memory:                       < 150 MB
  Memory pressure handling:          Respond to didReceiveMemoryWarning
  Jetsam limit awareness:            Stay below 50% of device limit

Size:
  App thinning (thin):               < 30 MB per variant
  Universal binary:                  < 100 MB
  Asset catalog:                     Use on-demand resources for large assets

Battery:
  Background CPU:                    < 3% sustained
  Location accuracy:                 Use significantLocationChanges when possible
  Network calls in background:       Batch with BGTaskScheduler
```

### Backend (API / Cloud Functions)

```
Latency:
  p50 response time:                 < 100ms
  p95 response time:                 < 500ms
  p99 response time:                 < 1s
  Database query time:               < 50ms (p95)

Throughput:
  Target RPS (per instance):         Define per endpoint (e.g., 500 RPS for read, 100 RPS for write)
  Autoscaling trigger:               CPU > 70% or RPS > 80% of target

Errors:
  Error rate budget:                 < 0.1% of requests (5xx errors)
  Timeout rate:                      < 0.05% of requests

Cold start (serverless):
  Cloud Functions cold start:        < 2s (target < 500ms)
  Minimum instances:                 Set for critical paths (auth, payments)

Database:
  Connection pool size:              10-20 per instance (tune per workload)
  Firestore read ops/request:        < 5 document reads per API call
  Cache hit rate:                    > 85% for hot data
```

## Step 4: Load Testing Plan

Default tool: **k6** (JS, CI-native thresholds). Locust for Python teams, Gatling for JVM teams. Never load-test production or third-party APIs (Stripe, Firebase Auth) without their permission — use test mode or stubs.

### Test Scenarios

```
1. Smoke Test
   Users:    5-10 concurrent
   Duration: 1-2 minutes
   Purpose:  Verify scripts work, endpoints respond
   Run:      Every deployment

2. Load Test (steady state)
   Users:    Expected peak concurrent users (e.g., 500)
   Duration: 10-15 minutes
   Ramp-up:  Linear over 2 minutes
   Purpose:  Validate system meets budgets under normal peak load
   Run:      Weekly or pre-release

3. Stress Test
   Users:    2x-3x expected peak (e.g., 1500)
   Duration: 10 minutes
   Ramp-up:  Linear over 3 minutes
   Purpose:  Find the breaking point, verify graceful degradation
   Run:      Monthly or before scaling events

4. Spike Test
   Users:    0 → 5x peak → 0 in 30 seconds
   Duration: 5 minutes
   Purpose:  Validate autoscaling, circuit breakers, queue handling
   Run:      Before marketing campaigns or launches

5. Soak Test
   Users:    70% of expected peak (e.g., 350)
   Duration: 2-4 hours
   Purpose:  Detect memory leaks, connection pool exhaustion, GC issues
   Run:      Before major releases
```

### k6 Script Template

```javascript
// k6 load test example
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // ramp up
    { duration: '10m', target: 100 },  // steady state
    { duration: '2m', target: 0 },     // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    http_reqs: ['rate>100'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/endpoint');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

### Success Criteria

```
Pass if ALL of:
  - p95 latency < defined budget
  - Error rate < 0.1%
  - No 5xx errors during ramp-up
  - CPU < 80% at steady state
  - Memory stable (no upward trend) during soak
  - Zero connection pool exhaustion
  - Autoscaling triggered within 60s of threshold breach
```

## Step 5: Optimization

Rank candidates by (expected metric gain × user reach) / effort, and tie each to the budget it fixes. Read `reference/details.md` when choosing fixes — it holds the Cure playbook of non-obvious, stack-specific levers and gotchas (Next.js caching, mobile startup, Firestore reads, serverless cold starts). Don't pad the list with generic advice the team already follows.

## Step 6: Regression Guards

- Lighthouse CI on PRs for key routes: assert LCP ≤2500ms, CLS ≤0.1, TBT ≤300ms (warn), 3 runs, median.
- Bundle-size check per route in CI; alert when the initial JS grows >10 KB or a route chunk >50 KB.
- Mobile: size check on the release artifact (APK/AAB, IPA) — alert on >1 MB growth; startup benchmark (Macrobenchmark on Android, XCTest launch metric on iOS) on release branches.
- Backend: k6 smoke test on every deploy with the Step 3 p95 threshold.

SLOs, error budgets, dashboards, and alert routing are owned by the `observability` skill — feed these budgets into it rather than defining a second alert set here.

## Step 7: Report

```markdown
# Performance Review — [app/feature], [platforms], [YYYY-MM-DD]
Type: [Initial audit / Optimization / Load plan / Regression check]

## Metrics vs budgets
| Metric | Current (source: field/lab) | Budget | Status | Priority |
|---|---|---|---|---|
| LCP p75 | 3.2s (CrUX) | ≤2.5s | OVER | P0 |

## Gaps and root causes
1. LCP 3.2s — 1.2 MB PNG hero, render-blocking CSS → est. impact on bounce

## Ranked recommendations
| # | Action | Metric moved | Expected gain | Effort |
|---|---|---|---|---|

## Load test results (if run)
| Scenario | VUs | Duration | p50 | p95 | p99 | Error % | Pass/Fail |

## Next steps (owner, date)
```

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: `/engagement-automation`).

- **Cadence:** monthly
- **Session loop:** session loops expire after 7 days, so a monthly cadence never fires in-session; it belongs in the cloud routine below. In-session alternative, during an active optimization push: `/loop 1d /cure-product-engineering:performance-review`.
- **Unattended:** scheduled cloud agent or CI cron — monthly performance pass over hot paths; compare against the previous run's baselines (recipes: `docs/AUTOMATION.md` in the cure-product-engineering plugin repo).
- **Budget:** ~150k tokens/run; cap at one run per monthly period.
- **Guardrails:** read-only run (advisory, not harness-enforced): no builds, deploys, or load tests against production; deliver findings as one issue per regression; report on failure rather than retrying.
