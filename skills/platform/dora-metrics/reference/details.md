# dora-metrics: detailed reference

> Reference material for the `dora-metrics` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 3: DORA Four Key Metrics
- Step 5: Data Collection Automation

## Step 3: DORA Four Key Metrics

### Metric 1: Deployment Frequency

```
Definition: How often the team deploys to production.

Measurement:
  Count production deployments per time period (day, week, month).
  Include: all production releases (features, fixes, config changes)
  Exclude: staging/dev deploys, rollbacks (count separately)

Performance tiers (from DORA research):
  Elite:    On-demand, multiple deploys per day
  High:     Between once per day and once per week
  Medium:   Between once per week and once per month
  Low:      Between once per month and once every six months

How to measure with GitHub Actions:
  - Count workflow runs on main/production branch with deployment status "success"
  - Tag deployments with metadata (team, service, type)
  - Query via GitHub API:
    GET /repos/{owner}/{repo}/actions/runs?branch=main&status=success

Targets by team type:
  Product team (web/mobile):  High minimum, Elite target
  Platform/infra team:        Medium minimum, High target
  Early-stage startup:        High minimum (ship fast, fix fast)
  Regulated industry:         Medium acceptable if change process is heavy

Common blockers:
  - Manual QA gates before every release
  - Monolithic architecture requiring full regression
  - Fear of breaking production (fix with feature flags + canary deploys)
  - Long-lived branches (fix with trunk-based development)
```

### Metric 2: Lead Time for Changes

```
Definition: Time from first commit to running in production.

Measurement:
  Start: timestamp of first commit in a PR/branch
  End: timestamp of production deployment containing that commit
  Report: median and p95 (not average -- outliers skew it)

Breakdown (identify bottleneck):
  Code time:    first commit → PR opened
  Review time:  PR opened → PR approved
  Merge time:   PR approved → PR merged
  Deploy time:  PR merged → production deployment

Performance tiers:
  Elite:    Less than one day
  High:     Between one day and one week
  Medium:   Between one week and one month
  Low:      Between one month and six months

How to measure:
  GitHub API + deployment tracking:
    - PR created_at, merged_at timestamps
    - Deployment timestamp from GitHub Actions / deploy workflow
    - Calculate: deployment_timestamp - first_commit_timestamp

  Tools that automate this:
    - LinearB, Sleuth, DX, Swarmia, Faros AI
    - Or build custom with GitHub webhooks + BigQuery

Bottleneck analysis:
  If code time is high:     Developer is context-switching, stories too large
  If review time is high:   Not enough reviewers, PRs too large, async review culture
  If merge time is high:    Approval process too heavy, merge conflicts, CI too slow
  If deploy time is high:   Manual deployment, infrequent release trains, staging bottleneck
```

### Metric 3: Mean Time to Restore (MTTR)

```
Definition: Time from production incident detection to resolution.

Measurement:
  Start: incident detected (alert fired or user report)
  End: service restored to normal operation
  Report: median across all incidents per severity

Performance tiers:
  Elite:    Less than one hour
  High:     Less than one day
  Medium:   Less than one week
  Low:      More than one week (or unknown -- you're not tracking)

How to measure:
  PagerDuty / Opsgenie:
    - incident.created_at → incident.resolved_at
    - Filter by severity level
    - Export via API for dashboard integration

  Manual tracking:
    - Maintain incident log (Notion, Google Sheet, Linear)
    - Record: detection time, acknowledgment time, resolution time
    - Calculate MTTR monthly

Improvement levers:
  Detection speed:   Better monitoring, tighter alert thresholds, synthetic checks
  Triage speed:      Runbooks, on-call training, clear escalation paths
  Resolution speed:  One-click rollback, feature flags, automated remediation
  Prevention:        Post-mortem action items, testing, canary deployments

Track separately:
  MTTD (Mean Time to Detect): incident start → detection
  MTTA (Mean Time to Acknowledge): detection → engineer engaged
  MTTR (Mean Time to Resolve): detection → resolution
```

### Metric 4: Change Failure Rate

