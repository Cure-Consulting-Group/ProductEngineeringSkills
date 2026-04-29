---
name: performance-review
version: "1.0.0"
description: "Define performance budgets, load testing plans, optimization strategies, and monitoring dashboards across mobile, web, and backend"
when_to_use: "Use when defining performance budgets, load testing plans, or optimization strategies across mobile, web, and backend. NOT for DORA metrics (use dora-metrics)."
argument-hint: "[app-or-feature]"
context: fork
---

# Performance Review

Define performance budgets, build load testing plans, identify optimization opportunities, and set up monitoring. Every target uses concrete numbers — no vague "make it faster."

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Automated Performance Baseline

Gather performance context before review:

1. **Bundle Analysis**:
   - Run: `npx next build 2>/dev/null | tail -20` or check for existing build stats
   - Glob for: `**/webpack-stats.json`, `**/bundle-analyzer*`
2. **Existing Configs**:
   - Glob for: `**/lighthouse*`, `**/k6*`, `**/artillery*`, `**/.lighthouserc*`
   - Read any found configs to understand current budgets
3. **Image Optimization**:
   - Glob for: `**/*.png` `**/*.jpg` `**/*.gif` larger than 500KB
   - Grep for: `<img` without `next/image` or lazy loading in web projects
4. **Database Queries**:
   - Grep for: `SELECT *` (unbounded queries)
   - Grep for: N+1 patterns (queries inside loops)
5. **Web Search**: Search for current Core Web Vitals benchmarks for the project's industry

Use findings to populate the performance baseline before applying the review framework.

## Step 1: Classify the Performance Review Type

| Type | When to Use | Primary Output |
|------|------------|----------------|
| Initial Audit | New project or first performance pass | Baseline metrics + budget definition |
| Optimization | Known performance issues or budget violations | Prioritized fix list with expected impact |
| Load Testing Plan | Pre-launch, scaling event, or new infrastructure | Test scenarios, scripts, success criteria |
| Monitoring Setup | Post-launch or missing observability | Dashboards, alerts, SLO/SLI definitions |
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
Core Web Vitals (must meet "Good" threshold):
  LCP  (Largest Contentful Paint):   < 2.5s  (target < 1.8s)
  FID  (First Input Delay):          < 100ms (target < 50ms)
  INP  (Interaction to Next Paint):  < 200ms (target < 150ms)
  CLS  (Cumulative Layout Shift):    < 0.1   (target < 0.05)

Loading:
  TTI  (Time to Interactive):        < 3.5s on 4G
  TTFB (Time to First Byte):        < 600ms (target < 200ms)
  First Contentful Paint:            < 1.8s

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
  dylib loading:                     < 6 frameworks recommended

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

### Tool Selection

```
Tool        | Best For                      | Language
------------|-------------------------------|----------
k6          | Developer-friendly, CI/CD     | JavaScript
Artillery   | Quick YAML-based tests        | YAML/JS
Locust      | Python teams, distributed     | Python
Gatling     | JVM teams, detailed reports   | Scala/Java
```

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

## Step 5: Optimization Strategies

### Web Optimization

```
Code splitting:
  - Route-based splitting with next/dynamic or React.lazy
  - Split vendor chunks > 50 KB into separate bundles
  - Defer below-fold component loading with Intersection Observer
  - Use barrel file elimination (avoid re-exporting entire modules)

Image optimization:
  - Serve WebP/AVIF with <picture> fallback
  - Use next/image with width/height (prevents CLS)
  - Implement responsive srcset (mobile: 640w, tablet: 1024w, desktop: 1920w)
  - Lazy load below-fold images (loading="lazy")
  - Use blur placeholder for hero images

Caching:
  - Static assets: Cache-Control max-age=31536000, immutable
  - API responses: stale-while-revalidate pattern
  - Service worker: cache-first for static, network-first for API
  - ISR (Incremental Static Regeneration): revalidate=60 for semi-static pages

Rendering:
  - SSG for marketing/content pages (build-time generation)
  - SSR for personalized/dynamic pages
  - Streaming SSR with React Suspense for progressive loading
  - Edge rendering for geo-sensitive content (Vercel Edge, Cloudflare Workers)

CDN:
  - All static assets served from CDN (Vercel, CloudFront, Cloudflare)
  - API responses cached at edge for public data (Cache-Control: s-maxage=60)
  - Purge strategy: deploy-time invalidation for static, TTL for dynamic
```

### Mobile Optimization (Android & iOS)

