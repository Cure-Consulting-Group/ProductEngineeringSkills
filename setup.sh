#!/usr/bin/env bash
#
# Cure Consulting Group — ProductEngineeringSkills Plugin Setup
#
# Sets up any project (including Antigravity projects) to use the
# ProductEngineeringSkills plugin with Claude Code.
#
# Usage:
#   npm install @cure-consulting-group/product-engineering-skills   # GitHub Package (recommended)
#   — or —
#   curl -sSL https://raw.githubusercontent.com/Cure-Consulting-Group/ProductEngineeringSkills/main/setup.sh | bash
#   — or —
#   ./setup.sh                     # Run from the target project directory
#   ./setup.sh /path/to/project    # Specify a target project
#   ./setup.sh --global            # Install for all projects (user-level)
#

set -euo pipefail

# --- Configuration ---
PLUGIN_REPO="https://github.com/Cure-Consulting-Group/ProductEngineeringSkills.git"
PLUGIN_NAME="cure-product-engineering"
PLUGIN_DIR_NAME="ProductEngineeringSkills"
INSTALL_BASE="${HOME}/.claude/plugins"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Parse arguments ---
MODE="project"  # project | global | legacy
TARGET_DIR="$(pwd)"

for arg in "$@"; do
  case "$arg" in
    --global)  MODE="global" ;;
    --legacy)  MODE="legacy" ;;
    --help|-h)
      echo "Usage: setup.sh [OPTIONS] [PROJECT_PATH]"
      echo ""
      echo "Options:"
      echo "  --global    Install plugin for all projects (user-level)"
      echo "  --legacy    Copy skills as .claude/commands/ (no plugin features)"
      echo "  --help      Show this help message"
      echo ""
      echo "Examples:"
      echo "  ./setup.sh                          # Setup current project"
      echo "  ./setup.sh /path/to/antigravity-app # Setup specific project"
      echo "  ./setup.sh --global                 # Install for all projects"
      echo "  ./setup.sh --legacy                 # Legacy copy mode (no hooks/agents)"
      exit 0
      ;;
    *)
      if [ -d "$arg" ]; then
        TARGET_DIR="$arg"
      else
        error "Directory not found: $arg"
      fi
      ;;
  esac
done

# --- Check prerequisites ---
check_prerequisites() {
  if ! command -v git &> /dev/null; then
    error "git is required but not installed."
  fi

  if ! command -v claude &> /dev/null; then
    warn "Claude Code CLI not found. Install it first: https://docs.anthropic.com/en/docs/claude-code"
    warn "Continuing with file-based setup..."
  fi
}

# --- Clone or update the plugin ---
install_plugin() {
  local dest="$1"

  if [ -d "$dest/.git" ]; then
    info "Plugin already cloned at $dest — pulling latest..."
    git -C "$dest" pull origin main --quiet 2>/dev/null || \
      git -C "$dest" pull origin master --quiet 2>/dev/null || \
      warn "Could not pull latest. Using existing version."
    ok "Plugin updated."
  else
    info "Cloning ProductEngineeringSkills plugin..."
    mkdir -p "$(dirname "$dest")"
    git clone --quiet "$PLUGIN_REPO" "$dest" 2>/dev/null || \
      error "Failed to clone plugin. Check your network and GitHub access."
    ok "Plugin cloned to $dest"
  fi
}

# --- Global install (user-level, all projects) ---
setup_global() {
  info "Installing plugin globally for all projects..."

  local plugin_path="${INSTALL_BASE}/${PLUGIN_DIR_NAME}"
  install_plugin "$plugin_path"

  # Create user-level settings if they don't exist
  local user_settings="${HOME}/.claude/settings.json"
  mkdir -p "${HOME}/.claude"

  if [ -f "$user_settings" ]; then
    # Check if plugin is already enabled
    if grep -q "$PLUGIN_NAME" "$user_settings" 2>/dev/null; then
      ok "Plugin already registered in user settings."
    else
      info "Adding plugin to user settings..."
      # Use python to safely merge JSON if available, otherwise warn
      if command -v python3 &> /dev/null; then
        python3 -c "
import json, sys
try:
    with open('$user_settings', 'r') as f:
        settings = json.load(f)
except:
    settings = {}

plugins = settings.get('enabledPlugins', [])
if '$PLUGIN_NAME' not in plugins:
    plugins.append('$PLUGIN_NAME')
settings['enabledPlugins'] = plugins

with open('$user_settings', 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')
"
        ok "Plugin registered in $user_settings"
      else
        warn "python3 not found. Manually add to $user_settings:"
        echo "  \"enabledPlugins\": [\"$PLUGIN_NAME\"]"
      fi
    fi
  else
    echo '{
  "enabledPlugins": ["'"$PLUGIN_NAME"'"]
}' > "$user_settings"
    ok "Created $user_settings with plugin enabled."
  fi

  echo ""
  ok "Global installation complete!"
  echo ""
  echo "  Plugin location: $plugin_path"
  echo "  User settings:   $user_settings"
  echo ""
  echo "  All Claude Code sessions will now have access to 58 skills."
  echo "  To update later: cd $plugin_path && git pull"
  echo ""
  echo "  Or load manually per-session:"
  echo "    claude --plugin-dir $plugin_path"
}

