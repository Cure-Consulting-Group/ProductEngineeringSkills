---
name: incident-response
description: "Create incident runbooks, severity classification, on-call procedures, post-mortems, and escalation paths"
when_to_use: "Use when creating incident runbooks, severity classification, on-call procedures, or post-mortem templates. NOT for DR planning (use disaster-recovery)."
argument-hint: "[incident-or-system]"
context: fork
---

# Incident Response

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

Structured incident response framework for production systems. Use during active incidents, when building on-call procedures, and when conducting post-mortems. Covers Firebase, mobile, web, and API infrastructure.

## Step 1: Classify the Incident Type

| Type | Indicators | Initial Response |
|------|-----------|-----------------|
| Production Outage | Service unreachable, 5xx errors, health checks failing | Page on-call, open incident channel, start status page update |
| Security Breach | Unauthorized access, data exfiltration, compromised credentials | Page security lead, isolate affected systems, preserve logs |
| Data Loss | Missing records, corrupted data, failed backups, replication lag | Stop writes to affected system, assess backup state, page DBA/infra |
| Performance Degradation | Latency spikes, timeout increases, queue backlog, high error rate | Check dashboards, identify bottleneck, consider rollback |
| Third-Party Failure | Vendor API errors, DNS issues, CDN outage, payment processor down | Confirm vendor status page, activate fallback, notify customers |

## Step 2: Gather Context

1. **Affected system** -- which services, endpoints, or platforms are impacted (Firebase, Cloud Functions, mobile apps, web app)?
2. **Severity** -- how many users are affected and what is the business impact (revenue, data integrity, security)?
3. **Timeline** -- when did the issue start, when was it detected, what changed recently (deploys, config changes, traffic spikes)?
4. **Users impacted** -- total affected users, percentage of traffic, geographic scope, specific customer segments?
5. **Current state** -- is the issue ongoing, intermittent, or resolved? Is the blast radius growing?
6. **Recent changes** -- last deployment timestamp, feature flag changes, infrastructure modifications, dependency updates?

## Step 3: Severity Classification Framework

### SEV1 -- Critical (Complete Outage)
```
Impact:        Service fully down, data loss active, security breach confirmed
Users:         >50% of users affected OR any data breach
Examples:      Firebase project unreachable, production database corruption,
               leaked credentials, payment processing completely down
Response time: Immediately (within 5 minutes of detection)
Escalation:    Engineering lead + CTO + all available engineers
Communication: Status page updated within 15 minutes, customer email within 1 hour
Cadence:       Updates every 30 minutes until resolved
Bridge:        Open dedicated Slack channel (#incident-YYYY-MM-DD-short-desc)
               and Google Meet / Zoom war room
```

### SEV2 -- High (Major Degradation)
```
Impact:        Core feature broken, significant performance degradation
Users:         10-50% of users affected OR key business flow broken
Examples:      Auth failures for subset of users, Cloud Functions cold start
               timeouts, mobile app crash loop on specific OS version,
               Stripe webhook failures
Response time: Within 15 minutes of detection
Escalation:    Engineering lead + team owning affected service
Communication: Status page updated within 30 minutes, customer comm if >1 hour
Cadence:       Updates every 1 hour until resolved
Bridge:        Slack incident channel
```

### SEV3 -- Medium (Minor Degradation)
```
Impact:        Non-critical feature broken, workaround available
Users:         <10% of users affected, no revenue impact
Examples:      Analytics pipeline delayed, non-critical API slow,
               push notifications delayed, image upload failures on one platform
Response time: Within 1 hour during business hours
Escalation:    Team owning affected service
Communication: Internal Slack update, no customer communication unless asked
Cadence:       Updates every 4 hours until resolved
Bridge:        Thread in team Slack channel
```

### SEV4 -- Low (Minor Issue)
```
Impact:        Cosmetic issue, minor bug, non-user-facing system degraded
Users:         Minimal or no user impact
Examples:      CI/CD pipeline slow, staging environment down,
               log ingestion delayed, non-critical cron job failed
Response time: Next business day
Escalation:    Add to sprint backlog
Communication: Internal ticket only
Cadence:       Standard ticket updates
Bridge:        None -- track in issue tracker
```

### Escalation Paths

```
SEV1 Flow:
  Detector → On-Call Engineer (5 min) → Engineering Lead (10 min)
    → CTO (15 min) → All Hands if needed (30 min)

SEV2 Flow:
  Detector → On-Call Engineer (15 min) → Team Lead (30 min)
    → Engineering Lead if not resolved in 1 hour

SEV3 Flow:
  Detector → Team Channel → Team Lead triages within 1 hour

SEV4 Flow:
  Detector → Create ticket → Prioritize in next sprint planning
```

