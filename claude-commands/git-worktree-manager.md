# Git Worktree Manager

**Outcome:** a worktree that runs side by side with the others — its own branch, port block, env
file, and (if needed) database — plus when and how to remove it. Done when the user has the
commands (run with their confirmation) and a cleanup date. Don't restructure the repo's tooling or
branching model.

Cure default: use worktrees on engagements with three or more parallel branches a week or dev
servers that take >30 s to start cold. Skip them when there's one branch at a time, tooling mutates
checked-in folders (`vendor/`), Docker volumes are mapped to the working directory without
per-worktree config, or submodules use relative paths (test first).

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Worktrees: !`git worktree list 2>/dev/null | head -10 || echo "(not a git repo)"`
- Env files: !`ls -a .env* 2>/dev/null | head -8 || echo "(none)"`
- Env ignored?: !`git check-ignore -q .env.local 2>/dev/null && echo "yes" || echo "NO — .env.local is not gitignored"`
- Listening dev ports: !`lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | grep -oE ':(30|50|80)[0-9]{2} ' | sort -u | head -8 || echo "(none)"`

## Step 1: Classify the Use Case

| Scenario | Pattern |
|----------|---------|
| Two features in active development | Two long-lived worktrees, each with its own port block |
| Hotfix while mid-feature | Ephemeral worktree off `main`; fix, PR, remove same day |
| Reviewing a PR without disturbing local state | Ephemeral `pr-<N>` worktree; review, remove |
| Comparing two branches' behaviour | Two worktrees, isolated DBs and ports |
| Bisecting while feature work continues | Detached bisect worktree |
| Local test merge before a PR | Throwaway worktree for the merge |

None apply → recommend `git switch` and stop.

## Step 2: Gather Context

Ask only what the auto-context didn't answer: branch strategy (trunk vs long-lived release
branches), how many services bind ports, whether migrations are destructive (decides the DB
approach), and disk budget (each worktree duplicates `node_modules` and build output — budget
1–5 GB per JS worktree; pnpm's content-addressable store cuts this).

## Step 3: Create the Worktree

Worktrees are siblings of the main checkout, named `<repo>-<purpose>` (e.g. `acme-payments`,
`acme-pr-1234`) — never inside the main tree, because jest/eslint/tsc globs would traverse other
branches' source. One name = one branch = one worktree; never reuse a name.

The bundled script does creation, port allocation, and env setup in one step (Python 3 stdlib;
run with `--dry-run` first and show the plan):

```bash
python3 <skill-dir>/scripts/worktree_create.py payments --branch feature/payments   # new or existing branch
python3 <skill-dir>/scripts/worktree_create.py pr-1234 --pr 1234                    # PR review
python3 <skill-dir>/scripts/worktree_create.py bisect --detach HEAD~50 --no-env      # bisect
```

It refuses to run if `.env.local` isn't gitignored. Equivalent raw git, if the user prefers:

```bash
git worktree add -b feature/payments ../acme-payments origin/main   # new branch
git fetch origin pull/1234/head:pr-1234                              # PR, without touching the
git worktree add ../acme-pr-1234 pr-1234                             #   current checkout
git worktree add --detach ../acme-bisect HEAD~50
```

Don't use `gh pr checkout` for this — it switches the *current* checkout to the PR branch, which is
exactly what the worktree is meant to avoid. Git refuses to check out one branch in two worktrees;
don't override that with `--force`.

## Step 4: Port Isolation

Two dev servers on one port fail silently: one gets EADDRINUSE, or a test talks to the wrong
worktree's API. Each worktree gets a 10-port block (web, api, worker, ws…): main = 3000–3009,
then 3010, 3020, …

Allocation must be stable. The script records slots in `worktree-ports.json` in the repo's shared
git dir, reuses a path's slot, and fills the lowest free slot — removing a worktree never shifts
another's ports. (Deriving the index from `git worktree list` order is the classic bug: ports move
whenever a worktree is removed, and grep on the path prefix-matches `acme` against `acme-payments`.)
It writes `PORT` and `PORT_BASE` into the worktree's `.env.local`; derive per-service ports as
`PORT_BASE + n`. Apps should assert their port at startup.

## Step 5: Env Files

| File | Strategy | Why |
|------|----------|-----|
| `.env.example` | Tracked | Already shared |
| `.env.local` (secrets + unique ports/DB) | Copied, then rewritten per worktree | Symlinking would propagate port edits |
| `.env.development`, `.env.test` (shared defaults) | Symlinked to main | No drift between worktrees |
| `.env.production` | Never in any worktree | Prod secrets don't live on laptops |

`.env*` must be in `.gitignore` before the first worktree exists, and a pre-commit hook should
refuse staged `.env*` files (see the `ci-cd-pipeline` skill) — a committed secret stays in history
even after `git rm`.

## Step 6: Database

| Approach | When |
|----------|------|
| Separate DB per worktree (`--db` writes `DATABASE_URL`; then `createdb <name>`, seed, migrate) | Destructive or slow migrations |
| Schema per worktree (Postgres `search_path`) | Low data volume, fast switching |
| Shared dev DB | Read-mostly work, no destructive migration in flight |
| Snapshot/restore (`pg_dump` once, `pg_restore` per worktree) | Heavy seed data |

Cure default: separate DB for long-lived worktrees, shared dev DB for ephemeral review worktrees.
Never point two long-lived worktrees at one DATABASE_URL without the user's explicit OK, and never
at production.

## Step 7: Cleanup

```bash
python3 <skill-dir>/scripts/worktree_report.py --stale-days 30        # merged / stale (exit 1 if any)
git worktree remove ../acme-payments && git branch -d feature/payments
git worktree prune --verbose                                          # after a manual rm -rf
python3 <skill-dir>/scripts/worktree_report.py --release-missing      # free their port slots
```

Ephemeral (PR, hotfix): remove the same day. Feature: within 24 h of merge. Bisect: on
`git bisect reset`. `git worktree remove --force` discards uncommitted work — confirm first.

## Step 8: Editors

VS Code / Cursor: one window per worktree (or a multi-root workspace). JetBrains: one project
window per worktree. tmux: one session per worktree. Shell helpers (`wt`, `wtrm`) are optional —
wrap the two scripts rather than re-implementing port logic in shell.

## Output

1. Diagnosis — current worktrees and what the user is trying to do.
2. Plan — name, branch, port block, DB approach, env handling.
3. Commands — script invocation (dry-run first) or raw git; run only with confirmation.
4. Cleanup — when to remove it and how.

## Scripts

- `scripts/worktree_create.py` — create a sibling worktree (branch, `--pr`, `--detach`) with a stable port slot and env files; `--dry-run`, `--json`.
- `scripts/worktree_report.py` — list merged/stale worktrees; `--release-missing` frees slots of removed ones; `--json`.

## Related Skills

`ci-cd-pipeline` (branching strategy, pre-commit env guard), `parallel-agent-orchestration`
(one worktree per agent session), `project-bootstrap` (adding the scripts to a new repo).
