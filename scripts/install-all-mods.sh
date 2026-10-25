#!/usr/bin/env bash
# Installs every Cure mod the marketplace lists (each plugin whose source is
# under ./mods/ in .claude-plugin/marketplace.json): no hardcoded list.
# Errors are shown, and the script exits 1 if any install fails.
#
# Usage: scripts/install-all-mods.sh [user|project|local]   (default: user)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKETPLACE="${ROOT}/.claude-plugin/marketplace.json"
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
if [ "${#MODS[@]}" -eq 0 ]; then echo "error: no mods found in ${MARKETPLACE}" >&2; exit 1; fi

echo "Installing ${#MODS[@]} Cure mods (scope: ${SCOPE}) from ${MARKETPLACE#"${ROOT}/"}"
if ! out=$(claude plugin marketplace update cure 2>&1); then
  echo "error: could not refresh the 'cure' marketplace:" >&2
  echo "${out}" | sed 's/^/  /' >&2
  exit 1
fi

failed=()
for mod in "${MODS[@]}"; do
  if out=$(claude plugin install "${mod}@cure" --scope "${SCOPE}" 2>&1); then
    echo "  ok      ${mod}"
  else
    echo "  FAILED  ${mod}" >&2
    echo "${out}" | sed 's/^/          /' >&2
    failed+=("${mod}")
  fi
done

echo "${#MODS[@]} listed, $(( ${#MODS[@]} - ${#failed[@]} )) installed, ${#failed[@]} failed."
echo "Retired mods still installed from before Wave 7? scripts/uninstall-all-mods.sh --retired"
[ "${#failed[@]}" -eq 0 ]
