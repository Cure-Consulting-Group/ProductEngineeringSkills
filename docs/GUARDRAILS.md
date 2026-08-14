# Guardrail Enforcement Inventory (T36)

Every safety-relevant guardrail in the library, classified by whether the
harness enforces it or it is prose. **Prose is not a control** — the audit
now flags any skill claiming read-only without `disallowed-tools`
(regression-tested), and this doc is the standing register.

Censused 2026-08-14 across 81 skills. Re-run the sweep at each quarterly
re-eval (`grep` patterns live in the audit's T36 rule).

## Class (a) — enforced by mechanism

| Skill | Claim | Mechanism |
|---|---|---|
| feature-audit | read-only audit | `disallowed-tools: Write Edit` |
| accessibility-audit | read-only audit | `disallowed-tools: Write Edit` |
| security-review | read-only review | `disallowed-tools` |
| proposal-generator | destructive/sensitive | `disable-model-invocation` |
| legal-doc-scaffold | sensitive | `disable-model-invocation` |
| env-secrets-manager | "read-only audits" | `disallowed-tools: Write Edit` — **added by T36** (was the `allowed-tools`-as-sandbox anti-pattern) |

Plus: 35 deny rules in `settings.json`, PreToolUse hooks blocking `.env`/lock/
credential/tfstate edits, and the skill-security-guard hook on library files.

## Class (c) — advisory by nature, now labeled

Recurring-mode guardrails ("read-only run" when fired from a loop/routine) in:
burn-rate-tracker, finops, investor-reporting, performance-review,
seo-content-engine, technology-radar. Frontmatter cannot express *per-mode*
restriction — these skills legitimately write report files interactively.
Each line now reads "(advisory — recurring-mode doctrine per AUTOMATION.md,
not harness-enforced)". The real backstop is AUTOMATION.md rule 1 plus the
deny rules.

Swept and cleared as false positives (prose mentions read-only concepts, not
skill guarantees): agent-designer, data-migration, git-worktree-manager,
mcp-server-builder, project-bootstrap, engagement-automation,
cure-infra-bootstrap (its `doctor` subcommand is read-only; `bootstrap` writes
by design).

## Non-Claude runtimes: no enforcement surface exists

Verified in Wave 2.5: Gemini CLI / Antigravity ignore `disallowed-tools` and
`disable-model-invocation` silently. Exported skills carry prose
READ-ONLY/DESTRUCTIVE blocks (T25) — those are **advisory, full stop**.
Consequence, inherited by RUNTIME-SELECTION (T33): **regulated or
payment-touching work stays on Claude Code, where controls are real.**

## Regulated-project overlay

Projects flagged `"regulated": true` in their cure-manifest.json require:

1. `mode: plugin` (no drifting vendored guardrails)
2. All class-(a) mechanisms current (version lag < 7 days)
3. Claude Code runtime only for agent work touching regulated data
4. The project's own deny rules reviewed at each canary promotion

Currently flagged: **Level5** (medical-scribe — HIPAA-adjacent today,
HIPAA-real the moment PHI flows). Add any project taking real payment volume
(stripe-integration consumers) when that day comes.
