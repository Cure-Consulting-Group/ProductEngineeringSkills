---
name: observability
description: "Set up observability stacks — structured logging, distributed tracing, alerting, SLO/SLI definition, and dashboards with Crashlytics, Sentry, or Datadog"
argument-hint: "[project-or-service]"
---

# Observability

Production observability framework covering the three pillars — logs, metrics, and traces — across all Cure Consulting Group platforms. Every production service ships with structured logging, health metrics, distributed tracing, SLO definitions, and actionable alerts. No service goes to production without observability.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Automated Observability Baseline

Scan for existing monitoring infrastructure:

1. **Logging**: Grep for logging libraries:
   - `winston|pino|bunyan|log4j|timber|os_log|slog`
   - Grep for: `console.log` count (debug logging in production)
2. **Monitoring**: Glob for configs:
   - `**/sentry*`, `**/datadog*`, `**/newrelic*`, `**/prometheus*`, `**/grafana*`
3. **Tracing**: Grep for:
   - `opentelemetry|jaeger|zipkin|@sentry/tracing|dd-trace`
4. **Alerting**: Glob for alert configs:
   - `**/alerts*`, `**/monitors*`, `**/*alert*`
5. **Health Checks**: Grep for:
   - `/health|/healthz|/ready|/live` endpoint definitions

Report observability maturity level before recommending improvements.

## Step 1: Classify the Observability Need

| Need | Scope | Starting Point |
|------|-------|---------------|
| Greenfield setup | Full observability stack from scratch — logging, metrics, tracing, dashboards, alerts | Start at Step 3 |
| Add monitoring to existing | Bolt on observability to a service that shipped without it | Audit current gaps first, then Step 3 |
| Incident-driven improvement | Post-mortem revealed monitoring gaps — targeted fixes | Identify specific gaps, apply relevant sections |
| SLO definition | Define reliability targets and error budgets for existing services | Jump to Step 5 |
| Alert tuning | Reduce noise, fix alert fatigue, improve signal-to-noise | Jump to Step 6 |

## Step 2: Gather Context

1. **Platforms** -- which platforms are in play (Android, iOS, Web, Firebase Functions, Cloud Run, third-party APIs)?
2. **Current tooling** -- what is already instrumented (Crashlytics, Sentry, Datadog, Cloud Monitoring, custom logging)?
3. **Scale** -- requests per second, daily active users, number of services, geographic distribution?
4. **Compliance requirements** -- HIPAA (no PHI in logs), SOC 2 (audit trails), GDPR (PII redaction), data residency?
5. **Budget** -- Datadog/New Relic licensing vs. GCP-native vs. open-source (Grafana/Prometheus)?
6. **Team maturity** -- is there an on-call rotation, are there existing runbooks, who owns observability?
7. **Pain points** -- what incidents have been missed, what takes too long to debug, where are the blind spots?

## Step 3: Three Pillars Framework -- Logs, Metrics, Traces

### Pillar 1: Structured Logging

Every log line must be machine-parseable. No `console.log("something happened")` in production.

#### Log Format Standard (JSON)
```json
{
  "timestamp": "2026-03-14T15:04:05.000Z",
  "severity": "ERROR",
  "service": "payment-api",
  "version": "2.1.0",
  "traceId": "abc123def456",
  "spanId": "span789",
  "correlationId": "req-uuid-here",
  "userId": "REDACTED",
  "message": "Stripe charge failed",
  "error": {
    "type": "StripeCardError",
    "message": "Card declined",
    "code": "card_declined"
  },
  "metadata": {
    "amount": 2999,
    "currency": "usd",
    "retryCount": 2
  }
}
```

#### Log Level Standards
```
LEVEL      When to Use                                    Production Volume
─────────────────────────────────────────────────────────────────────────────
DEBUG      Variable values, execution flow details         OFF in production
INFO       Business events: user signup, order placed,     Moderate — only
           deployment complete, feature flag changed        meaningful events
WARNING    Recoverable errors: retry succeeded, rate       Low — things that
           limit approaching, deprecated API used           need attention soon
ERROR      Failed operations: payment failed, API call     Low — every error
           returned 5xx, database write failed              should be actionable
CRITICAL   System-level failures: database unreachable,    Rare — pages on-call
           out of memory, certificate expiring              immediately
```

