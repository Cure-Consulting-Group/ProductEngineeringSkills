# DORA Metrics

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

Implement DORA four key metrics and SPACE framework for measuring software delivery performance and developer experience. Covers data collection automation, dashboard templates, improvement playbooks, and anti-patterns. Use this to baseline your team, set improvement targets, and report to leadership with real data instead of vibes.

## Step 1: Classify the Metrics Need

| Need | Scope | Typical Trigger |
|------|-------|-----------------|
| Baseline Measurement | Establish current DORA metrics for a team or project from scratch | New team, new project, engineering leadership request |
| Improvement Initiative | Identify bottlenecks and implement changes to move up DORA performance tiers | Team retrospective, slow delivery complaints, high failure rate |
| Executive Reporting | Build dashboards and reports for leadership visibility into engineering performance | Board meeting, investor due diligence, org-wide review |
| Team Health Check | Combine DORA with SPACE to assess developer experience and sustainability | Burnout signals, attrition risk, post-reorg assessment |

## Step 2: Gather Context

1. **CI/CD tooling** -- what pipeline tools are in use (GitHub Actions, Cloud Build, Fastlane, Vercel)? Are deployments automated or manual?
2. **Team size and structure** -- how many engineers? Single team or multiple squads? Shared codebase or microservices?
3. **Current deployment cadence** -- how often does the team deploy to production? Daily, weekly, ad-hoc?
4. **Incident tracking** -- where are incidents logged (PagerDuty, Opsgenie, Linear, Jira, Slack)? Is there a severity classification?
5. **Code review process** -- what is the typical PR lifecycle (open to merge)? Are there approval requirements?
6. **Existing metrics** -- is anything being tracked today? What tools (Datadog, Grafana, LinearB, Sleuth, DX)?
7. **Goals** -- what does success look like? Faster shipping, fewer incidents, better developer experience, all of the above?

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

## Step 4: SPACE Framework Overlay

### Satisfaction

```
What to measure:
  - Developer satisfaction survey (quarterly, anonymous)
  - eNPS (Employee Net Promoter Score): "How likely are you to recommend
    this team/company as a place to work?" (0-10 scale)
  - Tool satisfaction: "Do your tools help or hinder your work?"
  - Process satisfaction: "Is the development process reasonable?"

Survey template (quarterly, 5 questions):
  1. "I can ship changes to production with confidence" (1-5)
  2. "Our development tools and CI/CD work well" (1-5)
  3. "Code review is timely and valuable" (1-5)
  4. "I spend most of my time on meaningful work, not toil" (1-5)
  5. "I would recommend this engineering team to a friend" (0-10, eNPS)

Track over time: quarterly trend. Alert if satisfaction drops >10% quarter over quarter.
```

### Performance

```
What to measure:
  - DORA metrics (Step 3 above)
  - Code quality metrics: test coverage trend, lint violations, type safety
  - Reliability metrics: uptime, error rate, p95 latency

DO NOT use as individual performance metric. These are team-level indicators.
```

### Activity

```
What to measure:
  - PR throughput (PRs merged per week per engineer)
  - Deployment count per week
  - Code review volume (reviews given per week)
  - Incident response participation

WARNING: Activity metrics are the most dangerous category.
  - NEVER use as a productivity proxy for individuals
  - NEVER compare engineers by PR count or lines of code
  - Use only for team-level trends and capacity planning
  - A drop in activity might mean: vacation, deep work on hard problem,
    onboarding, technical debt paydown -- all valid and valuable

Safe usage:
  - Team-level trends over time (are we shipping more or less than last quarter?)
  - Capacity planning (how many PRs can this team handle per sprint?)
  - Process bottleneck identification (are PRs piling up in review?)
```

### Communication

