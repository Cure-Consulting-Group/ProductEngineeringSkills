# <project> — agent map

<One paragraph: what the product is, its platforms, and where production runs.> This file is the
map for every agent lane (Claude Code reads it through `CLAUDE.md`; Codex reads it directly).
Details live in `docs/`; this file points at them.

## Commands

| Task | Command |
|---|---|
| **The gate** (<what it runs>; <measured>s) | `scripts/verify.sh` |
| <Tests only> | `<command exactly as CI runs it>` |
| <Lint only> | `<command>` |
| <Native / slow suites that stay out of the gate> | `<command>` |

`scripts/verify.sh` is the definition of done. A Stop hook runs it when you change gated code,
and CI runs the same suites on every PR.

## Layout

| Path | What it is |
|---|---|
| `<dir>/` | <one line> |

## Where knowledge lives

- `docs/adr/`: decisions. Read the ADR before changing what it governs.
- `<runbook / PRD / backlog paths>`
- `STATE.md`: in-flight work, newest first. Read the top entry; add yours on top. History is in
  `docs/state-archive/`.

## Controls

Rules that matter are enforced, not just written. Each row names its enforcement.
`prose` means nothing checks it yet, so treat it as the rule most likely to be broken.

| Id | Rule | Enforced by |
|---|---|---|
| C-01 | Finish only on a green gate | `.claude/hooks/verify-on-stop.sh`, `<CI workflow>` |
| C-02 | Paths named in this file and `CLAUDE.md` exist | `<contract test path>` |
| C-03 | No `schedule:`/cron triggers in GitHub Actions (org policy 2026-08-08) | `<contract test path>` |
| C-04 | Deploys, applies and release tags prompt first; irreversible deletes are denied | `.claude/settings.json` |
| C-05 | <repo rule> | <test / lint / hook path, or `prose`> |
| C-NN | Merging a PR is the owner's call | prose |

## Gotchas that each cost a real incident

- <What happened, in one line, and what to do instead.>

## Working rules for agents

- **Check facts in files, not memory.** Open the file before asserting what it does. Run
  `git fetch` before judging repo state; local clones go stale.
- **In an isolated worktree, run one plain command per Bash call.** No `cd $(…) && git …`, no loops
  wrapping git, no `npx $var`. The isolation check refuses what it cannot prove stays in the tree.
- **Wait with Monitor or a background task, never a foreground `sleep`.**
- **Write knowledge another agent or machine needs here or in `docs/`.** Personal auto-memory is
  invisible to Codex, Antigravity, cloud routines and other workstations.
- **Branch and open a PR.** Never push to the default branch.