Rules:
- **Never log PII in plaintext** -- hash or redact emails, phone numbers, SSNs, payment details
- **Always include correlation IDs** -- every request gets a UUID at the edge, propagated through all services
- **Never log secrets** -- API keys, tokens, passwords must never appear in logs (use `[REDACTED]`)
- **Include service version** -- critical for correlating issues with deployments
- **Use structured fields, not string interpolation** -- `logger.info("Order placed", { orderId, amount })` not `logger.info(f"Order {orderId} placed for ${amount}")`

#### PII Redaction Implementation
```typescript
// lib/log-sanitizer.ts
const PII_PATTERNS: Record<string, RegExp> = {
  email: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
  phone: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g,
  ssn: /\b\d{3}-?\d{2}-?\d{4}\b/g,
  creditCard: /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g,
};

export function sanitize(obj: Record<string, unknown>): Record<string, unknown> {
  const serialized = JSON.stringify(obj);
  let sanitized = serialized;
  for (const [type, pattern] of Object.entries(PII_PATTERNS)) {
    sanitized = sanitized.replace(pattern, `[REDACTED:${type}]`);
  }
  return JSON.parse(sanitized);
}
```

#### Correlation ID Middleware
```typescript
// middleware/correlation.ts
import { randomUUID } from "crypto";

export function correlationMiddleware(req: Request, res: Response, next: NextFunction) {
  const correlationId = req.headers["x-correlation-id"] as string || randomUUID();
  req.correlationId = correlationId;
  res.setHeader("x-correlation-id", correlationId);
  // Attach to async context for downstream logging
  asyncLocalStorage.run({ correlationId, traceId: req.headers["x-cloud-trace-context"] }, next);
}
```

### Pillar 2: Metrics

#### Metric Types and When to Use Each
```
Type          Purpose                              Examples
─────────────────────────────────────────────────────────────────────────────
Counter       Monotonically increasing count       Requests served, errors, signups
Gauge         Point-in-time value                  Active connections, queue depth, memory usage
Histogram     Distribution of values               Request latency, payload size, processing time
Summary       Pre-calculated quantiles             Response time p50/p95/p99
```

#### Standard Metrics Every Service Must Emit
```
RED Metrics (Request-driven services):
  - Rate:      requests per second, by endpoint and status code
  - Errors:    error count and error rate, by type
  - Duration:  latency histogram (p50, p95, p99), by endpoint

USE Metrics (Resource-utilization services):
  - Utilization: CPU %, memory %, disk %, connection pool usage
  - Saturation:  queue depth, thread pool saturation, pending requests
  - Errors:      resource errors (OOM kills, connection timeouts, disk full)

Business Metrics:
  - Signups per hour
  - Orders placed per minute
  - Payment success/failure rate
  - Feature adoption rate (by feature flag)
  - Active sessions
```

#### Custom Metrics Implementation (Cloud Monitoring)
```typescript
// lib/metrics.ts
import { MetricServiceClient } from "@google-cloud/monitoring";

const client = new MetricServiceClient();
const projectPath = client.projectPath(process.env.GCP_PROJECT_ID!);

export async function recordMetric(
  metricType: string,
  value: number,
  labels: Record<string, string> = {}
) {
  const dataPoint = {
    interval: { endTime: { seconds: Math.floor(Date.now() / 1000) } },
    value: { doubleValue: value },
  };

  await client.createTimeSeries({
    name: projectPath,
    timeSeries: [{
      metric: { type: `custom.googleapis.com/${metricType}`, labels },
      resource: { type: "global", labels: { project_id: process.env.GCP_PROJECT_ID! } },
      points: [dataPoint],
    }],
  });
}

// Usage
await recordMetric("api/request_latency_ms", 142, { endpoint: "/api/orders", method: "POST" });
await recordMetric("business/orders_placed", 1, { plan: "pro", source: "web" });
```

### Pillar 3: Distributed Tracing

#### Span Naming Conventions
```
Format: <service>.<operation_type>.<resource>

Examples:
  payment-api.http.POST_/api/charges
  payment-api.stripe.create_charge
  payment-api.firestore.read_users
  order-service.pubsub.process_order_event
  auth-service.http.POST_/api/login
  auth-service.firebase_auth.verify_token

Rules:
  - Use dots as separators
  - Include the operation type (http, grpc, db, cache, queue)
  - Include the specific resource or endpoint
  - Keep consistent across all services
```

