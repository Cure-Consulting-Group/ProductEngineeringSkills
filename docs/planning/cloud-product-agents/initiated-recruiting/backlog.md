# Initiated Recruiting integration backlog

Prepared 2026-09-28. Hours are founder-active implementation and targeted validation estimates, before one 20% reserve. One founder owns delivery; runtime agent roles do not add human sprint capacity. The 82–148 base-hour range is a planning estimate, not measured velocity. Stories extend the [shared backlog](../backlog.md) and reference [Recruiting requirements](scope.md).

| Story | Requirement | R-sprint | Base hours | Done when |
|---|---|---|---:|---|
| IR-101 Inventory deployments, permissions, fixtures and baseline | IR-01, 02, 11 | R1 | 6–10 | Deployed revision is read from authorized source; environment and credential map is recorded; 7–14 days of current coordination work has task-level timing; missing access is listed as blocked. |
| IR-102 Claim adapter | IR-03, 07 | R1 | 8–12 | A disposable athlete claim produces expected review, captured notification and approval/ownership outcomes; seeded broken trigger and wrong owner fail; GA4 absence in E2E is not counted as funnel loss. |
| IR-103 Coach verification and Terminal adapter | IR-04, 11 | R2 | 14–24 | Unverified and revoked test coaches are denied; verified bound test coach sees only intended program data; mock admin bypass is off; stale compute and blocked OTP fixture are classified correctly. |
| IR-104 Discovery and recruiting-board adapter | IR-05 | R2 | 8–14 | Search/profile/board path matches authorized fixture state; offer/watchlist/commit, empty state and program A/B isolation pass; wrong-program row is caught. |
| IR-105 GA4/PM signal adapter | IR-06, 07, 13 | R3 | 8–16 | Deployed event names are reconciled with GA4; aggregates record cohort, dates, lag and denominator; low-volume or missing instrumentation returns insufficient data; PM rubric distinguishes observation from hypothesis. |
| IR-106 Data health and freshness adapter | IR-02, 05, 13 | R3 | 6–12 | Existing integrity, board parity and Terminal evidence is consumed by revision and freshness; a stale report or binding mismatch cannot produce a green result. |
| IR-107 Design and accessibility review | IR-06 | R3 | 8–14 | Redacted desktop/mobile states include loading, denied, empty and error; versioned rubric and screenshot provenance exist; independently verified defects are separate from subjective friction. |
| IR-108 Held-out evaluation and independent QA | IR-03–08, 11 | R3–R4 | 10–20 | At least 40 independently labeled feasibility cases cover all three journeys, no-change, stale fixture, known issue, access bypass and instruction injection; repeat representative cases; expand to 100/profile before broader unattended use. |
| IR-109 Scoped repair and outcome lifecycle | IR-09, 10, 11 | R4 | 8–16 | Policy denies protected paths; authorized patch is draft-only, tied to current SHA and independently rechecked; post-release outcome references actual deployed revision and can remain pending/unknown. |
| IR-110 Operations, isolation and Recruiting dashboard | IR-01, 08, 12 | R1–R4 | 6–10 | Shared dashboard shows due/completed/blocked runs, finding evidence and marginal cash; duplicate/stale findings coalesce; cross-product negative tests pass; shared schedules stay in GCP. |
| **Total** |  |  | **82–148** | **98–178 hours with 20% reserve** |

Acceptance uses *given/when/then* checks, including failures rather than only happy paths:

- **Claim:** Given a disposable athlete and an unclaimed fixture profile, when the claim is submitted, then one review record and captured notification appear. Given a missing trigger or a mismatched owner, the report names that failure and does not mark the journey healthy.
- **Coach/Terminal:** Given an unverified, verified-bound, revoked and wrong-program coach, when each accesses Terminal, then only the verified-bound identity receives its authorized program data. A development mock-admin session invalidates the access result.
- **Board:** Given two isolated programs and a known offer/watchlist/commit fixture, when a coach searches and views a board, then rows and empty states match the authorized state; another program's data is denied.
- **Analytics:** Given an E2E run with no measurement ID, when review runs, then it uses synthetic assertions only. Given production GA4 aggregates with a sparse denominator or stale event mapping, then it reports insufficient evidence and no uplift conclusion.
- **Repair:** Given an approved low-risk finding and current base revision, when a worker proposes a patch, then it creates at most one draft for that work order after policy and independent QA. Given a protected path, stale base, failed reproduction or missing evidence, then publication is denied or held.

The effort assumes usable shared control-plane primitives, stable staging/emulator fixtures, current CI artifacts and approved read access. A new Firebase auth redesign, unstable Terminal source pipeline, missing GA4 property access or large evaluation-bank authoring effort adds work and moves the gate. Do not treat the 16–32 hour generic second-product onboarding placeholder in the shared cost model as covering these Recruiting-specific journeys. Its provisional Sprint 9 slice is replaced by [R1–R6](sprint-plan.md); count work once.
