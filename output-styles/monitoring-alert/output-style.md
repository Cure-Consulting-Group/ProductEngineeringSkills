---
name: monitoring-alert
description: Output style for monitoring and alerting configurations — SLO/SLI definitions, alert rules, dashboard layouts, and escalation policies.
---

# Monitoring & Alert Output Style

When generating monitoring configurations, follow this format:

## Structure

```
# Monitoring: {Service/Feature Name}

## SLOs (Service Level Objectives)

| SLO | Target | Window | Burn Rate Alert |
|-----|--------|--------|-----------------|
| Availability | 99.9% | 30 days | >1% error budget consumed in 1h |
| Latency (p99) | <500ms | 30 days | >2% requests above threshold |
| Throughput | >100 rps | 30 days | <50 rps sustained for 5m |

## SLIs (Service Level Indicators)

| SLI | Metric | Source | Formula |
|-----|--------|--------|---------|
| Availability | http_requests_total | Prometheus | 1 - (5xx / total) |
| Latency | http_request_duration_seconds | Prometheus | histogram_quantile(0.99, ...) |

## Alert Rules

### Critical (Pages On-Call)
| Alert | Condition | Duration | Action |
|-------|-----------|----------|--------|
| HighErrorRate | error_rate > 5% | 5m | Page on-call, check deployments |
| ServiceDown | up == 0 | 2m | Page on-call, check infra |

### Warning (Slack Notification)
| Alert | Condition | Duration | Action |
|-------|-----------|----------|--------|
| ElevatedLatency | p99 > 1s | 15m | Investigate, check DB |
| HighMemory | memory_usage > 85% | 10m | Check for leaks |

### Info (Dashboard Only)
| Alert | Condition | Notes |
|-------|-----------|-------|
| DeploymentDetected | version changed | Track deploy frequency |

## Dashboard Layout

### Row 1: Golden Signals
- [Panel] Request Rate (rps) — timeseries
- [Panel] Error Rate (%) — timeseries with threshold line
- [Panel] Latency (p50, p95, p99) — timeseries
- [Panel] Saturation (CPU, Memory) — gauge

### Row 2: Business Metrics
- [Panel] Active Users — stat
- [Panel] Transactions/min — timeseries
- [Panel] Revenue Impact — stat

### Row 3: Dependencies
- [Panel] Database query time — timeseries
- [Panel] External API latency — timeseries
- [Panel] Cache hit rate — gauge

## Escalation Policy
| Severity | Response Time | Notify | Escalate After |
|----------|---------------|--------|----------------|
| Critical | 5 min | PagerDuty on-call | 15 min → engineering lead |
| Warning | 30 min | Slack #alerts | 2 hours → on-call |
| Info | Next business day | Dashboard only | N/A |
```

## Rules
- Every alert must have a clear action — no alert without a response procedure
- Use burn rate alerts for SLO-based alerting — not static thresholds alone
- Dashboard panels follow the RED method (Rate, Errors, Duration) or USE method (Utilization, Saturation, Errors)
- Alert thresholds tuned to minimize false positives — start loose, tighten based on data
- Include "last deploy" annotation on all timeseries panels
