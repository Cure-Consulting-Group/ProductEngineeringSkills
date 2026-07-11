# Cure Maintenance Loop

You are running the Cure Consulting Group standard maintenance loop for this
project. Each iteration, work through the checks below in order. Fix what is
safe to fix; report what is not. Stay read-only on anything listed under
"report only".

## Checks (in priority order)

1. **Dependency health.** Check for outdated dependencies and known
   vulnerabilities (`npm audit` / `pip-audit` / equivalent for this stack).
   Security patches with passing tests may be applied; major version bumps are
   report only.
2. **Lint and type drift.** Run the project's linter and type checker. Fix
   mechanical violations (unused imports, formatting, trivially wrong types).
   Anything requiring a design decision is report only.
3. **Test health.** Run the test suite. If it was green last iteration and is
   red now, bisect to the cause and fix it or flag the offending commit. Note
   coverage regressions against the 80% floor on new code.
4. **TODO/FIXME decay.** Scan for TODO/FIXME comments older than the last
   iteration's snapshot. Escalate any marked urgent or security-relevant;
   summarize the rest.
5. **Doc staleness.** If README/setup docs reference commands, files, or
   versions that no longer exist, fix the reference.

## Rules

- Never touch: production configs, migrations, secrets, lockfile major
  versions, anything under `.claude/`.
- Every applied fix must leave the test suite green. If tests were already red
  and you cannot fix them this iteration, do not apply other changes on top —
  report and stop.
- End each iteration with a short delta report: what was checked, what changed,
  what needs a human. If three consecutive iterations produce no findings,
  recommend widening the interval.
