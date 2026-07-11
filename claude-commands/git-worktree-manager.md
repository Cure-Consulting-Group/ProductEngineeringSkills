# Git Worktree Manager

A consultant's day looks like this: feature branch open in editor, client pings about a hotfix, a PR needs review, the QA team finds a regression on staging. Stashing and switching branches loses state, breaks dev servers, kills your terminal session. Worktrees solve this. One repo, multiple working directories, each on its own branch, each with its own dev server, each independent.

Cure default: long-running consulting engagements, three or more parallel branches per week, dev servers that take more than 30s to start cold.

## When NOT to use this skill

- You only ever work one branch at a time. Worktrees are overhead with no payoff.
- The repo has bound state in checked-in folders (e.g., a `vendor/` directory mutated by tooling) that worktrees can't isolate.
- The dev environment requires Docker volumes mapped to the working directory — port and volume isolation across worktrees needs explicit setup or it breaks silently.
- Submodules with relative paths — historically buggy with worktrees, test before committing.

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

Additionally gather (domain-specific):
- `git worktree list` — what worktrees already exist
- `git branch -a | head -20` — branch landscape
- `ls .env* 2>/dev/null` — env files in play
- `cat .gitignore | grep -E "^\.env"` — what's gitignored
- `lsof -iTCP -sTCP:LISTEN -P 2>/dev/null | grep -E "300[0-9]|800[0-9]"` — ports in use

## Step 1: Classify the Use Case

| Scenario | Pattern |
|----------|---------|
| Parallel feature work — two branches in active development | Two long-lived worktrees, one per feature, each with its own dev server on a unique port |
| Hotfix on top of a long-running review branch | Ephemeral worktree off `main`, fix, PR, delete |
| Reviewing a PR without disturbing local state | Ephemeral worktree at `pr-<number>`, run app, leave comments, delete |
| Running multiple test envs simultaneously (e.g., compare A vs. B behavior) | Two worktrees on different branches, isolated DBs, isolated ports |
| Bisecting a bug while feature work continues | Bisect worktree separate from feature worktree |
| Pre-merge integration test (merge X into Y locally before PR) | Throwaway worktree where you do the test merge |

If none of these apply, you don't need this skill. Use `git switch`.

## Step 2: Gather Context

1. **Branch strategy** — Trunk-based with short-lived branches? Long-running release branches? GitFlow?
2. **Env file complexity** — One `.env.local` or many (`.env.development`, `.env.test`, per-service)? Any committed templates?
3. **Port conflicts likely?** — Does the app bind hardcoded ports? Multiple services per app? Reverse proxies?
4. **Database state** — Does each worktree need its own DB, or is it OK to share? Migrations destructive?
5. **Disk budget** — Each worktree is a full checkout (no shared `.git/objects` issue, but `node_modules`, `.next`, build artifacts duplicate). Budget 1–5 GB per worktree for typical JS projects.

## Step 3: Worktree Creation Patterns

### Naming convention

Worktrees live as siblings to the main checkout, never inside it.

```
~/projects/
  acme/                       — main checkout (often on main)
  acme-feature-payments/      — worktree on feature/payments
  acme-hotfix-auth/           — worktree on hotfix/auth-bug
  acme-pr-1234/               — worktree reviewing PR #1234
  acme-bisect/                — worktree for git bisect runs
```

Pattern: `<repo>-<purpose>-<short-id>`. Never reuse a name. Names map 1:1 to branches.

### Lifecycle commands

```bash
# Create worktree on a new branch from main
git worktree add ../acme-feature-payments -b feature/payments origin/main

# Create worktree on an existing remote branch
git fetch origin feature/checkout
git worktree add ../acme-feature-checkout feature/checkout

# Create worktree on a PR (GitHub CLI)
gh pr checkout 1234 --branch pr-1234
git worktree add ../acme-pr-1234 pr-1234

# Detached HEAD for read-only review or bisect
git worktree add --detach ../acme-bisect HEAD~50

# List all worktrees
git worktree list

# Remove a worktree (after merging or abandoning the branch)
git worktree remove ../acme-feature-payments

# Force-remove if working directory has uncommitted changes (lose them)
git worktree remove --force ../acme-pr-1234

# Prune stale worktree records (after manual rm of the directory)
git worktree prune --verbose
```

### Rules

- Never check out the same branch in two worktrees. Git will refuse; if you bypass with `--force`, you'll create chaos.
- Never put a worktree inside the main repo's working tree. Always sibling directories.
- Treat worktree directories as ephemeral except for explicitly long-lived ones.

## Step 4: Port Isolation

Two dev servers on port 3000 cause silent failures: one binds, the other gets EADDRINUSE or — worse — a stale connection talks to the wrong server.

### Strategy: per-worktree port offset

```bash
# Pick a base port per worktree at creation time
# Main:                   PORT=3000
# acme-feature-payments:  PORT=3010
# acme-feature-checkout:  PORT=3020
# acme-hotfix-auth:       PORT=3030
```

Encode the offset in the worktree's `.env.local` (which is gitignored — see Step 5).

