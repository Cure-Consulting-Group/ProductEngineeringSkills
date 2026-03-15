#!/usr/bin/env bash
#
# Generate Gemini .skill files from Claude Code SKILL.md files
#
# Each .skill file is a ZIP archive containing:
#   {name}-skill/SKILL.md — The skill with Gemini-compatible frontmatter
#
# Usage: ./generate-gemini-skills.sh [--force]
#   --force: Regenerate even if .skill file already exists

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
GEMINI_DIR="$SCRIPT_DIR/gemini skills"
FORCE=false

for arg in "$@"; do
  case "$arg" in
    --force) FORCE=true ;;
  esac
done

mkdir -p "$GEMINI_DIR"

GENERATED=0
SKIPPED=0

for skill_dir in "$SKILLS_DIR"/*/; do
  SKILL_NAME=$(basename "$skill_dir")
  SKILL_FILE="$skill_dir/SKILL.md"
  GEMINI_FILE="$GEMINI_DIR/${SKILL_NAME}.skill"

  if [ ! -f "$SKILL_FILE" ]; then
    continue
  fi

  # Skip if already exists and not forcing
  if [ -f "$GEMINI_FILE" ] && [ "$FORCE" != "true" ]; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Extract description from YAML frontmatter
  DESCRIPTION=$(sed -n '/^---$/,/^---$/p' "$SKILL_FILE" | grep '^description:' | sed 's/^description: *"*//;s/"*$//')

  # Extract the content after frontmatter
  CONTENT=$(sed '1,/^---$/{ /^---$/!d; }' "$SKILL_FILE" | sed '1,/^---$/d')

  # Get the title (first # heading)
  TITLE=$(echo "$CONTENT" | grep -m1 '^# ' | sed 's/^# //')

  # Build the Gemini SKILL.md with enhanced frontmatter
  TMPDIR=$(mktemp -d)
  GEMINI_SKILL_DIR="$TMPDIR/${SKILL_NAME}-skill"
  mkdir -p "$GEMINI_SKILL_DIR"

  cat > "$GEMINI_SKILL_DIR/SKILL.md" << GEMINIEOF
---
name: ${SKILL_NAME}
description: >
  ${DESCRIPTION}

  Trigger this skill when the user asks about: ${SKILL_NAME//-/ }, ${DESCRIPTION}

  This skill follows Cure Consulting Group standards and generates opinionated,
  production-grade output aligned with Clean Architecture and modern engineering practices.
---

${CONTENT}
GEMINIEOF

  # Create the .skill ZIP
  (cd "$TMPDIR" && zip -qr "$GEMINI_FILE" "${SKILL_NAME}-skill/")

  # Cleanup
  rm -rf "$TMPDIR"

  GENERATED=$((GENERATED + 1))
  echo "  Generated: ${SKILL_NAME}.skill"
done

echo ""
echo "Done. Generated: $GENERATED, Skipped (existing): $SKIPPED"
echo "Total Gemini skills: $(ls "$GEMINI_DIR"/*.skill 2>/dev/null | wc -l | tr -d ' ')"
