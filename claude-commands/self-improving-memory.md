# Self-Improving Memory

Cure's auto-memory discipline, portable to every engagement. Four entry types — `user`,
`feedback`, `project`, `reference` — are canonical; map any new need onto one of them. Output per
mode is below; done when the user has a proposal to confirm (audit, patterns, health) or a seeded
index (bootstrap). Never delete or merge entries without confirmation.

## Where memory lives

| Runtime | Location |
|---|---|
| Claude Code | `~/.claude/projects/<project>/memory/` — `<project>` is derived from the git repo path (e.g. `-Volumes-CureVault-projects-Acme`), shared by all worktrees; `autoMemoryDirectory` in settings overrides it. `MEMORY.md` is the index; topic files (`feedback_*.md`, `project_*.md`) load on demand. |
| Codex, Antigravity | No Claude auto-memory. Keep the same files in the repo at `docs/memory/` (or a gitignored `.agents/memory/` for private notes) and add one line to `AGENTS.md` / `GEMINI.md`: "Read docs/memory/MEMORY.md at session start." Confirm your runtime version has no native memory feature that should be used instead. |

Only the first **200 lines or 25KB** of `MEMORY.md` load at session start (Claude Code); anything
past that is silently dropped, which is why the index stays one line per entry.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Claude memory dir: `for d in ~/.claude/projects/*"$(basename "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || pwd)")")"/memory; do [ -f "$d/MEMORY.md" ] && echo "$d: $(wc -l < "$d/MEMORY.md") index lines, $(ls "$d" | wc -l) files"; done 2>/dev/null | head -3`
- Repo memory (other runtimes): `wc -l docs/memory/MEMORY.md 2>/dev/null || echo "(no docs/memory)"`
- Repo age: `git log --reverse --format=%cs 2>/dev/null | head -1`

If the first line is empty, find the directory with `ls ~/.claude/projects | grep <repo-name>`.
Read `CLAUDE.md`/`AGENTS.md` too — anything already there must not be duplicated into memory.

## Step 1: Classify the Request

| Mode | When | Output |
|---|---|---|
| **bootstrap** | New engagement, no index yet | Starter `MEMORY.md` + kickoff interview for `user`, `project`, `reference` |
| **audit** | Index exists, user wants a sweep | Distribution by type, anti-patterns found, ranked recommendations |
| **detect-patterns** | Feedback piling up on similar topics | Consolidation proposals (merge, extract to CLAUDE.md, retire) |
| **health-check** | Periodic hygiene (every 2–4 weeks) | Triage table of stale / contradictory / duplicate entries |

Ambiguous → ask once which mode.

## Step 2: Gather Context

Entry distribution by `type:` frontmatter; feedback entries created in the last 14 days (high churn
= consolidation opportunity); project entries whose `By:` date has passed; entries citing paths that
no longer exist. If memory is inline in `MEMORY.md` rather than topic files, parse headings as entries.

## Step 3: Taxonomy (canonical)

| Type | Holds | Write when | Decay |
|---|---|---|---|
| `user` | Role, preferences, depth, communication style | First session; a preference observed 2+ times | Long |
| `feedback` | Corrections **and** validated approaches — Rule + Why + How to apply | User corrects you or explicitly validates an approach | ~60 days: re-validate before acting on older rules |
| `project` | Initiatives, absolute deadlines (`By: 2026-05-15`, never "next Friday"), stakeholders | Initiative starts, deadline lands, stakeholder changes | Fast: retire when shipped or `By:` passes |
| `reference` | Pointers: tracker project, channel, dashboard, runbook, account IDs | Pointer used 2+ times and not in CLAUDE.md | Silent: verify on recall |

## Step 4: Never save

- Code-derivable facts or git history — read the code / `git log`.
- CLAUDE.md/AGENTS.md content — project identity belongs there.
- Ephemeral state and one-off debug recipes.
- Secrets, credentials, tokens — memory files are plain text outside any vault.
- Negative judgments about the user.
- Feedback without a Why — unactionable; upgrade it or skip it.

## Step 5: Pattern Detection

| Trigger | Proposed action |
|---|---|
| ≥3 feedback entries on one topic | Consolidate into one Rule/Why/How entry, or extract to CLAUDE.md / a skill |
| ≥2 reference entries for one external system | One consolidated entry with all sub-pointers |
| Project entry past its `By:` date | Retire (shipped) or update with the slip rationale |
| Same fact re-derived from code in 3 sessions | Extract to CLAUDE.md; stop re-looking it up |

Show the cluster and the proposed replacement; write only after confirmation.

## Step 6: Health Checks

| Check | Detect | Action |
|---|---|---|
| Stale file refs | Cited path fails `test -f` | Update path or retire |
| Stale URLs | Tracker/Slack/dashboard links | Flag for human check (don't auto-fetch) |
| Contradictions | Two feedback rules conflict | Show both, ask which is current |
| Near-duplicates | Same type + topic, overlapping body | Propose merge |
| Expired project entries | `By:` passed, no status change | Retire or update |
| Why-less feedback | Missing Why or How | Upgrade or retire |
| Index bloat | `MEMORY.md` near 200 lines / 25KB | Consolidation pass |

## Step 7: Bootstrap

1. Create `MEMORY.md` from `templates/MEMORY.md.template` in the location for the runtime (table above).
2. Ask the kickoff interview in one message; pre-fill from CLAUDE.md/AGENTS.md:
   - **User:** role on the engagement; terse vs detailed; strong areas and areas to challenge
   - **Project:** sprint goal; deadlines in the next 30 days (date + what ships); stakeholders (name, role, what they care about)
   - **Reference:** tracker project URL, primary channel, dashboard/runbook, escalation contact
   - **Feedback seeds (optional):** carried-over rules as Rule + Why + How
3. Write one topic file per answer from `templates/feedback_template.md` / `templates/project_template.md`, and one index line per file.

## Recall discipline

Memory is a hint, not ground truth: confirm referenced files, dashboards, and people still exist;
when code and memory disagree, the code wins and the entry gets updated; cite the entry when using
it ("per feedback memory from 2026-03-12"); ask before acting on a feedback rule older than 60 days.

## Output Formats

- **audit:** counts per type, total index lines, each anti-pattern with count, then numbered recommendations (highest leverage first).
- **detect-patterns:** per cluster — entries, proposed consolidated entry, entries to retire.
- **health-check:** table `entry path | issue | proposed action`.

## Related Skills

- `project-bootstrap` — writes CLAUDE.md and STATE.md; pair at engagement start
- `client-handoff` — at engagement end, harvest reusable feedback into a generic playbook
