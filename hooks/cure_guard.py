#!/usr/bin/env python3
"""Cure hook guard — one entry point for the plugin's command hooks.

Usage (from hooks/hooks.json):  python3 "${CLAUDE_PLUGIN_ROOT}/hooks/cure_guard.py" <mode>

Modes:
  prompt         UserPromptSubmit  destructive-intent nudge (plain stdout reaches Claude here)
  edit           PreToolUse Edit|Write|MultiEdit|NotebookEdit  protected-file guard
  skill-content  PreToolUse Edit|Write|...  static scan of skill/agent/persona content
  bash           PreToolUse Bash   destructive-command guard
  telemetry      PreToolUse Skill  skill-usage log (~/.cure/telemetry)
  session-start  SessionStart startup  telemetry + opt-in provisioning (.claude/loop.md, workflows)
  failure        PostToolUseFailure  telemetry with the real tool_name + deterministic Bash triage
  agent-done     PostToolUse Agent   checklist after a write-capable Cure agent returns
  stop           Stop               deterministic verification gate (no model call)

Hook input arrives as JSON on stdin (tool fields under `tool_input`; the tool name is
`tool_name`). Before v7.9.1 these hooks read a nonexistent CLAUDE_TOOL_INPUT env var and
silently did nothing (Wave 5); until Wave 7 the failure telemetry read a nonexistent
CLAUDE_TOOL_NAME. Output channel rules (code.claude.com/docs/en/hooks, 2026-10-24):
plain stdout reaches Claude only on UserPromptSubmit, UserPromptExpansion, SessionStart and
PostModelSwitch; everywhere else context goes through JSON
`hookSpecificOutput.additionalContext`. Contract:
  * exit 2 + stderr message  -> block the tool call (PreToolUse)
  * exit 0                   -> allow; stdout may carry context (see above)
  * any internal error       -> exit 0 (fail open; a broken guard must never
                                wedge a session)
Stdlib only. Regression tests: python3 hooks/test_cure_guard.py
"""
import json
import os
import re
import shutil
import sys
import time

CODE_EXT = re.compile(
    r"\.(py|pyi|ts|tsx|js|jsx|mjs|cjs|kt|kts|java|swift|m|mm|go|rs|rb|php|cs|c|cc|cpp|cxx|h|hpp|"
    r"scala|dart|vue|svelte|ex|exs|clj|lua|sh)$", re.I)

# --- edit guard: files an agent must not hand-edit ---------------------------
ENV_ALLOWED = re.compile(r"\.env\.(example|sample|template|defaults)$")
SECRETS_DIR = re.compile(r"(^|/)secrets/", re.I)
SECRETS_MSG = "Credential and secret files must not be modified by AI. Manage these manually."
PROTECTED = [
    (re.compile(r"(^|/)\.env(\.[\w.-]+)?$"),
     "Do not modify .env files directly. Use environment variable management."),
    (re.compile(r"(^|/)(package-lock\.json|npm-shrinkwrap\.json|yarn\.lock|pnpm-lock\.yaml|"
                r"Cargo\.lock|poetry\.lock|Gemfile\.lock|composer\.lock|Podfile\.lock|go\.sum|uv\.lock)$"),
     "Lock files should only be modified by package managers, not manually."),
    (re.compile(r"(^|/)(credentials(\.json)?|id_rsa[^/]*|id_ed25519[^/]*|[^/]*\.pem|[^/]*\.p12|"
                r"service-?account[^/]*\.json|serviceAccount[^/]*\.json)$", re.I),
     SECRETS_MSG),
    (re.compile(r"\.tfstate(\.[\w-]+)?$"),
     "Terraform state files must never be manually edited. Use terraform state commands."),
]

# --- skill/agent/persona content guard ----------------------------------------
# Library files only: markdown or bundled scripts under skills/, and agent/persona
# markdown. App code that lives in src/agents/ or src/skills/ is not library content.
LIBRARY_PATH = re.compile(
    r"(^|/)skills/(.+/)?([^/]+\.md|scripts/[^/]+)$|(^|/)(agents|personas)/[^/]+\.md$")
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

# Whole words only: "swipe" must not read as "wipe".
DESTRUCTIVE_PROMPT = re.compile(
    r"\b(delete all|drop all|remove everything|wip(e|es|ed|ing)|nuk(e|es|ed|ing))\b")

