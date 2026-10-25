# Mods plan: what shipped, what was wrong, what holds now

This file replaces the October 2026 "ten new mods" scope. That scope was built at 0.1.0 in PR #80, and the Wave 7 evaluation (`docs/evaluations/2026-10-24/EVALUATION.md` §7) found most of it broken in use while its tests passed. Wave 7 (T71–T74) fixed, merged or dropped each mod. The [README](README.md) describes the nine that remain; this page records the design rules they now follow and why.

## Where each planned mod ended up

| Planned mod | Outcome (Wave 7) |
|---|---|
| `cure-secret-scrub` | Dropped (D6): `secret-redactor@vetted-mods` covers it, and two redactors redacted output twice |
| `cure-llm-ledger` | Dropped (D6): `token-ledger@vetted-mods` covers it; its "session" total was machine-wide and its prices were years stale |
| `cure-cite-check` | Fixed (T71): resolves against the session's repos, never edits the answer |
| `cure-claim-guard` | Merged into `cure-policy-guard` as the `state-claim` rule |
| `cure-ci-preview` | Dropped (D6) |
| `cure-agent-budget` | Rewritten (T71): per-session tracking by agent id; no model rewrite by default |
| `cure-egress-guard` | Merged into `cure-policy-guard` as the `ai-egress` rule |
| `cure-lane-board` | Kept: shared git module, calls in parallel |
| `cure-rules-band` | Kept: reads the shared repo table, draws nothing for repos without rules |
| `cure-handoff` | Dropped (D6): a skill does it better |

## What the plan assumed that was not true

Checked against the mods reference (code.claude.com/docs/en/plugins/mods/reference.md) and the 2.1.306 type declarations:

- **`$.store` is machine-wide.** Every session on the machine shares it (4 MiB of JSON in all). The plan kept live per-session counts there; agent-budget's never-reset count then denied spawns. Session values belong in `$.state` (declared in `types/index.d.ts`); `$.store` is for data that is meant to be shared, such as spend-band's one fetch per machine or an override log.
- **Subagents are tracked through `agent.spawn` and `turn.complete`.** `agent.spawn` answers the new `agentId`; the agent's run ends in a `turn.complete` carrying that id; `$.agent.list()` reports each agent's status. A `finally` after `next()` in a `tool.call` hook is not a completion signal.
- **Hardcoded model IDs and prices go stale.** The plan priced models by retired IDs and rewrote agents to one of them. The engine reports the session's cost (`$.session.usage().cost.usd`); a model choice is an alias (`sonnet`, `haiku`), never a full ID.
- **Limits.** A hook's own time is 10 s (50 ms for `prompt.edit`), not counting `next` or a `$` call other than `$.clock.sleep`; a `.catch` handler gets 1 s; `$.process.run` defaults to 30 s. A wait belongs inside a `$` call: `$.ui.ask` raced against `$.clock.after`, never a promise of the mod's own.
- **Registration.** One event registered twice without a matcher fails the module load; split by matcher (`{ tool: ['Bash', 'WebFetch'] }`). A function that receives `$`, and a `.catch` handler, must be declared at the top of a file of the mod.
- **Mods install one folder each.** A mod cannot import from a sibling folder, so shared code lives in `mods/shared/` and `mods/shared/vendor.py` copies it into each consumer's `hooks/shared/` (CI runs `--check`).
- **The events the mods use are documented**: `tool.call`, `agent.spawn`, `turn.step`, `turn.complete`, `session.start`, `session.end`, `prompt.submit`, `prompt.edit`, `prompt.attachment`, `session.receive`, `ui.render`, `command.run`.

## Design rules every Cure mod follows

1. **Fail closed on policy, open on plumbing.** A guard denies when nobody answers within its ask timeout, and its `.catch` denies if the guard itself fails before `next`. A band or report that cannot read git shows nothing or says "could not verify".
2. **Nothing on the hot path.** No subprocess per tool call or per render. Repo lookups are cached per folder; text checks run before any lookup; drawing reads `$.state` only.
3. **Resolve from the target, not the session cwd.** A file rule finds the repo of the file; a Bash rule uses the command's `cd`/`git -C`; git calls always pass `-C`.
4. **Bound everything kept.** Every list in state or store is capped (200 entries); caches are pruned.
5. **Configure through `userConfig`.** Environment variables remain as overrides where a mod had them.
6. **A test for each fixed defect that fails on the old code**, plus `claude plugin test` and `claude plugin validate --strict` green for every mod (`mods/check.py`).
