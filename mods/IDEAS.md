# More mods worth building

Ranked by value for effort.

Each idea comes from something observed in the portfolio, not a generic wish, and names:
- the event or API it uses (from the 2.1.289 mods reference);
- an estimate in hours.

Build one at a time, with the same bar as the first three: unit tests, a mutation pass, and a live run.

## Tier 1: closes a gap that exists today

### 1. LLM cost ledger (`cure-llm-ledger`), about 8 h
**Problem.** Anthropic spend never reaches `v_billing_unified`: there is no per-product billing export, and AG-102 is open. Claude Code sessions are the largest Anthropic spend in the portfolio, and none of it is attributed to a repo.

**Mod.**
- On `turn.step`, read each request's usage.
- On `session.measure`, read `$.session.usage().cost`.
- Append one JSONL row per turn: repo, branch, model, input/cached/output tokens, cost.
- `billing-watchdog` ingests the file into a new `anthropic_usage` table.

This gives a provider column and the first non-GCP AI spend in the cost plane.

**Risk.** It writes a file outside the plugin store. Keep that file under `~/.claude/` and never include prompt text.

### 2. Secret scrub on tool output (`cure-secret-scrub`), about 5 h
**Problem.** Sessions routinely read across 34 repos. The guard stops secrets being written, but nothing stops a `Read` of a `.env` file or a service-account key from reaching the model.

**Mod.**
- On `tool.call` for `Read`, `Bash` and `Grep`, wrap the result with `const r = await next(e)`.
- Redact the guard's secret patterns, plus `GCP_SA_KEY` values and `-----BEGIN` blocks, in `r.text` and `r.result` before returning.
- Show a toast saying what was redacted.

**Reuse.** The patterns already exist in `cure-policy-guard/hooks/rules.ts`.

### 3. Citation checker (`cure-cite-check`), about 6 h
**Problem.** Memory rule *verify before asserting architecture*: six inferred claims were wrong. Answers routinely cite `file:line`, and an agent's citations were stale this week (DistrictZero `materialize-firestore` line numbers).

**Mod.**
- On `turn.complete`, scan the final answer for `path:line` references.
- Check that each file exists and has that many lines. Where the answer quotes text, check it appears near that line.
- Return `{ text }` to print a line under the answer, such as "3 citations checked, 1 stale: X:522".

### 4. DistrictZero claim guard (`cure-claim-guard`), about 5 h
**Problem.** DistrictZero's CLAUDE.md says: "Two machines share this repo… Never build a row another machine owns." Machine B is the Mac mini. Nothing enforces this; it relies on agents reading `.agents/state-targets.md`.

**Mod.**
- On `tool.call` for file writes under a state's paths (`scripts/build-<st>-*`, `scripts/lib/<st>-*`, `scripts/data/<st>*`), parse `state-targets.md`.
- If the row's owner is the other machine, refuse with the owner's name.
- Identify this machine with `$.process.run(['scutil','--get','LocalHostName'])`.

**Rule source.** DistrictZero `CLAUDE.md` §Conventions and `.agents/state-targets.md`.

## Tier 2: makes a costly mistake visible before it happens

### 5. Push cost preview (`cure-ci-preview`), about 6 h
On `tool.call` for `Bash` when the command is `git push` or `gh pr create`:
- Compute the diff's paths.
- Run the repo's own change gate where one exists (DistrictZero `scripts/ci/classify-changes.mjs --stdin`; `statledger`'s iOS filter regex read from `ios.yml`).
- Show a toast with the jobs expected and their rough cost, for example "full CI + preview ≈ 45 billed min ≈ $0.27".
- Also warn when a commit mixes `.agents/` notes with code, since that loses the notes-only skip.

### 6. Agent fan-out budget (`cure-agent-budget`), about 4 h
On `agent.spawn`:
- Cap concurrent subagents per session (configurable, default 4).
- Route `Explore` and other read-only research types to a cheaper model unless the prompt asks otherwise. The hook can rewrite `model`.
- Log each spawn's model and type to the cost ledger (idea 1).

This makes fan-out cost a choice, not a side effect.

### 7. Outbound AI-vendor guard at run time (`cure-egress-guard`), about 5 h
**Problem.** The policy guard catches *code* that adds a vendor. Nothing catches a session that *sends data*.

**Mod.**
- On `tool.call` for `Bash` and `WebFetch` in Level5 or the minors' repos, refuse:
  - `curl` or `fetch` to model-vendor hosts (`api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com`, TypeSafe’s API host, …);
  - commands that pipe repo files into such tools.
- Same override-and-record flow as the guard.

**Context.** The 2026-10-04 review found Level5 already sends patient transcripts through the consumer Gemini key, and SPEDTECH sends student names.

### 8. Workflow lint on write (extend `cure-policy-guard`), about 3 h
When the guard sees a write to `.github/workflows/*.yml`:
- Run `actionlint` on the result, if it is installed, and show its errors before the write lands.
- Add a `requires-required-check` warning when a repo has no required status check. DistrictZero's `build` check is documented as required but is not enforced.

## Tier 3: quality of life

### 9. Lane board (`cure-lane-board`), about 8 h
A `/lanes` pane (`$.ui.open` plus `ui.render` on `Pane`) listing:
- each tri-lane run;
- its worktree and branch;
- live commits and diff size, using the lane verifier's git queries;
- whether its escaped-defect window is open.

Today, closed windows only print as session-start reminders ("defect window for bw-tests closed: lane-log.py update …").

A button runs the `lane-log.py update` command for a closed window after asking for the defect count.

### 10. Repo rules banner (`cure-rules-band`), about 3 h
On `ui.render` for `AbovePrompt`, show one line naming the current repo's hard constraints, for example:
- "minors' data · no new AI vendors" for TIR;
- "PHI · Vertex only" for Level5;
- "hash-pinned public claims · no AI field mapping" for DistrictFacts.

The rules come from a small `.cure/rules.json` per repo, so the guard (rule set) and the banner (display) share one source.

### 11. Handoff draft (`cure-handoff`), about 4 h
On `/handoff`, draft a STATE.md entry from:
- the session's commits, PRs opened and tests run (`$.session.messages()`);
- open alerts.

It opens the draft for review and never writes on its own. DistrictZero and `statledger` both keep dated STATE handoffs by hand today.

## Not worth building as mods

- **Anything a settings hook already does well.** A plain allow/deny on a Bash pattern is simpler as a `PreToolUse` hook. Use a mod when you need interface, rewriting, the store, or an override with a record.
- **Monitoring that must run when no session is open.** Mods live inside a Claude Code session. The hourly Actions monitor from 2026-10-03 belongs in `billing-watchdog` on Cloud Run, not in a mod.
