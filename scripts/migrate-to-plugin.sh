#!/bin/sh
# migrate-to-plugin.sh <project-path> [channel] — T31 remediation.
#
# Converts a consuming project from a vendored library copy to plugin mode:
#   1. Removes vendored library content ONLY where the name exists in this
#      library — project-local entries are always kept. Covers .claude/skills,
#      agents, rules, personas, output-styles and commands. hooks.json is
#      reported, never deleted (it may merge project-specific hooks).
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

removed_s=0; removed_a=0; removed_o=0
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

# Skills and agents are not the whole vendored surface. A vendored copy also
# carries rules/, personas/, output-styles/ and commands/, and leaving them
# behind produces a project that reads as migrated while still serving stale
# 7.4.x library content — which the census could not see (it only inspected
# .claude/skills). Remove library-named entries in those directories too.
for pair in "rules:rules" "personas:personas" "output-styles:output-styles" "commands:claude-commands"; do
  sub=${pair%%:*}; libdir=${pair#*:}
  [ -d "$PROJ/.claude/$sub" ] || continue
  for e in "$PROJ/.claude/$sub"/*; do
    [ -e "$e" ] || continue
    name=$(basename "$e")
    if [ -e "$LIB/$libdir/$name" ]; then
      rm -rf "$e"; removed_o=$((removed_o+1))
    fi
  done
done

# hooks.json is deliberately NOT removed: it is a single merged file that may
# carry project-specific hooks alongside the vendored library ones, so it needs
# a human read. Flag it rather than guess.
if [ -f "$PROJ/.claude/hooks/hooks.json" ]; then
  if cmp -s "$PROJ/.claude/hooks/hooks.json" "$LIB/hooks/hooks.json"; then
    echo "NOTE: .claude/hooks/hooks.json is identical to the library copy —"
    echo "      delete it to avoid double hook execution:"
    echo "      rm $PROJ/.claude/hooks/hooks.json"
  else
    echo "WARNING: .claude/hooks/hooks.json differs from the library copy."
    echo "         It may hold project-specific hooks. Review by hand:"
    echo "         diff $PROJ/.claude/hooks/hooks.json $LIB/hooks/hooks.json"
  fi
fi

python3 "$LIB/scripts/fleet-census.py" --write-manifest "$PROJ" --mode plugin --channel "$CHANNEL" >/dev/null

echo "removed $removed_s vendored skills, $removed_a vendored agents, $removed_o rules/personas/output-styles/commands (library-named only)"
echo "kept (project-local):"
ls "$PROJ/.claude/skills" 2>/dev/null || echo "  (none)"
echo "manifest -> plugin/$CHANNEL. Review with: git -C $PROJ status"
