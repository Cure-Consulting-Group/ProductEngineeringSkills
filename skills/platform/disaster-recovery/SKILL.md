---
name: disaster-recovery
description: "Designs disaster recovery plans: RTO/RPO tiers, Firestore and Cloud SQL backups, failover, DR drills. Use when planning backups, multi-region failover, or a DR test before launch or an audit."
when_to_use: "NOT for handling a live incident (use incident-response) or chaos experiments (use chaos-engineering)."
argument-hint: "[project-or-service]"
context: fork
metadata:
  verified: 2026-09-23
---

# Disaster Recovery

DR plans for Cure's Firebase/GCP stacks. **Done when** every production service has a tier, an
RTO/RPO, a backup (or "rebuild from source") strategy with a tested restore, a failover path, and a
drill date. Every production system gets this before launch. Match length to the need; no filler
sections or restated summaries.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Firebase config: `(cat firebase.json 2>/dev/null || echo "(no firebase.json)") | head -25`
- Firebase projects: `(cat .firebaserc 2>/dev/null || echo "(no .firebaserc)") | head -10`
- Existing DR assets: `(ls scripts/ docs/ 2>/dev/null | grep -iE 'backup|restore|dr|failover|runbook' || echo "(none)") | head -10`

## Step 1: Classify

| Need | Output |
|---|---|
| Greenfield DR plan | Tier matrix, backup config, failover design, runbooks, drill schedule |
| DR plan review | Findings against the current architecture — gaps with severity; no new files unless asked |
| Failover architecture | Design + config for the named services |
| DR test | Drill plan (tabletop / staging failover / production) with success criteria |
| Compliance-driven DR (SOC 2, HIPAA) | Plan plus evidence list; see `compliance-architect` for the control mapping |

## Step 2: Gather Context

Ask only what the repo doesn't show: production services and dependencies, data stores and volume,
promised SLA and contractual penalties, compliance scope, DR budget (hot/warm/cold), who executes
DR, and the date of the last successful restore test.

## Step 3: Tiers and Targets (Cure defaults)

| Tier | Examples | RTO | RPO | Strategy |
|---|---|---|---|---|
| 1 Critical | Auth, payments, core API, primary DB | <15 min | <5 min | Multi-region data, multi-region compute behind a global LB, automated failover |
| 2 Important | Notifications, search, uploads, analytics ingest | <1 h | <1 h | Regional redundancy, automated backups, semi-automated failover |
| 3 Standard | Admin, reporting, CI/CD, logs | <4 h | <24 h | Backup-and-restore or redeploy from source |

Typical placement: Firebase Auth T1 (Google-managed, RPO 0) · Firestore T1 (multi-region) · Cloud
Functions/Cloud Run API T1 (stateless — RPO N/A) · Stripe T1 (webhook retries + idempotency) ·
Cloud SQL T2 (regional HA) · Cloud Storage T2 (multi-region bucket) · analytics T3 (rebuild).
A region outage and a bad write are different disasters: replication covers the first, only
backups/PITR cover the second — every T1 data store needs both.

## Step 4: Backups

### Firestore (native backups + PITR — not export cron jobs)
```bash
# Point-in-time recovery: 7-day window, minute granularity. Off by default; billed as storage.
gcloud firestore databases update --database='(default)' --enable-pitr

# Scheduled backups: at most one daily and one weekly schedule per database; retention up to 14 weeks.
gcloud firestore backups schedules create --database='(default)' --recurrence=daily --retention=7d
gcloud firestore backups schedules create --database='(default)' --recurrence=weekly --day-of-week=SUN --retention=14w
```
Restores always land in a **new database** (`gcloud firestore databases restore` from a backup, or
`gcloud firestore databases clone --snapshot-time=…` from PITR) — plan how the app is repointed or how
documents are copied back. For retention beyond 14 weeks (compliance), add a managed export to a
locked bucket (`gcloud firestore export gs://BUCKET/…`, optionally with `--snapshot-time` from PITR).

### Cloud SQL
```bash
gcloud sql instances patch INSTANCE --availability-type=REGIONAL \
  --backup-start-time=02:00 --enable-point-in-time-recovery \
  --retained-backups-count=30 --retained-transaction-log-days=7
gcloud sql backups create --instance=INSTANCE --description="pre-migration"   # before risky changes
```