```
Lazy initialization:
  - Defer non-critical SDK init to after first frame
  - Use lazy properties (Kotlin: by lazy {}, Swift: lazy var)
  - Initialize analytics/crash reporting after UI is interactive
  - Background-init heavy singletons (database, image cache)

Image caching:
  - Android: Coil with disk cache (250 MB limit), memory cache (25% of heap)
  - iOS: Kingfisher with disk cache (300 MB), memory cache (100 MB)
  - Downscale images to display size before decoding
  - Prefetch next-screen images during idle time

List performance:
  - RecyclerView with DiffUtil (Android) / LazyColumn with keys (Compose)
  - UICollectionView with DiffableDataSource (iOS)
  - Pagination: 20 items per page, prefetch at 80% scroll position
  - Avoid nested scrollable containers

Threading:
  - Android: Dispatchers.IO for network/disk, Dispatchers.Default for computation
  - iOS: async/await with TaskGroup, never block MainActor
  - Image decoding on background thread (always)
  - JSON parsing off main thread for payloads > 1 KB
```

### Backend Optimization

```
Query optimization:
  - Add indexes for all WHERE/ORDER BY fields
  - Use EXPLAIN ANALYZE for queries > 50ms
  - Avoid N+1 queries: use JOINs or batch fetching
  - Paginate all list endpoints (max 100 items per page)

Connection pooling:
  - PostgreSQL: PgBouncer with transaction mode, pool size = (CPU cores * 2) + disk spindles
  - MySQL: ProxySQL for connection multiplexing
  - Close idle connections after 300s
  - Monitor pool utilization — alert at 80%

Caching layers:
  - L1: In-memory (application-level, <1ms, 100 MB limit)
  - L2: Redis/Memcached (<5ms, session data, computed results)
  - L3: CDN edge cache (<50ms, public API responses)
  - Cache invalidation: event-driven (pub/sub) over TTL when possible
  - Redis: set maxmemory-policy allkeys-lru, monitor hit rate

Denormalization:
  - Precompute aggregations for dashboard queries
  - Store derived fields (e.g., order_total) to avoid joins
  - Use materialized views for complex reporting queries
  - Rebuild strategy: async job, not in request path

Serverless cold start mitigation:
  - Minimum instances: 1-3 for critical functions (auth, payments, webhooks)
  - Keep dependencies minimal (< 50 MB deployment package)
  - Use lazy imports for heavy libraries
  - Prefer Cloud Run over Cloud Functions for sustained traffic
```

### Firebase-Specific Optimization

```
Firestore read optimization:
  - Design documents for read patterns (denormalize, don't normalize)
  - Keep documents < 10 KB for fast reads
  - Use subcollections for 1:N relationships (not arrays)
  - Limit query results: .limit(20) on all list queries
  - Use select() to fetch only needed fields

Composite indexes:
  - Create for all multi-field queries (equality + range + orderBy)
  - Monitor index usage in Firebase Console
  - Remove unused indexes (they cost write performance)

Offline persistence:
  - Enable on mobile: FirebaseFirestore.setSettings { isPersistenceEnabled = true }
  - Set cache size: 100 MB minimum for offline-first apps
  - Use source: .cache for non-critical reads
  - Implement optimistic UI updates with rollback on sync failure

Batch operations:
  - Use writeBatch() for multi-document writes (max 500 per batch)
  - Batch reads with getAll() instead of sequential gets
  - Transaction retry: max 5 attempts with exponential backoff
  - Use Firestore BulkWriter for server-side migrations
```

## Step 6: Monitoring & Alerting

### Monitoring Stack

```
Platform         | Tool                          | Purpose
-----------------|-------------------------------|---------------------------
Web              | Lighthouse CI                 | CWV tracking per deploy
Web              | Vercel Analytics / SpeedCurve | Real User Monitoring (RUM)
Android          | Firebase Performance          | Trace durations, network
iOS              | Firebase Performance          | Trace durations, network
Android          | Android Vitals (Play Console) | ANR, crash rate, startup
iOS              | Xcode Metrics / MetricKit     | Launch, hang rate, disk
Backend          | Datadog / Grafana / Cloud Mon | Latency, errors, throughput
All              | Sentry                        | Error tracking, tracing
All              | PagerDuty / Opsgenie          | Incident alerting
```

### Alert Thresholds

```
Severity: CRITICAL (page on-call immediately)
  - Error rate > 1% for 5 minutes
  - p99 latency > 5s for 5 minutes
  - Service availability < 99% for 5 minutes
  - Database connection pool > 95%
  - Memory usage > 90%

Severity: WARNING (Slack alert, fix within 4 hours)
  - Error rate > 0.5% for 10 minutes
  - p95 latency > 2x budget for 10 minutes
  - CPU > 80% sustained for 15 minutes
  - Cache hit rate < 70%
  - Cold start rate > 20% of invocations

Severity: INFO (dashboard review, weekly triage)
  - p50 latency trending up > 10% week-over-week
  - Bundle size increased > 10 KB from last deploy
  - LCP regression > 200ms from baseline
  - APK/IPA size increased > 1 MB
```