# --- Project-level install (plugin mode) ---
setup_project() {
  local project_dir="$1"
  info "Setting up plugin for project: $project_dir"

  # Verify it looks like a project directory
  if [ ! -d "$project_dir/.git" ]; then
    warn "$project_dir is not a git repository. Continuing anyway..."
  fi

  # Clone plugin to a shared location
  local plugin_path="${INSTALL_BASE}/${PLUGIN_DIR_NAME}"
  install_plugin "$plugin_path"

  # Create project .claude directory
  mkdir -p "$project_dir/.claude"

  # Create or update project CLAUDE.md with plugin reference
  local claude_md="$project_dir/.claude/CLAUDE.md"
  if [ -f "$claude_md" ]; then
    if grep -q "ProductEngineeringSkills" "$claude_md" 2>/dev/null; then
      ok "CLAUDE.md already references the plugin."
    else
      info "Appending plugin reference to existing CLAUDE.md..."
      cat >> "$claude_md" << 'CLAUDEMD'

## Cure Consulting Group Standards

This project uses the ProductEngineeringSkills plugin. Load it with:
```
claude --plugin-dir ~/.claude/plugins/ProductEngineeringSkills
```

Available skills: /cure-product-engineering:sdlc, /cure-product-engineering:feature-audit,
/cure-product-engineering:security-review, and 55 more. Run any skill with /cure-product-engineering:<name>.
CLAUDEMD
      ok "Updated $claude_md"
    fi
  else
    info "Creating project CLAUDE.md..."
    cat > "$claude_md" << 'CLAUDEMD'
# Project Standards

This project follows Cure Consulting Group engineering standards via the ProductEngineeringSkills plugin.

## Plugin Setup

Load the plugin when starting Claude Code:
```
claude --plugin-dir ~/.claude/plugins/ProductEngineeringSkills
```

## Available Skills (58)

Run any skill with `/cure-product-engineering:<skill-name>`:

**Engineering:** sdlc, android-feature-scaffold, ios-architect, nextjs-feature-scaffold, firebase-architect, api-architect, api-gateway, stripe-integration, ai-feature-builder, llmops, database-architect, data-migration, infrastructure-scaffold, edge-computing, micro-frontends, offline-first, i18n, notification-architect
**Quality:** feature-audit, testing-strategy, e2e-testing, test-accounts, uat, security-review, compliance-architect, accessibility-audit, performance-review, chaos-engineering, green-software
**Product:** product-manager, product-design, market-research, go-to-market, product-marketing, customer-onboarding, seo-content-engine
**Operations:** project-bootstrap, project-manager, ci-cd-pipeline, release-management, feature-flags, observability, dora-metrics, analytics-implementation, incident-response, disaster-recovery, growth-engineering, design-system
**Business:** engineering-cost-model, saas-financial-model, finops, legal-doc-scaffold
**Consulting:** client-handoff, client-communication, proposal-generator
**Design:** android-design-expert, ios-design-expert, web-design-expert

## Tech Stack

- Android: Kotlin + Compose + Hilt + MVI + Clean Architecture
- iOS: Swift + SwiftUI + MVVM + structured concurrency
- Web: Next.js + TypeScript + Tailwind CSS
- Backend: Firebase (Firestore, Cloud Functions v2, Auth)
- Payments: Stripe
- CI/CD: GitHub Actions
CLAUDEMD
    ok "Created $claude_md"
  fi

  # Copy path-specific rules to project
  info "Installing path-specific rules..."
  mkdir -p "$project_dir/.claude/rules"

  # Detect project type and copy relevant rules
  local rules_copied=0
  if find "$project_dir" -name "*.kt" -o -name "*.java" 2>/dev/null | head -1 | grep -q .; then
    cp "$plugin_path/rules/android.md" "$project_dir/.claude/rules/" 2>/dev/null && rules_copied=$((rules_copied + 1))
    info "  Detected Android project — installed android.md rules"
  fi
  if find "$project_dir" -name "*.swift" 2>/dev/null | head -1 | grep -q .; then
    cp "$plugin_path/rules/ios.md" "$project_dir/.claude/rules/" 2>/dev/null && rules_copied=$((rules_copied + 1))
    info "  Detected iOS project — installed ios.md rules"
  fi
  if find "$project_dir" -name "*.tsx" -o -name "*.ts" 2>/dev/null | head -1 | grep -q .; then
    cp "$plugin_path/rules/web.md" "$project_dir/.claude/rules/" 2>/dev/null && rules_copied=$((rules_copied + 1))
    info "  Detected Web project — installed web.md rules"
  fi
  if [ -f "$project_dir/firebase.json" ] || find "$project_dir" -path "*/functions/*" 2>/dev/null | head -1 | grep -q .; then
    cp "$plugin_path/rules/firebase.md" "$project_dir/.claude/rules/" 2>/dev/null && rules_copied=$((rules_copied + 1))
    info "  Detected Firebase project — installed firebase.md rules"
  fi

  if [ "$rules_copied" -eq 0 ]; then
    info "  No specific platform detected — installing all rules"
    cp "$plugin_path/rules/"*.md "$project_dir/.claude/rules/" 2>/dev/null || true
  fi

  ok "Rules installed to $project_dir/.claude/rules/"

  # Install Dependabot config for auto-updating the plugin package
  local dependabot_dir="$project_dir/.github"
  local dependabot_file="$dependabot_dir/dependabot.yml"
  mkdir -p "$dependabot_dir"

  if [ -f "$dependabot_file" ]; then
    if grep -q "cure-consulting-group" "$dependabot_file" 2>/dev/null; then
      ok "Dependabot already configured for plugin updates."
    else
      info "Appending npm ecosystem to existing dependabot.yml..."
      cat >> "$dependabot_file" << 'DEPBOT'

  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    allow:
      - dependency-name: "@cure-consulting-group/product-engineering-skills"
    labels:
      - "dependencies"
      - "skills-update"
    commit-message:
      prefix: "chore"
      include: "scope"
DEPBOT
      ok "Updated $dependabot_file"
    fi
  else
    cat > "$dependabot_file" << 'DEPBOT'
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    allow:
      - dependency-name: "@cure-consulting-group/product-engineering-skills"
    labels:
      - "dependencies"
      - "skills-update"
    commit-message:
      prefix: "chore"
      include: "scope"
DEPBOT
    ok "Created $dependabot_file for auto-updating skills plugin"
  fi

  # Create .gitignore entry for local settings
  local gitignore="$project_dir/.gitignore"
  if [ -f "$gitignore" ]; then
    if ! grep -q ".claude/settings.local.json" "$gitignore" 2>/dev/null; then
      echo -e "\n# Claude Code local settings\n.claude/settings.local.json" >> "$gitignore"
      ok "Added .claude/settings.local.json to .gitignore"
    fi
  fi

  echo ""
  ok "Project setup complete!"
  echo ""
  echo "  Project:       $project_dir"
  echo "  Plugin:        $plugin_path"
  echo "  Rules:         $project_dir/.claude/rules/"
  echo "  CLAUDE.md:     $claude_md"
  echo ""
  echo "  Start Claude Code with the plugin:"
  echo "    claude --plugin-dir $plugin_path"
  echo ""
  echo "  Files added (commit these to share with your team):"
  echo "    .claude/CLAUDE.md"
  echo "    .claude/rules/*.md"
}

