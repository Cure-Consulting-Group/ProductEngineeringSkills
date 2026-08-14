# Postmortems — blameless, mandatory, small

**Trigger (non-negotiable):** any canary BLOCKER finding, any canary
hard-stop, any release rollback, or any defect that shipped to ≥2 consuming
projects → a postmortem lands in this directory **within one week**. Smaller
incidents at the operator's discretion — when in doubt, write it; they're
cheap and they compound.

**Blameless means mechanisms, not people.** "The operator asserted X" is a
finding about a missing guard, never about the operator — the fix is always
a mechanism (lint, gate, check, doctrine line), because a lesson that lives
in a person's memory dies with their attention span.

## Format (one page, modeled on the first canary report)

```markdown
# YYYY-MM-DD — <one-line title naming the failure class>

**Severity:** blocker | major | minor · **Detected by:** <mechanism, not person>
**Status of guards:** shipped | pending (link tickets)

## What happened          — 3–6 sentences, plain language
## Timeline               — timestamped, terse
## Root cause             — the MECHANISM that allowed it, stated generally
## Why it wasn't caught earlier — which existing gate should have, and why it didn't
## Guards added           — each with its regression test
## What we'd still miss   — the honest residual
```

**The one rule of quality:** every "Guards added" entry names a *tested*
mechanism (seeded-regression or live fixture), not an intention. A guard that
hasn't been proven to fail on the bad input is a wish.

Postmortems are inputs to the quarterly re-eval: recurring failure classes
across postmortems become wave tickets.
