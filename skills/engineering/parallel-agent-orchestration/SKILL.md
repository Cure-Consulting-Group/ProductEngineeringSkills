---
name: parallel-agent-orchestration
description: "Run N simultaneous agent sessions on one repo safely — worktree-per-ticket, module-boundary decomposition, rate-limit budgeting, model tiering, single-owner destructive ops"
when_to_use: "Use when running 2+ concurrent sessions on one repo or parallelizing a wave. NOT worktree mechanics (git-worktree-manager). NOT unattended runs (engagement-automation)."
argument-hint: "[wave-or-ticket-list]"
---

# Parallel Agent Orchestration

The operating model for running multiple agent sessions on one project at
once. `git-worktree-manager` owns the *mechanics* (creating worktrees, ports,
env files); this skill owns the *judgment*: what parallelizes, who owns the
merge, how the token budget splits, and what must never run twice.

Cure default: any wave with 3+ independent tickets, or any day where a feature
session and a review/hotfix session run simultaneously.

## The iron rules

1. **One ticket = one worktree = one branch = one session.** No agent works
   across ticket boundaries. A session that discovers out-of-scope work files
   a ticket; it does not fix it.
2. **Parallelism buys wall-clock, not capacity.** Rate limits are per-account
   and shared: four concurrent Opus sessions burn one budget 4× faster.
   Parallelize to compress calendar time, never to "get more tokens."
3. **A script declares done, not the agent.** Every parallel ticket needs an
   executable acceptance gate (tests, lint, grep-check) before it is spawned.
   No gate → not parallelizable yet → write the gate first.
4. **Humans hold the merge.** Parallel branches are proposals. Merging is a
   serial, human act — this is the control that makes everything else safe.

## Step 1: Classify the parallel work

| Scenario | Pattern |
|---|---|
| Wave of scoped tickets (BACKLOG style) | Worktree per ticket, cheap-model mechanical tickets first, judgment tickets serial on the strong model |
| Feature + hotfix + PR review same day | Long-lived feature worktree + two ephemeral worktrees (see git-worktree-manager) |
| Repo-wide mechanical change | One orchestrating session fanning out subagents (`isolation: worktree`), not N manual sessions |
| Audit/review of a large surface | Parallel read-only subagents, one synthesis session; no worktrees needed (nothing mutates) |
| Two agents editing the same module | **Don't.** Re-decompose until they don't (Step 2) |

## Step 2: Decompose along module boundaries, not ticket numbers

Merge conflicts scale roughly with the square of concurrent branches touching
shared files. Before spawning sessions:

1. List the files/dirs each ticket will touch (from its scope line).
2. Overlaps between two tickets → serialize those two, or re-cut the boundary.
3. Files everyone touches (lockfiles, generated docs, version manifests) →
   designate ONE owner branch; everyone else leaves them alone and the owner
   regenerates after merge.
4. If you can't predict the touched files, the ticket is under-scoped —
   sharpen it before parallelizing, not after the conflict.

## Step 3: Budget the fleet

| Work type | Model/effort | Concurrency |
|---|---|---|
| Judgment: architecture, review, audits, tricky debugging | Strong model, high effort | Serial, or 2 max |
| Mechanical: migrations, test fixes, doc gen, scaffolds | Cheaper model / lower effort | Parallel freely |
| Verification of others' output | Strong model, but read-only | Parallel (no write conflicts) |

Watch the shared budget: if sessions start rate-limiting each other, cut
concurrency before cutting model quality on judgment work.

## Step 4: Blast radius → autonomy

Extends AUTOMATION.md rule 1 from unattended runs to interactive parallel work:

| Blast radius | Autonomy |
|---|---|
| Low (additive files, isolated module, gate-covered) | Run unattended in its worktree; review at merge |
| Medium (shared modules, config, CI, public interfaces) | Run attended; human reads the diff before PR |
| High (migrations, deploys, releases, secrets, deletions, anything regulated) | **Never parallel, never unattended.** Single owner, serial, human confirms each step |

## Step 5: Mutual exclusion on destructive ops

Two sessions must never both believe they own a destructive operation.
Convention: a `.cure-locks/` directory at repo root (gitignored).

```bash
# claim (fails loudly if held)
mkdir .cure-locks 2>/dev/null; ln -s "$(git branch --show-current)-$$" .cure-locks/migrate 2>/dev/null \
  || { echo "LOCKED by $(readlink .cure-locks/migrate)"; exit 1; }
# release when done
rm .cure-locks/migrate
```

Locked ops: db migrations, `release.sh`, deploys, seed/reset scripts, anything
on the AUTOMATION.md never-unattended list. Stale lock (owner session gone) is
a human call to break — never auto-broken by an agent.

## Step 6: Merge discipline

1. Merge order: lowest-risk first; the shared-file owner branch last.
2. Every branch re-runs its gate after rebase — a green branch pre-rebase
   proves nothing post-rebase.
3. One conflict-heavy merge means Step 2 failed: fix the decomposition for
   the next wave, don't get better at resolving conflicts.

## Anti-patterns

- Two sessions in the same working directory (state corruption, silent
  overwrites — always a worktree per session).
- Parallelizing to "go faster" on judgment work: review quality drops faster
  than wall-clock does.
- Letting an agent both write a change and grade it done — gates or a second
  read-only session verify.
- Spawning the wave before every ticket has a gate ("we'll check it at the
  end" = you won't).