# --- failure triage: deterministic, replaces the always-ok prompt hook ---------
FAILURE_TRIAGE = [
    ("migration-validator", "database or migration",
     re.compile(r"\b(migrat\w*|alembic|flyway|liquibase|knex|sequelize)\b|relation \S+ does not exist|"
                r"duplicate column", re.I)),
    ("deployment-validator", "deploy, infra or config",
     re.compile(r"\b(firebase deploy|gcloud (run|functions|app) deploy|vercel|netlify deploy|fly deploy|"
                r"kubectl (apply|rollout)|helm (install|upgrade)|terraform (plan|apply)|docker push|"
                r"eas (build|submit)|fastlane)\b", re.I)),
    ("dependency-auditor", "dependency or install",
     re.compile(r"\b(npm (i|install|ci)|pnpm (i|install|add)|yarn (install|add)|pip3? install|uv (add|sync|pip)|"
                r"poetry (add|install|lock)|bundle install|pod install|cargo (add|update)|go (get|mod))\b|"
                r"ERESOLVE|E404|ETARGET|peer dep|No matching distribution|Could not resolve dependenc|"
                r"version solving failed|ModuleNotFoundError|Cannot find module", re.I)),
    ("ci-debugger", "build or test",
     re.compile(r"\b(pytest|unittest|jest|vitest|mocha|playwright|cypress|tsc|eslint|go (test|build|vet)|"
                r"cargo (test|build|check|clippy)|gradlew?|xcodebuild|swift (test|build)|mvn|"
                r"(npm|pnpm|yarn|bun) (run )?(test|build|lint|typecheck))\b|"
                r"\bFAILED\b|AssertionError|error TS\d+|BUILD FAILED|compilation failed", re.I)),
]

# --- write-capable agents whose return deserves a checklist -------------------
WRITE_AGENTS = {"refactor-assistant", "project-bootstrapper", "release-coordinator"}

# --- stop gate ----------------------------------------------------------------
STOP_MARKER = "[cure-stop-gate]"
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
NON_PRODUCT = re.compile(
    r"(^|/)(tests?|__tests__|__mocks__|specs?|e2e|fixtures|testdata|androidTest|testFixtures|"
    r"node_modules|dist|build|vendor)/|"
    r"(^|/)(test_[^/]+\.py|[^/]+_test\.(py|go)|conftest\.py|[^/]+\.(test|spec)\.[^/]+|"
    r"[^/]+Tests?\.(kt|java|swift)|[^/]+\.config\.[cm]?[jt]s|\.[^/]+rc\.[cm]?js)$", re.I)
VERIFY_CMD = re.compile(
    r"\b(pytest|py\.test|unittest|tox|nox|mypy|pyright|ruff|flake8|pylint|jest|vitest|mocha|ava|"
    r"playwright|cypress|tsc|eslint|biome|golangci-lint|go\s+(test|build|vet)|"
    r"cargo\s+(test|build|check|clippy|nextest)|gradlew?|mvnw?|xcodebuild|swift\s+(test|build)|"
    r"fastlane|dotnet\s+(test|build)|flutter\s+(test|analyze)|dart\s+(test|analyze)|rspec|phpunit|"
    r"make|just|bazel\s+(test|build)|node\s+--test|deno\s+(test|check|lint)|bun\s+test|"
    r"(npm|pnpm|yarn|bun)\s+(run\s+)?(test|t|build|lint|typecheck|check|verify)|"
    r"firebase\s+emulators:exec|bats|shellcheck)\b|"
    r"\bpython3?\s+(-m\s+(pytest|unittest)|\S*test\S*\.py)", re.I)
VERIFY_AGENTS = re.compile(r"(test-runner|qa-engineer|ci-debugger|codex-reviewer)$")
WAKING_TASKS = {"subagent", "workflow", "teammate", "cloud session"}
SKIP_VERIFY = re.compile(
    r"\b(skip|no|without|don'?t|do not)\b[^.\n]{0,24}\b(tests?|testing|verif\w*|builds?|ci)\b", re.I)
NON_HUMAN_ORIGINS = {"scheduled", "sdk", "task_notification", "peer", "system", "auto_continuation"}
SUGGEST = [
    (re.compile(r"\.pyi?$"), "pytest (or python3 -m unittest)"),
    (re.compile(r"\.([cm]?[jt]sx?|vue|svelte)$"), "the package's test script and tsc --noEmit"),
    (re.compile(r"\.go$"), "go test ./..."),
    (re.compile(r"\.rs$"), "cargo test"),
    (re.compile(r"\.(kt|kts|java)$"), "./gradlew test"),
    (re.compile(r"\.(swift|m|mm)$"), "swift test or xcodebuild test"),
]
TRANSCRIPT_TAIL = 4 * 1024 * 1024


def load():
    raw = sys.stdin.read()
    return json.loads(raw) if raw.strip() else {}


