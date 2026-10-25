# Antigravity brief: Wave 7 close-out (2026-10-25)

You are the implementer. Claude Code is the architect and verifier, and the owner merges.
Follow this brief exactly. If a step can't be done as written, **stop and report**. Don't improvise around it.

## Hard rules (a breach voids the whole lane)

1. **Work only in a new worktree on a new branch:**
   ```bash
   cd /Users/rashadcureton/Documents/Cure-Consulting-Group/PES-w7-int
   git fetch origin && git status --short          # must print nothing; if not, STOP
   git worktree add ../PES-w7-agy -b wave7/agy-closeout feat/wave-7
   cd ../PES-w7-agy
   ```
   Never edit `PES-w7-int`, `ProductEngineeringSkills` (main), or any other `PES-*` worktree.
2. **No outward actions.** Don't `git push`, open or comment on PRs, merge, dismiss GitHub alerts,
   create tags, run `scripts/release.sh`, or call `gh` write APIs. Local commits only.
3. **No installs or machine changes.** Don't run `claude plugin …` install, update or uninstall,
   `claude update`, `scripts/install-runtimes.sh`, `npm install`, `npm install -g`, or `pip install`.
   The one exception is `npm ci` inside `bootstrap/` (lockfile only, no new deps). Don't touch
   `~/.claude`, `~/.codex`, `~/.gemini`, or `../vetted-mods*`.
4. **No version bump.** v7.14.0 is unreleased; everything ships inside it. Don't edit
   `.claude-plugin/plugin.json` versions, mod `plugin.json` versions, or the CHANGELOG version header.
5. **Scope is Tasks A–C below and nothing else.** Out of scope: T88, T91, T92, the
   post-merge machine steps, the upstream cc-pr-tracker PR, and any "while I'm here" cleanup.
   If you find something else, list it under *Found, not fixed* in the report.
6. **Never weaken a check to make it pass.** Don't delete or skip tests, loosen an audit
   threshold (other than the T90 change named below), add `# noqa` or `lgtm` suppressions, or edit
   expected outputs to match new behaviour without saying so in the report.
7. **Skill-file rules** (`CLAUDE.md` → Development Rules) apply to every SKILL.md edit:
   - Keep `description` + `when_to_use` ≤350 chars.
   - No "claude" or "anthropic" in names.
   - Escape literal dollars as `\$0`.
   - No inline `` !`cmd` ``.
   - No `version:` field.
   - Keep `claude-commands/` stubs in sync.
8. **One commit per task.** Use conventional messages (`fix(mods): …`, `fix(bootstrap): …`,
   `feat(audit): …`), each ending with the line
   `Co-Authored-By: Antigravity (Gemini) <noreply@google.com>`.
   The whole suite in *Gate* must be green **before** each commit.

## Gate (run after every task; paste the last 15 lines of each command)

```bash
python3 scripts/audit-library.py
python3 scripts/sync-metadata.py --check || python3 scripts/sync-metadata.py --write
python3 mods/check.py --no-claude
(cd bootstrap && npm ci --no-audit --no-fund && npm test)   # npm ci from the lockfile is the one allowed install
python3 hooks/test_cure_guard.py                            # a script, not unittest: ends `N/N passed`
scripts/verify-skill-scripts.sh
```
Baseline on `feat/wave-7` at 691006a, measured 2026-10-25: all six green (guard 109/109; bootstrap
green once `npm ci` has run). If any command is red **before** your change, record it and stop.

---

## Task A: clear the CodeQL gate on PR #88 (do this first)

**Problem.** CodeQL raises 18 high alerts on `vendorHostIn` in `mods/shared/rules.ts`
(around line 85). The function builds a `RegExp` from each host in `AI_VENDOR_HOSTS` and
escapes only the dots. The alerts repeat across the two copies that `vendor.py` generates
(`mods/cure-policy-guard/hooks/shared/rules.ts` and `mods/cure-rules-band/hooks/shared/rules.ts`).

**Do:**
1. Edit **only** `mods/shared/rules.ts`. Rewrite `vendorHostIn` **without constructing a RegExp**:
   - Lower-case the text.
   - For each host, scan every `indexOf` occurrence.
   - Accept a match only when the char before it is the start of text or not `[a-z0-9.-]`.
   - Also require that the text after it is not `[a-z0-9-]` and not `.` followed by `[a-z0-9]`.

   These are exactly the current semantics. Keep the signature, the JSDoc and the return type.
