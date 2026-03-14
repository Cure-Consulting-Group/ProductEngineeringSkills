# Disaster Recovery

Design and implement disaster recovery plans, business continuity procedures, and failover architecture. Covers RTO/RPO definition, backup strategies for Firebase/GCP infrastructure, multi-region failover, DR testing runbooks, and business continuity planning. Every production system needs a DR plan before launch -- not after the first outage.

## Step 1: Classify the DR Need

| Need | Scope | Typical Trigger |
|------|-------|-----------------|
| Greenfield DR Plan | Full DR strategy from scratch for a new or unprotected system | New production launch, compliance audit finding |
| DR Plan Review | Audit and update existing DR plan against current architecture | Annual review, post-incident gap analysis, infrastructure change |
| Failover Architecture | Design multi-region or multi-zone failover for specific services | SLA requirement, customer contract, regulatory mandate |
| DR Testing | Plan and execute DR drills -- tabletop, simulation, or live failover | Quarterly schedule, compliance requirement, new team onboarding |
| Compliance-Driven DR | DR plan aligned to specific frameworks (SOC 2, HIPAA, ISO 27001) | Audit preparation, customer security questionnaire, certification |

## Step 2: Gather Context

1. **Infrastructure inventory** -- what services run in production (Firebase, Cloud Run, Cloud SQL, Vercel, third-party APIs)? What are the dependencies between them?
2. **Data stores** -- what databases and storage systems hold production data (Firestore, Cloud SQL, Cloud Storage, Redis, BigQuery)? What is the data volume and growth rate?
3. **SLA commitments** -- what uptime has been promised to customers (99.9%, 99.95%, 99.99%)? Are there contractual penalties for downtime?
4. **Compliance requirements** -- does the system fall under HIPAA, SOC 2, PCI-DSS, GDPR, or other frameworks with DR mandates?
5. **Budget constraints** -- what is the acceptable cost for DR infrastructure (hot standby vs. warm vs. cold)?
6. **Team capacity** -- who will execute DR procedures? Is there a dedicated SRE/platform team or do application engineers handle operations?
7. **Current backup state** -- what backups exist today? When was the last successful restore test?

## Step 3: RTO/RPO Definition by Service Tier

### Tier Definitions

```
Tier 1 -- Critical (Revenue-generating, user-facing core flows)
  Examples:    Authentication, payment processing, core API, primary database
  RTO target:  <15 minutes
  RPO target:  <5 minutes (near-zero data loss)
  Strategy:    Hot standby, synchronous replication, automated failover
  Cost:        High -- multi-region active-active or active-passive

Tier 2 -- Important (Key features, degraded experience without them)
  Examples:    Push notifications, search, analytics ingestion, file uploads
  RTO target:  <1 hour
  RPO target:  <1 hour
  Strategy:    Warm standby, asynchronous replication, semi-automated failover
  Cost:        Medium -- cross-zone redundancy, automated backups

Tier 3 -- Standard (Internal tools, batch processing, non-urgent)
  Examples:    Admin dashboards, reporting pipelines, CI/CD, log aggregation
  RTO target:  <4 hours
  RPO target:  <24 hours
  Strategy:    Cold standby, daily backups, manual restore procedures
  Cost:        Low -- backup-and-restore only
```

### RTO/RPO Matrix Template

```
┌─────────────────────────┬──────┬──────────┬──────────┬──────────────────┬──────────┐
│ Service                 │ Tier │ RTO      │ RPO      │ Failover Type    │ Owner    │
├─────────────────────────┼──────┼──────────┼──────────┼──────────────────┼──────────┤
│ Firebase Auth           │ 1    │ <15 min  │ 0 min    │ Google-managed   │ Platform │
│ Firestore (primary)     │ 1    │ <15 min  │ <5 min   │ Multi-region     │ Platform │
│ Cloud Functions (API)   │ 1    │ <15 min  │ N/A      │ Multi-region     │ Platform │
│ Stripe Integration      │ 1    │ <15 min  │ <5 min   │ Webhook retry    │ Backend  │
│ Cloud SQL (if used)     │ 2    │ <1 hour  │ <15 min  │ HA replica       │ Platform │
│ Cloud Storage           │ 2    │ <1 hour  │ <1 hour  │ Multi-region     │ Platform │
│ Push Notifications      │ 2    │ <1 hour  │ <1 hour  │ Queue-based      │ Backend  │
│ Analytics Pipeline      │ 3    │ <4 hours │ <24 hours│ Rebuild from logs│ Data     │
│ Admin Dashboard         │ 3    │ <4 hours │ N/A      │ Redeploy         │ Frontend │
│ CI/CD Pipeline          │ 3    │ <4 hours │ N/A      │ GitHub fallback  │ Platform │
└─────────────────────────┴──────┴──────────┴──────────┴──────────────────┴──────────┘
```

## Step 4: Backup Strategy

### Firestore Backups