def tool_input(d):
    ti = d.get("tool_input")
    return ti if isinstance(ti, dict) else {}


def block(msg):
    print(f"BLOCKED: {msg}", file=sys.stderr)
    sys.exit(2)


def add_context(event, text):
    """The JSON channel Claude reads on events where plain stdout goes to the debug log."""
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def project_dir(d):
    return d.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def log_event(event, project, detail=""):
    try:
        base = os.path.expanduser("~/.cure/telemetry")
        os.makedirs(base, exist_ok=True)
        with open(os.path.join(base, "sessions.jsonl"), "a") as f:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": event,
                                "project": os.path.basename(project.rstrip("/")),
                                "detail": detail}) + "\n")
    except Exception:
        pass


def mode_prompt(d):
    p = (d.get("prompt") or "").lower()[:500]
    if DESTRUCTIVE_PROMPT.search(p):
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
    # A secrets/ directory holds secrets, unless the file is source code:
    # src/secrets/manager.ts is a module that handles secrets, not a secret.
    if SECRETS_DIR.search(path) and not CODE_EXT.search(path):
        block(SECRETS_MSG)


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
    add_context("PreToolUse", "Skill/agent/persona file change detected: run "
                "@skill-security-auditor before merging.")


def mode_bash(d):
    cmd = tool_input(d).get("command") or ""
    flat = re.sub(r"[\"']", "", cmd)  # `rm -rf "/"` must not slip past on quoting
    for pat in BASH_PATTERNS:
        if pat.search(flat):
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


# --- session-start: telemetry + opt-in provisioning ---------------------------

def plugin_root():
    return os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))


def opted_in(proj):
    """Provisioning writes files, so it needs an explicit Cure marker in the project:
    a .cure/ directory, a cure-infra-bootstrap manifest, or a CLAUDE.md naming Cure."""
    if os.path.isdir(os.path.join(proj, ".cure")):
        return True
    if os.path.isfile(os.path.join(proj, "claude.manifest.json")):
        return True
    for rel in ("CLAUDE.md", os.path.join(".claude", "CLAUDE.md")):
        try:
            with open(os.path.join(proj, rel), encoding="utf-8", errors="ignore") as f:
                if re.search(r"Cure Consulting Group|cure-product-engineering", f.read(200_000)):
                    return True
        except OSError:
            continue
    return False


def mode_session_start(d):
    proj = project_dir(d)
    log_event("session_start", proj)
    if not opted_in(proj):
        return
    root = plugin_root()
    done = []
    loop_src = os.path.join(root, "bootstrap", "templates", "loop.md")
    loop_dst = os.path.join(proj, ".claude", "loop.md")
    if os.path.isfile(loop_src) and not os.path.exists(loop_dst):
        os.makedirs(os.path.dirname(loop_dst), exist_ok=True)
        shutil.copyfile(loop_src, loop_dst)
        done.append(".claude/loop.md (Cure maintenance loop: run bare /loop)")
    wf_src = os.path.join(root, "workflows")
    wf_dst = os.path.join(proj, ".claude", "workflows")
    if os.path.isdir(wf_src) and not os.path.exists(wf_dst):
        scripts = [f for f in sorted(os.listdir(wf_src)) if f.endswith(".js")]
        if scripts:
            os.makedirs(wf_dst, exist_ok=True)
            for f in scripts:
                shutil.copyfile(os.path.join(wf_src, f), os.path.join(wf_dst, f))
            done.append(".claude/workflows (" + ", ".join("/" + f[:-3] for f in scripts) + ")")
    if done:
        print("Cure plugin provisioned: " + ", ".join(done) +
              ". Files are yours now: edit freely; existing files are never overwritten.")


# --- failure: real tool name + deterministic triage ---------------------------

def mode_failure(d):
    tool = d.get("tool_name") or "unknown"
    log_event("tool_failure", project_dir(d), tool)
    if tool != "Bash" or d.get("is_interrupt"):
        return
    text = (tool_input(d).get("command") or "") + "\n" + str(d.get("error") or "")[:4000]
    for agent, kind, pat in FAILURE_TRIAGE:
        if pat.search(text):
            add_context("PostToolUseFailure",
                        f"Cure triage: this looks like a {kind} failure. If it is not a quick fix, "
                        f"the cure-product-engineering:{agent} agent is built for it.")
            return


# --- agent-done: checklist in the parent session -------------------------------

def mode_agent_done(d):
    sub = str(tool_input(d).get("subagent_type") or "").rsplit(":", 1)[-1]
    if sub not in WRITE_AGENTS:
        return
    add_context("PostToolUse",
                f"{sub} (write-capable) finished. Before calling this done: tests added and passing "
                "(test-runner), lint and types clean (ci-debugger), PR ready (pr-reviewer), new "
                "surface documented (doc-generator).")


