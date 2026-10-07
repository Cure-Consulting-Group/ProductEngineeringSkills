# Initiated Recruiting — six two-week sprints

Prepared 2026-09-28. Start after HoopTrace G7 or an explicit narrower shared-platform decision. R1–R6 replace the **Recruiting portion** of provisional shared Sprint 9; shared Sprint 10's HoopTrace mobile/hardening work is separate. This is an incremental second-product plan, with no second platform build. Rashad has 20 focused hours/week (40 per sprint). Commit at most 34 hours in a full implementation sprint, leaving at least six hours for access, fixture and support variance. Observation sprints deliberately commit fewer hours; their uncommitted capacity is not a hidden estimate for extra features.

| Sprint | Weeks after start | Committed hours | Capacity buffer / uncommitted | Outcome and gate |
|---|---:|---:|---:|---|
| R1 | 1–2 | 28 | 12 | Live release/permission inventory, 7–14-day current-workflow baseline, claim adapter; G-IR1 fixture and provenance correctness |
| R2 | 3–4 | 30 | 10 | Coach/Terminal and board adapters; G-IR2 identity/program isolation |
| R3 | 5–6 | 30 | 10 | GA4, data freshness, design/PM and held-out cases; G-IR3 evidence quality and missing-data behavior |
| R4 | 7–8 | 20 | 20 | 14-day read-only shadow, adjudication and bounded repair policy; G-IR4 shadow quality/safety |
| R5 | 9–10 | 16 | 24 | Matched live comparison weeks 1–2; G-IR5 interim sample integrity |
| R6 | 11–12 | 16 | 24 | Comparison weeks 3–4, accepted outcomes and expand/extend/restrict decision; G-IR6 measured value |

The 140 committed hours fit 240 nominal focused hours over 12 weeks, with 100 uncommitted across observation and implementation. This schedule does **not** imply the full 98–178-hour build range can always finish by R4: R1–R4 commit 108 build/validation hours. Use remaining capacity for approved variance where gates permit; if high-end build or an access block exceeds it, extend the sprint sequence. Measurement windows must not be shortened to recover build delay.

## Sprint commitments

**R1 — baseline and claim (28 h):** inventory release/CI/GA4/staging permission and revision evidence (6); define current AI-assisted task baseline and log actual founder minutes (6); implement claim fixture/read adapter (10); record product manifest, isolation and initial dashboard state (6). Gate: valid fixture reaches review and approval with captured mail, wrong-owner/missing-trigger cases fail, and actual deployment revision is known. If fixtures or read access are unavailable, record blocked state and spend buffer on recovery before declaring the gate.

**R2 — controlled journeys (30 h):** coach verification and Terminal authorization/freshness adapter (16); board/discovery/parity adapter (10); cross-program and mock-admin-negative checks (4). Gate: unverified/revoked/wrong-program denial, correct verified binding and board rows pass in a production-like auth mode. Known two-clocks failures are labeled as known/fixture/system defects based on reproduction, not retried into false green.

**R3 — evidence and evaluation (30 h):** reconcile actual GA4 event map and aggregate denominators (8); data-health/freshness source (5); PM/design rubric plus redacted viewport states (7); held-out feasibility bank and adjudication (10). Gate: at least 40 independent labeled cases across three journeys, no-change, stale evidence, duplicate and access attacks; source-version provenance on every result; low-volume production funnels return insufficient data. The 40 cases test feasibility; build toward at least 100 per active review profile before broader unattended release.

**R4 — read-only shadow (20 h):** operate and adjudicate 14 days (8); fix triage/dedup/blocked classification and per-product cost display (5); authorize and test low-risk draft repair policy in isolated cases (5); freeze comparison design and readiness review (2). Gate: at least 95% due-run completion, at least 80% actionable precision with denominator, at least 90% held-out critical-journey recall with denominator, complete evidence on actionable findings, zero forbidden access. Aim for 30 adjudicated findings across controlled and live cases, reported separately. If the data are too sparse or quality misses, extend shadow operation. Read-only quality does not itself prove time savings.

**R5 — comparison weeks 1–2 (16 h):** operate assigned tasks and adjudicate all findings/repair attempts (8); reconcile time/cash and matched-class integrity (5); review sample and policy drift (3). Gate: every eligible task has arm, class, release, founder-active minutes, outcome and attributable spending. No midtrial prompt or policy change is silently pooled. Only authorized low-risk patches become drafts; human release authority remains.

**R6 — comparison weeks 3–4 (16 h):** finish task and independent repair adjudication (8); analyze matched time, quality and cost with uncertainty (5); decide expand/extend/restrict/stop and reforecast (3). Target at least 20 eligible live tasks per arm before quoting efficiency and at least 20 assigned repair attempts before quoting repair acceptance. Low volume extends the measurement period, not the claim. Release follow-up checks behavior at actual deployed revision immediately and 24–72 hours later; product conversion needs a separate valid cohort window.

## Measurement and decision protocol

The control arm is the founder's existing AI-assisted workflow, not unaided manual work. The assisted arm receives cloud evidence, routed specialist review and any permitted draft repair. Pre-register eligible task types and pair/randomize by journey and estimated difficulty. Keep linked findings from the same release together to reduce information leakage. Critical incidents follow the normal safety workflow outside the randomized trial and remain disclosed. Record failures, no-change results and rejected patches in assigned denominators.

Net coordination saving per comparable class is control founder coordination minutes minus assisted founder triage/review/correction minutes minus attributable operating/maintenance minutes. Track coding time, product research and common experiment adjudication separately. Build hours are investment, not monthly savings. Report totals and medians by class, task counts, precision, held-out recall, repair acceptance, due-run completion, evidence completeness, cost per useful finding/accepted repair and forbidden-access events. Production GA4 funnel movement is observational and separate from synthetic test pass rate; no revenue or conversion uplift is inferred from a small sample.

At G-IR6, expansion needs equal-or-better quality, at least 30% lower net coordination time on comparable scope, precision at least 80%, due-run completion at least 95%, zero forbidden access and acceptable marginal cost. Repair acceptance target is at least 60% only with 20+ attempts. A four-week window without enough eligible tasks yields an **extend** or narrower read-only decision. Reforecast all cloud and founder hours from measured Recruiting marginal usage before expanding to IR-14 journeys.