### Cloud Storage
```bash
gcloud storage buckets update gs://PROJECT-prod-uploads --versioning
gcloud storage buckets update gs://PROJECT-backups --retention-period=90d --lifecycle-file=lifecycle.json
```
Use `gcloud storage`, not `gsutil`. Lifecycle: Nearline at 30 d, Coldline at 90 d, delete
noncurrent versions at 365 d. A retention lock is irreversible — confirm with the client first.

### Restore verification (the part teams skip)
Daily: alert on backup-job failure. Monthly: restore to staging and run integrity checks (record
counts, sample queries, app smoke test). Quarterly: timed drill proving RTO. A backup never restored
is an assumption, not a control.

## Step 5: Failover

- **Firestore multi-region** (`nam5`, `eur3`) is strongly consistent across regions with automatic
  failover — no app action. Regional databases are cheaper and have no cross-region failover; pick per
  tier, and note the location is fixed at creation.
- **Cloud Run / Functions (v2)**: deploy to two regions behind a **global external Application Load
  Balancer with serverless NEGs**. Serverless NEGs don't support LB health checks — enable Cloud Run
  service health (readiness probes) or outlier detection so the LB drains a failing region. Don't
  CNAME a custom domain at `*.cloudfunctions.net` or `*.run.app` hosts: the Host header and TLS
  certificate won't match; the LB (or Firebase Hosting rewrites) fronts the services.
- **Cloud SQL**: `REGIONAL` HA fails over across zones automatically; for region loss, keep a
  cross-region read replica and promote it (`gcloud sql instances promote-replica`).
- **Memorystore Standard tier** replicates to another zone and fails over automatically within the
  region; for region loss treat Redis as a rebuildable cache.
- **Firebase Hosting / Vercel**: global CDN; DR is "redeploy the last good version" (see
  `ci-cd-pipeline` rollback table).

## Step 6: Runbooks

Read [reference/details.md](reference/details.md) (section "Step 6: DR Runbooks") whenever the output
includes runbooks — it holds the region-failure and data-corruption runbooks (with the Firestore
clone/restore commands) and the communication cadence. Adapt service names, regions, and owners to
the project; don't paste them unedited.

## Step 7: Drills

| Cadence | Format | Pass criteria |
|---|---|---|
| Quarterly | 60-min tabletop (e.g. "someone deleted `users`", "us-central1 is down", "Stripe webhook secret leaked") | Gaps logged with owners and dates |
| Twice a year | Staging failover following the runbook, timed | T1 RTO/RPO met; no undocumented steps |
| Yearly (mature teams) | Production failover in the lowest-traffic window, CTO sign-off, customers notified | Measured RTO/RPO; abort and treat as a real incident on unexpected customer impact |

Production drills are chaos experiments — design them with the `chaos-engineering` skill.

## Step 8: Business Continuity

Read the "Business continuity" section of [reference/details.md](reference/details.md) when the plan
must cover people and tooling (war-room channels, alternate tools, vendor contacts) — typically
compliance-driven DR or a client BCP request.

## Output

A DR plan: summary (plan type, services covered, T1 RTO/RPO, backup strategy, failover type, last and
next drill, compliance alignment), the tier matrix, backup and failover config, runbooks, drill
schedule, and open gaps with owners.

## Code/Artifact Generation

Applies only when Step 1 classified the request as a greenfield plan, failover architecture, or DR
test. Write what that classification needs, adapting to scripts already in the repo:

- Greenfield → `docs/disaster-recovery.md` (the plan), `scripts/dr/enable-firestore-backups.sh`
  (PITR + schedules above), restore script(s) for each data store.
- Failover architecture → the LB/NEG setup script or Terraform for the named services.
- DR test → `docs/dr-drill-<date>.md` with scenario, steps, and pass criteria.

A plan review returns findings only.

## Cross-References

- `incident-response` — handling the live incident a disaster starts as
- `infrastructure-scaffold` — base Firebase/GCP configuration
- `ci-cd-pipeline` — deploy rollback per platform
- `security-review` — credential-leak scenarios
