# 2026-08-14 — Advertised version ≠ served bits, and nothing failed loudly

**Severity:** blocker (F-1) + systemic (F-3) · **Detected by:** statledger canary loop, iterations 3–4 + step-1 version gate
**Status of guards:** shipped (v7.5.1) except one pending ticket

## What happened

The first canary soak of v7.5.0 surfaced two unrelated-looking problems that
turned out to be one failure class. F-1: the harness substitutes bare `$0`–`$9`
in skill bodies with the user's invocation arguments, so `finops` served
"$0.15" as "Canary.15" — silent corruption of decision-support numbers in 17
skills, present in every prior release. F-3: four separate mechanisms each
asserted a version that didn't match the bits actually served, and every one
reported success.

## Timeline

- 13:0x — canary iter 3 (`finops`): currency corrupted, first FINDING
- 13:1x — iter 4 (`git-worktree-manager`): `$1` corrupted → stop condition
- 13:2x — F-1 reproduced in a fixture; substitution surface mapped empirically
  (`$N`/`$ARGUMENTS` substitute; `\$N`, `${…}`, `$$`, `$UPPER` safe)
- 13:4x — 246 occurrences escaped across 17 skills; lint + live fixture t16 added (PR #22)
- 14:2x — v7.5.1 released through Ring 0 (t16 passed in-gate); re-soak 5/5 PASS

## Root cause

**No layer in the chain verifies that the version it advertises matches the
bits it serves.** Four instances in one day, all reporting success:

1. Manifest recorded the library checkout's version, not the installed plugin's (fixed, PR #21)
2. Marketplace clone was one commit stale while the tag existed — "not published" was the natural, wrong diagnosis
3. Correct content merged to main without a version bump — unreachable by any client, invisible
4. Operator asserted "PUBLISHED" from local git state rather than origin

F-1 is the same class one level down: the file on disk was correct; the
*delivered* text differed. Content review passes; users get corrupted output.

## Why it wasn't caught earlier

Every existing gate (audit, validate, Ring 0) reads **files at rest**. Nothing
tested **content as delivered** through the loader, and nothing compared
**advertised version to served version**. Conformance tooling structurally
cannot see either — this is the strongest single argument for the eval/canary
layer that caught it.

## Guards added

| Guard | Test |
|---|---|
| `\$N` escaping library-wide (246 sites) | live fixture t16: literal dollars delivered intact with args present — passed standalone AND inside Ring 0 |
| Audit T37 lint: unescaped `$N` → HIGH | seeded regression: pre-fix finops flags at 8.5, clean after |
| Manifest records plugin-cache version + `version_source` provenance | statledger re-run produced fact, not intent |
| Canary step 1 reads the cache directly; manifest demoted to cross-check | first re-soak exercised it |
| Operator doctrine: verify against origin/cache, never local state | encoded in memory + this postmortem |

## What we'd still miss

- The "content on main, no version bump" window (instance 3) has **no
  mechanism yet** — pending ticket: nightly-drift check for `skills/**`
  changed on main since the last tag.
- `/plugin update`'s silent no-op (instance 2) is upstream — suggested to
  Anthropic: report the marketplace clone HEAD, or fail when the requested
  version is absent from a refreshed index.
- Delivery-integrity is tested for `$` substitution only; other load-time
  transformations (if the harness adds any) would need their own t16-style
  fixture.