# --- Legacy install (copy commands, no plugin features) ---
setup_legacy() {
  local project_dir="$1"
  info "Legacy setup: copying skills to $project_dir/.claude/commands/"

  # Clone plugin to temp or shared location
  local plugin_path="${INSTALL_BASE}/${PLUGIN_DIR_NAME}"
  install_plugin "$plugin_path"

  # Copy command files
  mkdir -p "$project_dir/.claude/commands"
  cp "$plugin_path/claude-commands/"*.md "$project_dir/.claude/commands/"
  ok "Copied 58 skills to $project_dir/.claude/commands/"

  echo ""
  warn "Legacy mode: hooks, agents, output styles, and MCP configs are NOT included."
  warn "Consider using plugin mode instead: ./setup.sh $project_dir"
  echo ""
  echo "  Available as slash commands:"
  echo "    /sdlc, /feature-audit, /security-review, /android-feature-scaffold, etc."
}

# --- Main ---
main() {
  echo ""
  echo "╔══════════════════════════════════════════════════════════╗"
  echo "║  Cure Consulting Group — ProductEngineeringSkills Setup ║"
  echo "║  Plugin v3.0.0 — 58 Skills, Hooks, Agents, Rules       ║"
  echo "╚══════════════════════════════════════════════════════════╝"
  echo ""

  check_prerequisites

  case "$MODE" in
    global)  setup_global ;;
    project) setup_project "$TARGET_DIR" ;;
    legacy)  setup_legacy "$TARGET_DIR" ;;
  esac

  echo ""
  info "Documentation: https://github.com/Cure-Consulting-Group/ProductEngineeringSkills"
  echo ""
}

main
