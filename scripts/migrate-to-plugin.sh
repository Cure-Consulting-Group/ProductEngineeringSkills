#!/bin/sh
# migrate-to-plugin.sh <project-path> [channel] — T31 remediation.
#
# Converts a consuming project from a vendored library copy to plugin mode:
#   1. Removes .claude/skills/<name> and .claude/agents/<name>.md ONLY where
#      <name> exists in this library — project-local skills/agents are kept.
#   2. Writes cure-manifest.json with mode=plugin and the given channel.
#
# The project is a git repo: every removal shows as a deletion in its git
# status for review. Nothing is committed by this script. Rollback:
#   git -C <project> checkout -- .claude/
#
# Usage:  scripts/migrate-to-plugin.sh ~/Documents/Cure-Consulting-Group/statledger next
set -eu
PROJ="${1:?usage: migrate-to-plugin.sh <project-path> [channel]}"
CHANNEL="${2:-stable}"
LIB="$(cd "$(dirname "$0")/.." && pwd)"

[ -d "$PROJ/.git" ] || { echo "not a git repo: $PROJ (refusing — need git for rollback)"; exit 1; }

removed_s=0; removed_a=0
if [ -d "$PROJ/.claude/skills" ]; then
  for d in "$PROJ/.claude/skills"/*/; do
    name=$(basename "$d")
    if ls "$LIB/skills"/*/"$name"/SKILL.md >/dev/null 2>&1; then
      rm -rf "$d"; removed_s=$((removed_s+1))
    fi
  done
fi
if [ -d "$PROJ/.claude/agents" ]; then
  for f in "$PROJ/.claude/agents"/*.md; do
    [ -e "$f" ] || continue
    name=$(basename "$f" .md)
    if [ -f "$LIB/agents/$name.md" ]; then
      rm -f "$f"; removed_a=$((removed_a+1))
    fi
  done
fi

python3 "$LIB/scripts/fleet-census.py" --write-manifest "$PROJ" --mode plugin --channel "$CHANNEL" >/dev/null

echo "removed $removed_s vendored skills, $removed_a vendored agents (library-named only)"
echo "kept (project-local):"
ls "$PROJ/.claude/skills" 2>/dev/null || echo "  (none)"
echo "manifest -> plugin/$CHANNEL. Review with: git -C $PROJ status"
