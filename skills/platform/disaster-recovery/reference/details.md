# disaster-recovery: detailed reference

> Reference material for the `disaster-recovery` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 6: DR Runbooks (region failure, data corruption, communication plan)
- Business continuity (team comms, alternate work procedures, vendor contacts)

## Step 6: DR Runbooks

### Runbook: Complete Region Failure

```
DISASTER RECOVERY RUNBOOK: Region Failure
Trigger: Primary region (us-central1) is unreachable for >5 minutes
Severity: SEV1
Estimated recovery time: 15-30 minutes

STEP 1: CONFIRM THE OUTAGE (2 minutes)
  - Check GCP Status Dashboard: https://status.cloud.google.com/
  - Verify from multiple network locations (not just your office)
  - Confirm via Cloud Monitoring that the region is down, not just one service
  - Open incident channel: #incident-YYYY-MM-DD-region-failure

STEP 2: ACTIVATE FAILOVER (5 minutes)
  - Global load balancer (Cure default): confirm traffic has shifted to the healthy region's
    serverless NEG (Cloud Run service health / outlier detection) — no DNS change needed
  - DNS-failover setups only: switch the record to the secondary LB IP, flush CDN cache
  - Cloud SQL: Promote read replica to primary
    gcloud sql instances failover INSTANCE_NAME --project=PROJECT_ID
  - Cloud Run: Verify us-east1 service is healthy
    gcloud run services describe PROJECT_NAME-api --region=us-east1
  - Firebase: Firestore multi-region continues operating (no action needed)

STEP 3: VERIFY FAILOVER (5 minutes)
  - Run smoke tests against failover endpoints
  - Check error rates in Cloud Monitoring
  - Verify customer-facing flows (auth, core features, payments)
  - Monitor for data consistency issues

STEP 4: COMMUNICATE (concurrent with steps 2-3)
  - Update status page: "We are experiencing issues due to a cloud provider
    outage. Our systems have failed over to backup infrastructure."
  - Notify stakeholders via Slack and email
  - Set update cadence: every 30 minutes

STEP 5: MONITOR (ongoing)
  - Watch for secondary failures in failover region
  - Monitor data replication lag
  - Track customer support ticket volume
  - Watch for primary region recovery signals

STEP 6: FAILBACK (after primary region recovers)
  - DO NOT failback immediately -- wait for region to be stable for 1 hour
  - Verify primary region health checks pass consistently
  - Plan failback during low-traffic window
  - Reverse the failover steps in order
  - Run full smoke test suite after failback
  - Monitor for 2 hours post-failback
```

### Runbook: Data Corruption / Loss

```
DISASTER RECOVERY RUNBOOK: Data Corruption
Trigger: Corrupted or missing data detected in production database
Severity: SEV1 (if user-facing) or SEV2 (if internal-only)
Estimated recovery time: 1-4 hours depending on data volume

STEP 1: STOP THE BLEEDING (immediately)
  - Identify the scope: which collections/tables are affected?
  - If corruption is ongoing: disable the write path (feature flag, maintenance mode)
  - If caused by a deployment: rollback immediately
  - Preserve the current state: export affected collections before any fix

STEP 2: ASSESS DAMAGE (15 minutes)
  - Count affected records
  - Identify the time window of corruption
  - Determine root cause (bad migration, application bug, security breach)
  - Check if the corruption has propagated to backups

STEP 3: CHOOSE RECOVERY STRATEGY
  Option A -- Point-in-time restore (preferred if available):
    - Cloud SQL: restore to point before corruption
      gcloud sql backups restore BACKUP_ID --restore-instance=INSTANCE_NAME
    - Firestore, within 7 days (PITR enabled): clone to a new database at a minute before corruption
      gcloud firestore databases clone --source-database=projects/PROJECT_ID/databases/(default) \
        --snapshot-time=TIMESTAMP --destination-database=recovered
    - Firestore, older: restore a scheduled backup (always into a NEW database)
      gcloud firestore databases restore --source-backup=projects/PROJECT_ID/locations/LOCATION/backups/BACKUP_ID \
        --destination-database=recovered
    - Then copy the affected documents back, or repoint the app at the recovered database

  Option B -- Selective data repair:
    - Export clean data from backup
    - Merge with current production data (keep newer uncorrupted records)
    - Requires custom script -- test in staging first

  Option C -- Full restore from backup:
    - Last resort -- will lose all data since last backup
    - Restore to staging first, verify, then promote to production

STEP 4: VERIFY RECOVERY (30 minutes)
  - Run data integrity checks (record counts, checksums, referential integrity)
  - Test affected application flows end-to-end
  - Compare sample records against known-good state
  - Verify no secondary data stores are inconsistent

STEP 5: POST-RECOVERY
  - Re-enable write paths gradually
  - Monitor for recurrence
  - Schedule post-mortem within 48 hours
  - Update backup and monitoring procedures based on lessons learned
```

