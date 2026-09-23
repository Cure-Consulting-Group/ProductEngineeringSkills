# incident-response: reference

Read only the section the current mode needs: **Runbook phases** when writing runbooks,
**Communication templates** when drafting a status update, **Post-mortem template** when writing one.

## Runbook phases

**Detection (automated first):** Crashlytics crash-free users drop > 1 point; uptime check failing
from 2+ regions; Functions v2 / Cloud Run 5xx ratio > 5% over 5 min (`run.googleapis.com/request_count`
by `response_code_class`); Sentry error-volume spike; Stripe webhook failure alerts. Manual: support
ticket spike, social reports, dogfooding.

**Triage (first 15 min):** acknowledge the page and post "Investigating …" in `#incidents` → set
severity (SKILL.md Step 3) → SEV1/2: open the incident channel, assign Incident Commander, Tech Lead,
Comms Lead → check recent changes: `gcloud run revisions list`, Functions logs (last 30 min), merged
PRs, Remote Config / flag history → strong deploy correlation = roll back now.

**Mitigation:** SKILL.md Step 4 order and commands. Firebase specifics: Firestore → hotspots,
contention, rules denials; Functions → memory/timeout, max-instances ceiling, concurrency; Auth →
Identity Platform and OAuth provider status; Storage → bucket IAM and CORS. Mobile → Remote Config
kill switch, minimum-version gate, server-side toggle.

**Resolution:** error rate, latency, and health checks back to baseline; smoke-test the affected
flow; watch 30 min (SEV1/2) for recurrence; mark resolved in channel and status page; export logs
before retention expires and screenshot the dashboards for the timeline.

## Communication templates

Internal update (`#incidents`), every cadence tick:
```
[SEV-X] <system> — <Investigating | Identified | Mitigated | Resolved>
Impact: <what users see, who, where>   Started: <UTC>   Duration: <h:mm>
Done: <actions so far>   Next: <next action, ETA if known>
Next update: <UTC>   IC: <name>
```

Customer — active:
```
Subject: Service disruption — <feature>
We're seeing issues with <feature> that may affect <user action>. We identified it at <time UTC>
and are working on a fix. Not affected: <unaffected areas>. Next update by <time>. Help: <channel>.
```

Customer — resolved:
```
Subject: Resolved — <feature> disruption
Resolved at <time UTC> (<start>–<end>). What happened: <plain-language cause>.
What you saw: <impact>. What we're changing: <1–2 actions>. Still seeing issues? <channel>.
```

Leadership briefing: one-sentence TL;DR with revenue impact; timeline (began, detected, engaged,
mitigated, resolved); users affected, revenue, data exposure yes/no, SLA breach yes/no; root cause in
one plain paragraph; top 2–3 actions with owners and dates.

Breach or personal-data exposure: stop and route customer/regulator notices through counsel —
notification deadlines and content are regulated (see compliance-architect).

## Post-mortem template

```
POST-MORTEM: <title>        Date · Severity · Author · Status (Draft/In review/Final)
SUMMARY        2–3 sentences: what happened, impact, resolution
TIMELINE (UTC) impact start · detected (how) · engaged · root cause found · mitigated · resolved
DETECTION      time to detect; could we have detected sooner?
ROOT CAUSE     specific: code, config, or infrastructure; systems, not people
CONTRIBUTING   missing alert, no staged rollout, untested path, …
IMPACT         duration · users (#/%) · revenue · data · SLA credits
WENT WELL / WENT WRONG
ACTIONS        # | action | category (Prevent/Detect/Mitigate/Process) | priority | owner | due
REVIEW         reviewers · date · action follow-up date (≈2 weeks)
```
