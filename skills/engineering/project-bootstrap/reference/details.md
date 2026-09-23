# project-bootstrap: CLAUDE.md and STATE.md templates

Read this file at Step 3, once the interview is answered. Fill only sections the inspection or
interview confirmed; delete every section that has no data. Keep the generated CLAUDE.md under
~150 lines — Claude Code loads it in full every session and adherence drops as it grows
(code.claude.com/docs/en/memory targets <200 lines).

## CLAUDE.md template

````markdown
# [PROJECT_NAME]
> [ONE_SENTENCE_DESCRIPTION]

---

## Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| [Layer]     | [Technology]                        |

---

## Architecture

- Pattern: [MVI | MVVM | TCA | Clean | etc.]
- Module structure: [describe if monorepo, feature modules, etc.]
- State management: [StateFlow + MVI | TCA Store | Redux | etc.]

---

## Key Dependencies

- [Dependency] — [purpose]

---

## Agent Roles

| Agent         | Responsibility                          |
|---------------|-----------------------------------------|
| Claude Code   | [what Claude Code owns on this project] |
| Codex         | [what Codex owns]                       |
| Antigravity   | [what Antigravity owns]                 |
| Cursor        | [what Cursor owns]                      |

*(list only agents the interview confirmed)*

---

## Rules — Always

- [Rule 1]
- [Rule 2]

## Rules — Never

- [Rule 1]
- [Rule 2]

---

## Firebase Collections

| Collection    | Description              | Auth Scope     |
|---------------|--------------------------|----------------|
| [collection]  | [purpose]                | [uid scoped?]  |

*(omit section if Firebase not used)*

---

## Stripe Configuration

- Platform account: [yes/no]
- Connect type: [Express | Standard | Custom | N/A]
- Webhook events handled: [list]
- Idempotency keys: required on all PaymentIntent creates

*(omit section if Stripe not used)*

---

## Environment Files

- `.env.local` — [what it contains]
- `google-services.json` — [Android Firebase config]
- `GoogleService-Info.plist` — [iOS Firebase config]

*(list only what exists)*

---

## Firestore Schema

| Collection         | Key Fields                        | Auth Scope          | Notes                     |
|--------------------|-----------------------------------|---------------------|---------------------------|
| [collection_path]  | [field: type, field: type]        | [uid-scoped? yes/no]| [any migration notes]     |

> Field type must be explicit — never assume. Mismatches between clients cause silent data corruption.
> If a field type changes, add a migration note here and in the Decisions Log.

*(omit section if Firestore not used)*

---

## Environment Matrix

| Env      | Firebase Project       | Stripe Mode | Build Variant | Notes                    |
|----------|------------------------|-------------|---------------|--------------------------|
| dev      | [project-id]-dev       | test        | debug         | local emulator preferred |
| staging  | [project-id]-staging   | test        | release       | CI deploys here          |
| prod     | [project-id]-prod      | live        | release       | manual deploy only       |

> Agents must verify active environment before any Firebase write or Stripe call.
> Never use live Stripe keys outside of prod build variant.

*(customize rows to match actual project environments)*

---

## Compliance Requirements

*(Omit entire section if no compliance flags apply.)*

### HIPAA *(include if PHI is handled)*
- PHI fields: [list field names]
- PHI must never appear in: logs, Crashlytics, analytics events, error messages
- Firebase collections containing PHI: [list paths]
- Encryption at rest: required for all PHI fields in Firestore
- Agents must not add new PHI fields without explicit human approval

### COPPA *(include if any users may be under 13)*
- Guardian consent flow: required before any data collection for minors
- Date of birth collection: must gate all feature access
- No behavioral advertising targeting minors
- Agents must not skip or stub the consent gate — ever

### PCI *(include if payment card data flows through app)*
- Card data: never stored locally, never logged, fully delegated to Stripe SDK
- Stripe Elements / PaymentSheet: required — no custom card input fields
- Agents must not build custom card number, CVV, or expiry input components

### GDPR / CCPA *(include if EU or California users)*
- Data deletion: user-initiated delete must purge all Firestore docs + Auth record
- Consent: explicit opt-in required before analytics or marketing events
- Data export: must be implementable on request

---

## Locale Configuration

| Locale | Language   | Status              | String Source                        |
|--------|------------|---------------------|--------------------------------------|
| en     | English    | default             | [strings.xml / Localizable.strings]  |
| [es]   | [Spanish]  | [active / planned]  | [same / Firestore Remote Config]     |

- Default locale: [en]
- RTL support required: [yes / no]
- Agents must not hardcode user-facing strings — use resource keys only
- New strings must be added to ALL active locale files simultaneously

*(omit section if single-locale only)*

---

## Git Protocol

- Branching strategy: [Gitflow | trunk-based | feature branches]
- Branch naming: `feature/[TASK_ID]-short-description` | `fix/[TASK_ID]-short-description`
- Commit format: [Conventional Commits — `feat:` `fix:` `chore:` `refactor:` `test:`]
- PR requirements: passing CI + STATE.md updated + zero TODO comments + agent review note
- Protected branches — never commit directly: `main`, `release/*`
- Hotfix path: `hotfix/[description]` → PR to `main` + backmerge to `develop`

