#!/usr/bin/env python3
"""Cure hook guard — one entry point for the plugin's command hooks.

Usage (from hooks/hooks.json):  python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" <mode>

Modes: prompt | edit | skill-content | bash | telemetry

Hook input arrives as JSON on stdin (tool fields under `tool_input`). Before
v7.9.1 these hooks read a nonexistent CLAUDE_TOOL_INPUT env var and silently
did nothing (Wave 5 finding). Contract:
  * exit 2 + stderr message  -> block the tool call (PreToolUse)
  * exit 0                   -> allow; stdout may add context
  * any internal error       -> exit 0 (fail open; a broken guard must never
                                wedge a session)
Stdlib only. Regression tests: python3 hooks/test_cure_guard.py
"""
import json
import os
import re
import sys
import time

# --- edit guard: files an agent must not hand-edit ---------------------------
ENV_ALLOWED = re.compile(r"\.env\.(example|sample|template|defaults)$")
PROTECTED = [
    (re.compile(r"(^|/)\.env(\.[\w.-]+)?$"),
     "Do not modify .env files directly. Use environment variable management."),
    (re.compile(r"(^|/)(package-lock\.json|npm-shrinkwrap\.json|yarn\.lock|pnpm-lock\.yaml|"
                r"Cargo\.lock|poetry\.lock|Gemfile\.lock|composer\.lock|Podfile\.lock|go\.sum|uv\.lock)$"),
     "Lock files should only be modified by package managers, not manually."),
    (re.compile(r"(^|/)(credentials(\.json)?|id_rsa[^/]*|id_ed25519[^/]*|[^/]*\.pem|[^/]*\.p12|"
                r"service-?account[^/]*\.json|serviceAccount[^/]*\.json)$|(^|/)secrets/", re.I),
     "Credential and secret files must not be modified by AI. Manage these manually."),
    (re.compile(r"\.tfstate(\.[\w-]+)?$"),
     "Terraform state files must never be manually edited. Use terraform state commands."),
]

# --- skill/agent/persona content guard ----------------------------------------
LIBRARY_PATH = re.compile(r"(^|/)(skills|agents|personas)/")
CONTENT_PATTERNS = [
    (r"curl[^\n]*\|\s*(ba|z)?sh\b", "pipes a remote download into a shell"),
    (r"wget[^\n]*\|\s*(ba|z)?sh\b", "pipes a remote download into a shell"),
    (r"base64\s+(-d|--decode)[^\n]*\|\s*(ba|z)?sh\b", "executes base64-decoded code"),
    (r"rm\s+-rf\s+(/(\s|$)|~(/?\s|/?$)|\$HOME\b)", "recursive delete of home or root"),
    (r"(id_rsa|id_ed25519|\.aws/credentials)", "references credential files"),
    (r"(nc|ncat|curl|wget)[^\n]*\$\(\s*(cat|env|printenv)", "exfiltrates local data to the network"),
]

# --- bash guard: unambiguous system-destroying commands only ------------------
BASH_PATTERNS = [
    re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?[a-zA-Z]*\s+(--no-preserve-root\s+)?"
               r"(/|/\*|~|~/|~/\*|\$HOME|\$HOME/|\$HOME/\*|\.|\./|\*)(\s|;|&|\||$)"),
    re.compile(r"\bmkfs(\.\w+)?\b"),
    re.compile(r"\bdd\b[^\n]*\bof=/dev/(disk|sd|nvme|hd|rdisk)"),
    re.compile(r":\(\)\s*\{\s*:\|:&\s*\};:"),  # fork bomb
]

DESTRUCTIVE_PROMPT = ("delete all", "drop all", "remove everything", "wipe", "nuke")


def load():
    raw = sys.stdin.read()
    return json.loads(raw) if raw.strip() else {}


def tool_input(d):
    ti = d.get("tool_input")
    return ti if isinstance(ti, dict) else {}


def block(msg):
    print(f"BLOCKED: {msg}", file=sys.stderr)
    sys.exit(2)


def mode_prompt(d):
    p = (d.get("prompt") or "").lower()[:500]
    if any(k in p for k in DESTRUCTIVE_PROMPT):
        print("Destructive intent detected in the prompt: confirm scope with the user "
              "before any irreversible action.")


def target_path(ti):
    return ti.get("file_path") or ti.get("notebook_path") or ""


def proposed_content(ti):
    """Everything an Edit/Write/MultiEdit/NotebookEdit call would put on disk."""
    parts = [ti.get("content") or "", ti.get("new_string") or "", ti.get("new_source") or ""]
    for e in ti.get("edits") or []:
        if isinstance(e, dict):
            parts.append(e.get("new_string") or "")
    return "\n".join(parts)


def mode_edit(d):
    path = target_path(tool_input(d))
    if not path:
        return
    for i, (pat, msg) in enumerate(PROTECTED):
        if i == 0 and ENV_ALLOWED.search(path):
            continue  # .env.example etc. are templates; other rules still apply
        if pat.search(path):
            block(msg)


def mode_skill_content(d):
    ti = tool_input(d)
    path = target_path(ti)
    if not LIBRARY_PATH.search(path):
        return
    content = proposed_content(ti)
    for pat, why in CONTENT_PATTERNS:
        if re.search(pat, content):
            block(f"proposed skill/agent/persona content {why}. If intentional, get it "
                  "reviewed by @skill-security-auditor and apply manually.")
    print("Skill/agent/persona file change detected — run @skill-security-auditor before merging.")


def mode_bash(d):
    cmd = tool_input(d).get("command") or ""
    cmd = re.sub(r"[\"']", "", cmd)  # `rm -rf "/"` must not slip past on quoting
    for pat in BASH_PATTERNS:
        if pat.search(cmd):
            block("Dangerous system command detected.")


def mode_telemetry(d):
    ti = tool_input(d)
    skill = ti.get("skill") or ti.get("name") or ""
    if not skill:
        return
    base = os.path.expanduser("~/.cure/telemetry")
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "skill-usage.jsonl"), "a") as f:
        f.write(json.dumps({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "skill": skill,
            "project": os.path.basename(d.get("cwd") or os.getcwd()),
        }) + "\n")


MODES = {
    "prompt": mode_prompt,
    "edit": mode_edit,
    "skill-content": mode_skill_content,
    "bash": mode_bash,
    "telemetry": mode_telemetry,
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in MODES:
        if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
            print(__doc__)
        sys.exit(0)
    try:
        MODES[sys.argv[1]](load())
    except SystemExit:
        raise
    except Exception:
        pass  # fail open
    sys.exit(0)


if __name__ == "__main__":
    main()
