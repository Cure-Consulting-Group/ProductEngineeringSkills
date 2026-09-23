#!/usr/bin/env bash
#
# release.sh — One-command release for the Cure skill library.
#
# Bumps the single source-of-truth version, propagates it everywhere, runs the
# full quality gate, regenerates all derived artifacts, and commits. A release
# cannot ship half-synced or below quality bar.
#
# Usage:
#   scripts/release.sh patch        # 7.0.1 -> 7.0.2
#   scripts/release.sh minor        # 7.0.1 -> 7.1.0
#   scripts/release.sh major        # 7.0.1 -> 8.0.0
#   scripts/release.sh 7.3.0        # explicit
#   scripts/release.sh --dry-run patch
set -euo pipefail
cd "$(dirname "$0")/.."

DRY=0
if [ "${1:-}" = "--dry-run" ]; then DRY=1; shift; fi
LEVEL="${1:-patch}"

PLUGIN=.claude-plugin/plugin.json
CUR=$(python3 -c "import json;print(json.load(open('$PLUGIN'))['version'])")

# Compute next version
NEXT=$(python3 - "$CUR" "$LEVEL" <<'PY'
import sys, re
cur, level = sys.argv[1], sys.argv[2]
if re.fullmatch(r"\d+\.\d+\.\d+", level):
    print(level); sys.exit()
a, b, c = map(int, cur.split("."))
print({"patch": f"{a}.{b}.{c+1}", "minor": f"{a}.{b+1}.0", "major": f"{a+1}.0.0"}[level])
PY
)

echo "Release: v$CUR -> v$NEXT  (level: $LEVEL)"
[ "$DRY" = "1" ] && echo "(dry-run — no writes)"

# 1) Pre-flight gate on CURRENT tree (don't bump a broken library)
echo "==> Quality gate"
python3 scripts/audit-library.py --fail-under 9.0 --min-item 7.0 >/dev/null
python3 scripts/fix-library.py --check >/dev/null
python3 scripts/check-doc-claims.py >/dev/null
echo "    audit + compliance + doc-claims OK"

# Ring 0 (T30 → T60): eval-gate any skills changed since the last tag with
# `claude plugin eval` (plugin-evals/, cases tagged by skill name). With-arm
# only, 1 run: routing (`tool_used: Skill`) is scored under --ablation none,
# so a T53-style description regression fails here. Runs the real agent CLI
# locally on the maintainer's plan (CI can't). Skips cleanly when nothing
# covered changed. Override the bar with RING0_THRESHOLD (default 0.5).
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
  echo "==> Ring 0 eval gate (changed skills vs $LAST_TAG)"
  RING0_TAGS=$(python3 scripts/check-plugin-evals.py --changed-tags "$LAST_TAG") \
    || { echo "plugin-evals/ is invalid — fix before releasing"; exit 1; }
  if [ -z "$RING0_TAGS" ]; then
    echo "    no eval-covered skills changed — pass"
  elif [ "$DRY" = "1" ]; then
    echo "    would run: claude plugin eval . --tag $RING0_TAGS (1 run, with-arm only)"
  elif ! command -v claude >/dev/null 2>&1; then
    echo "Ring 0 needs the claude CLI (v2.1.269+) on PATH"; exit 1
  else
    # shellcheck disable=SC2086  # RING0_TAGS is a space-separated list of skill names
    claude plugin eval . --tag $RING0_TAGS \
      --runs 1 --ablation none -j 4 --threshold "${RING0_THRESHOLD:-0.5}" \
      --trust-plugin --scaffold --allow-tools Write Edit "Bash(python3 *)" \
      --no-publish --max-cost-usd "${RING0_MAX_COST:-15}" \
      || { echo "Ring 0 eval regression — fix before releasing"; exit 1; }
  fi
  # t16 (\$N substitution integrity, statledger F-1) needs a project-level fixture
  # skill, which `claude plugin eval` never loads (plugin-only sessions) — so it
  # stays on the legacy harness and runs on every release. ~20 s, skill arm only.
  if [ "$DRY" = "1" ]; then
    echo "    would run: run-evals.py --tasks t16-substitution-integrity --skill on --reps 1"
  else
    python3 scripts/run-evals.py --tasks t16-substitution-integrity --skill on --reps 1 \
      || { echo "t16 substitution-integrity regression — fix before releasing"; exit 1; }
  fi
fi

if [ "$DRY" = "1" ]; then
  echo "Would bump $PLUGIN, sync metadata, regenerate OVERVIEW + legacy commands, commit, and print tag command."
  exit 0
fi

# 2) Bump the single source of truth
python3 - "$PLUGIN" "$NEXT" <<'PY'
import json, sys
f, v = sys.argv[1], sys.argv[2]
d = json.load(open(f)); d["version"] = v
json.dump(d, open(f, "w"), indent=2); open(f, "a").write("\n")
PY
# Keep package.json in lockstep (npm vendoring path)
python3 - package.json "$NEXT" <<'PY'
import json, sys
f, v = sys.argv[1], sys.argv[2]
d = json.load(open(f)); d["version"] = v
json.dump(d, open(f, "w"), indent=2); open(f, "a").write("\n")
PY

# 3) Propagate version + counts to every doc/config
echo "==> Sync metadata"
python3 scripts/sync-metadata.py --write >/dev/null

# 4) Regenerate derived artifacts (OVERVIEW, legacy commands)
echo "==> Regenerate OVERVIEW + legacy commands"
python3 scripts/generate-overview.py >/dev/null
python3 scripts/sync-legacy-commands.py --write >/dev/null

# 5) Final gate (post-sync) + commit
python3 scripts/sync-metadata.py --check >/dev/null
git add -A
git commit -q -m "chore(release): v$NEXT" -m "Bumped version, synced metadata, regenerated OVERVIEW + legacy commands."
echo
echo "Committed v$NEXT. To publish:"
echo "    git tag v$NEXT && git push && git push --tags"
echo "CI (publish.yml) will release; consumers update with /plugin update cure-product-engineering."