```
What to measure:
  - Code review turnaround time (PR opened → first review)
  - PR cycle time (PR opened → merged)
  - Handoff friction (how many times does a PR bounce between author and reviewer?)
  - Cross-team dependency wait time (blocked on another team)
  - Documentation freshness (when were runbooks/docs last updated?)

Targets:
  First review: <4 hours during business hours
  PR cycle time: <24 hours for standard PRs, <4 hours for hotfixes
  Review rounds: <=2 rounds average (if higher, PRs are too large or standards unclear)
  Cross-team blocks: track and report -- no target, but visibility drives improvement
```

### Efficiency

```
What to measure:
  - Flow state time: hours of uninterrupted coding per day (survey-based)
  - Context switching: meetings per day, Slack interruption frequency
  - Toil ratio: time on manual/repetitive tasks vs. feature work (survey-based)
  - Build/CI wait time: how long do engineers wait for CI to complete?
  - Environment setup time: how long for a new engineer to make first commit?

Targets:
  Flow state:      >=4 hours per day of uninterrupted work
  Meeting load:    <=2 hours of meetings per day for IC engineers
  CI wait time:    <10 minutes for full pipeline
  Onboarding:      <1 day from laptop to first commit in dev environment
  Toil ratio:      <20% of time on repetitive tasks (automate the rest)
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

## Step 6: Dashboard Templates

### Team-Level Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENGINEERING METRICS — [TEAM NAME]                │
│                    Period: [MONTH YEAR]                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  DORA METRICS                                                       │
│  ┌──────────────────────┬────────────┬────────────┬───────────────┐ │
│  │ Metric               │ This Month │ Last Month │ Target        │ │
│  ├──────────────────────┼────────────┼────────────┼───────────────┤ │
│  │ Deploy Frequency     │ 42/month   │ 38/month   │ Daily (High)  │ │
│  │ Lead Time (median)   │ 18 hours   │ 24 hours   │ <1 day (High) │ │
│  │ MTTR (median)        │ 45 min     │ 1.2 hours  │ <1 hr (Elite) │ │
│  │ Change Failure Rate  │ 12%        │ 15%        │ <15% (Elite)  │ │
│  └──────────────────────┴────────────┴────────────┴───────────────┘ │
│                                                                     │
│  DORA Performance Level: HIGH (3 of 4 metrics at High or above)    │
│                                                                     │
│  PR HEALTH                                                          │
│  ┌──────────────────────────────────┬────────────┐                  │
│  │ Median time to first review      │ 3.2 hours  │                  │
│  │ Median PR cycle time             │ 14 hours   │                  │
│  │ Average review rounds            │ 1.8        │                  │
│  │ PRs merged this month            │ 87         │                  │
│  │ Average PR size (additions)      │ 142 lines  │                  │
│  └──────────────────────────────────┴────────────┘                  │
│                                                                     │
│  INCIDENTS                                                          │
│  ┌───────────┬───────┬───────┬───────┬───────┐                      │
│  │ Severity  │ Count │ MTTD  │ MTTA  │ MTTR  │                      │
│  ├───────────┼───────┼───────┼───────┼───────┤                      │
│  │ SEV1      │ 0     │ --    │ --    │ --    │                      │
│  │ SEV2      │ 1     │ 3 min │ 5 min │ 45 min│                      │
│  │ SEV3      │ 3     │ 15 min│ 22 min│ 2.1 hr│                      │
│  │ SEV4      │ 5     │ N/A   │ N/A   │ N/A   │                      │
│  └───────────┴───────┴───────┴───────┴───────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Org-Level Executive Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│              ENGINEERING HEALTH — [ORG NAME] — [QUARTER]           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  DORA PERFORMANCE BY TEAM                                           │
│  ┌──────────────┬────────┬───────────┬────────┬────────┬──────────┐│
│  │ Team         │ Deploy │ Lead Time │ MTTR   │ CFR    │ Level    ││
│  │              │ Freq   │ (median)  │(median)│        │          ││
│  ├──────────────┼────────┼───────────┼────────┼────────┼──────────┤│
│  │ Product      │ Daily  │ 16 hr     │ 40 min │ 11%    │ Elite    ││
│  │ Platform     │ Weekly │ 3 days    │ 1.5 hr │ 18%    │ High     ││
│  │ Mobile       │ Weekly │ 5 days    │ 2 hr   │ 22%    │ High     ││
│  │ Data         │ Monthly│ 2 weeks   │ 4 hr   │ 30%    │ Medium   ││
│  └──────────────┴────────┴───────────┴────────┴────────┴──────────┘│
│                                                                     │
│  QUARTER OVER QUARTER TREND                                         │
│  Deploy Frequency:  ↑ 15%  (improving)                              │
│  Lead Time:         ↓ 20%  (improving — lower is better)            │
│  MTTR:              ↓ 30%  (improving — lower is better)            │
│  Change Failure:    ↓  5%  (improving — lower is better)            │
│                                                                     │
│  DEVELOPER EXPERIENCE (from quarterly survey)                       │
│  eNPS: 42 (↑ from 35 last quarter)                                 │
│  Top concern: CI wait times (addressed — reduced 40% this quarter)  │
│  Toil ratio: 18% (↓ from 25% — automation investments paying off)  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Step 7: Improvement Playbooks

### Moving from Low to Medium

```
Typical blockers at Low level:
  - No CI/CD pipeline or mostly manual deploys
  - No incident tracking or severity classification
  - Long-lived feature branches (weeks or months)
  - No automated testing