---

## Cost Guardrails

### AI APIs *(include if Anthropic / Gemini / Vertex / OpenAI / Bedrock detected)*
- Never call AI APIs inside a loop without an explicit item limit
- Always paginate before passing list data to a model
- Cache responses where TTL is acceptable — do not re-call for identical inputs
- Log token usage in dev; alert if single-session cost exceeds $[X]

### Firestore *(include if Firebase detected)*
- Never read an entire collection without `.limit(n)` — max [50] docs per read
- Use compound queries over client-side filtering
- Avoid `onSnapshot` listeners on large collections without scoped queries
- Index all fields used in compound `where` + `orderBy` queries

### Firebase Functions *(include if Cloud Functions detected)*
- No recursive triggers — a Firestore write in a Function must never trigger itself
- All HTTP Functions must have auth middleware — no public endpoints without explicit approval
- Set memory/timeout limits explicitly — do not rely on defaults

### Stripe *(include if Stripe detected)*
- Live keys: environment variable only — never hardcoded, never committed
- Test/live key mismatch guard: assert `BuildConfig.STRIPE_MODE == "test"` in non-prod builds
- Idempotency keys: required on all `PaymentIntent` creates and confirms
- Webhook handlers: must be idempotent — check event ID before processing

---

## Incident Protocol

| Priority | Condition                                              | Agent Action                                              |
|----------|--------------------------------------------------------|-----------------------------------------------------------|
| P0       | Auth broken / payments failing / data loss / PHI leak  | Halt all tasks. Update STATE.md. Notify human immediately.|
| P1       | Core feature degraded / error rate > 5% / deploy fails | Complete current atomic unit. Flag in STATE.md blocker.   |
| P2       | Non-critical bug / UI issue / test failure             | Log in STATE.md unresolved. Continue sprint.              |

> On any P0: agents must stop mid-task, write incident summary to STATE.md under a new
> `## INCIDENT` header, and await human instruction before resuming any work.

---

## Definition of Done

A task is shippable when:
- [ ] Feature logic complete with error handling on all failure paths
- [ ] Unit tests written and passing; coverage meets the testing-strategy threshold
- [ ] No hardcoded strings, magic numbers, or TODO / FIXME comments
- [ ] Firebase security rules updated to cover any new collections
- [ ] Environment matrix verified — correct project targeted
- [ ] Compliance checklist passed for any PHI, minor, or payment-adjacent changes
- [ ] Locale files updated for all active locales if new strings added
- [ ] STATE.md updated — task marked Done, decisions logged
- [ ] Reviewed by a second agent or a human before merge
````

## STATE.md template

````markdown
# STATE.md — [PROJECT_NAME]
> Session runtime state. Agents read and write this file. Do not edit manually mid-session.

---

## Session Info

| Field          | Value                            |
|----------------|----------------------------------|
| Sprint goal    | [CURRENT_SPRINT_GOAL]            |
| Session opened | [YYYY-MM-DD HH:MM]               |
| Orchestrator   | [Claude Code / Codex / Antigravity]|
| Active branch  | [branch name]                    |

---

## Task Queue

| ID    | Task                              | Owner       | Status       | Blocker              |
|-------|-----------------------------------|-------------|--------------|----------------------|
| [T01] | [task description]                | [owner]     | [status]     | [blocker or —]       |

**Status values:** `Queued` | `In Progress` | `Blocked` | `In Review` | `Done`

---

## Context Handoff Block

> Copy this block verbatim when starting a new agent session on this project.

```
Project: [PROJECT_NAME]
Stack: [condensed stack]
Sprint goal: [CURRENT_SPRINT_GOAL]
Active env: [dev | staging | prod]
Last decision: [most recent architectural or product decision]
Hard constraints: [comma-separated never-rules]
Compliance flags: [HIPAA | COPPA | PCI | GDPR | none]
Active blocker: [blocker or "none"]
Resume from: [task ID and file/line if applicable]
```

---

## Decisions Log

Record any architectural, product, or integration decision made this session.
Format: `[YYYY-MM-DD] [DECISION] — [RATIONALE]`

- [date] [decision] — [why]

---

## Resolved This Session

- [ ] [task that was completed]

---

## Unresolved / Carry Forward

- [ ] [open question or task that did not get resolved]

---

## Agent Handoff Notes

Instructions for the next agent picking up this session:

- **[Agent] →** [what it left off / what to pick up, with file + line]

*(one line per active agent)*

---

## INCIDENT LOG

*(Only populated on P0/P1. Format: `[YYYY-MM-DD HH:MM] [P0|P1] [description] — [status]`)*

---

## Sprint Archive

When the sprint ends, rename this file to `STATE_[SPRINT_END_DATE].md` and create a fresh `STATE.md`.
````
