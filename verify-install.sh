#!/usr/bin/env bash
# Verify the cure-product-engineering skill library is vendored into this project.
#
# Run from the consuming project root (the project that depends on
# @cure-consulting-group/product-engineering-skills via npm).
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

EXPECTED_SKILLS=80
EXPECTED_AGENTS=39
ERRORS=0

ok()   { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; ERRORS=$((ERRORS + 1)); }
warn() { echo -e "${YELLOW}!${NC} $1"; }

PROJECT_ROOT="${1:-$(pwd)}"
CLAUDE_DIR="$PROJECT_ROOT/.claude"

echo ""
echo "Cure Skills — Vendor Verification"
echo "Project: $PROJECT_ROOT"
echo "================================="
echo ""

if [ ! -d "$CLAUDE_DIR" ]; then
  fail ".claude/ directory not found at $CLAUDE_DIR"
  echo ""
  echo "Install with:"
  echo "  npm install --save-dev @cure-consulting-group/product-engineering-skills"
  echo ""
  echo "If already installed but no .claude/ appeared, re-run the postinstall:"
  echo "  CURE_SKILLS_FORCE=1 node node_modules/@cure-consulting-group/product-engineering-skills/install-plugin.js"
  exit 1
fi

ok ".claude/ directory present"

SKILL_COUNT=$(find "$CLAUDE_DIR/skills" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$SKILL_COUNT" -eq "$EXPECTED_SKILLS" ]; then
  ok "All $EXPECTED_SKILLS skills vendored"
elif [ "$SKILL_COUNT" -gt 0 ]; then
  warn "Vendored $SKILL_COUNT skills (expected $EXPECTED_SKILLS) — upstream may have changed"
else
  fail "No skills found under .claude/skills/"
fi

NESTED_SKILLS=$(find "$CLAUDE_DIR/skills" -mindepth 3 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$NESTED_SKILLS" -gt 0 ]; then
  fail "$NESTED_SKILLS skill(s) nested too deep — Claude Code discovery needs .claude/skills/<name>/SKILL.md, not .claude/skills/<category>/<name>/SKILL.md"
else
  ok "Skills layout is flat (Claude Code-discoverable)"
fi

if [ -d "$CLAUDE_DIR/claude-commands" ] && [ ! -d "$CLAUDE_DIR/commands" ]; then
  fail "Found legacy .claude/claude-commands/ — Claude Code reads .claude/commands/. Rename: mv .claude/claude-commands .claude/commands"
elif [ -d "$CLAUDE_DIR/commands" ]; then
  CMD_COUNT=$(find "$CLAUDE_DIR/commands" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  ok ".claude/commands/ present ($CMD_COUNT slash commands)"
fi

AGENT_COUNT=$(find "$CLAUDE_DIR/agents" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
if [ "$AGENT_COUNT" -eq "$EXPECTED_AGENTS" ]; then
  ok "All $EXPECTED_AGENTS agents vendored"
elif [ "$AGENT_COUNT" -gt 0 ]; then
  warn "Vendored $AGENT_COUNT agents (expected $EXPECTED_AGENTS)"
else
  fail "No agents found under .claude/agents/"
fi

for sub in personas rules output-styles hooks; do
  if [ -d "$CLAUDE_DIR/$sub" ] && [ -n "$(ls -A "$CLAUDE_DIR/$sub" 2>/dev/null)" ]; then
    COUNT=$(find "$CLAUDE_DIR/$sub" -type f | wc -l | tr -d ' ')
    ok ".claude/$sub/ present ($COUNT files)"
  else
    warn ".claude/$sub/ missing or empty"
  fi
done

for f in .mcp.json .lsp.json; do
  if [ -f "$PROJECT_ROOT/$f" ]; then
    ok "$f present at project root"
  else
    warn "$f missing at project root (optional)"
  fi
done

if [ -d "$PROJECT_ROOT/.git" ]; then
  if git -C "$PROJECT_ROOT" ls-files --error-unmatch .claude/skills >/dev/null 2>&1; then
    ok ".claude/ is tracked in git"
  else
    warn ".claude/ is NOT tracked in git yet — run: git add .claude/ && git commit"
  fi
fi

echo ""
if [ "$ERRORS" -eq 0 ]; then
  ok "Verification passed."
  exit 0
else
  fail "Verification failed with $ERRORS error(s)."
  exit 1
fi
