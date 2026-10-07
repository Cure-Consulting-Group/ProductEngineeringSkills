# PRD-CPA-IR-001 — Initiated Recruiting product-agent integration

Date: 2026-09-28. Owner: Rashad. Parent: [shared platform PRD](../scope.md). Proposed second-product scope, contingent on HoopTrace G7. This document supersedes the Recruiting-specific order in the initial cross-product plan while retaining its shared-platform contracts.

## Problem and outcome

Recruiting serves athletes, parents, club/director staff, verified college coaches and administrators. A code-level review cannot establish whether a profile claim really reaches review, whether the right coach sees the right program data, or whether board data remains consistent. Manual checks must combine browser behavior, emulator state, release evidence and real-user analytics. The platform should gather that evidence continuously, classify failures accurately, prepare bounded repairs, and report whether a released fix worked.

Success is fewer founder coordination hours **at equal or better quality**. No agent gets to invent athlete evaluations, scholarship spend, coach identity, NIL terms, revenue, or a product growth claim. Product decisions remain with Rashad; development and deployment rules in the Recruiting repository remain authoritative.

## Initial journeys and sources of truth

| Journey | Contract and evidence | Failure classes |
|---|---|---|
| Athlete finds and claims profile | `claim_started → claim_submitted`; backend `pending_review` and notification/mail queue; approval produces verified ownership and an active visible profile. Source: claim E2E and tracking plan. | Claim broken; trigger fan-out missing; inappropriate duplicate; wrong identity; stale analytics |
| Coach verification → Terminal | Unverified coach denied; admin review + institutional OTP + correct program binding grants intended access; email/identity change revokes it. Terminal data follows approved freshness and program boundaries. | Access bypass; wrong program; missing/stale metrics; failed revocation; test auth bypass |
| Coach discovers athlete → recruiting board | Search/profile/board path, offer/watchlist/commit representation, program isolation and empty state. Source: board E2E and parity gate. | Missing/misclassified row; cross-program disclosure; action fails; fixture drift |
| Data health and freshness | Consume integrity/board parity evidence, approved aggregate reads, `terminal_qa_reports` and compute freshness where access exists. | Broken feed; stale compute; binding mismatch; authorization unknown |
| Design and accessibility | Rendered athlete/coach journeys at mobile and desktop sizes; loading, denied, empty and error states. | Friction hypothesis or verified accessibility/layout defect |
| Product analytics | GA4 claim and scouting funnel summaries, role/cohort denominators and source/version metadata. | Tracking gap, low-volume unknown, credible shift requiring investigation |

Use actual deployed revision and environment, not a historic doc or local branch name, as the review target. The local checkout inspected for this plan had `dev` at 2026-09-24 and a locally stale `main` reference; these are snapshots, not a claim about current production. Discover live release state through authenticated GitHub/Firebase read adapters at implementation.

GA4 is the approved analytics provider. The [tracking plan](</Users/rashadcureton/Documents/Cure-Consulting-Group/initiated-recruiting/docs/tracking-plan.md>) includes older PostHog wording in places, so verify deployed event names and GA4 source before measuring. Emulator/E2E builds omit the measurement ID; do not interpret synthetic sessions as production conversion. [Claim test](</Users/rashadcureton/Documents/Cure-Consulting-Group/initiated-recruiting/tests/e2e/flows/claim-funnel.e2e.ts>), [coach verification test](</Users/rashadcureton/Documents/Cure-Consulting-Group/initiated-recruiting/tests/e2e/flows/coach-verification-lifecycle.e2e.ts>), and [board test](</Users/rashadcureton/Documents/Cure-Consulting-Group/initiated-recruiting/tests/e2e/flows/recruiting-board.e2e.ts>) provide behavioral anchors.

## Goals and acceptance measures

| Measure | Baseline method | Proposed gate |
|---|---|---|
| Founder coordination time | 7–14 days of existing workflow by task type; measure current AI-assisted work | At least 30% lower net coordination time on comparable task classes, if sufficient task volume |
| Confirmed finding precision | Human adjudication with independent reproduction | At least 80% of proposed actionable findings, including false positives in denominator |
| Critical-journey defect recall | Held-out seeded/historical defects in isolated fixtures | At least 90% on the labeled bank, with denominator reported |
| Repair acceptance | Every assigned attempt, including failures | At least 60% accepted after independent QA, if at least 20 attempts |
| Access-policy safety | Negative cases for unverified, revoked and other-program coach; athlete ownership | Zero unauthorized reads/writes or forbidden tool calls |
| Due-run completion | Scheduled manifest versus recorded completions | At least 95% within the configured window |
| Cost and evidence | Provider metering, CI/job minutes, founder minutes per task | Every run has source revision, outcome, cost and blocked reason when applicable |
| Product funnel outcomes | Production GA4 with consistent event/cohort denominator | Report observed changes only when data is sufficient; no numeric uplift promise |

