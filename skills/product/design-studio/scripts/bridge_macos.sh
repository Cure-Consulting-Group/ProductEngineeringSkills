#!/usr/bin/env bash
#
# bridge_macos.sh
# Run an ExtendScript (.jsx) inside Adobe Illustrator or Adobe Photoshop on macOS via AppleScript.
#
# Usage:
#   bridge_macos.sh "Adobe Illustrator" /path/to/script.jsx
#   bridge_macos.sh "Adobe Photoshop"   /path/to/script.jsx
#
# Only those two application names are accepted; the script must exist, end in .jsx, declare #target, and
# contain no shell/network/eval primitives (callSystem, app.system, File.execute, Socket, $.evalFile, eval, #include).
# Exit codes: 1 usage, 2 application not installed, 3 osascript failure.

set -euo pipefail

APP_NAME="${1:-}"
SCRIPT_PATH="${2:-}"

case "$APP_NAME" in
  "Adobe Illustrator"|"Adobe Photoshop") ;;
  *) echo "Usage: $0 <\"Adobe Illustrator\"|\"Adobe Photoshop\"> <path_to_script.jsx>" >&2; exit 1 ;;
esac

if [ -z "$SCRIPT_PATH" ] || [ ! -f "$SCRIPT_PATH" ]; then
  echo "Error: .jsx script not found: ${SCRIPT_PATH:-<empty>}" >&2
  exit 1
fi
case "$SCRIPT_PATH" in
  *.jsx) ;;
  *) echo "Error: script must be a .jsx file" >&2; exit 1 ;;
esac

if [ "$(uname -s)" != "Darwin" ]; then
  echo "Error: this bridge needs macOS (AppleScript)" >&2
  exit 2
fi

ABS_SCRIPT_PATH="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)/$(basename "$SCRIPT_PATH")"

# Content gate: ExtendScript can reach the shell and the network. Refuse anything that tries.
if ! grep -qE '^#target (illustrator|photoshop)' "$ABS_SCRIPT_PATH"; then
  echo "Error: script must start with '#target illustrator' or '#target photoshop'" >&2
  exit 1
fi
if grep -nE 'callSystem|app\.system\s*\(|\.execute\s*\(|\bSocket\b|\$\.evalFile|\beval\s*\(|#include|\.ssh|\.aws|/etc/' "$ABS_SCRIPT_PATH"; then
  echo "Error: script contains shell, network, eval, include, or credential-path primitives; refusing to run it" >&2
  exit 1
fi

if ! osascript -e "id of application \"${APP_NAME}\"" >/dev/null 2>&1; then
  echo "Error: ${APP_NAME} is not installed (or not visible to AppleScript). Install it from Creative Cloud and retry." >&2
  exit 2
fi

echo "Running ${ABS_SCRIPT_PATH} in ${APP_NAME}..."
# The path is passed as an AppleScript argument, never interpolated into the script body.
if ! osascript - "$APP_NAME" "$ABS_SCRIPT_PATH" <<'EOF'
on run argv
    set appName to item 1 of argv
    set scriptPath to item 2 of argv
    if appName is "Adobe Illustrator" then
        tell application "Adobe Illustrator"
            activate
            do javascript (POSIX file scriptPath)
        end tell
    else
        tell application "Adobe Photoshop"
            activate
            do javascript (POSIX file scriptPath)
        end tell
    end if
end run
EOF
then
  echo "Error: ${APP_NAME} reported a failure running the script" >&2
  exit 3
fi
echo "Done: ${APP_NAME} finished ${ABS_SCRIPT_PATH}"
