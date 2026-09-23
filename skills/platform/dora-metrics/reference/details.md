# dora-metrics: reference

Read the section you need: **SPACE** when running a developer-experience survey or a team-health check;
**Data Collection** when the team wants continuous collection instead of a one-off baseline.
Metric definitions and benchmarks live in SKILL.md (the source of truth).

## SPACE

SPACE (Forsgren et al., 2021) supplements DORA with satisfaction, performance, activity,
communication, and efficiency. Cure uses a quarterly anonymous 5-question survey:

1. "I can ship changes to production with confidence" (1–5)
2. "Our development tools and CI/CD work well" (1–5)
3. "Code review is timely and valuable" (1–5)
4. "I spend most of my time on meaningful work, not toil" (1–5)
5. "I would recommend this engineering team to a friend" (0–10, eNPS)

Flag a >10% quarter-over-quarter drop on any item. Cure working targets (team-level, not individual):

| Signal | Target |
|---|---|
| Time to first review | < 4 business hours |
| PR cycle time | < 24 h standard, < 4 h hotfix |
| Review rounds | ≤ 2 average (higher → PRs too big or standards unclear) |
| Full CI pipeline | < 10 min |
| Laptop → first commit (new engineer) | < 1 day |
| Toil | < 20% of time |
| IC meeting load | ≤ 2 h/day |

Activity counts (PRs, commits, reviews) are for team capacity and trend only — a drop can mean
vacation, deep work, onboarding, or debt paydown.

## Data Collection

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
        uses: actions/github-script@v9  # pin by SHA per rules/cicd.md
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
              // PR created_at approximates first commit; fetch the PR commits for the exact start
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
        uses: actions/github-script@v9  # pin by SHA per rules/cicd.md
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
