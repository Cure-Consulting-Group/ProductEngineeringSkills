# Self-Improving Memory

Codifies Cure's auto-memory pattern so it's portable to every client engagement. The four memory types (`user`, `feedback`, `project`, `reference`) are canonical — do not invent new ones. This skill bootstraps memory for new engagements, audits existing `MEMORY.md`, detects when memories should be consolidated or extracted, and runs health checks for staleness, contradictions, and duplicates.

## Pre-Processing (Auto-Context)

Before starting, gather context silently:

- Check for `MEMORY.md` at repo root and `.claude/memory/` directory
- Run: `ls -la .claude/memory/ 2>/dev/null` to see memory entry layout
- Run: `wc -l MEMORY.md 2>/dev/null` to gauge index size
- Run: `git log --format=%cI -1 MEMORY.md 2>/dev/null` for last-touched timestamp
- Read `CLAUDE.md` if present — distinguishes project identity from session memory
- Today's date is needed to evaluate freshness of `project` entries — assume the system date

## Step 1: Classify the Request

| Mode | When to Use | Output |
|------|-------------|--------|
| **bootstrap** | New engagement, no MEMORY.md yet | Starter MEMORY.md + kickoff interview to populate `user` + `project` |
| **audit** | MEMORY.md exists, user wants a sweep | Scored report — distribution by type, anti-patterns, recommendations |
| **detect-patterns** | Feedback memories piling up on similar topics | Consolidation proposals (extract rule, merge entries, retire entries) |
| **health-check** | Periodic hygiene (every 2-4 weeks) | List of stale / contradictory / duplicate entries with proposed actions |

If the user's request is ambiguous, ask one question: "Bootstrap a new engagement, audit existing memory, detect patterns, or run a health check?"

## Step 2: Gather Context

Required signals before any mode runs:

1. **Engagement age** — `git log --reverse --format=%cI | head -1` for first commit; compare to today
2. **MEMORY.md size** — line count; index over 200 lines is a smell
3. **Entry distribution** — count entries by `type:` frontmatter across `.claude/memory/*.md`
4. **Recent feedback count** — feedback memories created in last 14 days (high churn = consolidation opportunity)
5. **Stale candidates** — project memories with `by:` dates in the past, or files referencing paths that no longer exist

If `.claude/memory/` is not a directory but memory is stored inline in MEMORY.md, treat MEMORY.md as the corpus and parse headings as entries.

## Step 3: Memory Taxonomy (Canonical)

Four types. Do not invent more. Each has a distinct trigger and a distinct decay profile.

### `user`
**What:** role, preferences, knowledge depth, responsibilities, communication style.
**Write when:** learning who the user is — first-session intros, "I'm the X at Y" statements, observed preferences ("they always want unit tests first").
**Lifespan:** long. User memories rarely go stale within a single engagement.
**Example body:** `Rashad is the founder of Cure Consulting Group. Prefers terse, opinionated output with concrete numbers. Knows Kotlin/Compose deeply; less hands-on with Rust.`

