#!/usr/bin/env bash
# Verify ProductEngineeringSkills plugin installation
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

EXPECTED_SKILLS=58
ERRORS=0

ok()   { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; ERRORS=$((ERRORS + 1)); }
warn() { echo -e "${YELLOW}!${NC} $1"; }

echo ""
echo "ProductEngineeringSkills — Installation Verification"
echo "====================================================="
echo ""

# 1. Check plugin directory exists
PLUGIN_DIR="${HOME}/.claude/plugins/ProductEngineeringSkills"
if [ -d "$PLUGIN_DIR" ] || [ -L "$PLUGIN_DIR" ]; then
  ok "Plugin directory exists: $PLUGIN_DIR"
  if [ -L "$PLUGIN_DIR" ]; then
    TARGET=$(readlink "$PLUGIN_DIR")
    ok "  Symlinked to: $TARGET"
  fi
else
  fail "Plugin directory not found at $PLUGIN_DIR"
fi

# 2. Check plugin.json
PLUGIN_JSON="$PLUGIN_DIR/.claude-plugin/plugin.json"
if [ -f "$PLUGIN_JSON" ]; then
  VERSION=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])" 2>/dev/null || echo "unknown")
  ok "Plugin manifest found (v$VERSION)"
else
  fail "Plugin manifest missing: $PLUGIN_JSON"
fi

# 3. Count skills
SKILL_COUNT=$(find "$PLUGIN_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$SKILL_COUNT" -eq "$EXPECTED_SKILLS" ]; then
  ok "All $EXPECTED_SKILLS skills found"
else
  fail "Expected $EXPECTED_SKILLS skills, found $SKILL_COUNT"
  if [ "$SKILL_COUNT" -gt 0 ]; then
    warn "  Missing skills:"
    # List expected vs found
    find "$PLUGIN_DIR/skills" -name "SKILL.md" -exec dirname {} \; | xargs -I{} basename {} | sort > /tmp/found_skills.txt
    echo "  Found: $(cat /tmp/found_skills.txt | tr '\n' ', ')"
  fi
fi

# 4. Count legacy commands
LEGACY_COUNT=$(find "$PLUGIN_DIR/claude-commands" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$LEGACY_COUNT" -eq "$EXPECTED_SKILLS" ]; then
  ok "All $EXPECTED_SKILLS legacy commands found"
else
  fail "Expected $EXPECTED_SKILLS legacy commands, found $LEGACY_COUNT"
fi

# 5. Check skills match legacy commands
if [ "$SKILL_COUNT" -eq "$LEGACY_COUNT" ]; then
  ok "Skills and legacy commands are in sync"
else
  fail "Skills ($SKILL_COUNT) and legacy commands ($LEGACY_COUNT) are out of sync"
fi

# 6. Check hooks
if [ -f "$PLUGIN_DIR/hooks/hooks.json" ]; then
  HOOK_COUNT=$(python3 -c "
import json
hooks = json.load(open('$PLUGIN_DIR/hooks/hooks.json'))['hooks']
count = sum(len(v) for v in hooks.values())
print(count)
" 2>/dev/null || echo "0")
  ok "Hooks loaded ($HOOK_COUNT hook definitions)"
else
  fail "hooks.json not found"
fi

# 7. Check agents
AGENT_COUNT=$(find "$PLUGIN_DIR/agents" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$AGENT_COUNT" -ge 2 ]; then
  ok "Custom agents found ($AGENT_COUNT)"
else
  fail "Expected at least 2 agents, found $AGENT_COUNT"
fi

# 8. Check rules
RULE_COUNT=$(find "$PLUGIN_DIR/rules" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$RULE_COUNT" -ge 4 ]; then
  ok "Path-specific rules found ($RULE_COUNT)"
else
  warn "Only $RULE_COUNT rules found (expected 4+)"
fi

# 9. Check output styles
STYLE_COUNT=$(find "$PLUGIN_DIR/output-styles" -name "output-style.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$STYLE_COUNT" -ge 4 ]; then
  ok "Output styles found ($STYLE_COUNT)"
else
  warn "Only $STYLE_COUNT output styles found (expected 4+)"
fi

# 10. Check settings.json registration
SETTINGS="${HOME}/.claude/settings.json"
if [ -f "$SETTINGS" ]; then
  if grep -q "cure-product-engineering" "$SETTINGS" 2>/dev/null; then
    ok "Plugin registered in $SETTINGS"
  else
    fail "Plugin NOT registered in $SETTINGS — skills won't auto-load"
  fi
else
  fail "Claude settings file not found at $SETTINGS"
fi

# Summary
echo ""
echo "====================================================="
if [ "$ERRORS" -eq 0 ]; then
  echo -e "${GREEN}All checks passed.${NC} Plugin is properly installed."
else
  echo -e "${RED}$ERRORS check(s) failed.${NC} See above for details."
  echo ""
  echo "To fix, try:"
  echo "  npm update @cure-consulting-group/product-engineering-skills"
  echo "  — or —"
  echo "  /path/to/ProductEngineeringSkills/setup.sh --global"
fi
echo ""