### Communication Plan

```
Audience            Channel              Cadence            Owner
─────────────────────────────────────────────────────────────────────
Engineering team    Slack #incidents     Every 15 min       Incident Commander
Leadership/Exec    Slack DM + Email     Every 30 min       Engineering Lead
Customers          Status page + Email  Every 1 hour       Communications Lead
Support team       Slack #support       As needed          Support Lead
Partners/Vendors   Email                As needed          Account Manager
```

## Business continuity

Read when the plan must cover people and tooling, not just systems (compliance-driven DR, SOC 2 BCP evidence).

### Team Communication During Outage

```
Primary:    Slack (if Slack is up)
Secondary:  Google Meet / Zoom bridge (pre-configured, link in runbooks)
Tertiary:   Phone tree (maintained in 1Password shared vault)
Emergency:  SMS group via PagerDuty / Opsgenie

War room setup:
  - Dedicated Slack channel: #incident-YYYY-MM-DD-[description]
  - Video bridge: always-on Google Meet link (pinned in #incidents)
  - Shared doc: Google Doc for real-time notes (template pre-created)
  - Status page: Statuspage.io / Instatus for external communication
```

### Alternate Work Procedures

```
If primary development tools are down:
  GitHub down:       Use local git, push when restored. Mirror to GitLab if >4 hours.
  CI/CD down:        Manual deploy using gcloud CLI / firebase CLI
  Slack down:        Google Chat or Discord backup workspace
  GCP Console down:  Use gcloud CLI or Terraform for infrastructure changes
  Jira/Linear down:  Track work in shared Google Sheet until restored

If office/network is unavailable:
  All team members should be able to work remotely (VPN + laptop)
  Critical credentials accessible via 1Password (not stored only on office network)
  No single point of failure for network access to production systems
```

### Vendor Contact List (support tiers are examples — confirm each contract before relying on it)

```
┌──────────────────────┬────────────────────────┬──────────────────────────────┐
│ Vendor               │ Support Channel        │ SLA                          │
├──────────────────────┼────────────────────────┼──────────────────────────────┤
│ Google Cloud (GCP)   │ Cloud Support Console  │ P1: 15 min (Premium)         │
│ Firebase             │ Firebase Support        │ Same as GCP                  │
│ Stripe               │ support@stripe.com     │ 24/7 for critical issues     │
│ Vercel               │ vercel.com/support     │ Enterprise: 1 hour           │
│ Cloudflare           │ cloudflare.com/support │ Enterprise: 15 min           │
│ PagerDuty            │ support@pagerduty.com  │ 24/7 phone support           │
│ Sentry               │ sentry.io/support      │ Business: 8 hour response    │
│ Domain Registrar     │ [registrar support]    │ Varies                       │
│ SSL Certificate      │ [CA support]           │ Varies (usually Let's Encrypt│
│                      │                        │  -- auto-renewal, no support)│
└──────────────────────┴────────────────────────┴──────────────────────────────┘

Maintain this list in a shared location (1Password, Notion, or internal wiki).
Update quarterly. Verify support contracts are active before you need them.
```

