#!/usr/bin/env bash
set -euo pipefail

# Uninstalls all 15 Cure Claude Code mods
# Usage: ./scripts/uninstall-all-mods.sh [scope: user|project|local]

MODS=(
  "cure-policy-guard"
  "cure-lane-verifier"
  "cure-spend-band"
  "cure-cache-band"
  "cure-image-viewer"
  "cure-secret-scrub"
  "cure-llm-ledger"
  "cure-cite-check"
  "cure-claim-guard"
  "cure-ci-preview"
  "cure-agent-budget"
  "cure-egress-guard"
  "cure-rules-band"
  "cure-handoff"
  "cure-lane-board"
)

SCOPE="${1:-user}"

echo "============================================================"
echo "  Cure Claude Code Mods — Batch Uninstaller"
echo "============================================================"
echo "Scope: ${SCOPE}"
echo ""

for mod in "${MODS[@]}"; do
  echo -n "Uninstalling ${mod}@cure ... "
  claude plugin uninstall "${mod}@cure" --scope "${SCOPE}" >/dev/null 2>&1 || true
  echo "✔ Done"
done

echo ""
echo "All Cure mods uninstalled for scope: ${SCOPE}"