```bash
# Automated daily export to Cloud Storage
gcloud firestore export gs://PROJECT_NAME-backups/firestore/$(date +%Y-%m-%d) \
  --project=PROJECT_ID

# Schedule via Cloud Scheduler
gcloud scheduler jobs create http firestore-daily-backup \
  --schedule="0 2 * * *" \
  --uri="https://firestore.googleapis.com/v1/projects/PROJECT_ID/databases/(default):exportDocuments" \
  --http-method=POST \
  --message-body='{"outputUriPrefix":"gs://PROJECT_NAME-backups/firestore/"}' \
  --oauth-service-account-email=PROJECT_ID@appspot.gserviceaccount.com \
  --time-zone="UTC"

# Retention policy: keep daily for 30 days, weekly for 90 days, monthly for 1 year
# Implement via Cloud Storage lifecycle rules on the backup bucket
```

### Cloud SQL Automated Backups

```bash
# Enable automated backups with point-in-time recovery
gcloud sql instances patch INSTANCE_NAME \
  --backup-start-time=02:00 \
  --enable-point-in-time-recovery \
  --retained-backups-count=30 \
  --retained-transaction-log-days=7

# Create on-demand backup before major changes
gcloud sql backups create --instance=INSTANCE_NAME --description="Pre-migration backup"

# Verify backup exists
gcloud sql backups list --instance=INSTANCE_NAME
```

### Cloud Storage Versioning and Retention

```bash
# Enable object versioning on critical buckets
gsutil versioning set on gs://PROJECT_NAME-prod-uploads

# Set retention policy (cannot delete objects for 90 days)
gsutil retention set 90d gs://PROJECT_NAME-prod-critical-data

# Lifecycle rules for backup bucket
cat > backup-lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": { "type": "SetStorageClass", "storageClass": "NEARLINE" },
        "condition": { "age": 30 }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "COLDLINE" },
        "condition": { "age": 90 }
      },
      {
        "action": { "type": "Delete" },
        "condition": { "age": 365, "isLive": false }
      }
    ]
  }
}
EOF
gsutil lifecycle set backup-lifecycle.json gs://PROJECT_NAME-backups
```

### Backup Verification

```
Backup Verification Schedule:
  Daily:    Automated check that backup job completed (Cloud Monitoring alert on failure)
  Weekly:   Verify backup file sizes are within expected range (detect empty/truncated backups)
  Monthly:  Full restore test to staging environment (prove RPO is achievable)
  Quarterly: Full DR drill including data verification (prove RTO is achievable)

Verification checklist:
  - [ ] Backup completed without errors
  - [ ] Backup size is within 20% of previous backup (detect anomalies)
  - [ ] Backup can be downloaded / accessed from backup storage
  - [ ] Restore to staging succeeds
  - [ ] Data integrity checks pass (record counts, checksums, sample queries)
  - [ ] Application functions correctly against restored data
```

## Step 5: Failover Architecture

### Multi-Region Firebase

```
Architecture: Active-Passive with Firestore Multi-Region

Primary Region:   us-central1 (or nam5 multi-region for Firestore)
Secondary Region: us-east1 (Cloud Functions, Cloud Run)
Firestore:        Use nam5 (multi-region) for automatic cross-region replication
Cloud Functions:  Deploy to both regions, route via Cloud Load Balancing
Cloud Storage:    Use multi-region bucket (US, EU, or ASIA)
Firebase Hosting: Global CDN (automatic, no config needed)

Failover trigger: Cloud Monitoring detects primary region unhealthy
Failover method:  DNS update via Cloud DNS or external DNS provider (Cloudflare)
Failover time:    DNS propagation (60-300 seconds with low TTL)
```

### Cloud Run Failover

```yaml
# Deploy to multiple regions
gcloud run deploy PROJECT_NAME-api --region=us-central1 --source .
gcloud run deploy PROJECT_NAME-api --region=us-east1 --source .

# Create global load balancer with health checks
gcloud compute health-checks create http api-health-check \
  --port=8080 \
  --request-path=/health \
  --check-interval=10 \
  --timeout=5 \
  --healthy-threshold=2 \
  --unhealthy-threshold=3

# Backend services with failover
gcloud compute backend-services create api-backend \
  --global \
  --health-checks=api-health-check \
  --load-balancing-scheme=EXTERNAL_MANAGED

# Add primary and failover NEGs
gcloud compute backend-services add-backend api-backend \
  --global \
  --network-endpoint-group=api-neg-us-central1 \
  --network-endpoint-group-region=us-central1

gcloud compute backend-services add-backend api-backend \
  --global \
  --network-endpoint-group=api-neg-us-east1 \
  --network-endpoint-group-region=us-east1 \
  --failover
```

### DNS Failover