These are proposed gates, not current performance claims. A four-week trial can still be inconclusive if eligible live tasks or real users are few. The system must say "insufficient evidence" instead of treating a sparse funnel as a product improvement.

## Requirements

| ID | Priority | Requirement |
|---|---|---|
| IR-01 | Must | Register Recruiting's product goals, approved journeys, release and environment mapping in shared platform |
| IR-02 | Must | Read current CI/release status, approved issues and aggregate product signals with source provenance |
| IR-03 | Must | Run isolated profile claim journey and classify product failure versus fixture/auth/trigger failure |
| IR-04 | Must | Run verified/unverified/revoked coach and Terminal program-access checks |
| IR-05 | Must | Validate recruiting board behavior, program isolation, empty state and data parity |
| IR-06 | Must | Use versioned PM/design rubrics and screenshots for athlete/coach journeys |
| IR-07 | Must | Keep GA4 production funnels separate from synthetic E2E data and report insufficient denominators |
| IR-08 | Must | Deduplicate findings against known tickets, stale evidence and existing CI failures |
| IR-09 | Must after read-only gate | Prepare only scoped draft repairs and obtain independent QA verdict |
| IR-10 | Must | Track deployment and 24–72 hour behavior follow-up, with later product-metric review when adequate data exists |
| IR-11 | Must | Enforce role-specific privacy, product isolation, no-customer-contact and spend limits |
| IR-12 | Must | Show Recruiting in shared dashboard/digest with due-run, evidence, costs and decision state |
| IR-13 | Should | Analyze claim/scouting funnel drop-off by valid cohorts and data freshness |
| IR-14 | Could, later | Coach recruiting-loop and subscriptions expansion after initial journeys validate |

Out of scope: new agent-facing features inside Recruiting, changing production Firestore documents, approving real coach verification, processing real athlete claims, sending email, contacting coaches/athletes, charging Stripe, legal/NIL determinations, publishing scouting evaluations, automatic merge/deploy, and changing established deployment triggers. Synthetic write tests use emulators or approved disposable staging fixtures and captured email. No browser-agent action may use live customer accounts.

## Autonomy and review

Start read-only. Shared platform A0/A1/A2 policy applies, but HoopTrace permissions do not transfer to Recruiting. Explicit Recruiting-scoped configuration is needed for bot-owned issues and draft PR writes. Identity, rules, payments, minors' data, athlete publication, coach access, legal terms and source-data repair are review/proposal only by default. A repair worker may change allowlisted low-risk UI or tests after its category is authorized; an independent reviewer must rerun the original case. Source claims and product copy affecting real athletes need product-owner acceptance.

The Recruiting repo deliberately blocks GitHub Actions cron and runs heavy E2E at release or on demand. Schedule lightweight read-only checks in GCP and reuse CI artifacts by SHA. Do not cause the cloud service to dispatch full E2E nightly. The documented two-clocks E2E problem is a known test/production-time diagnosis to classify; do not label every failure a new product regression or hide the underlying bug with retries.

## Rollout and gates

1. **R0 ready:** HoopTrace platform G7 meets its evidence/time decision, or a deliberately narrower shared platform is accepted. Verify current Recruiting deployed revisions, staging isolation, GA4 read access and test fixtures.
2. **R1–R3 integration:** claim, coach/Terminal, board/data and PM/design adapters with held-out correctness/access cases. Gate: no cross-product access and reproducible behavioral truth.
3. **R4 shadow:** 14 days of read-only review, human adjudication, source freshness and cost measurement. Gate: actionable precision, reliability, safety and missing-data handling.
4. **R5–R6 comparison:** four weeks of matched current-workflow versus cloud-assisted tasks, with authorized low-risk repairs only if safe. Decision: expand, extend, restrict or stop. Low task volume means extend, not fabricate significance.

Retain raw evidence according to shared retention policy; role/identity data is minimized. GA4 summaries use counts/cohorts, not a dump of individual athlete or coach identities. The shared platform remains the system of record for runs and findings; Recruiting's existing source repo remains the system of record for product code and release policy.

Open implementation facts: current production revision and function allow-list, GA4 query access and event integrity, known E2E flake status, staging test account validity, actual live task volume, baseline founder coordination time, and approval of any draft-PR write categories. Resolve these in R1 before relying on modeled costs or announcing a launch date.