```bash
# acme-feature-payments/.env.local
PORT=3010
DATABASE_URL=postgresql://localhost:5432/acme_feature_payments
NEXT_PUBLIC_API_URL=http://localhost:3010
```

### Multi-service apps

If the app has 4 services (web, api, worker, ws), allocate a 10-port block per worktree.

```
Main worktree:        3000 (web)  3001 (api)  3002 (worker)  3003 (ws)
Feature-payments:     3010        3011        3012           3013
Feature-checkout:     3020        3021        3022           3023
```

Use a helper:

```bash
# scripts/worktree-port.sh — sourced by .envrc or shell init
WORKTREE_INDEX=$(git worktree list | grep -n "$(pwd)" | cut -d: -f1)
export PORT_BASE=$((3000 + (WORKTREE_INDEX - 1) * 10))
export WEB_PORT=$PORT_BASE
export API_PORT=$((PORT_BASE + 1))
```

## Step 5: Env File Sync

Three categories. Get this wrong and you commit secrets, or worse, run prod against staging.

| File | Strategy | Why |
|------|----------|-----|
| `.env.example` | Tracked in git | Already shared. No worktree-specific action. |
| `.env.local` (gitignored, contains secrets and worktree-unique values like ports) | **Copy** at worktree creation, then **edit** for unique values | Each worktree needs its own ports/DB; can't symlink because edits would propagate |
| `.env.development` (shared dev defaults, gitignored) | **Symlink** to main checkout | Avoid drift — all worktrees share the same dev defaults |
| `.env.test` (test fixtures) | **Symlink** | Tests should run identically across worktrees |
| `.env.production` | Never on local. Period. | Prod secrets do not live in any worktree. |

### Bootstrap script

```bash
# scripts/worktree-init.sh
#!/usr/bin/env bash
set -euo pipefail

WORKTREE_DIR="$1"
MAIN_REPO="$(git rev-parse --show-toplevel)"
PORT_OFFSET="${2:-10}"

cd "$WORKTREE_DIR"

# Symlink shared dev/test env defaults
ln -sf "$MAIN_REPO/.env.development" .env.development 2>/dev/null || true
ln -sf "$MAIN_REPO/.env.test" .env.test 2>/dev/null || true

# Copy and rewrite .env.local
if [ -f "$MAIN_REPO/.env.local" ]; then
  cp "$MAIN_REPO/.env.local" .env.local
  # Rewrite ports
  sed -i.bak "s/PORT=3000/PORT=$((3000 + PORT_OFFSET))/g" .env.local
  rm -f .env.local.bak
fi

# Per-worktree DB
WORKTREE_NAME=$(basename "$WORKTREE_DIR")
echo "DATABASE_URL=postgresql://localhost:5432/$WORKTREE_NAME" >> .env.local

echo "Worktree $WORKTREE_NAME initialized. Ports offset by $PORT_OFFSET."
```

### Hard rules

- `.env*` must be in `.gitignore` at the repo root before any worktree is created.
- Never `git add -f` an env file from a worktree.
- A pre-commit hook should refuse any staged `.env*` (see `rules/cicd.md` and `/git-workflow`).

## Step 6: Database Considerations

The right answer depends on migration cost and data volume.

| Approach | When | Setup |
|----------|------|-------|
| **Separate DB per worktree** | Migrations are destructive or slow; you need to test schema changes in isolation | `createdb acme_feature_payments` per worktree; DATABASE_URL in `.env.local` |
| **Schema per worktree** (one DB, multiple schemas) | Postgres-only, fast schema switches, low data volume | `CREATE SCHEMA worktree_payments;` + `search_path` set in `.env.local` |
| **Shared dev DB** | Read-mostly work, reproducible seed data, no destructive migrations in flight | All worktrees point at the same DB; accept that one bad migration breaks all |
| **Snapshot-and-restore** | Heavy seed data (analytics dumps, anonymized prod), slow to recreate | `pg_dump` once → `pg_restore` per worktree on creation; refresh weekly |

Cure default: separate DB per long-lived worktree, shared dev DB for ephemeral review worktrees.

```bash
# Postgres per-worktree DB bootstrap
WORKTREE_NAME=$(basename "$(pwd)")
DB_NAME="${WORKTREE_NAME//-/_}"
createdb "$DB_NAME" || true
psql "$DB_NAME" < "$MAIN_REPO/db/seed.sql"
echo "DATABASE_URL=postgresql://localhost:5432/$DB_NAME" >> .env.local
npm run db:migrate
```

## Step 7: Cleanup

Worktrees that outlive their branches become bit-rot landmines. Stale `node_modules`, expired tokens, drifted env files.

### Detection

```bash
# List worktrees with their branches
git worktree list

# Find worktrees whose branches are merged into main
for wt in $(git worktree list --porcelain | awk '/^worktree / {print $2}' | tail -n +2); do
  branch=$(git -C "$wt" branch --show-current 2>/dev/null)
  if [ -n "$branch" ] && git merge-base --is-ancestor "$branch" origin/main 2>/dev/null; then
    echo "Mergeable/merged: $wt ($branch)"
  fi
done

# Find worktrees with no commits in 30+ days
for wt in $(git worktree list --porcelain | awk '/^worktree / {print $2}'); do
  last=$(git -C "$wt" log -1 --format=%ct HEAD 2>/dev/null)
  if [ -n "$last" ] && [ $(( ($(date +%s) - last) / 86400 )) -gt 30 ]; then
    echo "Stale (>30d): $wt"
  fi
done
```