#### OpenTelemetry Setup (Node.js)
```typescript
// instrumentation.ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { TraceExporter } from "@google-cloud/opentelemetry-cloud-trace-exporter";
import { Resource } from "@opentelemetry/resources";

const sdk = new NodeSDK({
  resource: new Resource({
    "service.name": process.env.SERVICE_NAME || "unknown",
    "service.version": process.env.SERVICE_VERSION || "0.0.0",
    "deployment.environment": process.env.NODE_ENV || "development",
  }),
  traceExporter: new TraceExporter(),
  instrumentations: [getNodeAutoInstrumentations({
    "@opentelemetry/instrumentation-fs": { enabled: false },
  })],
});

sdk.start();
```

#### Custom Span Example
```typescript
import { trace, SpanStatusCode } from "@opentelemetry/api";

const tracer = trace.getTracer("payment-api");

export async function processPayment(orderId: string, amount: number) {
  return tracer.startActiveSpan("payment-api.stripe.create_charge", async (span) => {
    span.setAttributes({
      "order.id": orderId,
      "payment.amount": amount,
      "payment.currency": "usd",
    });
    try {
      const charge = await stripe.charges.create({ amount, currency: "usd" });
      span.setAttributes({ "payment.charge_id": charge.id, "payment.status": charge.status });
      span.setStatus({ code: SpanStatusCode.OK });
      return charge;
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: String(error) });
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

## Step 4: Platform-Specific Setup

### Android: Crashlytics + Firebase Performance
```kotlin
// Application.kt
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        // Crashlytics — automatic crash reporting
        FirebaseCrashlytics.getInstance().apply {
            setCrashlyticsCollectionEnabled(!BuildConfig.DEBUG)
            setCustomKey("build_type", BuildConfig.BUILD_TYPE)
            setCustomKey("app_version", BuildConfig.VERSION_NAME)
        }

        // Performance monitoring — automatic HTTP/screen traces
        FirebasePerformance.getInstance().isPerformanceCollectionEnabled = !BuildConfig.DEBUG

        // StrictMode for dev builds — catch ANRs and leaks early
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(StrictMode.ThreadPolicy.Builder()
                .detectDiskReads().detectDiskWrites().detectNetwork()
                .penaltyLog().build())
            StrictMode.setVmPolicy(StrictMode.VmPolicy.Builder()
                .detectLeakedSqlLiteObjects().detectLeakedClosableObjects()
                .penaltyLog().build())
        }
    }
}

// Custom trace for critical flows
suspend fun <T> traceOperation(name: String, block: suspend () -> T): T {
    val trace = FirebasePerformance.getInstance().newTrace(name)
    trace.start()
    return try {
        val result = block()
        trace.putAttribute("status", "success")
        result
    } catch (e: Exception) {
        trace.putAttribute("status", "error")
        trace.putAttribute("error_type", e.javaClass.simpleName)
        FirebaseCrashlytics.getInstance().recordException(e)
        throw e
    } finally {
        trace.stop()
    }
}
```

#### ANR Detection
```kotlin
// Automatic with Crashlytics. Additionally:
// - Firebase Performance auto-detects frozen frames (>700ms) and slow frames (>16ms)
// - Set up alerts in Firebase Console for ANR rate > 0.5%
// - Use Perfetto traces for deep ANR investigation in Android Studio
```

### iOS: Crashlytics + MetricKit + os_signpost
```swift
// AppDelegate.swift
import FirebaseCrashlytics
import FirebasePerformance
import MetricKit
import os.signpost

class AppDelegate: UIResponder, UIApplicationDelegate, MXMetricManagerSubscriber {
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Crashlytics
        Crashlytics.crashlytics().setCrashlyticsCollectionEnabled(!isDebugBuild)
        Crashlytics.crashlytics().setCustomValue(Bundle.main.appVersion, forKey: "app_version")

        // MetricKit — system-level performance metrics delivered daily
        MXMetricManager.shared.add(self)

        return true
    }

    // MetricKit daily payload
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            let data = payload.jsonRepresentation()
            // Upload to your analytics backend for trending
            AnalyticsService.shared.uploadMetricKitPayload(data)
        }
    }

    // MetricKit diagnostic payload (hangs, crashes, disk writes)
    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            Crashlytics.crashlytics().log("MetricKit diagnostic: \(payload.jsonRepresentation())")
        }
    }
}

