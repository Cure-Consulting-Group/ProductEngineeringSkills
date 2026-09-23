#!/usr/bin/env bash
#
# install-runtimes.sh — put the Cure library into Codex and Antigravity on THIS machine.
#
# Claude Code needs nothing here: it installs via the `cure` marketplace and auto-updates.
# Codex and Antigravity install snapshots, so run this after every library release
# (and once on any new machine). Idempotent: safe to re-run.
#
# Usage:
#   scripts/install-runtimes.sh            # pull main, install/refresh both, verify
#   scripts/install-runtimes.sh --no-pull  # skip the git pull (e.g. testing a branch)
#   scripts/install-runtimes.sh --help
#
# Steps:
#   1. git pull --ff-only (only on a clean `main` checkout; otherwise skipped with a note)
#   2. Codex:       add/upgrade the `cure` marketplace, add cure-product-engineering@cure,
#                   set skills.max_context_tokens = 10000 in ~/.codex/config.toml (Codex caps
#                   explicit values at 10000; below ~8000 descriptions get truncated)
#   3. Antigravity: scripts/export-antigravity.py --install (flat plugin → ~/.gemini/config/plugins/cure)
#   4. Verify:      scripts/codex-smoke.py and scripts/antigravity-smoke.py (zero model calls)
# A runtime whose CLI is not on PATH is skipped with a note, not treated as an error.
set -uo pipefail
cd "$(dirname "$0")/.."

PULL=1
case "${1:-}" in
  --no-pull) PULL=0 ;;
  -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
  "") ;;
  *) echo "unknown option: $1 (see --help)"; exit 2 ;;
esac

REPO_SLUG="Cure-Consulting-Group/ProductEngineeringSkills"
fail=0
say() { printf '==> %s\n' "$*"; }

# 1) Pull
if [ "$PULL" = 1 ]; then
  branch=$(git rev-parse --abbrev-ref HEAD)
  if [ "$branch" = "main" ] && [ -z "$(git status --porcelain)" ]; then
    say "git pull --ff-only (main)"
    git pull -q --ff-only origin main || { echo "pull failed — resolve, then re-run"; exit 1; }
  else
    say "skipping pull (on '$branch'$( [ -n "$(git status --porcelain)" ] && echo ', dirty tree'))"
  fi
fi
echo "    library version: $(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")"

# 2) Codex
if command -v codex >/dev/null 2>&1; then
  say "Codex ($(codex --version 2>/dev/null | head -1))"
  # Capture before matching: under pipefail, `grep -q` exiting early SIGPIPEs codex and fails the pipe.
  mkts=$(codex plugin marketplace list 2>&1)
  if grep -Eq '^(Marketplace )?`?cure`?([[:space:]]|$)' <<<"$mkts"; then
    codex plugin marketplace upgrade cure >/dev/null 2>&1 || echo "    marketplace upgrade reported an error (continuing)"
  else
    codex plugin marketplace add "$REPO_SLUG" || { echo "    marketplace add failed"; fail=1; }
  fi
  codex plugin add cure-product-engineering@cure || { echo "    plugin add failed"; fail=1; }
  CFG="${CODEX_HOME:-$HOME/.codex}/config.toml"
  if [ -f "$CFG" ] && grep -Eq '^\s*max_context_tokens\s*=' "$CFG"; then
    echo "    skills.max_context_tokens already set: $(grep -E '^\s*max_context_tokens' "$CFG" | head -1 | tr -d ' ')"
  elif [ -f "$CFG" ] && grep -Eq '^\[skills\]' "$CFG"; then
    echo "    [skills] table exists without max_context_tokens — add 'max_context_tokens = 10000' under it by hand"
  else
    mkdir -p "$(dirname "$CFG")"
    printf '\n# Cure library: 103 skills need the full listing budget (Codex caps explicit values at 10000).\n[skills]\nmax_context_tokens = 10000\n' >> "$CFG"
    echo "    set skills.max_context_tokens = 10000 in $CFG"
  fi
else
  say "Codex CLI not found — skipped"
fi

# 3) Antigravity
if command -v agy >/dev/null 2>&1; then
  say "Antigravity ($(agy --version 2>/dev/null | head -1))"
  python3 scripts/export-antigravity.py --install || { echo "    export/install failed"; fail=1; }
else
  say "Antigravity CLI (agy) not found — skipped"
fi

# 4) Verify (zero model calls). The smokes prove the package in throwaway homes;
#    the two checks after them prove the REAL install on this machine.
say "verify"
python3 scripts/codex-smoke.py || fail=1
python3 scripts/antigravity-smoke.py || fail=1
if command -v codex >/dev/null 2>&1; then
  plugins=$(codex plugin list 2>&1)   # plugin rows are printed on stderr
  if grep -Eq '^cure-product-engineering@cure[[:space:]]+installed, enabled' <<<"$plugins"; then
    echo "    real Codex install: cure-product-engineering@cure installed, enabled"
  else
    echo "    real Codex install: NOT installed"; fail=1
  fi
fi
if command -v agy >/dev/null 2>&1; then
  if [ -f "$HOME/.gemini/config/plugins/cure/plugin.json" ]; then
    echo "    real Antigravity install: ~/.gemini/config/plugins/cure ($(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.gemini/config/plugins/cure/plugin.json'))).get('version','?'))"))"
  else
    echo "    real Antigravity install: NOT installed"; fail=1
  fi
fi

[ "$fail" = 0 ] && say "done" || { say "finished with errors (see above)"; exit 1; }
