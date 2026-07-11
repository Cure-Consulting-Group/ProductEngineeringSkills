#!/usr/bin/env bash
#
# verify-workflows.sh — Syntax-check every workflow script in workflows/.
#
# Workflow scripts run inside an async function context (top-level return and
# await are legal), so a bare `node --check` rejects them. This wraps each
# script the way the Claude Code workflow runtime does, then syntax-checks it.
set -euo pipefail
cd "$(dirname "$0")/.."

FAIL=0
for f in workflows/*.js; do
  [ -e "$f" ] || continue
  if python3 - "$f" <<'PY' | node --input-type=module --check; then
import sys
src = open(sys.argv[1]).read()
src = src.replace("export const meta", "const meta", 1)
print("async function __workflow(args, agent, pipeline, parallel, log, phase, budget, workflow) {")
print(src)
print("}")
PY
    echo "OK   $f"
  else
    echo "FAIL $f"
    FAIL=1
  fi
done
exit $FAIL
