# incident-response: detailed reference

> Reference material for the `incident-response` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 4: Incident Runbook Template

## Step 4: Incident Runbook Template

### Phase 1: Detection
```
Automated detection (preferred):
  - Firebase Crashlytics alerts (crash rate spike >1%)
  - Cloud Monitoring uptime checks (failure on 2+ regions)
  - Cloud Functions error rate alert (>5% error rate over 5 min)
  - Custom Datadog / Grafana dashboards with PagerDuty integration
  - Sentry error volume alerts
  - Stripe webhook failure alerts

Manual detection:
  - Customer support ticket spike
  - Social media reports
  - Internal QA or dogfooding
```

### Phase 2: Triage (First 15 Minutes)
```
1. Acknowledge the alert
   - Claim the PagerDuty / Opsgenie incident
   - Post in #incidents Slack channel: "Investigating [brief description]"

2. Assess severity using Step 3 framework
   - How many users affected?
   - Is revenue impacted?
   - Is data at risk?

3. Open incident channel if SEV1/SEV2
   - #incident-YYYY-MM-DD-[short-desc]
   - Pin initial assessment message
   - Assign roles: Incident Commander, Technical Lead, Communications Lead

4. Check recent changes
   - Last deploy: `gcloud app versions list --sort-by=~version`
   - Firebase console → Functions → Logs (last 30 min)
   - GitHub → recent merged PRs
   - Feature flag changes (LaunchDarkly / Firebase Remote Config)

5. Quick rollback decision
   - If deploy correlation is strong → rollback immediately
   - Firebase Hosting: `firebase hosting:clone SOURCE TARGET`
   - Cloud Functions: redeploy previous version from CI/CD
   - Mobile: disable feature via Remote Config (can't rollback app store)
```

### Phase 3: Mitigation (Stop the Bleeding)
```
Priority order:
  1. Rollback if deploy-related
  2. Scale up if capacity-related (Cloud Run instances, Firestore capacity)
  3. Disable feature via feature flag / Remote Config
  4. Enable maintenance mode if needed
  5. Failover to backup system if available
  6. Rate limit or block abusive traffic (Cloud Armor, WAF rules)

Firebase-specific mitigations:
  - Firestore: check and increase capacity, review security rules
  - Cloud Functions: increase memory/timeout, check concurrent execution limits
  - Hosting: rollback to previous deploy
  - Auth: check Identity Platform status, verify OAuth provider status
  - Storage: check bucket permissions, verify CORS configuration

Mobile-specific mitigations:
  - Force update via Remote Config minimum version
  - Kill switch for broken features
  - Server-side toggle to disable client-side code paths
```

### Phase 4: Resolution
```
1. Confirm the fix
   - Error rates returning to baseline
   - Latency returning to normal
   - Health checks passing
   - Manual smoke testing of affected flows

2. Monitor for recurrence
   - Watch dashboards for 30 minutes post-fix (SEV1/SEV2)
   - Confirm no secondary failures

3. Stand down
   - Update incident channel: "Resolved at [time]. Monitoring for recurrence."
   - Update status page: "Resolved"
   - Notify stakeholders

4. Preserve evidence
   - Export relevant logs before retention window
   - Screenshot dashboards showing incident timeline
   - Save any temporary debugging artifacts
```

### Phase 5: Communication
```
Internal (Slack #incidents):
  - OPENED: "[SEV-X] [System] - [Brief description]. Investigating."
  - UPDATE: "[SEV-X] [System] - [What we know]. [What we're doing]. ETA: [estimate]."
  - MITIGATED: "[SEV-X] [System] - Mitigated via [action]. Monitoring."
  - RESOLVED: "[SEV-X] [System] - Resolved at [time]. Root cause: [brief]. Post-mortem scheduled."

External (status page / customer email):
  - Use Step 6 templates below
```
