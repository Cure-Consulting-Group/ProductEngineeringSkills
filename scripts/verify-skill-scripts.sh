#!/usr/bin/env bash
# verify-skill-scripts.sh — smoke-test every bundled skill script.
#
# Walks skills/*/*/scripts/*.py and runs each with --help.
# Fails if any script exits non-zero, prints stack traces, or is unreadable.
# Intended to run in CI and as a pre-commit guardrail.
#
# Usage:
#   scripts/verify-skill-scripts.sh
#   scripts/verify-skill-scripts.sh --quiet   # only print failures and summary
#
# Exit: 0 on success, 1 on any failure, 2 on missing python3.

set -u

QUIET=0
if [[ "${1:-}" == "--quiet" ]]; then
  QUIET=1
fi

# Resolve repo root from this script's location.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 not found on PATH" >&2
  exit 2
fi

SCRIPTS_LIST="$(find "${REPO_ROOT}/skills" -mindepth 4 -maxdepth 5 \
  -type f -path '*/scripts/*.py' 2>/dev/null | sort)"

if [[ -z "${SCRIPTS_LIST}" ]]; then
  echo "no scripts found under skills/*/*/scripts/*.py"
  exit 0
fi

TOTAL=0
PASS=0
FAIL=0
FAILED_LIST=""

while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  TOTAL=$((TOTAL + 1))
  rel="${f#${REPO_ROOT}/}"
  out="$(python3 "$f" --help 2>&1)"
  rc=$?
  if [[ $rc -ne 0 ]]; then
    FAIL=$((FAIL + 1))
    FAILED_LIST="${FAILED_LIST}${rel} (exit ${rc})"$'\n'
    echo "FAIL  $rel (exit $rc)"
    echo "$out" | sed 's/^/      /'
    continue
  fi
  if echo "$out" | grep -q "Traceback (most recent call last)"; then
    FAIL=$((FAIL + 1))
    FAILED_LIST="${FAILED_LIST}${rel} (traceback)"$'\n'
    echo "FAIL  $rel (stack trace in --help output)"
    continue
  fi
  if ! echo "$out" | grep -q '^usage:'; then
    FAIL=$((FAIL + 1))
    FAILED_LIST="${FAILED_LIST}${rel} (no usage line)"$'\n'
    echo "FAIL  $rel (no 'usage:' line in --help)"
    continue
  fi
  PASS=$((PASS + 1))
  if [[ $QUIET -eq 0 ]]; then
    echo "ok    $rel"
  fi
done <<< "${SCRIPTS_LIST}"

echo
echo "summary: ${PASS} passed, ${FAIL} failed (of ${TOTAL})"

if [[ $FAIL -gt 0 ]]; then
  echo "failures:"
  printf '%s' "${FAILED_LIST}" | sed 's/^/  - /'
  exit 1
fi
exit 0
