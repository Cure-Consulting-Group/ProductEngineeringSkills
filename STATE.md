# STATE — machine setup and current library state

Read this on any machine that has this repo checked out. `CLAUDE.md` points here.

## Every machine: install the library into Codex and Antigravity

Claude Code needs nothing: it installs from the `cure` marketplace and auto-updates.
Codex and Antigravity install **snapshots**, so they fall behind until refreshed.

**Run on a new machine, and again after every library release:**

```bash
git pull --ff-only origin main   # the script also pulls when on a clean main
scripts/install-runtimes.sh
```

What it does (idempotent, safe to re-run; `--help` for details):

1. Pulls `main` (skipped on another branch or a dirty tree).
2. **Codex:** adds or upgrades the `cure` marketplace, installs
   `cure-product-engineering@cure`, sets `skills.max_context_tokens = 10000` in
   `~/.codex/config.toml` (Codex caps explicit values at 10000; lower budgets truncate the
   103 skill descriptions and hurt routing).
3. **Antigravity:** builds the flat plugin and installs it to `~/.gemini/config/plugins/cure`
   (`scripts/export-antigravity.py --install`).
4. **Verifies** with zero model calls: packaging smokes plus a check of the *real* installs.
   A runtime whose CLI isn't installed is skipped, not failed.

Done when the output ends with `==> done` and shows both `real … install` lines.

Gemini CLI is not a target (it can't run models on consultant accounts —
`docs/evaluations/2026-09-23/platform-facts.md`).

## Current state (update on each release)

| | |
|---|---|
| Library version | 7.10.1 (2026-09-23) |
| Last wave | Wave 5 — tri-runtime (Opus 5.5 / Codex / Antigravity); see BACKLOG.md |
| Machines verified with `install-runtimes.sh` | primary Mac (codex 0.155.0, agy 1.2.9) — 2026-09-23 |
| Open owner decisions | BACKLOG.md → Wave 5 → "Owner decisions surfaced by the pass" |
