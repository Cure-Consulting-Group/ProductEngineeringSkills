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
echo "    audit + compliance OK"

if [ "$DRY" = "1" ]; then
  echo "Would bump $PLUGIN, sync metadata, regenerate OVERVIEW + Gemini, commit, and print tag command."
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

# 4) Regenerate derived artifacts (OVERVIEW, legacy commands, Gemini skills)
echo "==> Regenerate OVERVIEW + legacy commands + Gemini skills"
python3 scripts/generate-overview.py >/dev/null
python3 scripts/sync-legacy-commands.py --write >/dev/null
[ -x ./generate-gemini-skills.sh ] && ./generate-gemini-skills.sh --force >/dev/null 2>&1 || true

# 5) Final gate (post-sync) + commit
python3 scripts/sync-metadata.py --check >/dev/null
git add -A
git commit -q -m "chore(release): v$NEXT" -m "Bumped version, synced metadata, regenerated OVERVIEW + Gemini skills."
echo
echo "Committed v$NEXT. To publish:"
echo "    git tag v$NEXT && git push && git push --tags"
echo "CI (publish.yml) will release; consumers update with /plugin update cure-product-engineering."