Actions:
  1. Implement basic CI/CD: automate build, test, deploy on merge to main
     → Cross-ref: /ci-cd-pipeline
  2. Adopt trunk-based development: short-lived branches (<2 days), small PRs
  3. Start tracking incidents: severity, detection time, resolution time
     → Cross-ref: /incident-response
  4. Add basic automated tests: unit tests on critical paths, CI gate on test pass
     → Cross-ref: /testing-strategy
  5. Deploy at least weekly: if weekly feels scary, you need more tests and feature flags

Expected improvement timeline: 1-2 quarters
```

### Moving from Medium to High

```
Typical blockers at Medium level:
  - CI/CD exists but is slow (>30 min pipeline)
  - Manual QA gate before every release
  - No feature flags — all-or-nothing deployments
  - Incident response is ad-hoc, no runbooks

Actions:
  1. Speed up CI: parallelize tests, cache dependencies, remove flaky tests
  2. Implement feature flags: decouple deploy from release
     → Ship dark, enable gradually, kill switch for rollback
  3. Build runbooks for top 5 failure modes
     → Cross-ref: /incident-response
  4. Automate deployment: merge to main triggers deploy (with canary or staged rollout)
  5. Reduce PR size: target <200 lines changed per PR
  6. Automate code review basics: linting, type checking, security scanning in CI

Expected improvement timeline: 1-2 quarters
```

### Moving from High to Elite

```
Typical blockers at High level:
  - Deploy multiple times per day but some manual steps remain
  - Good testing but no canary deployments or progressive delivery
  - Fast MTTR but detection could be faster
  - Change failure rate stubbornly above 15%

Actions:
  1. Progressive delivery: canary deployments with automatic rollback on error spike
  2. Shift-left testing: contract tests, integration tests in CI, synthetic monitoring
  3. Observability investment: distributed tracing, custom metrics, anomaly detection
     → Cross-ref: /analytics-implementation
  4. Automated rollback: deploy pipeline auto-rolls back if error rate exceeds threshold
  5. Reduce blast radius: deploy per-service, not monolith. Microservice or modular architecture.
  6. Invest in developer experience: fast local dev, instant preview environments, excellent docs

Expected improvement timeline: 2-4 quarters (Elite is genuinely hard)
```

## Step 8: Anti-Patterns

```
ANTI-PATTERN: Gaming metrics
  Problem:  Splitting one deploy into multiple to inflate deployment frequency.
            Or not counting incidents to lower MTTR.
  Fix:      Automate measurement. Remove human judgment from data collection.
            Make metrics a tool for learning, not judgment.