## Step 4: Incident Runbook Template

See [reference/details.md](reference/details.md) (section “Step 4: Incident Runbook Template”) for full detail.

## Step 5: On-Call Procedures

### Rotation Schedule
```
Structure:
  - Primary on-call: 1 week rotation (Monday 10AM → Monday 10AM)
  - Secondary on-call: backup, escalation target
  - Minimum 2 people in rotation per team
  - No back-to-back weeks
  - Handoff meeting: 15 min at rotation start (review open issues, recent deploys)

Expectations:
  - Acknowledge alerts within 5 minutes (SEV1/SEV2)
  - Acknowledge alerts within 15 minutes (SEV3)
  - Laptop and internet access required (no airplane mode)
  - Response SLA: 15 minutes to begin investigation
  - If unreachable after 10 minutes → auto-escalate to secondary
```

### Escalation Matrix
```
┌─────────────────────┬───────────────────┬──────────────────┬──────────────┐
│ System              │ Primary           │ Secondary        │ Exec Sponsor │
├─────────────────────┼───────────────────┼──────────────────┼──────────────┤
│ Firebase / GCP      │ Platform Engineer │ Engineering Lead │ CTO          │
│ Mobile (Android)    │ Android Lead      │ Mobile Team      │ CTO          │
│ Mobile (iOS)        │ iOS Lead          │ Mobile Team      │ CTO          │
│ Web / Next.js       │ Frontend Lead     │ Full-Stack Team  │ CTO          │
│ API / Cloud Funcs   │ Backend Lead      │ Platform Engineer│ CTO          │
│ Payments / Stripe   │ Backend Lead      │ Engineering Lead │ CEO          │
│ Auth / Security     │ Security Lead     │ Engineering Lead │ CTO          │
│ Data / Analytics    │ Data Engineer     │ Platform Engineer│ CTO          │
└─────────────────────┴───────────────────┴──────────────────┴──────────────┘
```

### On-Call Tooling Checklist
```
Required access (verify during onboarding):
  - [ ] PagerDuty / Opsgenie account with push notifications enabled
  - [ ] GCP Console access (Viewer minimum, Editor for production)
  - [ ] Firebase Console access (all projects)
  - [ ] Slack desktop + mobile installed, #incidents channel joined
  - [ ] GitHub access to all production repositories
  - [ ] CI/CD pipeline access (GitHub Actions / Cloud Build)
  - [ ] Status page admin access (Statuspage.io / Instatus)
  - [ ] Sentry / Crashlytics access
  - [ ] Datadog / Grafana / Cloud Monitoring dashboards bookmarked
  - [ ] VPN configured and tested
  - [ ] Production database read access (Firestore, Cloud SQL)
  - [ ] Stripe Dashboard access (for payment incidents)
  - [ ] 1Password / secrets vault access for emergency credentials

Required bookmarks:
  - Production dashboards (latency, error rate, throughput)
  - Deployment pipeline status page
  - Firebase Console → all production projects
  - GCP Console → Error Reporting, Cloud Logging
  - Runbook repository (this document)
  - Vendor status pages (Firebase, GCP, Stripe, Vercel, Cloudflare)
```

## Step 6: Communication Templates

### Internal Status Update
```
Subject: [SEV-X] [System Name] — [Status: Investigating/Mitigated/Resolved]

Current Status: [Investigating / Identified / Mitigated / Resolved]
Started: [YYYY-MM-DD HH:MM UTC]
Duration: [X hours Y minutes]
Impact: [Description of user-facing impact]
Affected: [Systems, users, regions]

What happened:
  [Brief factual description of the incident]

What we've done:
  [Actions taken so far]

Next steps:
  [What we're doing next, ETA if known]

Next update: [Time of next scheduled update]
Incident Commander: [Name]
```

### Customer Communication -- Active Incident
```
Subject: Service Disruption — [Feature/System Name]

We're currently experiencing issues with [feature/system] that may affect
your ability to [specific user action].

Our engineering team identified the issue at [time] and is actively
working on a resolution.

What's affected:
  - [Specific feature or workflow]

What's NOT affected:
  - [Reassure about unaffected systems]

We'll provide an update within [timeframe]. For urgent issues, contact
[support channel].

We apologize for the inconvenience.
```