// os_signpost for custom performance instrumentation
let log = OSLog(subsystem: "com.app.performance", category: .pointsOfInterest)

func loadDashboard() async throws -> Dashboard {
    let signpostID = OSSignpostID(log: log)
    os_signpost(.begin, log: log, name: "LoadDashboard", signpostID: signpostID)
    defer { os_signpost(.end, log: log, name: "LoadDashboard", signpostID: signpostID) }

    let trace = Performance.startTrace(name: "load_dashboard")
    defer { trace?.stop() }

    let dashboard = try await repository.fetchDashboard()
    trace?.setValue(Int64(dashboard.widgets.count), forMetric: "widget_count")
    return dashboard
}
```

### Web: Sentry + Web Vitals + Next.js Instrumentation
```typescript
// lib/sentry-client.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  release: process.env.NEXT_PUBLIC_APP_VERSION,
  tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
  profilesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.replayIntegration({ maskAllText: false, blockAllMedia: false }),
    Sentry.browserTracingIntegration(),
    Sentry.feedbackIntegration({ colorScheme: "system" }),
  ],
  beforeSend(event) {
    // Scrub PII from error events
    if (event.request?.headers) {
      delete event.request.headers["Authorization"];
      delete event.request.headers["Cookie"];
    }
    return event;
  },
});

// Web Vitals reporting
// app/layout.tsx — Next.js App Router
export function reportWebVitals(metric: NextWebVitalsMetric) {
  const body = { name: metric.name, value: metric.value, id: metric.id };

  // Send to analytics
  if (metric.name === "LCP" && metric.value > 2500) {
    Sentry.captureMessage(`Poor LCP: ${metric.value}ms`, { level: "warning", extra: body });
  }
  if (metric.name === "CLS" && metric.value > 0.1) {
    Sentry.captureMessage(`Poor CLS: ${metric.value}`, { level: "warning", extra: body });
  }
  if (metric.name === "INP" && metric.value > 200) {
    Sentry.captureMessage(`Poor INP: ${metric.value}ms`, { level: "warning", extra: body });
  }
}
```

#### Web Vitals Budgets
```
Metric    Good        Needs Work    Poor        Our Target
──────────────────────────────────────────────────────────
LCP       ≤2.5s       2.5-4.0s      >4.0s       ≤2.0s
INP       ≤200ms      200-500ms     >500ms      ≤150ms
CLS       ≤0.1        0.1-0.25      >0.25       ≤0.05
TTFB      ≤800ms      800-1800ms    >1800ms     ≤500ms
FCP       ≤1.8s       1.8-3.0s      >3.0s       ≤1.5s
```

### Firebase Functions: Cloud Logging + Cloud Trace
```typescript
// functions/src/lib/logger.ts
import { logger } from "firebase-functions/v2";

export function logBusinessEvent(event: string, data: Record<string, unknown>) {
  logger.info(event, {
    ...sanitize(data),
    event,
    service: "cloud-functions",
    version: process.env.K_REVISION || "unknown",
  });
}

export function logError(message: string, error: Error, context: Record<string, unknown> = {}) {
  logger.error(message, {
    ...sanitize(context),
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack,
    },
    service: "cloud-functions",
  });
}

// Cloud Trace auto-instrumentation is enabled by default in Cloud Functions v2.
// Custom spans via OpenTelemetry are also supported — see Step 3.
```

## Step 5: SLO/SLI Definition

### SLI Definitions (Service Level Indicators)
```
SLI Type       Measurement                                  Formula
────────────────────────────────────────────────────────────────────────────────
Availability   Ratio of successful requests                 (200-399 responses) / total requests
Latency        Ratio of requests faster than threshold      requests < threshold / total requests
Error Rate     Ratio of failed requests                     (500+ responses) / total requests
Throughput     Requests served per second                   count(requests) / time_window
Freshness      Ratio of data updated within threshold       stale_records < threshold / total records
Correctness    Ratio of correct outputs                     correct_responses / total_responses
```

### SLO Template Per Service
```
SERVICE: [Name]
Owner: [Team]
Tier: [Critical / Standard / Best-effort]