2. Regenerate the copies: `python3 mods/shared/vendor.py`. Never hand-edit a vendored copy.
3. Add test cases in the existing policy-guard and rules-band test files. Cover:
   - `curl https://api.openai.com/v1` → `api.openai.com`
   - `notapi.openai.com.example.org` → undefined
   - `api.openai.com.evil.io` → undefined
   - `https://x.io/docs/api.openai.com-guide` → undefined
   - `API.OPENAI.COM:443` → `api.openai.com`
   - the empty string → undefined

   Run each mod's tests with `claude plugin test <mod>` if `claude` is on PATH (read-only).
   Otherwise run the mod's own test runner, and say which one you used.
4. Don't touch `hooks/cure_guard.py:164`. That alert is a false positive the owner will dismiss.

**Done when:** the Gate is green, the new tests fail on the old implementation (prove it with
`git stash` → run → `git stash pop`, and paste both runs), and `grep -n "new RegExp" mods/shared/rules.ts` prints nothing.

## Task B: T89, bootstrap hooks Claude Code never loads

**Problem.** `bootstrap/src/generated/index.mjs:14` renders `claude-hooks.json.ejs` to
`.claude/hooks/hooks.json`. Claude Code reads project hooks only from the `hooks` key of
`.claude/settings.json` or `.claude/settings.local.json`, so the generated hooks never run.

**Do:**
1. Stop writing `.claude/hooks/hooks.json`. Instead, merge the rendered hooks into the `hooks`
   key of the project's `.claude/settings.json`:
   - Create the file if it's absent.
   - Preserve every other key and every hook the user already has.
   - Don't add duplicates on re-run (idempotent).
   - Use the bootstrap's existing conflict and decision mechanism for user-modified files.
     Don't invent a new one.
2. Any hook that prints a reminder must emit
   `{"hookSpecificOutput":{"hookEventName":"<Event>","additionalContext":"…"}}` on
   SessionStart and UserPromptSubmit, not plain stdout.
3. `bootstrap doctor` must report a leftover `.claude/hooks/hooks.json` from an older bootstrap
   as stale. It reports only; it must not delete the file.
4. Update `bootstrap/test/slice-a.test.mjs`:
   - Assert the hooks land in `.claude/settings.json` → `hooks`.
   - Assert no `.claude/hooks/hooks.json` is created.
   - Assert existing settings keys survive.
   - Assert a second `init`/`apply` is a no-op.
5. Update `bootstrap/README.md` where it names the old path.

**Done when:** the Gate is green and the new tests fail on the old code (show the stash run as in Task A).
The live acceptance (`/hooks` lists them in a real Claude Code session) is **not yours**. List it
under *Needs Claude verification*.

## Task C: T90, tighten the trigger window to 85 chars

**Step 1, measure (no edits yet).** Run `codex --version`, then
`codex debug prompt-input` (see `docs/evaluations/2026-10-24/platform-facts.md` for the exact
method used in T86). Record the observed description cut-off on the default model.
- If the measured cut is **not** in 95–110 chars, STOP after measuring and report.
  The ticket's premise has moved.
- If `codex` isn't installed, STOP and report.

**Step 2, change the gate.** In `scripts/audit-library.py`, set `TRIGGER_STRICT_WINDOW = 85`.
Change nothing else in the audit.

**Step 3, rewrite failing descriptions.**
- For each skill the audit now flags, move the trigger clause ("Use when …") so it starts by
  char 85 and at least 2 trigger words end before the measured cut.
- Rewrite only the `description` (and `when_to_use` if present). Keep the meaning, the
  skill's routing nouns, and any "NOT for …" disambiguation. Don't edit skill bodies.
- Mirror the change into the matching `claude-commands/*.md` stub when it carries the description.

**Step 4.** Run `python3 scripts/generate-overview.py` and the Gate.

**Done when:**
- The audit is green at 85.
- The report has a table with these columns: skill · old first 100 chars · new first 100 chars · chars to trigger.
- The skill count with ≥2 trigger words inside the measured cut is now 104/104 automatic
  skills. Give before and after numbers.

---

## Report (return exactly this, nothing else)

```
LANE: antigravity · BRANCH: wave7/agy-closeout · WORKTREE: ../PES-w7-agy
BASELINE: <green | red: which command, last 15 lines>
TASK A: <done | stopped: why> · commit <sha> · files: …
  evidence: stash-run fail output + post-change pass output (last 15 lines each)
TASK B: <done | stopped: why> · commit <sha> · files: …
  evidence: …
TASK C: <done | stopped: why> · commit <sha> · measured cut: <n> chars on <model>, codex <ver>
  table: …
GATE (final): last 15 lines of each Gate command
git log --oneline feat/wave-7..wave7/agy-closeout
git diff --stat feat/wave-7..wave7/agy-closeout
NEEDS CLAUDE VERIFICATION: …
FOUND, NOT FIXED: …
```
Paste real command output only. Don't write "tests pass" without the output that shows it.
An empty diff reported as done is a failed lane.