### Customer Communication -- Resolved
```
Subject: Resolved — [Feature/System Name] Service Disruption

The issue affecting [feature/system] has been resolved as of [time UTC].

What happened:
  [Brief, non-technical explanation]

Duration: [start time] to [end time] ([total duration])

Impact:
  [What users experienced]

What we're doing to prevent recurrence:
  - [Action item 1]
  - [Action item 2]

If you continue experiencing issues, please contact [support channel].

We apologize for the disruption and thank you for your patience.
```

### Stakeholder Briefing (for CEO/Leadership)
```
Subject: Incident Briefing — [SEV-X] [System] — [Date]

TLDR: [One sentence summary. Include revenue impact if applicable.]

Timeline:
  [HH:MM] Issue began
  [HH:MM] Detected by [method]
  [HH:MM] Engineering engaged
  [HH:MM] Root cause identified
  [HH:MM] Mitigated
  [HH:MM] Fully resolved

Business Impact:
  - Users affected: [number/percentage]
  - Revenue impact: [estimated $ or "none"]
  - Data impact: [any data loss or breach — yes/no]
  - SLA impact: [any SLA violations — yes/no]

Root Cause: [One paragraph, non-technical]

Prevention: [Top 2-3 action items with owners and deadlines]
```

## Step 7: Post-Mortem Template

```
POST-MORTEM: [Incident Title]
Date: [YYYY-MM-DD]
Severity: [SEV-1/2/3/4]
Author: [Name]
Status: [Draft / In Review / Final]

SUMMARY
  [2-3 sentence description of what happened, impact, and resolution]

TIMELINE (all times UTC)
  [HH:MM] — [Event: what happened]
  [HH:MM] — [Event: alert fired / user report]
  [HH:MM] — [Event: engineer paged]
  [HH:MM] — [Event: investigation started]
  [HH:MM] — [Event: root cause identified]
  [HH:MM] — [Event: mitigation applied]
  [HH:MM] — [Event: incident resolved]
  [HH:MM] — [Event: monitoring confirmed stable]

DETECTION
  How was the incident detected? [Alert / Customer report / Internal testing]
  Time to detect (TTD): [duration from start to detection]
  Could we have detected it faster? [Yes/No — explain]

ROOT CAUSE
  [Technical explanation of what caused the incident. Be specific.
   Include code references, configuration errors, or infrastructure
   issues. This is NOT a blame statement — focus on systems, not people.]

CONTRIBUTING FACTORS
  - [Factor 1: e.g., missing monitoring on the affected endpoint]
  - [Factor 2: e.g., deploy happened Friday afternoon with no staged rollout]
  - [Factor 3: e.g., no integration test for the affected code path]

IMPACT
  Duration: [total time from start to resolution]
  Users affected: [number and percentage]
  Revenue impact: [$X or estimated]
  Data impact: [any data loss, corruption, or exposure]
  SLA impact: [any SLA breaches, credits owed]

WHAT WENT WELL
  - [Thing that worked: e.g., alerting fired within 2 minutes]
  - [Thing that worked: e.g., rollback process was smooth]
  - [Thing that worked: e.g., team coordination in Slack was effective]

WHAT WENT WRONG
  - [Problem: e.g., no runbook for this failure mode]
  - [Problem: e.g., escalation took 30 minutes because pager was misconfigured]
  - [Problem: e.g., customer communication was delayed by 2 hours]

ACTION ITEMS
  ┌────┬──────────────────────────────────────┬──────────┬────────────┬──────────┐
  │ #  │ Action                               │ Priority │ Owner      │ Due Date │
  ├────┼──────────────────────────────────────┼──────────┼────────────┼──────────┤
  │ 1  │ [Prevent: fix root cause]            │ P0       │ [Name]     │ [Date]   │
  │ 2  │ [Detect: add monitoring/alert]       │ P1       │ [Name]     │ [Date]   │
  │ 3  │ [Mitigate: improve rollback speed]   │ P1       │ [Name]     │ [Date]   │
  │ 4  │ [Process: update runbook]            │ P2       │ [Name]     │ [Date]   │
  │ 5  │ [Test: add integration/load test]    │ P2       │ [Name]     │ [Date]   │
  └────┴──────────────────────────────────────┴──────────┴────────────┴──────────┘

  Action item categories (every post-mortem should have at least one of each):
    - Prevent: eliminate the root cause
    - Detect: catch it faster next time
    - Mitigate: reduce blast radius or recovery time
    - Process: improve human response procedures

LESSONS LEARNED
  [What did this incident teach us about our systems, processes, or assumptions?
   This section should inform architectural decisions and team practices going forward.]

POST-MORTEM REVIEW
  Reviewed by: [Names]
  Review date: [Date]
  Follow-up date for action items: [Date — typically 2 weeks out]
```