┌────────────────────┬──────────────┬────────────────┬─────────────┬──────────────┐
│ SLI                │ Target       │ Window         │ Error Budget│ Burn Rate    │
│                    │              │                │ (30d)       │ Alert        │
├────────────────────┼──────────────┼────────────────┼─────────────┼──────────────┤
│ Availability       │ 99.9%        │ 30-day rolling │ 43.2 min    │ >2% in 1hr   │
│ Latency (p95)      │ <500ms       │ 30-day rolling │ 0.1% budget │ >5% in 1hr   │
│ Latency (p99)      │ <2000ms      │ 30-day rolling │ 0.1% budget │ >10% in 1hr  │
│ Error rate         │ <0.1%        │ 30-day rolling │ 43.2 min    │ >1% in 15min │
└────────────────────┴──────────────┴────────────────┴─────────────┴──────────────┘

Error Budget Policy:
  - If >50% budget consumed → freeze non-critical deploys, prioritize reliability work
  - If >80% budget consumed → freeze all deploys except hotfixes
  - If budget exhausted → incident response mode, all hands on reliability
```

### SLO Tiers by Service Type
```
Critical (99.9% availability):
  - Authentication service
  - Payment processing
  - Core API endpoints
  - Production database

Standard (99.5% availability):
  - Admin dashboard
  - Analytics pipeline
  - Email/notification service
  - Search functionality

Best-effort (99.0% availability):
  - Internal tools
  - Staging environments
  - Batch processing jobs
  - Non-critical background tasks
```

## Step 6: Alerting Strategy

### Severity Tiers
```
P1 — Page immediately (24/7):
  - SLO burn rate critical (>10x in 5 minutes)
  - Service completely down (zero successful requests)
  - Data loss or security breach detected
  - Payment processing failure rate >5%
  → Route: PagerDuty/Opsgenie → phone call + SMS + push

P2 — Page during business hours:
  - SLO burn rate elevated (>2x in 1 hour)
  - Error rate sustained above threshold
  - Latency p95 above SLO for >15 minutes
  - Disk/memory utilization >85%
  → Route: PagerDuty/Opsgenie → push notification

P3 — Slack notification:
  - SLO burn rate slightly elevated (>1.5x in 6 hours)
  - Non-critical service degradation
  - Certificate expiry within 30 days
  - Dependency deprecation warning
  → Route: Slack #alerts channel

P4 — Ticket only:
  - Informational: deployment completed, backup succeeded
  - Trend warning: gradual latency increase
  - Capacity planning: approaching resource limits
  → Route: Create ticket in issue tracker
```

### Alert Fatigue Prevention Rules
```
Rules:
  1. Every alert MUST be actionable — if there's nothing to do, delete the alert
  2. Every alert MUST have a runbook link — no alert without documentation
  3. Group related alerts — don't fire 10 alerts for one root cause
  4. Use alert windows (not instantaneous) — 5-minute minimum evaluation window
  5. Auto-resolve alerts — if the condition clears, the alert resolves
  6. Review alert volume monthly — target <5 pages per on-call week
  7. Track false positive rate — target <10%, delete alerts with >30% false positive rate
  8. Deduplicate — same alert from same source within 1 hour = single notification

Anti-patterns:
  ✗ Alerting on individual errors (use error rate instead)
  ✗ Alerting on CPU >50% (use sustained >85% for >5 minutes)
  ✗ Alerting on log messages containing "error" (use structured metrics)
  ✗ Email-only alerts for P1/P2 (must page)
  ✗ Alerts without owners
```

## Step 7: Dashboard Templates

### Service Health Dashboard
```
Layout:
  Row 1: Traffic overview
    - [Timeseries] Requests per second (by status code)
    - [Stat]       Current RPS
    - [Stat]       Error rate (last 5 min)
    - [Stat]       Availability (30-day rolling)

  Row 2: Latency
    - [Timeseries] Latency percentiles (p50, p95, p99)
    - [Heatmap]    Latency distribution
    - [Stat]       p95 latency (last 5 min)

  Row 3: SLO tracking
    - [Gauge]      Error budget remaining (30-day)
    - [Timeseries] SLO burn rate
    - [Stat]       Days until budget exhaustion at current rate

  Row 4: Infrastructure
    - [Timeseries] CPU and memory utilization
    - [Timeseries] Active instances / container count
    - [Timeseries] Database connection pool usage
