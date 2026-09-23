# Observability

Outcome: a service that can't fail silently — structured logs with PII redaction, RED metrics,
traces with correlation IDs, SLOs with error budgets, and burn-rate alerts that each link a
runbook. Done when every alert is actionable and owned, and the maturity table in Step 8 is filled
in with evidence. Cure rule: no service goes to production without this baseline.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Stack: !`head -30 package.json 2>/dev/null || head -30 app/build.gradle.kts 2>/dev/null || echo "(no package.json / gradle)"`
- Monitoring SDKs: !`grep -rhoE "@sentry/[a-z-]+|[d]d-trace|@opentelemetry/[a-z-]+|firebase-crashlytics|pino|winston" --include=package.json --include=*.gradle.kts --include=Podfile . 2>/dev/null | sort -u | head -12 || echo "(none found)"`

## Step 1: Classify the Observability Need

| Need | Scope | Start at |
|------|-------|---------------|
| Greenfield setup | Full stack: logs, metrics, traces, SLOs, alerts, dashboards | Step 3 |
| Add monitoring to existing | Baseline scan, then fill the gaps | Baseline scan, then Step 3 |
| Incident-driven improvement | Targeted fixes for gaps a post-mortem found | The relevant step only |
| SLO definition | Reliability targets and error budgets | Step 5 |
| Alert tuning | Noise, fatigue, missed pages | Step 6 |

## Step 2: Gather Context

Ask only for what is missing: platforms (Android, iOS, Web, Functions, Cloud Run), current
tooling, scale (RPS, DAU), compliance (HIPAA → no PHI in logs; GDPR → PII redaction; data
residency), budget (Datadog vs GCP-native vs Grafana), on-call maturity, and recent blind spots.

**Baseline scan** (existing services): search the code for logging libraries (`winston|pino|bunyan|timber|os_log|slog`)
and `console.log` counts, monitoring configs (`sentry*`, `datadog*`, `prometheus*`), tracing
(`opentelemetry|dd-trace`), alert configs, and health endpoints (`/health|/healthz|/ready`).
Report maturity before recommending.

## Step 3: Logs, Metrics, Traces

Cure defaults: JSON logs with `service`, `version`, `trace_id`, `user_id` (hashed), redaction
before emit; RED metrics (rate, errors, duration) per endpoint plus business counters;
OpenTelemetry for traces (JS SDK 2.x API) with W3C `traceparent` propagation. Read
[reference/details.md](reference/details.md) (section "Step 3") when writing the log schema,
redaction code, correlation middleware, metric types, or OpenTelemetry setup.

## Step 4: Platform-Specific Setup

Android: Crashlytics + Firebase Performance, ANR tracking. iOS: Crashlytics + MetricKit +
`os_signpost`. Web: Sentry (`@sentry/nextjs`) + `useReportWebVitals` (INP, not FID). Functions:
`firebase-functions/v2` logger to Cloud Logging, Cloud Trace. Read
[reference/details.md](reference/details.md) (section "Step 4") when writing SDK initialization
code for any of these platforms.

## Step 5: SLOs and Error Budgets

One convention for all Cure services, so availability and error rate never disagree:

- **Good event** = response that is not 5xx and not a timeout, served within the latency threshold
  when the SLI is latency. 4xx are client errors and count as good (except 429 caused by our own
  throttling, which counts as bad).
- **Availability SLI** = good requests / valid requests. **Error rate** = 1 − availability.
- Measure on a 30-day rolling window.

| Tier | Examples | Availability | Latency (p95) | 30-day budget |
|---|---|---|---|---|
| Critical | auth, payments, core API | 99.9% | < 500 ms | 43.2 min |
| Standard | admin, analytics, notifications, search | 99.5% | < 1 s | 3.6 h |
| Best-effort | internal tools, staging, batch | 99.0% | — | 7.2 h |

Error-budget policy: >50% consumed → freeze non-critical deploys; >80% → hotfixes only;
exhausted → reliability work is the sprint.

## Step 6: Alerting

Use the Google SRE Workbook multiwindow, multi-burn-rate alerts (sre.google/workbook/alerting-on-slos)
for every SLO. An alert fires only when both the long and short windows exceed the burn rate:

| Budget consumed | Long window | Short window | Burn rate | Action |
|---|---|---|---|---|
| 2% | 1 h | 5 min | 14.4× | Page (P1) |
| 5% | 6 h | 30 min | 6× | Page (P2) |
| 10% | 3 d | 6 h | 1× | Ticket (P3) |

Also page on: zero successful requests, detected data loss or security breach, payment failure
rate > 5% over 10 min. Route P1/P2 through PagerDuty/Opsgenie (phone + push), P3 to Slack, P4 to
the tracker.

Alert hygiene, because pages that don't need action train people to ignore pages:
- Every alert is actionable and has an owner and a runbook link; delete the ones that aren't.
- Alert on rates and SLO burn, never on single errors, raw CPU > 50%, or log lines containing "error".
- Evaluate over ≥ 5-minute windows, auto-resolve, and group by root cause.
- Targets: < 5 pages per on-call week; delete alerts with > 30% false positives.

## Step 7: Dashboards and On-Call

Three dashboards per product:
- **Service health:** RPS by status class, error rate, availability (30-day), latency p50/p95/p99, error budget remaining and burn rate, instances, DB pool.
- **User experience:** LCP/INP/CLS at p75, app start time, crash-free sessions, ANR (Android) and hang rate (iOS), signup and checkout funnels.
- **Business:** MRR, payment success rate, signups, DAU/WAU/MAU, cost per user.

On-call: one PagerDuty/Opsgenie service per critical system; escalation primary → secondary
(10 min no-ack) → engineering lead (20 min). Synthetic checks for login, checkout, and health
endpoints from ≥ 2 regions (GCP Uptime Checks or Checkly).

## Step 8: Output

A maturity table (logging, metrics, tracing, SLOs, alerting, dashboards, on-call: not started /
partial / complete, with the evidence), the SLO table for each service, the alert policy list,
and the ranked gaps. Match length to the need; no filler sections.

## Code/Artifact Generation

Applies only when Step 1 classified the request as greenfield setup, add-monitoring, or
incident-driven improvement. SLO definition and alert tuning produce the Step 5/6 tables.
Write the files the gaps call for — typically the logger with redaction, correlation-ID
middleware, OpenTelemetry init, platform SDK init, and alert policies as code — and nothing else.

## Cross-References

`incident-response` (runbooks, post-mortems), `performance-review` (performance budgets, load
tests), `infrastructure-scaffold` (Cloud Monitoring policies as code), `dora-metrics` (delivery
metrics and MTTR definition).
