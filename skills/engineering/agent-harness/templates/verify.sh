#!/usr/bin/env bash
# The gate. Agents, the Stop hook (.claude/hooks/verify-on-stop.sh) and people run this before
# calling work done. Budget: under 60s. Suites that can't fit stay in CI; AGENTS.md lists them.
#
#   scripts/verify.sh           checks for what differs from origin/<default>
#   scripts/verify.sh --all     every step, whatever changed
#   scripts/verify.sh --quiet   silent when green; failing steps only
#
# Template from the cure-product-engineering `agent-harness` skill. Keep the steps that apply,
# delete the rest, and time the result with every tree touched.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

DEFAULT_BRANCH=main
QUIET=0
ALL=0
for arg in "$@"; do
  case "$arg" in
    --quiet) QUIET=1 ;;
    --all) ALL=1 ;;
    *) echo "verify.sh: unknown argument: $arg" >&2; exit 64 ;;
  esac
done
say() { [ "$QUIET" -eq 1 ] || echo "$@"; }

FAILED=0
run_step() {
  local name="$1"; shift
  local out
  if out=$("$@" 2>&1); then
    say "ok    $name"
  else
    FAILED=1
    echo "FAIL  $name" >&2
    printf '%s\n' "$out" | tail -40 >&2
  fi
}

# ---- what changed ---------------------------------------------------------
BASE=$(git merge-base HEAD "origin/$DEFAULT_BRANCH" 2>/dev/null || git rev-parse HEAD)
CHANGED=$( { git diff --name-only "$BASE"; git ls-files -o --exclude-standard; } | sort -u )
# touched <regex>: true under --all, or when a changed path matches. Copy CI's path filters here.
touched() { [ "$ALL" -eq 1 ] || printf '%s\n' "$CHANGED" | grep -qE "$1"; }

# ---- Node: install only when a lockfile is newer than its install ---------
# for dir in . web functions; do
#   if [ ! -f "$dir/node_modules/.package-lock.json" ] || [ "$dir/package-lock.json" -nt "$dir/node_modules/.package-lock.json" ]; then
#     out=$(npm --prefix "$dir" ci --no-audit --no-fund --loglevel=error 2>&1) || { printf '%s\n' "$out" | tail -20 >&2; exit 1; }
#   fi
# done

# ---- Python: one venv, rebuilt when requirements change -------------------
# if [ ! -x .venv/bin/python ] || ! cmp -s <(cat requirements*.txt) .venv/.req-hash 2>/dev/null; then
#   python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt && cat requirements*.txt > .venv/.req-hash
# fi

# ---- steps: keep what applies -----------------------------------------------
# Contract tests: always (they guard the docs and config every change can break).
# run_step "harness contracts" npx vitest run scripts/harness-contracts.test.ts
# run_step "harness contracts" .venv/bin/python -m pytest scripts/test_harness_contracts.py -q

# TypeScript package: whole suite if it fits the budget.
# if touched '^web/|^package(-lock)?\.json$'; then
#   run_step "web typecheck" npm --prefix web run --silent typecheck
#   run_step "web tests" npm --prefix web run --silent test
# fi

# Lint errors only, on changed files.
# LINT=$(printf '%s\n' "$CHANGED" | grep -E '^web/.*\.(ts|tsx)$' | sed 's#^web/##')
# [ -n "$LINT" ] && run_step "web lint" bash -c 'cd web && npx eslint --quiet --no-warn-ignored "$@"' _ $LINT

# Python.
# if touched '^(services|scripts)/'; then
#   run_step "ruff" .venv/bin/python -m ruff check services scripts
#   run_step "pytest" .venv/bin/python -m pytest services scripts -q -p no:warnings -x
# fi

# Terraform formatting (validate needs init; leave it to CI).
# if touched '^terraform/' && command -v terraform >/dev/null 2>&1; then
#   run_step "terraform fmt" terraform fmt -check -recursive terraform
# fi

exit "$FAILED"
