#!/usr/bin/env bash
# Stop hook: before an agent may finish a turn on a branch whose gated code differs from
# origin/<default> (committed or not), scripts/verify.sh must be green. Silent when green or when
# nothing gated changed; on red, exit 2 hands the failures back to the agent.
#
# One forced retry per stop: if the agent is already continuing because of this hook
# (stop_hook_active), let it stop rather than loop. CI still gates.
#
# Template from the cure-product-engineering `agent-harness` skill. Set GATED to the paths
# whose change can turn the gate red; docs and state-file edits should not trigger it.
set -uo pipefail

input=$(cat)
if printf '%s' "$input" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0
DEFAULT_BRANCH=main
GATED=(src scripts package.json package-lock.json AGENTS.md CLAUDE.md .github/workflows)

if [ -z "$(git status --porcelain -- "${GATED[@]}" 2>/dev/null)" ] &&
   [ -z "$(git diff --name-only "origin/$DEFAULT_BRANCH...HEAD" -- "${GATED[@]}" 2>/dev/null)" ]; then
  exit 0
fi

# Skip if this exact tree already passed: an agent may stop several times without touching
# code in between.
SIG=$( { git rev-parse HEAD
         git diff HEAD -- "${GATED[@]}"
         git ls-files -o --exclude-standard -- "${GATED[@]}" | while read -r f; do shasum "$f"; done
       } 2>/dev/null | shasum | cut -d' ' -f1)
STAMP=.claude/.verify-stamp
[ "$(cat "$STAMP" 2>/dev/null)" = "$SIG" ] && exit 0

if OUT=$(scripts/verify.sh --quiet 2>&1); then
  echo "$SIG" > "$STAMP"
  exit 0
fi

{
  echo "scripts/verify.sh is red on your changes. Fix these before finishing (AGENTS.md C-01):"
  printf '%s\n' "$OUT" | tail -60
} >&2
exit 2
