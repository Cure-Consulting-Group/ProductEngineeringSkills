# disaster-recovery: detailed reference

> Reference material for the `disaster-recovery` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 6: DR Runbooks

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
  - DNS: Update api.example.com to point to us-east1 endpoint
    - Cloudflare: automatic if health checks configured
    - Manual: update DNS record, flush CDN cache
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
    - Firestore: import from most recent clean export
      gcloud firestore import gs://PROJECT_NAME-backups/firestore/YYYY-MM-DD

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