```

### User Experience Dashboard
```
Layout:
  Row 1: Web Vitals
    - [Timeseries] LCP by page (p75)
    - [Timeseries] INP by interaction type (p75)
    - [Stat]       CLS (p75, last 24h)

  Row 2: Mobile performance
    - [Timeseries] App startup time (Android/iOS)
    - [Timeseries] Crash-free sessions rate
    - [Stat]       ANR rate (Android)
    - [Stat]       Hang rate (iOS)

  Row 3: User flows
    - [Funnel]     Signup completion rate
    - [Funnel]     Checkout completion rate
    - [Timeseries] Feature adoption over time
```

### Business Metrics Dashboard
```
Layout:
  Row 1: Revenue
    - [Stat]       MRR / ARR
    - [Timeseries] Daily revenue
    - [Stat]       Payment success rate

  Row 2: Growth
    - [Timeseries] Daily signups
    - [Timeseries] DAU / WAU / MAU
    - [Stat]       Activation rate (7-day)

  Row 3: Cost
    - [Timeseries] Infrastructure spend by service
    - [Stat]       Cost per user
    - [Stat]       Budget remaining (month)
```

## Step 8: On-Call Integration

### PagerDuty / Opsgenie Setup
```
Configuration:
  1. Create service per critical system (API, payments, auth, database)
  2. Create escalation policy:
     - Level 1: Primary on-call (immediate)
     - Level 2: Secondary on-call (after 10 min no-ack)
     - Level 3: Engineering lead (after 20 min no-ack)
  3. Integrate alert sources:
     - Cloud Monitoring → PagerDuty Events API v2
     - Sentry → PagerDuty integration
     - Crashlytics → Cloud Functions → PagerDuty
     - Custom health checks → PagerDuty
  4. Configure notification rules per severity:
     - P1: Phone + SMS + Push + Email
     - P2: Push + Email
     - P3: Slack only (not paged)

Runbook Links:
  Every PagerDuty service MUST have a runbook URL in the service description.
  Format: https://docs.company.com/runbooks/{service-name}
  Every alert MUST include a runbook link in the alert body.

Incident Auto-Creation:
  P1/P2 alerts → auto-create incident in PagerDuty
  Incident → auto-create Slack channel (#incident-{date}-{short-desc})
  Incident → auto-post to #incidents channel with severity and summary
  Resolution → auto-create post-mortem ticket
```

### Synthetic Monitoring
```
Set up synthetic checks for critical user flows:
  - Homepage load: every 1 minute from 3 regions
  - Login flow: every 5 minutes from 2 regions
  - Checkout flow: every 5 minutes from 2 regions
  - API health endpoint: every 30 seconds from 3 regions

Tools:
  - GCP Uptime Checks (basic HTTP/HTTPS)
  - Datadog Synthetic Monitoring (browser + API tests)
  - Checkly (programmable synthetic monitoring)
```

## Step 9: Output

```
OBSERVABILITY REPORT
Service: [NAME]
Date: [TODAY]
Prepared by: [NAME]

CURRENT STATE ASSESSMENT
┌──────────────────────┬──────────────────────────────────────┐
│ Pillar               │ Status                               │
├──────────────────────┼──────────────────────────────────────┤
│ Structured Logging   │ [Not started / Partial / Complete]   │
│ Metrics              │ [Not started / Partial / Complete]   │
│ Distributed Tracing  │ [Not started / Partial / Complete]   │
│ SLO/SLI Defined      │ [Not started / Partial / Complete]   │
│ Alerting             │ [Not started / Partial / Complete]   │
│ Dashboards           │ [Not started / Partial / Complete]   │
│ On-Call Integration  │ [Not started / Partial / Complete]   │
└──────────────────────┴──────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Structured logging implementation with PII redaction
  - [ ] Correlation ID middleware
  - [ ] Custom metrics per service (RED + business)
  - [ ] Distributed tracing setup (OpenTelemetry or platform-native)
  - [ ] Platform-specific monitoring (Crashlytics, Sentry, Web Vitals)
  - [ ] SLO/SLI definitions with error budgets
  - [ ] Alerting rules with severity tiers and runbook links
  - [ ] Dashboard templates (service health, UX, business)
  - [ ] PagerDuty/Opsgenie integration with escalation policies
  - [ ] Synthetic monitoring for critical flows
```

Cross-references: Use `/incident-response` for runbook templates and post-mortems. Use `/performance-review` for performance budgets and load testing. Use `/infrastructure-scaffold` for Cloud Monitoring and alerting policy setup. Use `/ci-cd-pipeline` for deploying observability configs alongside application code.