### `feedback`
**What:** corrections AND validated approaches. Both "don't do X" and "do Y, it worked."
**Write when:** the user corrects you, OR an approach you took was explicitly validated.
**Required fields:** **Rule** (the directive), **Why** (rationale — without this it's noise), **How to apply** (concrete trigger).
**Lifespan:** medium. Feedback decays when the underlying constraint changes — re-validate before relying on a >60-day-old feedback rule.
**Example body:** `Rule: Never commit without running the lint script. Why: pre-commit hook is advisory; CI rejects unlinted code and burns 6 minutes per failure. How: before any git commit, run `npm run lint`.`

### `project`
**What:** initiatives in flight, deadlines, stakeholder context, sprint goals.
**Write when:** a new initiative starts, a deadline lands, a stakeholder enters/exits.
**Required:** convert relative dates to absolute (`by 2026-05-15`, not `next Friday`).
**Lifespan:** short. Project memories decay fast — retire when `by:` passes or the initiative ships.
**Example body:** `Q2 push: ship Stripe Connect onboarding by 2026-05-15. Owner: Rashad. Blocker: waiting on client legal review of Connect agreement.`

### `reference`
**What:** pointers to external systems — Linear projects, Slack channels, dashboards, runbooks, account IDs.
**Write when:** a pointer is referenced more than once and isn't already in CLAUDE.md.
**Lifespan:** medium-long. Reference memories go stale silently — verify URL/handle on recall.
**Example body:** `Linear project for this engagement: linear.app/cure/project/cure-acme-q2. Slack channel: #cure-acme. Status dashboard: dash.cure.dev/acme.`

## Step 4: When to Save (Triggers)

| Type | Trigger |
|------|---------|
| `user` | First session, or observed preference repeated 2+ times |
| `feedback` | Explicit correction, OR explicit validation of an approach |
| `project` | New initiative, new deadline, new/changed stakeholder, sprint kickoff |
| `reference` | External pointer used 2+ times in conversation |

Save eagerly when the trigger fires. Memory you skip writing is memory you can't recall.

## Step 5: When NOT to Save

Hard rules. Violating these is the fastest way to make MEMORY.md useless.

- **Code-derivable facts.** "The User model has a `stripe_customer_id` field" — read the code. Don't memorize it.
- **Git history.** "Last commit was about auth refactor" — `git log` already knows.
- **CLAUDE.md duplicates.** If it's project identity (stack, architecture, hard rules), it goes in CLAUDE.md, not MEMORY.md.
- **Ephemeral state.** "Just installed dependencies" — irrelevant by next session.
- **Debug recipes.** "Ran `lsof -i :8080` to find the port hog" — this is a runbook entry, not a memory.
- **Secrets, credentials, tokens.** Ever. Use the credential vault.
- **Negative judgments about the user.** "User is impatient" — not memory, just bias.
- **Feedback without Why.** "Don't use `any`" with no rationale is unactionable noise — skip or upgrade it.

## Step 6: Pattern Detection (The Self-Improving Part)

Run during `detect-patterns` mode, or opportunistically when adding a new entry.

### Trigger 1: ≥3 feedback memories on the same topic
Action: propose **consolidation** into a single feedback rule with explicit Why/How, OR **extraction** into a new project-level rule (CLAUDE.md addition or new skill). Show the user the cluster and the proposed consolidated rule.

Example cluster:
- "Don't ship without tests"
- "Tests should run before commit"
- "Failed tests in CI cost 6 min — run locally first"

Proposed consolidation:
> Rule: Run `npm test` locally before every commit. Why: CI failures cost 6+ min per cycle and block the team. How: pre-commit checklist — lint, test, type-check.

### Trigger 2: ≥2 reference memories pointing at the same external system
Action: propose a **single consolidated reference entry** with all sub-pointers (project URL, channel, dashboard, on-call rota) in one place. Delete the fragments.

### Trigger 3: A project memory's `by:` date has passed
Action: propose **retire** (initiative shipped) or **update** (slipped to new date with rationale). Don't let dead deadlines accumulate — they erode trust in the index.

### Trigger 4: Three sessions in a row recall the same fact from code
Action: that fact is stable enough — propose extraction into CLAUDE.md (project identity) or a feedback rule. Don't let recurring lookups burn context budget.

## Step 7: Memory Health Checks

Run during `health-check` mode. Output a triage list with proposed action per entry.

| Check | How to Detect | Action |
|-------|---------------|--------|
| **Stale file references** | Memory cites `path/to/file.ts`; run `test -f` — file moved or deleted | Update path or retire entry |
| **Stale URL references** | Reference entries with `linear.app/...`, `*.slack.com`, dashboards | Flag for human verification (don't auto-fetch) |
| **Contradictions** | Two feedback memories with conflicting rules on the same topic | Surface both, ask user which is current, retire loser |
| **Near-duplicates** | Two entries with high-overlap bodies on the same type+topic | Propose merge |
| **Expired project entries** | `by:` date in past, no shipped/retired marker | Retire or update |
| **Why-less feedback** | Feedback entries missing Why or How fields | Upgrade in place or retire |
| **Index bloat** | MEMORY.md > 200 lines | Force consolidation pass |

Output format: a table of `(entry, issue, proposed action)` rows. Do not auto-delete — propose, then wait for confirmation.

## Step 8: Seeding for New Engagements (`bootstrap` mode)

### 8.1 Write the starter index

Create `MEMORY.md` from `templates/MEMORY.md.template`. Replace `[ENGAGEMENT_NAME]` and `[YYYY-MM-DD]`. Leave the four type sections present but empty — entries get added as they're earned.

### 8.2 Run the kickoff interview

Ask in a single grouped message. Pre-fill anything detectable from `CLAUDE.md` or repo state.

```
Memory bootstrap — answer what you can, skip what you can't:

1. USER MEMORY
   - Your role on this engagement?
   - Communication style preference (terse / detailed / Socratic)?
   - Domain depth — strong areas, weak areas, areas you want me to challenge?

2. PROJECT MEMORY
   - Current sprint goal (one sentence)?
   - Hard deadlines in the next 30 days (date + what ships)?
   - Active stakeholders (name + role + what they care about)?

3. REFERENCE MEMORY
   - Linear / Jira / Asana project URL?
   - Primary Slack / Teams channel?
   - Status dashboard or runbook URL?
   - On-call rota or escalation contact?

4. FEEDBACK SEEDS (optional)
   - Any rules from prior engagements you want me to carry over?
     (Format each as: Rule + Why + How to apply.)
```

### 8.3 Write the seeded entries

For each answer, write a memory entry using the right template (`feedback_template.md`, `project_template.md`, etc.). Update `MEMORY.md` to index the new entries.

## Step 9: When Recalling

Memory is a hint, not a source of truth. On every recall:

1. **Verify before acting.** If the memory references a file, dashboard, or person, confirm it still exists / still applies.
2. **Trust observation over recall when they conflict.** If MEMORY.md says "the API uses Bearer tokens" and the code uses cookie auth, the code wins — and the memory needs an update.
3. **Cite the memory when surfacing it.** "Per a feedback memory from 2026-03-12: ..." — gives the user context to validate or override.
4. **Decay-aware:** if a feedback memory is >60 days old and you're about to act on it, ask "is this still current?" before proceeding.

## Anti-Patterns

- **Saving info derivable from code** — bloats memory, ages instantly.
- **Saving secrets** — memory is not a vault. Ever.
- **Saving negative judgments about the user** — bias, not memory.
- **Saving feedback without Why** — unactionable; you'll re-derive the rationale anyway.
- **Saving project memory without an absolute date** — "next sprint" is meaningless in 90 days.
- **Letting MEMORY.md grow past 200 lines** — the index becomes noise. Force a consolidation pass.
- **Inventing memory types** — only `user`, `feedback`, `project`, `reference`. Mapping novel needs to one of the four is the discipline.
- **Saving CLAUDE.md content** — project identity belongs in CLAUDE.md. Memory is for state, preferences, and pointers.

## Output Format

### `audit` mode output

```
MEMORY AUDIT — [ENGAGEMENT_NAME]
Generated: [YYYY-MM-DD]

Distribution:
  user:       [N] entries
  feedback:   [N] entries
  project:    [N] entries
  reference:  [N] entries
  Total:      [N] entries / [N] lines in MEMORY.md

Anti-patterns detected:
  - [count] feedback entries missing Why field
  - [count] project entries with passed `by:` date
  - [count] reference entries pointing at the same Linear project
  - [count] entries with paths that no longer exist

Recommendations:
  1. [highest-leverage cleanup]
  2. [next]
  ...
```

### `detect-patterns` mode output

For each cluster: the cluster, the proposed consolidation, the entries to retire after consolidation. Wait for confirmation before writing.

### `health-check` mode output

A triage table: `entry path | issue | proposed action`. Wait for confirmation before any retire/merge.

## Templates

- `templates/MEMORY.md.template` — starter index for new engagements
- `templates/feedback_template.md` — frontmatter + Rule/Why/How skeleton
- `templates/project_template.md` — frontmatter + initiative/deadline/stakeholder skeleton

## Related Skills

- `/project-bootstrap` — generates CLAUDE.md and STATE.md; pair with this skill at engagement start
- `/client-handoff` — at engagement end, harvest reusable feedback memories into a generic playbook before retiring the engagement-specific MEMORY.md