### SLO / SLI Definitions

```
SLI (Service Level Indicator):
  - Availability:  successful requests / total requests
  - Latency:       % of requests < threshold (e.g., p95 < 500ms)
  - Throughput:     requests per second at steady state
  - Error rate:     5xx responses / total responses

SLO (Service Level Objective):
  - Availability:  99.9% monthly (43.8 min downtime/month allowed)
  - Latency:       95% of requests < 500ms
  - Error rate:    < 0.1% monthly

Error Budget:
  - Monthly budget: 100% - SLO = allowed failures
  - 99.9% SLO → 0.1% error budget → ~43 minutes/month
  - Track burn rate: if budget consumed > 50% in first week, freeze deploys
  - Reset monthly, review in retrospective
```

### Lighthouse CI Configuration

```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "url": ["https://example.com/", "https://example.com/dashboard"]
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "first-contentful-paint": ["warn", { "maxNumericValue": 1800 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "total-blocking-time": ["warn", { "maxNumericValue": 300 }]
      }
    },
    "upload": {
      "target": "lhci",
      "serverBaseUrl": "https://lhci.example.com"
    }
  }
}
```

## Step 7: Performance Report Template

```markdown
# Performance Review Report

## Overview
- App/Feature:       [name]
- Platform(s):       [Web / Android / iOS / Backend]
- Review type:       [Initial Audit / Optimization / Regression Check]
- Date:              [YYYY-MM-DD]
- Reviewed by:       [name]

## Current Metrics vs. Targets

| Metric              | Current    | Target     | Status   | Priority |
|---------------------|-----------|------------|----------|----------|
| LCP                 | 3.2s      | < 2.5s     | OVER     | P0       |
| CLS                 | 0.08      | < 0.1      | OK       | -        |
| Bundle size (init)  | 220 KB    | < 150 KB   | OVER     | P1       |
| API p95 latency     | 380ms     | < 500ms    | OK       | -        |
| Cold start          | 1.8s      | < 1s       | OVER     | P0       |
| Error rate          | 0.08%     | < 0.1%     | OK       | -        |

## Gaps & Root Causes

1. **LCP 3.2s (target < 2.5s)**
   - Root cause: Unoptimized hero image (1.2 MB PNG), render-blocking CSS
   - Impact: 15% bounce rate increase on slow connections

2. **Bundle size 220 KB (target < 150 KB)**
   - Root cause: Full lodash import, unshaken date-fns
   - Impact: 400ms additional parse time on mid-tier mobile

3. **Cold start 1.8s (target < 1s)**
   - Root cause: Heavy dependency initialization, no minimum instances
   - Impact: First request after idle fails SLO

## Prioritized Recommendations

| # | Action                                    | Impact  | Effort | Expected Gain     |
|---|------------------------------------------|---------|--------|-------------------|
| 1 | Convert hero image to AVIF + resize      | High    | Low    | LCP -1.0s         |
| 2 | Tree-shake lodash → lodash-es            | Medium  | Low    | Bundle -40 KB     |
| 3 | Set minimum instances = 1                | High    | Low    | Cold start < 500ms|
| 4 | Add route-based code splitting           | Medium  | Medium | Bundle -50 KB     |
| 5 | Implement Redis cache for hot queries    | High    | Medium | p95 latency -30%  |
| 6 | Enable ISR for product pages             | Medium  | Medium | LCP -500ms        |

## Load Test Results (if applicable)

| Scenario    | VUs  | Duration | p50    | p95    | p99    | Error % | Result |
|-------------|------|----------|--------|--------|--------|---------|--------|
| Smoke       | 10   | 2m       | 85ms   | 180ms  | 350ms  | 0%      | PASS   |
| Load        | 500  | 15m      | 120ms  | 420ms  | 890ms  | 0.02%   | PASS   |
| Stress      | 1500 | 10m      | 450ms  | 1.8s   | 4.2s   | 1.2%    | FAIL   |
| Soak        | 350  | 4h       | 130ms  | 480ms  | 920ms  | 0.04%   | PASS   |

## Next Steps

- [ ] Implement P0 fixes before next release
- [ ] Schedule follow-up review after P0/P1 fixes
- [ ] Set up missing monitoring dashboards
- [ ] Add Lighthouse CI to PR pipeline
- [ ] Run load test after optimization round
```