# --- stop: deterministic gate --------------------------------------------------

def read_tail(path, limit=TRANSCRIPT_TAIL):
    with open(os.path.expanduser(path), "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - limit))
        data = f.read()
    lines = data.decode("utf-8", errors="ignore").splitlines()
    return lines[1:] if size > limit else lines  # the first line may be cut


def is_prompt(entry):
    """A turn-starting user message: not a tool result, not meta, not a subagent."""
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isSidechain"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        return not any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)
    return False


def prompt_text(entry):
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content or [] if isinstance(b, dict))


def current_turn(lines):
    """(prompt_entry, raw_lines_after, entries_after) for the latest turn, or (None, [], [])."""
    parsed = []
    for raw in lines:
        try:
            parsed.append((raw, json.loads(raw)))
        except Exception:
            continue
    for i in range(len(parsed) - 1, -1, -1):
        if is_prompt(parsed[i][1]):
            rest = parsed[i + 1:]
            return parsed[i][1], [r for r, _ in rest], [e for _, e in rest]
    return None, [], []


def stop_exempt(d):
    """Documented signals first (stop_hook_active, session_crons, background_tasks), then env."""
    if d.get("stop_hook_active"):
        return True  # already continuing because of a stop hook: never block twice
    if d.get("session_crons"):
        return True  # /loop, CronCreate or ScheduleWakeup: an unattended iteration
    for t in d.get("background_tasks") or []:
        if isinstance(t, dict) and (t.get("type") in WAKING_TASKS or
                                    VERIFY_CMD.search(str(t.get("command") or ""))):
            return True  # paused on work that will wake the session (not a dev server)
    ep = os.environ.get("CLAUDE_CODE_ENTRYPOINT", "")
    if ep.startswith("sdk") or ep == "remote" or os.environ.get("CLAUDE_CODE_REMOTE") or os.environ.get("CI"):
        return True  # headless, routine, cloud or CI run: nobody to answer a nudge
    return False


def mode_stop(d):
    log_event("session_stop", project_dir(d))
    if stop_exempt(d):
        return
    tp = d.get("transcript_path")
    if not tp:
        return
    prompt, raw_after, after = current_turn(read_tail(tp))
    if prompt is None:
        return
    # Undocumented transcript fields, used only to exempt (absent -> no effect).
    origin = prompt.get("turnOrigin")
    if (isinstance(origin, str) and origin in NON_HUMAN_ORIGINS) or \
            str(prompt.get("entrypoint") or "").startswith("sdk"):
        return
    if SKIP_VERIFY.search(prompt_text(prompt)):
        return
    if any(STOP_MARKER in raw for raw in raw_after):
        return  # already nudged this turn: never twice
    pending = []  # product source files edited since the last verification
    for e in after:
        if e.get("type") != "assistant" or e.get("isSidechain"):
            continue
        for b in (e.get("message") or {}).get("content") or []:
            if not isinstance(b, dict) or b.get("type") != "tool_use":
                continue
            name, ti = b.get("name"), b.get("input") or {}
            if name in EDIT_TOOLS:
                path = target_path(ti)
                if CODE_EXT.search(path) and not NON_PRODUCT.search(path) and path not in pending:
                    pending.append(path)
            elif name == "Bash" and VERIFY_CMD.search(str(ti.get("command") or "")):
                pending = []
            elif name in ("Agent", "Task") and VERIFY_AGENTS.search(str(ti.get("subagent_type") or "")):
                pending = []
    if not pending:
        return
    proj = project_dir(d)
    names = [os.path.relpath(p, proj) if os.path.isabs(p) else p for p in pending]
    hint = next((s for pat, s in SUGGEST if pat.search(pending[-1])), "the project's test command")
    shown = ", ".join(names[:6]) + (f" and {len(names) - 6} more" if len(names) > 6 else "")
    add_context("Stop",
                f"{STOP_MARKER} Source files were edited this turn with no test, build or "
                f"verification command after the last edit: {shown}. Run {hint} (or the project's "
                "own check), or tell the user why it can't run, before finishing. "
                "This gate fires at most once per turn.")


MODES = {
    "prompt": mode_prompt,
    "edit": mode_edit,
    "skill-content": mode_skill_content,
    "bash": mode_bash,
    "telemetry": mode_telemetry,
    "session-start": mode_session_start,
    "failure": mode_failure,
    "agent-done": mode_agent_done,
    "stop": mode_stop,
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