### Cleanup workflow

```bash
# Safe removal — only if clean working tree
git worktree remove ../acme-feature-payments

# After merging the branch
git branch -d feature/payments

# After accidentally rm -rf'ing a worktree directory
git worktree prune

# Nuclear (force, lose uncommitted work)
git worktree remove --force ../acme-pr-1234
git branch -D pr-1234
```

### Rule of thumb

- Ephemeral worktrees (PR review, hotfix): remove same day.
- Feature worktrees: remove within 24 hours of branch merge.
- Bisect worktrees: remove on `git bisect reset`.

## Step 8: Tooling

### Shell helpers

```bash
# Add to .zshrc / .bashrc
# Quick worktree creation with bootstrap
wt() {
  local name="$1"
  local branch="${2:-$1}"
  local repo_root=$(git rev-parse --show-toplevel)
  local repo_name=$(basename "$repo_root")
  local target="$(dirname "$repo_root")/${repo_name}-${name}"

  git worktree add -b "$branch" "$target" origin/main || \
    git worktree add "$target" "$branch"

  bash "$repo_root/scripts/worktree-init.sh" "$target"
  cd "$target"
}

# Quick switch
wtcd() {
  local target=$(git worktree list --porcelain | awk '/^worktree / {print $2}' | fzf)
  cd "$target"
}

# Quick list
wtls() {
  git worktree list
}

# Quick remove
wtrm() {
  local target=$(git worktree list --porcelain | awk '/^worktree / {print $2}' | tail -n +2 | fzf)
  git worktree remove "$target"
}
```

### IDE integration

| Editor | How |
|--------|-----|
| **VS Code** | Open each worktree as a separate window. Or use a multi-root workspace: `File > Add Folder to Workspace`. Each worktree gets its own debugger config, terminals, and extensions state. |
| **IntelliJ / WebStorm** | "Open" each worktree as a separate project. JetBrains does not handle multi-root well; one window per worktree is cleaner. |
| **Neovim / tmux** | One tmux session per worktree (`tmux new -s payments`); tmuxinator config per worktree to start dev servers. |
| **Cursor** | Same as VS Code. |

## Anti-Patterns

| Anti-Pattern | Why It Hurts | Fix |
|--------------|--------------|-----|
| Long-lived worktrees that bit-rot | Stale `node_modules`, drifted env files, expired tokens — when you finally use it, nothing works | Cleanup ritual: weekly review of `git worktree list`, remove anything older than 30 days |
| Port collisions causing silent test failures | Test hits port 3000 expecting worktree A's API, gets worktree B's | Per-worktree port offset, encoded in `.env.local`, asserted at startup |
| `.env` files committed by accident from a worktree | Secrets in repo history; `git rm` doesn't unleak them | Pre-commit hook refusing `.env*`, gitignore `.env*` at root before any worktree exists |
| Worktree inside the main checkout (`./worktrees/foo`) | Tooling globs (jest, eslint, tsc) traverse into other branches' source — surreal errors | Always create worktrees as siblings of the main repo, never as children |
| Two worktrees both pointing at the same prod DB | Concurrent destructive migrations corrupt data | Per-worktree DB or hard-asserted read-only `DATABASE_URL` |
| Forgetting `git worktree prune` after manual `rm -rf` | Git still tracks the path; subsequent operations confuse-warn | After any manual deletion: `git worktree prune --verbose` |
| Sharing a `node_modules` via symlink across worktrees | Different branches need different deps; symlinked `node_modules` causes phantom failures | Each worktree gets its own `node_modules`. Disk is cheap. Use pnpm to share via content-addressable store. |
| Reusing worktree directory names | Stale git records, confused branch state | One name = one branch = one worktree, ever |

## Cross-References

- `/git-workflow` — for the team-wide branching and PR conventions worktrees support
- `/ci-cd-pipeline` — when running ephemeral CI workers as worktrees on a host
- `/project-bootstrap` — for `scripts/worktree-init.sh` template at project setup
- `rules/cicd.md` — for pre-commit hook standards that prevent committed env files

## Step 9: Output

When invoked, produce:
1. **Diagnosis** — current worktree state (`git worktree list`), what the user is trying to do.
2. **Recommended worktree plan** — name, branch, port offset, DB strategy, env file plan.
3. **Concrete commands** — `git worktree add ...`, `scripts/worktree-init.sh ...`, `cd ...`. Run them with the user's confirmation.
4. **Cleanup reminder** — when this worktree should be removed and how.
5. **Aliases / IDE setup** — if the user doesn't have shell helpers or multi-root workspace, generate them.

Never create a worktree without first verifying `.env*` is gitignored. Never share a DATABASE_URL between long-lived worktrees without explicit confirmation.