```
DNS Configuration (Cloudflare recommended):
  Record:     api.example.com
  Type:       CNAME (proxied)
  Primary:    us-central1-PROJECT_ID.cloudfunctions.net
  Failover:   us-east1-PROJECT_ID.cloudfunctions.net
  Health check: GET /health every 30 seconds
  Failover trigger: 3 consecutive failures
  TTL:        60 seconds (low TTL for fast failover)

Alternative (Cloud DNS):
  Use routing policies with health checks for weighted or failover routing.
  gcloud dns record-sets create api.example.com \
    --type=A \
    --zone=example-zone \
    --routing-policy-type=failover \
    --routing-policy-primary-data=PRIMARY_IP \
    --routing-policy-backup-data=BACKUP_IP \
    --health-check=api-health-check
```

### Database Replication

```
Firestore (built-in):
  - Multi-region mode (nam5, eur3) provides automatic replication
  - No manual failover needed -- Google manages it
  - Strong consistency within region, eventual across regions

Cloud SQL (if used):
  - Enable HA with automatic failover: --availability-type=REGIONAL
  - Create read replica in secondary region for read traffic
  - Promote replica to primary during DR event
  gcloud sql instances failover INSTANCE_NAME

Redis (Memorystore):
  - Standard tier provides automatic failover within zone
  - For cross-region: use Redis replication or application-level caching
```

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

## Step 7: DR Testing Schedule

### Quarterly: Tabletop Exercises

```
Format: 60-minute meeting with engineering team
Facilitator: Engineering Lead or SRE

Scenario examples:
  - "Firestore is returning errors for all writes. What do you do?"
  - "A developer accidentally deleted the users collection. Walk through recovery."
  - "GCP us-central1 is down. How do we failover?"
  - "Our Stripe webhook secret was leaked. What are the steps?"

Process:
  1. Present scenario (5 min)
  2. Team walks through response steps verbally (30 min)
  3. Identify gaps in runbooks or tooling (15 min)
  4. Assign action items to close gaps (10 min)

Track results:
  - Time to identify correct response steps
  - Gaps found in documentation
  - Missing access or tooling identified
  - Action items with owners and deadlines
```

### Bi-Annually: Simulated Failover

```
Format: Controlled failover test in staging environment
Duration: 2-4 hours
Team: On-call engineer + backup + observer

Process:
  1. Pre-test: verify staging mirrors production architecture
  2. Inject failure: disable primary service/region in staging
  3. Execute runbook: follow DR runbook step by step
  4. Measure: record actual RTO and RPO achieved
  5. Verify: confirm all services recovered correctly
  6. Document: record deviations from runbook, actual timings

Success criteria:
  - RTO achieved within target for all Tier 1 services
  - RPO achieved within target (no unexpected data loss)
  - Runbook was sufficient (no undocumented steps needed)
  - All team members knew their roles
```

### Annually: Live Failover (Chaos Day)

```
Format: Controlled failure injection in production during low-traffic window
Duration: 4-8 hours (including preparation and monitoring)
Approval: CTO sign-off required
Notification: Customers notified in advance if any impact expected

Process:
  1. Schedule during lowest-traffic period (typically Sunday 2-6 AM)
  2. Notify all stakeholders 1 week in advance
  3. Have full team on standby
  4. Inject failure (kill primary region endpoint, corrupt test data, etc.)
  5. Execute failover using production runbooks
  6. Measure actual RTO/RPO in production conditions
  7. Failback and verify
  8. Full debrief within 48 hours

Escalation: If test causes unexpected customer impact, abort immediately
  and treat as real incident.
```

## Step 8: Business Continuity Plan

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

### Vendor Contact List

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

## Step 9: Output

```
DISASTER RECOVERY PLAN
Project: [NAME]
Date: [TODAY]
Prepared by: [NAME]
Review date: [NEXT QUARTER]

PLAN SUMMARY
┌──────────────────────┬────────────────────────────────────┐
│ Field                │ Value                              │
├──────────────────────┼────────────────────────────────────┤
│ DR Plan Type         │ [From Step 1 classification]       │
│ Services Covered     │ [Count and list]                   │
│ Tier 1 RTO / RPO    │ [Target values]                    │
│ Backup Strategy      │ [Summary]                          │
│ Failover Type        │ [Hot / Warm / Cold]                │
│ Last DR Test         │ [Date and result]                  │
│ Next DR Test         │ [Scheduled date]                   │
│ Compliance Alignment │ [SOC 2 / HIPAA / None]             │
└──────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] RTO/RPO matrix for all services
  - [ ] Backup strategy with retention policies
  - [ ] Failover architecture diagram and configuration
  - [ ] DR runbooks (region failure, data corruption, service failure)
  - [ ] Communication plan and templates
  - [ ] DR testing schedule (quarterly/bi-annual/annual)
  - [ ] Business continuity procedures
  - [ ] Vendor contact list

CROSS-REFERENCES:
  - /incident-response — for active incident handling procedures
  - /infrastructure-scaffold — for infrastructure configuration
  - /security-review — for security aspects of DR planning
  - /ci-cd-pipeline — for deployment rollback procedures
```
