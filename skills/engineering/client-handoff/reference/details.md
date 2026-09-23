# client-handoff: long-form templates

> Read when drafting the architecture document, the knowledge-transfer session plan, or the
> maintenance SLA. The procedure, runbook format, credential protocol, and sign-off checklist live
> in SKILL.md.

## Architecture Document

```
ARCHITECTURE — [Project] — v[X.Y.Z] — [Date] — [Author], Cure Consulting Group

SYSTEM OVERVIEW
  [2–3 paragraphs: what it does, who uses it, the business problem it solves]

DIAGRAM (Mermaid)
  flowchart LR
    App[Mobile app] --> Auth[Firebase Auth]
    App --> API[Cloud Functions]
    API --> DB[(Firestore)]
    API --> Pay[Stripe]

COMPONENT RESPONSIBILITIES
  | Component | Responsibility | Owner after handoff |

DATA FLOWS
  [Signup, core transaction, payment, notification delivery — one short paragraph each]

STACK
  | Layer | Technology | Version | Notes |

KEY DECISIONS
  [Link each ADR; one line on the trade-off it made]
```

## Knowledge-Transfer Session Plan

| # | Session | Length | Audience | Content | Deliverable |
|---|---------|--------|----------|---------|-------------|
| 1 | Architecture | 2 h | Whole team | Walkthrough, decisions and trade-offs, core business logic | Recording |
| 2 | Codebase tour | 3 h | Engineers | Repo layout, conventions, key modules, live "add a feature", tests, review process | Recording + annotated tour doc |
| 3 | Deploy & operate | 2 h | Engineers + DevOps | CI/CD, live staging deploy (audience follows), dashboards, incident walkthrough, rollback demo | Recording + verified runbook |
| 4 | Infra & cost | 1.5 h | Eng lead + finance | Cloud footprint, cost by service, scaling limits, budget alerts | Recording + cost model |
| 5 | Q&A & shadowing kickoff | 1 h | Whole team | Open questions, shadowing expectations, transition channels | Shadowing schedule |

Recordings: name `KT-[#]-[topic]-[date]`, add timestamps, store with the project docs in client
storage (not personal drives). Shadowing channel: `#project-handoff-[name]`, 4-business-hour
response target, email escalation to the Cure lead after that.

## Maintenance SLA — default table (replace with SOW terms)

| Severity | Definition | Response | Resolution target |
|----------|-----------|----------|-------------------|
| P0 | Service down, data loss, security breach, payments broken | 1 h, 24/7 | 4 h |
| P1 | Core feature broken, no workaround | 4 business hours | 1 business day |
| P2 | Degraded, workaround exists | 1 business day | 3 business days |
| P3 | Cosmetic, enhancement, non-urgent | 2 business days | Next sprint, best effort |

In scope: bug fixes, security patches and dependency updates, infra upkeep (scaling, certificates),
alert response, minor config changes, database maintenance. Out of scope: new features, redesigns,
platform migrations, client-initiated third-party changes, optimisation beyond the current baseline.

Change requests: client files in [tracker] → Cure triages within 1 business day → in scope goes to
the next maintenance window; out of scope gets an estimate for a separate SOW → everything ships
through the standard pipeline.

Billing options:
- **Retainer** — [X] h/month, no rollover, overage at the SOW rate; P0 outside retainer hours
  covered; monthly usage report.
- **Time & materials** — SOW hourly rate, 1-hour minimum per incident, out-of-hours P0 premium,
  weekly timesheet, Net 30.
- **Hybrid** — small retainer for routine upkeep plus T&M for incidents beyond it; review quarterly.