ANTI-PATTERN: Using activity as productivity
  Problem:  Ranking engineers by PRs merged, lines of code, or commits.
  Fix:      Activity metrics are team-level only. A senior engineer mentoring
            juniors ships zero PRs that week but creates massive value.
            Never use DORA metrics in performance reviews for individuals.

ANTI-PATTERN: Comparing teams unfairly
  Problem:  Comparing a 2-person team maintaining legacy code to a 10-person
            team building greenfield. Different contexts, different targets.
  Fix:      Compare teams to their own past performance, not to each other.
            Set context-appropriate targets. A regulated industry team at
            Medium is doing great. An early-stage startup at Medium is too slow.

ANTI-PATTERN: Measuring without acting
  Problem:  Beautiful dashboards that nobody looks at. Metrics collected but
            no improvement initiatives funded.
  Fix:      Every metrics review must produce at least one action item.
            Block time in the sprint for improvement work (20% rule).
            Report improvement trends to leadership alongside the metrics.

ANTI-PATTERN: Optimizing one metric at the expense of others
  Problem:  Deploying 10x per day but change failure rate is 50%. Or MTTR
            is great because you never detect incidents (low MTTD).
  Fix:      DORA metrics are designed to be used together. Improving all four
            simultaneously is the goal. If one improves while another degrades,
            investigate the tradeoff.

ANTI-PATTERN: Skipping the developer experience dimension
  Problem:  All four DORA metrics are Elite but engineers are burned out,
            attrition is high, and nobody enjoys the work.
  Fix:      Supplement DORA with SPACE (Step 4). Sustainable pace matters.
            Survey quarterly. Act on the results.
```

## Step 9: Output

```
DORA & SPACE METRICS REPORT
Team: [NAME]
Period: [MONTH/QUARTER YEAR]
Prepared by: [NAME]

CURRENT PERFORMANCE
┌──────────────────────┬────────────────────────────────────┐
│ Field                │ Value                              │
├──────────────────────┼────────────────────────────────────┤
│ Metrics Need         │ [From Step 1 classification]       │
│ DORA Performance     │ [Elite / High / Medium / Low]      │
│ Deploy Frequency     │ [Value + tier]                     │
│ Lead Time            │ [Value + tier]                     │
│ MTTR                 │ [Value + tier]                     │
│ Change Failure Rate  │ [Value + tier]                     │
│ eNPS                 │ [Score]                            │
│ Top Bottleneck       │ [Identified bottleneck]            │
└──────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] DORA baseline measurement for all four metrics
  - [ ] SPACE framework assessment
  - [ ] Data collection automation (GitHub Actions workflows)
  - [ ] Dashboard templates (team-level and org-level)
  - [ ] Improvement playbook with prioritized actions
  - [ ] Anti-pattern checklist reviewed

CROSS-REFERENCES:
  - /ci-cd-pipeline — for deployment automation and pipeline optimization
  - /incident-response — for MTTR improvement and incident tracking
  - /project-manager — for sprint planning and improvement initiative tracking
  - /analytics-implementation — for metrics data collection and dashboards
```

## Automated Metric Collection

Before analysis, gather actual DORA data from the project:

1. **Deployment Frequency**: Run `git tag --list --sort=-creatordate | head -20` and count tags per week/month
2. **Lead Time**: Run `git log --oneline --since="30 days ago"` to estimate PR-to-deploy time
3. **Change Failure Rate**: Grep git log for `revert|hotfix|rollback` commits as % of total
4. **MTTR**: Grep for incident-related commits and measure time between incident start and resolution

## Code Generation (Required)

Generate metric collection automation using Write:

1. **Metric collector**: `scripts/collect-dora-metrics.sh` — parses git history into DORA metrics
2. **Dashboard config**: `monitoring/dora-dashboard.json` — Grafana/Datadog dashboard template
3. **CI integration**: `.github/workflows/dora-report.yml` — weekly DORA metric collection
4. **Team report**: `docs/dora-report-template.md` — monthly report template
