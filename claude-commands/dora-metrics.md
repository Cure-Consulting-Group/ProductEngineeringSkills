# DORA Metrics

**Outcome:** real numbers for the DORA metrics (from the bundled scripts or the team's tools, never estimated from vibes), each placed against the dated benchmark below, plus the one or two bottlenecks worth fixing next. **Done** when every metric has a value with its data source and window, or an explicit "not measurable yet — here is what to instrument".

This skill **owns the Cure definitions** of the delivery metrics, including recovery time / MTTR. Other skills (incident-response, observability, investor-reporting) link here instead of restating them.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):
- Release tags: !`git tag --list --sort=-creatordate 2>/dev/null | head -10 || echo "(no tags)"`
- Deploy workflows: !`ls .github/workflows/ 2>/dev/null | head -10 || echo "(no GitHub workflows)"`

## Step 1: Classify the Metrics Need

| Need | Deliverable |
|------|-------------|
| Baseline | Current values for the five metrics + data-gap list |
| Improvement | Baseline + bottleneck analysis + 1–3 prioritized changes |
| Executive reporting | One-page report (Step 6) with trend vs. last period |
| Team health | Baseline + SPACE survey results (read `reference/details.md` § SPACE when running a survey) |
| Build collection | Automation files (see Code/Artifact Generation) |

## Step 2: Gather Context

Ask only what the repo can't answer: where production deploys are recorded (tags, workflow runs, Vercel/Firebase history), where incidents live (PagerDuty, Opsgenie, Linear, a sheet), team size, and the reporting window. If deploys aren't tagged or incidents aren't logged, say so — that gap is the first finding.

## Step 3: Definitions (Cure standard)

DORA's current set is five metrics (dora.dev/guides/dora-metrics, updated 2026-01-05). "MTTR" is the legacy name; DORA now says **failed deployment recovery time**.

| Metric | Cure definition | Measure with |
|---|---|---|
| Deployment frequency | Successful **production** deploys per period (features, fixes, config). Exclude staging/preview deploys and rollbacks. | `scripts/deployment_frequency.py` (tags or commits) |
| Change lead time | First commit of the change → running in production. Report **median and p95**, never mean. Break down: code → review → merge → deploy to find the bottleneck. | GitHub PR + deploy timestamps (reference) |
| Change fail rate | Deploys needing **immediate intervention** (rollback, hotfix, incident, flag kill) ÷ total production deploys. Vendor outages and planned maintenance don't count. | `scripts/change_failure_rate.py` |
| Failed deployment recovery time | Failing deploy reaches production (or impact start, if later) → service restored (rollback, roll-forward, or flag off). Restored, not root-caused. | `scripts/mttr_calculator.py` on deploy-caused incidents |
| Deployment rework rate | Unplanned deploys made because of a production incident ÷ total deploys. | Tag hotfix deploys; count |

**Incident MTTR (all incidents, not only deploy-caused)** — the number incident-response and post-mortems report: **impact start** (earliest evidence of user impact, backfilled from logs — not the alert time) → **service restored**. Report median per severity. Sub-intervals: MTTD = impact start → detection; MTTA = detection → human engaged; time to restore = impact start → restored. Using detection as the start hides slow detection, which is usually the biggest lever.

Gotchas:
- The scripts read `opened_at`; populate it with **impact start**, not the ticket-creation time.
- Count rollbacks as the recovery event of the failed deploy, not as a new deploy.
- Monorepos: measure per deployable service, or frequency is inflated by unrelated deploys.
- Mobile store releases have review lag; report lead time to *submitted* and to *available* separately.

## Step 4: Benchmarks (dated)

DORA 2024 report clusters — the last report to publish tiers; the 2025 report replaced tiers with seven team archetypes, so cite these as "2024 clusters" and compare a team mainly to its own trend.

| Cluster (2024) | Lead time | Deploy frequency | Change fail rate | Recovery time |
|---|---|---|---|---|
| Elite | < 1 day | On demand | ~5% | < 1 hour |
| High | 1 day – 1 week | Daily – weekly | ~20% | < 1 day |
| Medium | 1 week – 1 month | Weekly – monthly | ~10% | < 1 day |
| Low | 1 – 6 months | Monthly – biannually | ~40% | 1 week – 1 month |

The 2024 medium cluster had a lower fail rate than high — the metrics no longer move together, so never collapse them into one "level". Cure targets for client product teams: deploy at least daily to staging and weekly to production, lead time < 1 week, change fail rate ≤ 15%, recovery < 1 day. Regulated or store-gated teams: weekly production cadence is acceptable.

## Step 5: Collect and Analyze

Run the bundled scripts (stdlib Python, `--help` and `--json` on each). Paths are relative to this skill's directory; with the plugin enabled in Claude Code they are also on PATH as `cure-deploy-frequency`, `cure-change-failure-rate`, `cure-mttr`.

```bash
python3 scripts/deployment_frequency.py --repo . --since <start> --until <end> --json   # tags matching ^v\d by default
python3 scripts/change_failure_rate.py --csv deployments.csv --json   # id, deployed_at, caused_incident
python3 scripts/mttr_calculator.py --csv incidents.csv --severity SEV1,SEV2 --json   # id, opened_at, resolved_at[, severity]
```

If the team has no deploy log or incident CSV, build them from tags/workflow runs and the incident tracker first; the reference file has GitHub Actions snippets for lead time and PR metrics. Read `reference/details.md` § Data Collection when the team needs continuous collection rather than a one-off baseline.

Bottleneck reading: long code time → stories too big; long review time → PRs > 200 lines or too few reviewers; long merge time → slow CI or heavy approvals; long deploy time → manual release trains. High fail rate with fast deploys → add canary/staged rollout and automated rollback before pushing frequency further.

Rules that protect the data: metrics are team-level only — never rank individuals by PRs, commits, or lines (it destroys the signal and trust); compare a team to its own history, not to other teams; automate collection so nobody hand-edits counts; every review produces at least one funded action.

## Step 6: Output

Match length to the need; no filler sections or restated summaries.

```
DORA REPORT — [team] — [window]            Data sources: [tags / workflow runs / incident tracker]
Metric                         Value (median/p95)   vs last period   2024 cluster   Source
Deployment frequency           …
Change lead time               …
Change fail rate               …
Failed deployment recovery     …
Deployment rework rate         …
Incident MTTR by severity      …
Data gaps: …
Top bottleneck + next 1–3 actions (owner, expected metric movement): …
```

Cross-references: `ci-cd-pipeline` (pipeline speed, automated rollback), `incident-response` (incident logging that feeds MTTR), `feature-flags` (decouple deploy from release).

## Code/Artifact Generation

Applies only when Step 1 classified the request as **Build collection** (or the user asks for automation). Write:

1. `.github/workflows/dora-report.yml` — scheduled job that runs the three bundled scripts and uploads the JSON as an artifact.
2. `docs/dora-report-template.md` — the Step 6 template.
3. Optional `monitoring/dora-dashboard.json` when the team names a dashboard tool (Grafana/Datadog/Looker).

Reuse the bundled scripts; don't write a second collector.
