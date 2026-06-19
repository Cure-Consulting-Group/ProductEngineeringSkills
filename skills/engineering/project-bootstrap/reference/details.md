# project-bootstrap: detailed reference

> Reference material for the `project-bootstrap` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 2: Developer Interview

## Step 2: Developer Interview

Ask the following questions **in a single grouped message**. Do not ask them one by one. Pre-fill any answers you already know from Step 1 and mark them as `[detected]` so the developer can confirm or correct.

```
Bootstrap Interview — Answer all that apply:

1. PROJECT NAME
   What is this project called?

2. PRODUCT DESCRIPTION
   One sentence: what does this product do and who is it for?

3. PLATFORM(S) — Check all that apply:
   [ ] Android (Kotlin / Jetpack Compose)
   [ ] iOS (Swift / SwiftUI)
   [ ] React Web / Next.js
   [ ] Firebase Backend (Firestore / Functions / Auth)
   [ ] Node.js / Express API
   [ ] Other: ___________

4. ARCHITECTURE PATTERN
   Primary architecture? (e.g. MVI, MVVM, TCA, Clean Architecture, Redux)

5. KEY DEPENDENCIES
   Major libraries or services this project uses.
   (e.g. Hilt, Stripe Connect, Gemini API, Vertex AI, Coroutines, Orbit MVI)

6. CURRENT SPRINT GOAL
   What is the team trying to ship RIGHT NOW? One sentence.

7. ACTIVE TASKS
   List up to 5 tasks currently in progress or queued.
   Format: [TASK_ID] Description — Owner (Claude Code | Cursor | Gemini CLI | Human)

8. KNOWN BLOCKERS
   Anything currently blocked or waiting on an external dependency?

9. HARD CONSTRAINTS — Rules agents must NEVER violate:
   (e.g. "Never use LiveData", "All prices in USD cents", "Stripe webhooks require idempotency keys")

10. AGENT OWNERS — Which agents are active on this project?
    [ ] Claude Code (primary engineer)
    [ ] Cursor (code generation / refactor)
    [ ] Gemini CLI (research / review)
    [ ] Antigravity (orchestrator)
    [ ] Other: ___________

11. COMPLIANCE FLAGS — Check all that apply:
    [ ] HIPAA — handles PHI (Protected Health Information)
         If yes → list PHI field names: ___________
    [ ] COPPA — any users under 13, requires guardian consent flow
    [ ] PCI — payments in scope (or fully delegated to Stripe?)
    [ ] GDPR / CCPA — EU or California users
    [ ] None of the above

12. ENVIRONMENTS — List your Firebase projects / build variants:
    Format: [env] → [Firebase project ID] | [Stripe mode: test/live] | [build variant]

13. LOCALES / LANGUAGES
    Default language: ___________
    Additional locales supported: ___________
    String source of truth: [ ] strings.xml  [ ] Localizable.strings  [ ] Firestore Remote Config  [ ] i18n JSON

14. GIT PROTOCOL
    Branching strategy: [ ] Gitflow  [ ] trunk-based  [ ] feature branches  [ ] other: ___
    Commit format: [ ] Conventional Commits  [ ] free-form  [ ] other: ___
    Protected branches (never commit directly): ___________

15. COST GUARDRAIL CONTEXT
    [ ] Using AI APIs (Gemini / Vertex / OpenAI) — need per-call limits
    [ ] Firestore at scale — need pagination enforcement
    [ ] Firebase Functions — need recursion guards
    [ ] Stripe live keys exist in repo — need hard env block
    [ ] None / not applicable yet
```
