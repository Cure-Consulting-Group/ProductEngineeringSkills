#!/usr/bin/env bash
#
# Cure Consulting Group — ProductEngineeringSkills Auto-Update
#
# Pulls the latest version of the plugin from GitHub.
# Can be run manually, via cron, or via launchd.
#
# Usage:
#   ./auto-update.sh                    # Update the global plugin install
#   ./auto-update.sh --install-cron     # Install a daily cron job
#   ./auto-update.sh --install-launchd  # Install a macOS launchd agent (recommended on macOS)
#   ./auto-update.sh --uninstall        # Remove scheduled updates

set -euo pipefail

PLUGIN_DIR="${HOME}/.claude/plugins/ProductEngineeringSkills"
LOG_FILE="${HOME}/.claude/plugins/update.log"
LAUNCHD_PLIST="${HOME}/Library/LaunchAgents/com.cure-consulting.skills-update.plist"
CRON_MARKER="# cure-skills-auto-update"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

# --- Perform the update ---
do_update() {
  if [ ! -d "$PLUGIN_DIR/.git" ]; then
    log "ERROR: $PLUGIN_DIR is not a git clone. Use 'setup.sh --global' first or install via npm."
    exit 1
  fi

  log "Checking for updates..."

  cd "$PLUGIN_DIR"

  # Fetch without modifying working tree
  git fetch origin main --quiet 2>/dev/null || git fetch origin master --quiet 2>/dev/null || {
    log "ERROR: Failed to fetch from origin. Check network."
    exit 1
  }

  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null)

  if [ "$LOCAL" = "$REMOTE" ]; then
    log "Already up to date. ($(git describe --tags --always 2>/dev/null || echo $LOCAL))"
    exit 0
  fi

  # Count what changed
  CHANGES=$(git log --oneline "$LOCAL..$REMOTE" | wc -l | tr -d ' ')
  NEW_AGENTS=$(git diff "$LOCAL..$REMOTE" --stat -- agents/ | grep -c "\.md" 2>/dev/null || echo "0")
  NEW_SKILLS=$(git diff "$LOCAL..$REMOTE" --stat -- skills/ | grep -c "SKILL\.md" 2>/dev/null || echo "0")

  log "Updating: $CHANGES commits ($NEW_AGENTS agent changes, $NEW_SKILLS skill changes)"

  git pull origin main --quiet 2>/dev/null || git pull origin master --quiet 2>/dev/null || {
    log "ERROR: Failed to pull. You may have local changes. Run: cd $PLUGIN_DIR && git stash && git pull"
    exit 1
  }

  # Read new version
  NEW_VERSION=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])" 2>/dev/null || echo "unknown")
  AGENT_COUNT=$(ls -1 agents/*.md 2>/dev/null | wc -l | tr -d ' ')
  SKILL_COUNT=$(find skills -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')

  log "Updated to v${NEW_VERSION} — ${SKILL_COUNT} skills, ${AGENT_COUNT} agents."
  log "Next Claude Code session will use the new version."
}

# --- Install cron job (Linux/macOS) ---
install_cron() {
  # Run daily at 9am
  SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/auto-update.sh"
  CRON_LINE="0 9 * * * $SCRIPT_PATH $CRON_MARKER"

  # Check if already installed
  if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
    echo "Cron job already installed."
    crontab -l | grep "$CRON_MARKER"
    return
  fi

  # Add to crontab
  (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
  echo "Installed daily cron job (9:00 AM)."
  echo "  View: crontab -l"
  echo "  Remove: $0 --uninstall"
}

# --- Install launchd agent (macOS) ---
install_launchd() {
  SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/auto-update.sh"

  mkdir -p "$(dirname "$LAUNCHD_PLIST")"
  cat > "$LAUNCHD_PLIST" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cure-consulting.skills-update</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${SCRIPT_PATH}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>${LOG_FILE}</string>
    <key>StandardErrorPath</key>
    <string>${LOG_FILE}</string>
</dict>
</plist>
PLIST

  launchctl unload "$LAUNCHD_PLIST" 2>/dev/null || true
  launchctl load "$LAUNCHD_PLIST"

  echo "Installed macOS launchd agent (daily at 9:00 AM)."
  echo "  Plist: $LAUNCHD_PLIST"
  echo "  Logs: $LOG_FILE"
  echo "  Remove: $0 --uninstall"
}

# --- Uninstall scheduled updates ---
uninstall() {
  # Remove cron
  if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
    crontab -l | grep -v "$CRON_MARKER" | crontab -
    echo "Removed cron job."
  fi

  # Remove launchd
  if [ -f "$LAUNCHD_PLIST" ]; then
    launchctl unload "$LAUNCHD_PLIST" 2>/dev/null || true
    rm -f "$LAUNCHD_PLIST"
    echo "Removed launchd agent."
  fi

  echo "Scheduled updates removed. You can still run $0 manually."
}

# --- Main ---
case "${1:-}" in
  --install-cron)    install_cron ;;
  --install-launchd) install_launchd ;;
  --uninstall)       uninstall ;;
  --help|-h)
    echo "Usage: auto-update.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  (none)              Pull latest plugin updates"
    echo "  --install-cron      Install daily cron job (Linux/macOS)"
    echo "  --install-launchd   Install macOS launchd agent (recommended)"
    echo "  --uninstall         Remove scheduled updates"
    echo "  --help              Show this help"
    ;;
  *)                 do_update ;;
esac
