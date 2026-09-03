#!/usr/bin/env python3
"""PreToolUse guard for cure-tri-lane.

Reads the Bash tool input (stdin JSON, falling back to $CLAUDE_TOOL_INPUT) and
refuses lane invocations that would run without an explicit sandbox:

  codex exec ...            without -s / --sandbox      (review subcommand is exempt: read-only by design)
  codex ... --dangerously-bypass-approvals-and-sandbox
  agy -p / --print / --prompt without --sandbox
  agy ... --mode accept-edits
  agy ... --dangerously-skip-permissions

Exit 2 blocks the call and the message on stderr reaches Claude. Anything
unexpected exits 0 so the hook can never break a session. Stdlib only.
"""
import json
import os
import re
import sys


def load_command() -> str:
    raw = ""
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
    except Exception:
        raw = ""
    if not raw.strip():
        raw = os.environ.get("CLAUDE_TOOL_INPUT", "")
    try:
        d = json.loads(raw)
    except Exception:
        return ""
    if isinstance(d, dict):
        ti = d.get("tool_input", d)
        if isinstance(ti, dict):
            return str(ti.get("command", ""))
    return ""


def refuse(msg: str) -> int:
    sys.stderr.write("cure-tri-lane guard: " + msg + "\n")
    return 2


WRAPPERS = {"gtimeout", "timeout", "env", "nice", "caffeinate", "command", "exec"}


def lead_command(seg: str) -> str:
    """Return the program a shell segment actually runs, skipping VAR=.. prefixes and timeout/env wrappers."""
    toks = seg.strip().split()
    i = 0
    while i < len(toks):
        t = toks[i]
        if re.match(r"^[A-Za-z_]\w*=", t):
            i += 1
            continue
        base = t.rsplit("/", 1)[-1]
        if base in WRAPPERS:
            i += 1
            # skip wrapper options and a numeric duration (timeout 600 / gtimeout -k 5 600)
            while i < len(toks) and (toks[i].startswith("-") or re.match(r"^\d+[smhd]?$", toks[i])):
                i += 1
            continue
        return base
    return ""


def main() -> int:
    cmd = load_command()
    if not cmd:
        return 0
    # Split on shell separators so each pipeline segment is judged on its own flags.
    segments = re.split(r"\s*(?:&&|\|\||;|\|)\s*", cmd)
    for seg in segments:
        s = " " + seg.strip() + " "
        lead = lead_command(seg)
        if lead == "codex":
            if "--dangerously-bypass-approvals-and-sandbox" in s:
                return refuse("codex may not bypass approvals and sandbox. Use -s workspace-write or -s read-only.")
            is_exec = re.search(r"\bcodex\s+(exec|e)\b", s) is not None
            is_review = re.search(r"\bcodex\s+(exec\s+)?review\b", s) is not None
            if is_exec and not is_review:
                if not re.search(r"\s(-s|--sandbox)(\s|=)", s):
                    return refuse("codex exec needs an explicit sandbox: add -s workspace-write (implementer) or -s read-only (analysis). The user config defaults to danger-full-access.")
                if "danger-full-access" in s:
                    return refuse("codex exec may not use danger-full-access in a lane.")
        if lead == "agy":
            if "--dangerously-skip-permissions" in s:
                return refuse("agy may not skip permissions in a lane.")
            if re.search(r"--mode(\s+|=)accept-edits", s):
                return refuse("the Antigravity lane is read-only: use --mode plan --sandbox in a read-only worktree.")
            is_print = re.search(r"\s(-p|--print|--prompt)(\s|=)", s) is not None
            is_slash_only = re.search(r"\s(-p|--print|--prompt)\s+[\"']?/(usage|credits|quota|model|models|skills|help)\b", s) is not None
            if is_print and not is_slash_only and "--sandbox" not in s:
                return refuse("headless agy needs --sandbox (plan mode alone does not prevent writes; it reverted a live tree on 2026-09-02).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
