#!/usr/bin/env bash
set -euo pipefail

# Installs all 15 Cure Claude Code mods from the @cure marketplace
# Usage: ./scripts/install-all-mods.sh [scope: user|project|local]

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
echo "  Cure Claude Code Mods — Batch Installer"
echo "============================================================"
echo "Scope: ${SCOPE}"
echo "Total mods to install: ${#MODS[@]}"
echo ""

echo "==> Refreshing 'cure' marketplace catalog..."
claude plugin marketplace update cure || true
echo ""

installed=0
failed=0

for mod in "${MODS[@]}"; do
  echo -n "Installing ${mod}@cure ... "
  if claude plugin install "${mod}@cure" --scope "${SCOPE}" >/dev/null 2>&1; then
    echo "✔ Done"
    installed=$((installed + 1))
  else
    echo "✗ Failed"
    failed=$((failed + 1))
  fi
done

echo ""
echo "============================================================"
echo "  Installation Summary: ${installed}/${#MODS[@]} installed (Failed: ${failed})"
echo "============================================================"
echo "Verify active plugins with: claude plugin list"
