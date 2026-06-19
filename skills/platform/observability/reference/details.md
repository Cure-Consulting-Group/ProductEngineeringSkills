# observability: detailed reference

> Reference material for the `observability` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 3: Three Pillars Framework -- Logs, Metrics, Traces
- Step 4: Platform-Specific Setup

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
