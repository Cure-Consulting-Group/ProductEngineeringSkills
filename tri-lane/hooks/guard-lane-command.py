#!/usr/bin/env python3
"""PreToolUse guard for cure-tri-lane.

Reads the Bash tool input (stdin JSON, falling back to $CLAUDE_TOOL_INPUT), splits the
command into shell segments (including newlines), tokenises each with shlex, and refuses
lane invocations that would run without an explicit sandbox:

  codex ... exec|e ...        without -s / --sandbox        (review subcommand exempt from the -s requirement)
  codex ...                   with --dangerously-bypass-approvals-and-sandbox, --yolo, or danger-full-access
  agy -p|--print|--prompt ... unless BOTH --mode plan AND --sandbox are present
  agy ...                     with -y, --yolo, --approval-mode, --dangerously-skip-permissions, --mode accept-edits

Read-only agy slash commands (/usage, /credits, /quota, /model, /models, /skills, /help) are exempt.

Exit 2 blocks the call; the stderr message reaches Claude. Any unexpected error is
written to stderr and exits 0 so the hook can never break a session. Stdlib only.
"""
import json
import os
import re
import shlex
import sys

WRAPPERS = {"gtimeout", "timeout", "env", "nice", "caffeinate", "command", "exec", "time"}
CODEX_BYPASS = {"--dangerously-bypass-approvals-and-sandbox", "--yolo"}
AGY_BYPASS = {"-y", "--yolo", "--dangerously-skip-permissions"}
AGY_READONLY_SLASH = {"/usage", "/credits", "/quota", "/model", "/models", "/skills", "/help"}


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


def tokens(seg: str) -> list:
    try:
        return shlex.split(seg, comments=True)
    except ValueError:
        return seg.split()


def program_and_args(toks: list):
    """Skip VAR=.. prefixes and timeout/env wrappers; return (basename, remaining args)."""
    i = 0
    while i < len(toks):
        t = toks[i]
        if re.match(r"^[A-Za-z_]\w*=", t):
            i += 1
            continue
        base = t.rsplit("/", 1)[-1]
        if base in WRAPPERS:
            i += 1
            while i < len(toks) and (toks[i].startswith("-") or re.match(r"^\d+(\.\d+)?[smhd]?$", toks[i])):
                i += 1
            continue
        return base, toks[i + 1:]
    return "", []


def flag_value(args: list, flag: str):
    for i, t in enumerate(args):
        if t == flag and i + 1 < len(args):
            return args[i + 1]
        if t.startswith(flag + "="):
            return t.split("=", 1)[1]
    return None


def check_codex(args: list):
    if any(t in CODEX_BYPASS for t in args):
        return "codex may not bypass approvals and sandbox. Use -s workspace-write or -s read-only."
    if any("danger-full-access" in t for t in args):
        return "codex lanes may not use danger-full-access."
    # subcommand = first non-flag token, skipping values of root-level options that take an argument
    sub = ""
    skip = False
    for t in args:
        if skip:
            skip = False
            continue
        if t in ("-c", "--config", "-m", "--model", "-C", "--cd", "-p", "--profile", "--add-dir", "-i", "--image"):
            skip = True
            continue
        if t.startswith("-"):
            continue
        sub = t
        break
    if sub in ("exec", "e"):
        is_review = "review" in args[: args.index(sub) + 3] if sub in args else False
        if not is_review:
            if flag_value(args, "-s") is None and flag_value(args, "--sandbox") is None:
                return "codex exec needs an explicit sandbox: add -s workspace-write (implementer) or -s read-only (analysis). The user config defaults to danger-full-access."
    return None


def check_agy(args: list):
    if any(t in AGY_BYPASS for t in args):
        return "agy may not auto-approve in a lane (-y, --yolo, --dangerously-skip-permissions)."
    if any(t == "--approval-mode" or t.startswith("--approval-mode=") for t in args):
        return "agy --approval-mode is not allowed in a lane."
    mode = flag_value(args, "--mode")
    if mode == "accept-edits":
        return "the Antigravity lane is read-only: use --mode plan --sandbox in a read-only worktree."
    is_print = any(t in ("-p", "--print", "--prompt") or t.startswith(("-p=", "--print=", "--prompt=")) for t in args)
    if not is_print:
        return None
    prompt = flag_value(args, "-p") or flag_value(args, "--print") or flag_value(args, "--prompt") or ""
    if prompt.strip().split(" ")[0] in AGY_READONLY_SLASH:
        return None
    if mode != "plan":
        return "headless agy must pass --mode plan (plan mode plus --sandbox; plan alone reverted a live tree on 2026-09-02)."
    if not any(t == "--sandbox" or t == "--sandbox=true" for t in args):
        return "headless agy needs --sandbox."
    return None


def main() -> int:
    cmd = load_command()
    if not cmd:
        return 0
    for seg in re.split(r"\s*(?:&&|\|\||;|\||\n)\s*", cmd):
        if not seg.strip():
            continue
        prog, args = program_and_args(tokens(seg))
        if prog == "codex":
            msg = check_codex(args)
            if msg:
                return refuse(msg)
        elif prog == "agy":
            msg = check_agy(args)
            if msg:
                return refuse(msg)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # fail open, but loudly
        sys.stderr.write(f"cure-tri-lane guard: internal error, allowing command: {e}\n")
        sys.exit(0)
