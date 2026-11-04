#!/usr/bin/env bash
# Uninstalls every Cure mod the marketplace lists (each plugin whose source is
# under ./mods/ in .claude-plugin/marketplace.json). With --retired, also the
# mods Wave 7 removed from the marketplace. A mod that is not installed is
# skipped; any other error is shown and the script exits 1.
#
# Usage: scripts/uninstall-all-mods.sh [--retired] [user|project|local]   (default: user)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKETPLACE="${ROOT}/.claude-plugin/marketplace.json"
# Removed in Wave 7 (T73): dropped per D6, or merged into cure-policy-guard.
RETIRED=(cure-llm-ledger cure-ci-preview cure-handoff cure-secret-scrub cure-egress-guard cure-claim-guard)

WITH_RETIRED=0
if [ "${1:-}" = "--retired" ]; then WITH_RETIRED=1; shift; fi
SCOPE="${1:-user}"
case "${SCOPE}" in user|project|local) ;; *) echo "error: scope must be user, project or local (got '${SCOPE}')" >&2; exit 2 ;; esac
command -v claude >/dev/null || { echo "error: claude is not on PATH" >&2; exit 2; }

MODS=()
while IFS= read -r mod; do MODS+=("${mod}"); done < <(python3 - "${MARKETPLACE}" <<'PY'
import json, sys
for p in json.load(open(sys.argv[1]))['plugins']:
    if str(p.get('source', '')).startswith('./mods/'):
        print(p['name'])
PY
)
[ "${WITH_RETIRED}" -eq 1 ] && MODS+=("${RETIRED[@]}")
if [ "${#MODS[@]}" -eq 0 ]; then echo "error: no mods found in ${MARKETPLACE}" >&2; exit 1; fi

echo "Uninstalling ${#MODS[@]} Cure mods (scope: ${SCOPE})"
failed=()
removed=0
for mod in "${MODS[@]}"; do
  if out=$(claude plugin uninstall "${mod}@cure" --scope "${SCOPE}" 2>&1); then
    echo "  removed  ${mod}"
    removed=$((removed + 1))
  elif echo "${out}" | grep -qiE "not installed|not found"; then
    echo "  skipped  ${mod} (not installed in ${SCOPE} scope)"
  else
    echo "  FAILED   ${mod}" >&2
    echo "${out}" | sed 's/^/           /' >&2
    failed+=("${mod}")
  fi
done

echo "${removed} removed, ${#failed[@]} failed."
[ "${#failed[@]}" -eq 0 ]