### Post-Mortem Process
```
Rules:
  - Blameless: focus on systems and processes, not individuals
  - Required for all SEV1 and SEV2 incidents
  - Optional but encouraged for SEV3
  - Draft due within 48 hours of resolution
  - Review meeting within 5 business days
  - Action items tracked in issue tracker with due dates
  - Action item completion reviewed in engineering standup
```

## Step 8: Incident Metrics

### Key Metrics to Track

```
MTTD (Mean Time to Detect):
  Definition: Time from incident start to first detection (alert or human)
  Target: <5 minutes for SEV1, <15 minutes for SEV2
  Measure: Timestamp of first symptom → timestamp of first alert/report
  Improve: Better monitoring, tighter alert thresholds, synthetic monitoring

MTTR (Mean Time to Resolve):
  Definition: Time from detection to full resolution
  Target: <1 hour for SEV1, <4 hours for SEV2
  Measure: Timestamp of detection → timestamp of confirmed resolution
  Improve: Better runbooks, faster rollbacks, automated remediation

MTTA (Mean Time to Acknowledge):
  Definition: Time from alert firing to engineer acknowledging
  Target: <5 minutes for SEV1/SEV2
  Measure: PagerDuty/Opsgenie acknowledgment timestamps
  Improve: Pager configuration, on-call hygiene, escalation policies

MTBF (Mean Time Between Failures):
  Definition: Average time between incidents for a given system
  Target: Increasing quarter over quarter
  Measure: Track per-system, per-severity
  Improve: Address root causes from post-mortems, invest in reliability

Incident Frequency by Severity:
  Track monthly:
    - Total incidents per severity level
    - Incidents per system/service
    - Incidents by root cause category
    - Repeat incidents (same root cause)
  Target: Decreasing trend, zero repeat incidents
```

### Metrics Dashboard
```
Recommended tooling:
  - Datadog / Grafana for real-time operational dashboards
  - PagerDuty Analytics for on-call and response metrics
  - Google Sheets or Notion for monthly incident tracking
  - BigQuery for long-term incident data analysis

Monthly review checklist:
  - [ ] Total incidents by severity (trend vs. prior months)
  - [ ] MTTD, MTTA, MTTR averages by severity
  - [ ] Top 3 systems by incident count
  - [ ] Open action items from post-mortems (% completion)
  - [ ] On-call load distribution (pages per person)
  - [ ] False positive alert rate (target: <10%)
  - [ ] Repeat incident rate (target: 0%)

Quarterly reliability report:
  - MTBF trend per critical system
  - Incident cost estimate (engineer hours * hourly cost + revenue impact)
  - SLA compliance percentage
  - Top action item themes (monitoring, testing, process, architecture)
  - Reliability investment recommendations for next quarter
```

### Incident Report Output

```
INCIDENT RESPONSE REPORT
System: [NAME]
Date: [TODAY]
Prepared by: [NAME]

INCIDENT SUMMARY
┌──────────────────────┬────────────────────────────────────┐
│ Field                │ Value                              │
├──────────────────────┼────────────────────────────────────┤
│ Incident Type        │ [From Step 1 classification]       │
│ Severity             │ [SEV-1/2/3/4]                      │
│ Status               │ [Active / Mitigated / Resolved]    │
│ Duration             │ [HH:MM]                            │
│ Users Affected       │ [Number / Percentage]              │
│ Revenue Impact       │ [$X / None]                        │
│ Root Cause           │ [Brief description]                │
│ Resolution           │ [Brief description]                │
└──────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Severity classification completed
  - [ ] Incident runbook followed / created
  - [ ] Communication sent (internal + external as needed)
  - [ ] Post-mortem drafted (required for SEV1/SEV2)
  - [ ] Action items created with owners and due dates
  - [ ] Metrics recorded
  - [ ] On-call procedures updated if gaps found
```

## Code Generation (Required)

Generate incident management artifacts using Write:

1. **Runbook template**: `docs/runbooks/template.md` with the standard Cure format
2. **Post-mortem template**: `docs/post-mortems/template.md`
3. **PagerDuty webhook**: `functions/src/incident-webhook.ts` (Cloud Function that creates incident records)
4. **Slack notification**: Generate Slack Block Kit JSON for incident announcements
5. **Status page update script**: `scripts/update-status.sh`

Before generating, Glob for existing runbooks and post-mortems to match format.
