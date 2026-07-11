---
name: observability
description: "Set up observability stacks — structured logging, distributed tracing, alerting, SLO/SLI definition, and dashboards with Crashlytics, Sentry, or Datadog"
when_to_use: "Use when setting up structured logging, distributed tracing, alerting, SLO/SLI definition, or dashboards with Crashlytics, Sentry, or Datadog."
argument-hint: "[project-or-service]"
context: fork
---

# Observability

Production observability framework covering the three pillars — logs, metrics, and traces — across all Cure Consulting Group platforms. Every production service ships with structured logging, health metrics, distributed tracing, SLO definitions, and actionable alerts. No service goes to production without observability.

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

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

See [reference/details.md](reference/details.md) (section “Step 3: Three Pillars Framework -- Logs, Metrics, Traces”) for full detail.

## Step 4: Platform-Specific Setup

See [reference/details.md](reference/details.md) (section “Step 4: Platform-Specific Setup”) for full detail.

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
