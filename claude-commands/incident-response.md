# Incident Response

**Outcome depends on the mode Step 1 picks:**
- **Live incident** — a severity call, the next 1–3 mitigation actions with exact commands, and the next status message. Done when the service is restored and a post-mortem owner is named. **Write no files and scaffold no code during a live incident**: every minute spent generating artifacts extends user impact, and unreviewed code shipped mid-incident is a common cause of a second outage.
- **Post-mortem** — a blameless write-up with a timeline and Prevent/Detect/Mitigate/Process actions. Done when every action has an owner and a date.
- **Build on-call** — runbooks, rotation, escalation matrix, and templates for a system. Done when a new on-call engineer could follow them unaided.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):
- Recent changes (the first suspect in most incidents): `git log --since="3 days ago" --oneline 2>/dev/null | head -10 || echo "(not a git repo)"`
- Existing runbooks: `ls docs/runbooks/ docs/post-mortems/ 2>/dev/null | head -10 || echo "(none)"`

## Step 1: Classify the Mode

| Mode | Signal | Go to |
|---|---|---|
| Live incident | "down", "errors spiking", "users can't…", alert firing now | Step 3 → Step 4 |
| Post-mortem | Incident is resolved; user wants the write-up | Step 5 |
| Build on-call | Runbooks, rotation, escalation, templates, tooling | Step 6 + Code/Artifact Generation |

Within a live incident, also classify the type — it decides the first move:

| Type | First move |
|---|---|
| Outage / degradation after a deploy or flag change | Roll back or flag off before diagnosing |
| Security breach (leaked key, unauthorized access) | Rotate/revoke credentials, isolate, **preserve logs** before cleanup; page security lead |
| Data loss / corruption | Stop writes to the affected collection or service; do not "fix forward" over evidence; check PITR/backup state (see disaster-recovery) |
| Capacity / performance | Find the bottleneck; scale or shed load |
| Third-party (Stripe, Vercel, GCP, APNs/FCM) | Confirm on the vendor status page; activate fallback; tell customers it's upstream |

## Step 2: Gather Context

Ask only what isn't already known: what users see, when it started (impact start, not alert time), what changed recently (deploys, flags, config, dependency bumps, traffic), how many users/which segments, and whether the blast radius is growing. In a live incident, ask at most two questions before recommending a first action.

## Step 3: Severity (Cure thresholds)

| Sev | Impact | Respond | Escalate | Comms |
|---|---|---|---|---|
| SEV1 | Service down, active data loss, or **any** confirmed breach; >50% users | ≤5 min | On-call → eng lead (10 min) → CTO (15 min) | Status page ≤15 min, customer email ≤1 h, updates every 30 min; dedicated channel `#incident-YYYY-MM-DD-slug` + call bridge |
| SEV2 | Core flow broken (auth, checkout, sync) or 10–50% users | ≤15 min | On-call → team lead (30 min) → eng lead at 1 h | Status page ≤30 min; customer comms if >1 h; hourly updates |
| SEV3 | Non-critical feature broken, workaround exists, <10% users | ≤1 h business hours | Owning team | Internal thread; updates every 4 h |
| SEV4 | Cosmetic, staging, or internal tooling | Next business day | Backlog | Ticket only |

When unsure between two levels, pick the higher and downgrade later — under-declaring delays the people who can fix it. Payments/Stripe incidents escalate to the CEO as exec sponsor; everything else to the CTO.

## Step 4: Live Incident — Mitigate First

Mitigation order: roll back → disable via feature flag / Remote Config → scale or shed load → maintenance mode → fail over → block abusive traffic (Cloud Armor/WAF). Diagnose root cause after impact stops.

Cure stack rollback commands (confirm project/site/service names before running; each changes production):

```bash
# Firebase Hosting — restore a known-good version to live
firebase hosting:clone <SITE_ID>@<VERSION_ID> <SITE_ID>:live
# Cloud Functions v2 / Cloud Run — shift traffic back to the previous revision
gcloud run revisions list --service=<svc> --region=<region> --limit=5
gcloud run services update-traffic <svc> --region=<region> --to-revisions=<prev-revision>=100
# Vercel — promote the previous production deployment
vercel rollback <deployment-url-or-id>
```

Gotchas:
- Mobile builds can't be rolled back in the stores — use Remote Config kill switches or a forced minimum version; halt a staged rollout in Play Console / App Store Connect.
- Firestore has no capacity knob. Errors under load are usually hotspotting (sequential IDs, ramp faster than the 500/50/5 rule), transaction contention, or security-rule failures — check those, not "scale up".
- A Cloud Functions redeploy from `main` is not a rollback if `main` contains the bad change; shift traffic to the old revision instead.
- After `vercel rollback`, production domains stop auto-assigning to new deploys until you `vercel promote` the fixed deployment — note it in the incident log.
- Rotate secrets in Secret Manager / 1Password and redeploy consumers; revoking alone breaks the running service.

After each action, give the next status update text (read the Communication templates section of `reference/details.md` when drafting customer-facing or leadership messages). Record timestamps as you go — they become the post-mortem timeline and the MTTR input.

## Step 5: Post-Mortem

Blameless: systems and decisions, not people. Required for SEV1/SEV2 (draft within 48 h, review within 5 business days), encouraged for SEV3. Read the Post-mortem template section of `reference/details.md` when writing one. Every post-mortem has at least one action in each category — **Prevent, Detect, Mitigate, Process** — each with an owner and due date in the issue tracker; repeat incidents (same root cause) are the headline metric.

Metric definitions (MTTR, MTTD, MTTA, impact start vs. detection) are owned by `dora-metrics` — use its definitions so incident reports and delivery metrics agree. Cure response targets: MTTD < 5 min (SEV1) / < 15 min (SEV2); MTTA < 5 min for SEV1/SEV2; restore < 1 h (SEV1) / < 4 h (SEV2); false-positive page rate < 10%.

## Step 6: On-Call Setup

- Rotation: 1-week primary + secondary, ≥2 people, no back-to-back weeks, 15-min handoff reviewing open issues and recent deploys; auto-escalate to secondary after 10 min unacknowledged.
- Escalation matrix (primary → secondary → exec): Firebase/GCP: platform eng → eng lead → CTO · Android/iOS: platform lead → mobile team → CTO · Web/Next.js: frontend lead → full-stack → CTO · API/Functions: backend lead → platform eng → CTO · Payments/Stripe: backend lead → eng lead → CEO · Auth/security: security lead → eng lead → CTO.
- Access checked at onboarding, not during the incident: pager app, GCP/Firebase consoles (Viewer; production Editor via just-in-time grant), Sentry/Crashlytics, dashboards, status-page admin, Stripe dashboard, 1Password emergency vault, vendor status pages bookmarked.
- One runbook per top failure mode, each with: symptoms, dashboards, first three commands, rollback, owner. Read the Runbook phases section of `reference/details.md` when writing runbooks.

## Code/Artifact Generation

Applies only when Step 1 classified the request as **Build on-call** (or a post-mortem the user wants saved). Never during a live incident. Match existing formats in `docs/runbooks/` if present. Write only what was asked:

1. `docs/runbooks/<failure-mode>.md` — one per failure mode named.
2. `docs/post-mortems/template.md` and/or the filled post-mortem.
3. On request only: pager-webhook function, Slack Block Kit announcement JSON, status-page update script.

Match length to the need; no filler sections or restated summaries.
