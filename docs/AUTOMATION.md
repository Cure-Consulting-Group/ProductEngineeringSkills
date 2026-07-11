# AUTOMATION — Recurring Execution Recipes

Copy-paste recipes for putting Cure engagement work on autopilot with Claude
Code's recurring-execution mechanisms. Mechanism selection and the full
guardrail policy live in the `/engagement-automation` skill; this doc is the
recipe book.

**The unattended-run rules (non-negotiable):**

1. Unattended runs are read-only: they report, humans apply. Production
   deploys, migrations, auto-merged upgrades, secrets, and billing are never
   automated.
2. Every cloud routine gets a per-run token limit and a daily run cap.
3. Every run delivers its result somewhere durable (issue, PR comment, report
   file). Output that only exists in a transcript doesn't exist.
4. Routines run on Anthropic infrastructure with no local permission prompts —
   scope them as if the least careful person on the team wrote the prompt.
5. Interactively-authenticated MCP servers are absent in headless runs. Don't
   build a routine around one.
6. Every iteration terminates — non-blocking is non-negotiable. No watch mode,
   no dev servers, no interactive prompts, hard timeouts on slow checks. A
   blocked iteration doesn't fail loudly; it silently kills the automation.

---

## Session loops (`/loop`) — while you work

The project maintenance loop (vendored to `.claude/loop.md` at install):

```
/loop
```

Fixed-interval skill runs:

```
/loop 30m check CI on this branch and fix failures as they appear
/loop 1w /cure-product-engineering:burn-rate-tracker
```

Self-paced, goal-driven (the model chooses its cadence and stops itself):

```
/loop keep the test suite green; stop when it passes 3 consecutive runs or after 5 fix attempts, and report either way
```

Notes: loops are session-scoped (die with the session), expire after 7 days,
and only fire skills Claude may auto-invoke — never `disable-model-invocation`
on a loopable skill.

## Cloud routines (`/schedule`) — no machine required

### Weekly dependency + security audit

```
/schedule Every Monday 07:00: run a dependency audit (outdated packages,
known CVEs by severity) and a security sweep of code changed in the last week.
Read-only. File one GitHub issue titled "Weekly audit YYYY-MM-DD" with findings
ranked by severity; if nothing found, still file it with "clean".
```

Budget: ~150k tokens/run, 1 run/day cap.

### Monthly investor-update draft

```
/schedule First business day of each month 08:00: draft the monthly investor
update using the investor-reporting skill — metrics deltas, milestones from
merged PRs, risks. Write to reports/investor-update-YYYY-MM.md as a DRAFT.
Never send anything; a human reviews and sends.
```

Budget: ~120k tokens/run, 1 run/day cap.

### PR-triggered review (GitHub webhook)

```
/schedule On pull request opened or ready-for-review: run the security-review
skill against the PR diff only. Post findings as PR comments with file:line
references; approve nothing, merge nothing, request no changes formally.
```

Budget: ~100k tokens/run. Cap daily runs to your realistic PR volume — a
runaway webhook is the classic four-figure surprise.

### API-triggered incident triage

```
/schedule API trigger: given an incident description in the trigger payload,
run incident-response triage — classify severity, identify likely subsystems
from the repo, produce a first-response checklist. Post to the incident issue.
Read-only; humans execute the runbook.
```

Budget: ~80k tokens/run, cap 10 runs/day.

## CI cron — when no LLM judgment is needed

Deterministic checks (lint, `npm audit --audit-level=high`, license scans,
link checkers) belong in `.github/workflows/` on a cron, not in an LLM loop.
Scaffold with `/ci-cd-pipeline`. Rule of thumb: if a shell script's exit code
answers the question, tokens are the wrong currency.

## Liveness

Automations rot silently: loops expire in 7 days, webhook secrets rotate, auth
lapses. Put a monthly "verify the automations still run" line in the
engagement's ops checklist, and treat a missing weekly report as an incident,
not a shrug.
