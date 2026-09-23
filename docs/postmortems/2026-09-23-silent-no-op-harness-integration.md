# 2026-09-23 — Harness integrations that silently did nothing (dead hooks, unloadable skills)

**Severity:** major (security guards absent; 69 skills unloadable in non-interactive sessions) · **Detected by:** Wave 5 platform re-evaluation (hooks) and `claude plugin eval` traces (skills)
**Status of guards:** shipped (v7.9.1, v7.10.1)

## What happened

Two unrelated-looking defects share one failure class: a Claude Code integration point that
fails *silently* and reports success. (1) Five plugin hooks — the `.env`/lockfile/credential edit
guard, the skill-content security guard, the dangerous-Bash guard, the prompt warning, and skill
telemetry — read a `CLAUDE_TOOL_INPUT` environment variable that Claude Code has never set (hook
input arrives as JSON on stdin). Every hook exited 0 without inspecting anything, in every
consuming project, since v3. Telemetry therefore recorded 0/103 skills used, which the usage
report presented as data. (2) 69 skills carried inline `` !`cmd` `` context injection without
pre-approving Bash. Injection runs through the Bash permission check at skill-load time; wherever
Bash isn't pre-approved (headless `claude -p`, CI, routines, restrictive modes) the check is denied
and the whole skill fails to load. The model then answers bare — often correctly — so nothing looks
wrong.

## Timeline

- v3.x — hooks written against `$CLAUDE_TOOL_INPUT`; never exercised with real hook input
- 2026-07-11 (Wave 2, T20) — dynamic context injection migrated into 72 skills
- 2026-09-23 10:0x — Wave 5 re-eval: usage report shows 0 invocations → traced to the hook; docs
  confirm stdin contract → `hooks/cure_guard.py` + 28-case matrix (v7.9.1)
- 2026-09-23 15:5x — full `claude plugin eval` sweep: Δ=0 on 34/39 cases
- 2026-09-23 16:3x — `market-research` trace: "Bash permission was denied" at skill load;
  `dora-metrics` (a *passing* case) shows the same → 69 skills affected; converted (v7.10.1)

## Root cause

Integration points were validated by **shape** (hooks.json parses; prompt hooks are on allowed
events; skill frontmatter is valid) but never by **observed behavior under the real harness**. Both
failures fail open by design — a hook that can't read input allows, a skill that can't load lets
the model proceed — so the absence of an effect is indistinguishable from "nothing to report".

## Why it wasn't caught earlier

- CI's hook checks assert placement and timeouts, not that a hook ever sees a real payload.
- The Wave 3 eval harness ran skills via slash-invocation with project settings and permissive
  tools, so the injection permission path never triggered; pass/fail graders on generic
  correctness pass with or without the skill, hiding a non-loading skill.
- The one signal that *was* anomalous (0/103 skills used) was read as a finding about skills,
  not about the instrument.

## Guards added

- `hooks/test_cure_guard.py` — 33 cases feed real hook-shaped stdin JSON and assert block/allow
  (seeded: `.env`, `rm -rf "/"`, MultiEdit `edits[]`); CI fails if hooks.json mentions
  `CLAUDE_TOOL_INPUT`.
- `audit-library.py` CRIT: inline injection without Bash in `allowed-tools`; self-test fixtures
  fire on the pre-fix shape; verified to flag exactly the 69 skills on the pre-fix tree.
- Doctrine: CLAUDE.md + `docs/AUTHORING.md` §2 ("default: don't inject").

## What we'd still miss

- A skill that loads but whose guidance is ignored still passes generic graders — `tool_used:
  Skill` proves the call, not the load. Graders that check Cure-specific conventions, plus a trace
  check that the Skill result is not an error, are the next step (not built).
- Hooks are tested in isolation, not end-to-end inside a live session.
- Any other "instrument reads zero" metric (SCORECARD layers stuck at "no data") deserves the same
  suspicion before it is read as a finding.