```
Definition: Percentage of deployments that cause a failure in production.

Measurement:
  Numerator:   deployments that result in degraded service, rollback,
               hotfix, or incident within 24 hours of deploy
  Denominator: total production deployments
  Report:      percentage, tracked monthly

Performance tiers:
  Elite:    0-15%
  High:     16-30%
  Medium:   31-45%
  Low:      46-60%+

How to measure:
  Option A (automated):
    - Tag each deployment with a unique ID
    - If an incident is opened within 24 hours and linked to a deploy → failure
    - If a rollback workflow runs within 24 hours → failure
    - Calculate: failures / total deploys

  Option B (manual):
    - After each deploy, on-call engineer marks pass/fail
    - Weekly review of deployment log
    - Calculate monthly

What counts as a failure:
  YES: rollback, hotfix, incident caused by deploy, degraded performance
  NO: planned maintenance, config change with expected brief disruption,
      incident caused by external factors (vendor outage)

Improvement levers:
  Pre-deploy:    Better testing, staging validation, canary deployment
  At deploy:     Feature flags, gradual rollout, automated smoke tests
  Post-deploy:   Fast rollback capability, monitoring, alerting
```

## Step 5: Data Collection Automation

### GitHub Actions Deployment Tracking

```yaml
# .github/workflows/track-deployment.yml
name: Track Deployment Metrics

on:
  workflow_run:
    workflows: ["Deploy to Production"]
    types: [completed]

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - name: Record deployment
        run: |
          curl -X POST "${{ secrets.METRICS_WEBHOOK_URL }}" \
            -H "Content-Type: application/json" \
            -d '{
              "event": "deployment",
              "repo": "${{ github.repository }}",
              "sha": "${{ github.event.workflow_run.head_sha }}",
              "branch": "${{ github.event.workflow_run.head_branch }}",
              "status": "${{ github.event.workflow_run.conclusion }}",
              "timestamp": "${{ github.event.workflow_run.updated_at }}",
              "run_id": "${{ github.event.workflow_run.id }}"
            }'

      - name: Calculate lead time
        uses: actions/github-script@v7
        with:
          script: |
            const sha = context.payload.workflow_run.head_sha;
            const deployTime = new Date(context.payload.workflow_run.updated_at);

            // Find the PR that introduced this commit
            const { data: prs } = await github.rest.repos.listPullRequestsAssociatedWithCommit({
              owner: context.repo.owner,
              repo: context.repo.repo,
              commit_sha: sha,
            });

            if (prs.length > 0) {
              const pr = prs[0];
              const firstCommitTime = new Date(pr.created_at);
              const leadTimeHours = (deployTime - firstCommitTime) / (1000 * 60 * 60);
              console.log(`Lead time: ${leadTimeHours.toFixed(1)} hours`);
              // Send to metrics store
            }
```

### PR Metrics Collection

```yaml
# .github/workflows/pr-metrics.yml
name: PR Metrics

on:
  pull_request:
    types: [opened, closed]

jobs:
  track:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Record PR metrics
        uses: actions/github-script@v7
        with:
          script: |
            const pr = context.payload.pull_request;
            const createdAt = new Date(pr.created_at);
            const mergedAt = new Date(pr.merged_at);
            const cycleTimeHours = (mergedAt - createdAt) / (1000 * 60 * 60);

            // Get review timeline
            const { data: reviews } = await github.rest.pulls.listReviews({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: pr.number,
            });

            const firstReview = reviews.length > 0
              ? new Date(reviews[0].submitted_at)
              : null;
            const reviewTimeHours = firstReview
              ? (firstReview - createdAt) / (1000 * 60 * 60)
              : null;

            const metrics = {
              pr_number: pr.number,
              cycle_time_hours: cycleTimeHours.toFixed(1),
              time_to_first_review_hours: reviewTimeHours?.toFixed(1),
              additions: pr.additions,
              deletions: pr.deletions,
              review_count: reviews.length,
              author: pr.user.login,
              merged_at: pr.merged_at,
            };

            console.log(JSON.stringify(metrics, null, 2));
            // Send to metrics store (BigQuery, Datadog, custom API)
```

### Incident Tracking Integration

```
PagerDuty → BigQuery pipeline:
  1. Configure PagerDuty webhook to Cloud Function
  2. Cloud Function transforms event and writes to BigQuery
  3. BigQuery table: incidents(id, severity, created_at, acknowledged_at,
     resolved_at, service, team, description)
  4. Calculate MTTR: resolved_at - created_at
  5. Calculate MTTA: acknowledged_at - created_at

Alternative (manual but effective):
  Google Sheet with columns:
    Date | Severity | Service | Detected | Acknowledged | Resolved |
    Cause | Deploy-related? | Action items

  Monthly: calculate averages, identify trends, report in team retro
```
