#!/usr/bin/env python3
"""
audit-library.py — Score every skill, agent, and persona against the official
Anthropic Agent Skills + Claude Code subagent specifications.

Stdlib only (zero pip), matches repo convention. Supports --json and --help.

Rubric sources (June 2026):
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  - https://code.claude.com/docs/en/skills
  - https://code.claude.com/docs/en/sub-agents

Scoring: each item starts at 10.0 and loses points per violation. Hard spec
violations (invalid name, missing description) are heavily weighted; soft
best-practice misses (over 500 lines, missing argument-hint) are lighter.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
AGENTS_DIR = ROOT / "agents"
PERSONAS_DIR = ROOT / "personas"

# Documented field allow-lists ------------------------------------------------
SKILL_FIELDS = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools",
    "disallowed-tools", "model", "context", "paths", "effort", "shell",
    "agent", "hooks",
    # documented per code.claude.com/docs/en/skills (verified 2026-09-23)
    "metadata", "background", "license", "compatibility",
}
# Tolerated-but-non-functional skill fields (no penalty beyond a note)
SKILL_FIELDS_INERT = {"version"}

AGENT_FIELDS = {
    "name", "description", "tools", "disallowedTools", "model", "permissionMode",
    "maxTurns", "skills", "mcpServers", "hooks", "memory", "background",
    "effort", "color", "isolation",
}
VALID_MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
VALID_EFFORT = {"low", "medium", "high", "xhigh", "max"}
VALID_ISOLATION = {"worktree"}
# Context-budget policy (Wave 2 T24): the combined description + when_to_use
# of every skill competes for the session skill-listing budget (~1% of model
# context by default). Keep individual trigger text tight.
DESC_COMBINED_WARN = 350
DESC_COMBINED_FAIL = 500
# Preload policy (Wave 2 T12): agents should preload at most ~300 lines of
# skill bodies; everything else belongs in the body as an on-demand reference.
PRELOAD_POLICY_LINES = 300
NAME_RE = re.compile(r"^[a-z0-9-]+$")
FIRST_PERSON_RE = re.compile(r"\b(I can|I will|I'll|you can use this|let me)\b", re.I)
TIME_SENSITIVE_RE = re.compile(
    r"\b(as of (?:January|February|March|April|May|June|July|August|September|"
    r"October|November|December|20\d\d)|before 20\d\d|after 20\d\d|"
    r"in 20\d\d you|currently in 20\d\d)\b", re.I)


# --- T52: runtime-portability lints ------------------------------------------
# Codex and Antigravity parse frontmatter with a strict YAML parser and
# silently DROP a skill whose frontmatter is invalid; Claude tolerates it.
# `parse_frontmatter` below is deliberately naive, so it cannot catch this —
# `frontmatter_yaml_errors` does. PyYAML is used when importable (it is not
# installed in CI — validate.yml is stdlib-only), and a stdlib structural
# checker ALWAYS runs so local and CI verdicts agree on the common failure
# classes (orphan indented keys under a scalar, duplicate keys, unterminated
# quotes, unquoted `: ` in a plain scalar).
try:
    import yaml as _yaml  # optional; never required
except Exception:  # pragma: no cover - depends on environment
    _yaml = None

# Trigger phrase that must appear early in `description` (T52 advisory; T53
# tightens). Codex truncates descriptions to ~110 chars at our library size
# and neither Codex nor Antigravity reads `when_to_use`.
DESC_TRIGGER_WINDOW = 110
DESC_TRIGGER_RE = re.compile(r"\b(use when|use for|use this|use to|use on|use before|use after|when)\b", re.I)
# Session /loop tasks expire after 7 days, so an interval >= 7d never fires.
LOOP_MAX_SECONDS = 7 * 86400
LOOP_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 7 * 86400}
# Hyphenated Claude Code built-in / sibling-plugin slash commands that are
# legitimately referenced as `/name` and are not skills in this library.
BUILTIN_SLASH = {
    "add-dir", "pr-comments", "release-notes", "output-style", "install-github-app",
    "terminal-setup", "privacy-settings", "code-review", "fewer-permission-prompts",
    "skill-doctor", "update-config", "tri-lane", "security-review",
}
KEBAB = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+"
# Currency (feeds T59): `metadata.verified: YYYY-MM-DD` on every skill. LOW
# when absent or older than VERIFIED_STALE_DAYS; HIGH for client-facing
# regulated skills older than VERIFIED_STALE_DAYS_STRICT. Advisory-only
# (no score effect, never fails) until STALENESS_ENFORCED flips — no skill
# carries the field yet (Wave 5 T53/T59 add it).
STALENESS_ENFORCED = False
VERIFIED_STALE_DAYS = 180
VERIFIED_STALE_DAYS_STRICT = 365
STRICT_CURRENCY_DOMAINS = {"tax", "legal"}
STRICT_CURRENCY_SKILLS = {"compliance-architect", "qsbs-compliance"}


def _split_frontmatter_raw(text):
    """Return (raw_frontmatter, error) using the same `---` delimiting that
    Codex/agy use: an opening `---` line and a closing `---` line."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None  # no frontmatter; other checks report missing fields
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), None
    return None, "frontmatter opened with `---` but never closed"


def _stdlib_yaml_errors(raw):
    """Minimal strict checker for the flat frontmatter subset this library
    uses. Not a YAML parser — it flags the structures a strict parser rejects."""
    errs = []
    seen = set()
    # state of the last top-level key: 'open' (empty value -> nested block
    # allowed), 'block' (| or > scalar), 'quoted' (multi-line quoted scalar
    # still open), 'flow' (multi-line [..]/{..}), or 'scalar' (closed).
    state, quote_ch, flow_depth = None, None, 0
    for ln, line in enumerate(raw.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indented = line[0] in " \t"
        if state == "quoted":
            if quote_ch in line:
                state = "scalar"
            continue
        if state == "flow":
            flow_depth += line.count("[") + line.count("{") - line.count("]") - line.count("}")
            if flow_depth <= 0:
                state = "scalar"
            continue
        if indented:
            if state in ("open", "block"):
                continue
            errs.append(f"line {ln}: indented `{line.strip()[:40]}` under a scalar value "
                        f"(orphan key — strict YAML parsers reject the whole frontmatter)")
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):(?:\s+(.*)|\s*)$", line)
        if not m:
            errs.append(f"line {ln}: `{line.strip()[:40]}` is not a `key: value` pair")
            state = "scalar"
            continue
        key, val = m.group(1), (m.group(2) or "").rstrip()
        if key in seen:
            errs.append(f"line {ln}: duplicate key `{key}`")
        seen.add(key)
        if not val:
            state = "open"
        elif re.match(r"^[|>][+-]?\d*$", val):
            state = "block"
        elif val[0] in "\"'":
            q = val[0]
            rest = val[1:]
            if q == '"':
                rest = re.sub(r'\\.', "", rest)
                close = rest.find('"')
            else:
                close = rest.replace("''", "").find("'")
                rest = rest.replace("''", "")
            if close == -1:
                state, quote_ch = "quoted", q
            else:
                tail = rest[close + 1:].strip()
                if tail and not tail.startswith("#"):
                    errs.append(f"line {ln}: `{key}` has text after its closing quote")
                state = "scalar"
        elif val[0] in "[{":
            flow_depth = val.count("[") + val.count("{") - val.count("]") - val.count("}")
            state = "flow" if flow_depth > 0 else "scalar"
        else:
            if val[0] in "@`%":
                errs.append(f"line {ln}: `{key}` plain value starts with reserved `{val[0]}` — quote it")
            elif re.search(r":\s", val) or val.endswith(":"):
                errs.append(f"line {ln}: `{key}` unquoted value contains `: ` — quote it")
            state = "scalar"
    if state == "quoted":
        errs.append("unterminated quoted value")
    return errs


def frontmatter_yaml_errors(text, force_stdlib=False):
    """Strict-parse errors for a file's frontmatter (empty list = valid)."""
    raw, err = _split_frontmatter_raw(text)
    if err:
        return [err]
    if raw is None:
        return []
    errs = _stdlib_yaml_errors(raw)
    if _yaml is not None and not force_stdlib:
        try:
            data = _yaml.safe_load(raw)
            if data is not None and not isinstance(data, dict):
                errs.append("frontmatter is not a mapping")
            elif isinstance(data, dict):
                for k in ("name", "description", "when_to_use", "argument-hint"):
                    if k in data and data[k] is not None and not isinstance(data[k], str):
                        errs.append(f"`{k}` parses as {type(data[k]).__name__}, not a string — quote it")
        except Exception as e:  # yaml.YAMLError and friends
            msg = " ".join(str(e).split())[:160]
            if not errs:  # stdlib checker missed it; report the parser's view
                errs.append(f"PyYAML: {msg}")
    return errs


_NAME_SETS = None


def name_sets():
    """Known names for cross-reference resolution (cached)."""
    global _NAME_SETS
    if _NAME_SETS is None:
        _NAME_SETS = {
            "skills": {p.parent.name for p in SKILLS_DIR.rglob("SKILL.md")},
            "agents": {p.stem for p in AGENTS_DIR.glob("*.md")},
            "workflows": {p.stem for p in (ROOT / "workflows").glob("*.js")},
            "styles": {p.name for p in (ROOT / "output-styles").iterdir() if p.is_dir()}
                      if (ROOT / "output-styles").is_dir() else set(),
            "domains": {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()},
        }
    return _NAME_SETS


def _line_of(text, pos):
    return text[:pos].count("\n") + 1


def cross_ref_issues(text, names, check_slash=True):
    """Broken /cure-product-engineering:<x>, `/x`, "see `x`", "`x` skill",
    "(use x)" routing references. Returns list of messages."""
    skills, agents = names["skills"], names["agents"]
    invocable = skills | names["workflows"]
    known_any = skills | agents | names["workflows"] | names["styles"]
    out = []

    def add(n, ln, why):
        out.append(f"line {ln}: references nonexistent {why} `{n}`")

    for m in re.finditer(r"/cure-product-engineering:([a-z0-9-]+)", text):
        n = m.group(1)
        if n not in invocable:
            add(n, _line_of(text, m.start()),
                "skill (agents are not slash commands)" if n in agents else "skill")
    if check_slash:
        # `/name` exactly (closing backtick or space follows; paths like
        # `/api-v1/users` are excluded by the lookahead).
        for m in re.finditer(r"`/(" + KEBAB + r")(?=[`\s])", text):
            n = m.group(1)
            if n not in invocable and n not in BUILTIN_SLASH:
                add(n, _line_of(text, m.start()),
                    "slash command (agents are not slash commands)" if n in agents else "slash command")
    for m in re.finditer(r"\bsee\s+(?:the\s+)?`/?(" + KEBAB + r")`", text, re.I):
        if m.group(1) not in known_any:
            add(m.group(1), _line_of(text, m.start()), "skill")
    for m in re.finditer(r"`/?(" + KEBAB + r")`\s*\(?when available", text, re.I):
        if m.group(1) not in skills:
            add(m.group(1), _line_of(text, m.start()), "skill")
    for m in re.finditer(r"`/?(" + KEBAB + r")`\s+(skill|agent)\b", text):
        n, kind = m.group(1), m.group(2)
        if n not in (skills if kind == "skill" else agents):
            add(n, _line_of(text, m.start()), kind)
    return out


def routing_ref_issues(meta):
    """`(use x)` / `(use x agent)` / `(use x, then y)` in description or
    when_to_use must name a real skill (or agent when suffixed `agent`)."""
    names = name_sets()
    out = []
    for grp in re.findall(r"\(use ([^)]*)\)", meta):
        for tok in re.split(r",|\bthen\b|\bor\b|\band\b", grp):
            tok = tok.strip()
            m = re.match(r"^(" + KEBAB + r"|[a-z0-9]+)(\s+agent)?(\s+when available)?$", tok)
            if not m:
                continue
            n, is_agent = m.group(1), bool(m.group(2))
            if is_agent:
                if n not in names["agents"]:
                    out.append(f"routes to nonexistent agent `{n}`")
            elif n not in names["skills"] and ("-" in n or m.group(3)):
                out.append(f"routes to nonexistent skill `{n}`" +
                           (" (\"when available\" placeholder)" if m.group(3) else ""))
    return out


def path_ref_issues(body, skill_dir):
    """Relative links / backticked reference|references|scripts paths must
    exist relative to the skill dir; `python3 skills/...` must exist from ROOT."""
    names = name_sets()
    out = []
    for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", body):
        u = m.group(1).split("#")[0]
        if not u or re.match(r"^[a-z][a-z0-9+.-]*:", u, re.I) or u.startswith("/"):
            continue
        if not (skill_dir / u).exists():
            out.append(f"line {_line_of(body, m.start())}: broken relative link `{u}`")
    # `reference/x.md`, `references/x`, `${CLAUDE_SKILL_DIR}/scripts/x.py`, `scripts/x.py`.
    # Must start the backtick span (so `irc-lookup/reference/x.md` and
    # `$STUDIO/scripts/x.py` are out of scope). Non-.py `scripts/*` paths are
    # files the skill GENERATES in the consumer repo, not bundled — skipped.
    for m in re.finditer(r"`(?:\$\{CLAUDE_SKILL_DIR\}/|\./)?((?:references?/[^`\s]+)|(?:scripts/[\w.-]+\.py))", body):
        u = m.group(1).rstrip(".,;:)")
        if "*" in u or "<" in u or "{" in u:
            continue
        if not (skill_dir / u).exists():
            out.append(f"line {_line_of(body, m.start())}: `{u}` does not exist in the skill dir")
    for m in re.finditer(r"\bpython3?\s+(skills/[^\s`'\"]+)", body):
        u = m.group(1)
        parts = u.split("/")
        if len(parts) < 2 or parts[1] not in names["domains"]:
            out.append(f"line {_line_of(body, m.start())}: stale script path `{u}` "
                       f"(missing domain folder: skills/<domain>/<name>/…)")
        elif not (ROOT / u).exists():
            out.append(f"line {_line_of(body, m.start())}: script path `{u}` does not exist")
    return out


def loop_interval_issues(body):
    out = []
    for m in re.finditer(r"/loop\s+(\d+)\s*([smhdw])\b", body):
        secs = int(m.group(1)) * LOOP_UNIT_SECONDS[m.group(2)]
        if secs >= LOOP_MAX_SECONDS:
            out.append(f"line {_line_of(body, m.start())}: `/loop {m.group(1)}{m.group(2)}` "
                       f"never fires — session loops expire after 7 days (use /schedule)")
    return out


def t42_skill_issues(text, fm, body, skill_dir):
    """All T52 checks for one SKILL.md. Returns list of (severity, msg)."""
    issues = []
    for e in frontmatter_yaml_errors(text):
        issues.append(("CRIT", f"invalid YAML frontmatter: {e} — Codex/Antigravity silently drop this skill (T52)"))
    for e in path_ref_issues(body, skill_dir):
        issues.append(("CRIT", f"{e} (T52)"))
    names = name_sets()
    for e in cross_ref_issues(body, names):
        issues.append(("CRIT", f"{e} (T52)"))
    for e in routing_ref_issues(fm.get("description", "") + " " + fm.get("when_to_use", "")):
        issues.append(("CRIT", f"frontmatter {e} (T52)"))
    for e in loop_interval_issues(body):
        issues.append(("CRIT", f"{e} (T52)"))
    desc = fm.get("description", "")
    if desc and not DESC_TRIGGER_RE.search(desc[:DESC_TRIGGER_WINDOW]):
        issues.append(("WARN", f"no trigger phrase ('Use when…') in first {DESC_TRIGGER_WINDOW} chars of "
                               f"description — Codex truncates there and ignores when_to_use (T52 advisory; T53)"))
    return issues


def parse_metadata(text):
    """Return the `metadata:` map (one level: block or inline flow) as
    {key: str}. parse_frontmatter is top-level only, so nested keys need this."""
    raw, _ = _split_frontmatter_raw(text)
    if not raw:
        return {}
    out, inside = {}, False
    for line in raw.splitlines():
        m = re.match(r"^metadata:\s*(.*)$", line)
        if m:
            val = m.group(1).strip()
            if val.startswith("{") and val.endswith("}"):
                for part in val[1:-1].split(","):
                    if ":" in part:
                        k, v = part.split(":", 1)
                        out[k.strip()] = v.strip().strip("'\"")
                return out
            inside = not val
            continue
        if inside:
            if line.strip() and line[0] not in " \t":
                break
            m = re.match(r"^\s+([A-Za-z0-9_.-]+):\s*(.*)$", line)
            if m and re.match(r"^\s{1,4}\S", line):
                out[m.group(1)] = m.group(2).strip().strip("'\"")
    return out


def currency_issues(text, skill_dir, today=None):
    """metadata.verified staleness (see STALENESS_ENFORCED)."""
    import datetime
    today = today or datetime.date.today()
    rel = skill_dir.relative_to(SKILLS_DIR).parts if SKILLS_DIR in skill_dir.parents else ()
    strict = bool(rel) and (rel[0] in STRICT_CURRENCY_DOMAINS or skill_dir.name in STRICT_CURRENCY_SKILLS)
    tag = "" if STALENESS_ENFORCED else " — advisory until enforced (T59)"
    v = parse_metadata(text).get("verified", "")
    if not v:
        return [("LOW", f"no `metadata.verified: YYYY-MM-DD` (currency tracking){tag}")]
    try:
        d = datetime.date.fromisoformat(v[:10])
    except ValueError:
        return [("LOW", f"`metadata.verified` is not an ISO date: `{v}`{tag}")]
    age = (today - d).days
    if strict and age > VERIFIED_STALE_DAYS_STRICT:
        return [("HIGH", f"`metadata.verified` {v} is {age}d old (>{VERIFIED_STALE_DAYS_STRICT}d; regulated content){tag}")]
    if age > VERIFIED_STALE_DAYS:
        return [("LOW", f"`metadata.verified` {v} is {age}d old (>{VERIFIED_STALE_DAYS}d){tag}")]
    return []


def is_t42_hard(issue):
    sev, msg = issue
    return sev == "CRIT" and msg.endswith("(T52)")


def parse_frontmatter(text):
    """Return (dict, body_str). Naive YAML: top-level `key: value` only."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw, body = parts[1], parts[2]
    fm = {}
    for line in raw.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            fm[key] = val.strip('"').strip("'")
    return fm, body


def score_skill(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)
    name = fm.get("name", "")
    desc = fm.get("description", "")
    when = fm.get("when_to_use", "")
    body_lines = len([l for l in body.splitlines()])
    issues = []
    score = 10.0

    # --- Hard spec: name ---
    if not name:
        issues.append(("CRIT", "missing `name`")); score -= 4
    else:
        if len(name) > 64:
            issues.append(("CRIT", f"name >64 chars ({len(name)})")); score -= 2
        if not NAME_RE.match(name):
            issues.append(("CRIT", "name not lowercase/numbers/hyphens")); score -= 2
        if "claude" in name.lower() or "anthropic" in name.lower():
            issues.append(("CRIT", "name uses reserved word")); score -= 3

    # --- Hard spec: description ---
    if not desc:
        issues.append(("CRIT", "missing/empty `description`")); score -= 4
    else:
        if len(desc) > 1024:
            issues.append(("HIGH", f"description >1024 chars ({len(desc)})")); score -= 1.5
        if FIRST_PERSON_RE.search(desc):
            issues.append(("MED", "description not third-person")); score -= 1
        # trigger/"when" signal must exist somewhere in discovery metadata
        if not re.search(r"\b(use when|when |for )\b", (desc + " " + when), re.I):
            issues.append(("MED", "no 'when to use' trigger in desc/when_to_use")); score -= 1

    # combined description listing truncation (1536 char cap)
    combined = len(desc) + len(when)
    if combined > 1536:
        issues.append(("HIGH", f"desc+when_to_use {combined} >1536 (trigger text truncated)")); score -= 1.5
    elif combined >= DESC_COMBINED_FAIL:
        issues.append(("MED", f"desc+when_to_use {combined} chars ≥{DESC_COMBINED_FAIL} (listing-budget policy: tighten)")); score -= 0.5
    elif combined > DESC_COMBINED_WARN:
        issues.append(("LOW", f"desc+when_to_use {combined} chars >{DESC_COMBINED_WARN} (listing-budget policy: consider tightening)")); score -= 0.1

    # --- effort value validity ---
    if fm.get("effort") and fm["effort"] not in VALID_EFFORT:
        issues.append(("HIGH", f"invalid effort `{fm['effort']}` (valid: {sorted(VALID_EFFORT)})")); score -= 1.0

    # --- dynamic-injection safety: !`cmd` blocks auto-execute before Claude
    # reads the skill, so they must be read-only and non-destructive.
    for cmd in re.findall(r"!`([^`]+)`", body):
        # fd redirects to /dev/null are read-only noise suppression, not writes
        stripped = re.sub(r"\d*>+\s*/dev/null", "", cmd)
        if re.search(r"\brm\b|\bmv\b|\bdd\b|>\s*\S|\btee\b|\bcurl\b|\bwget\b|git\s+(push|commit|reset|checkout)|\bnpm\s+(install|publish)\b|\bpip\s+install\b", stripped):
            issues.append(("CRIT", f"injected command is not read-only: `{cmd[:60]}`")); score -= 2.0

    # --- Best practice: body length ---
    if body_lines > 500:
        over = body_lines - 500
        pen = min(2.0, 0.5 + over / 400.0)
        issues.append(("HIGH", f"body {body_lines} lines >500 (progressive disclosure)")); score -= pen

    # --- Convention: argument-hint present (this repo standardizes on it) ---
    if "argument-hint" not in fm:
        issues.append(("LOW", "missing `argument-hint`")); score -= 0.5

    # --- allowed-tools misuse: claims read-only via allowed-tools ---
    # allowed-tools does NOT restrict; audit skills need disallowed-tools.
    audit_like = bool(re.search(r"audit|review|analy|assess|inspect", name))
    if "allowed-tools" in fm and "disallowed-tools" not in fm and audit_like:
        issues.append(("MED", "uses allowed-tools as a sandbox (it does NOT restrict; use disallowed-tools)")); score -= 0.5

    # --- Unknown/inert fields ---
    for k in fm:
        if k in SKILL_FIELDS or k in SKILL_FIELDS_INERT:
            continue
        issues.append(("LOW", f"unknown frontmatter field `{k}`")); score -= 0.25
    for k in (fm.keys() & SKILL_FIELDS_INERT):
        issues.append(("INFO", f"inert field `{k}` (not read by harness)"))

    # --- context value validity ---
    if "context" in fm and fm["context"] not in {"fork", "shared", "isolated"}:
        issues.append(("LOW", f"context='{fm['context']}' not a known value")); score -= 0.25

    # --- time-sensitive content ---
    if TIME_SENSITIVE_RE.search(body):
        issues.append(("LOW", "time-sensitive phrasing in body")); score -= 0.25

    # --- argument-substitution safety (T37): the harness substitutes bare
    # $0-$9 (and $ARGUMENTS) in skill bodies with the user's invocation args.
    # Literal dollars (currency, shell snippets) MUST be escaped \$N or they
    # are silently corrupted at load ($0.15 -> "<first-arg>.15"). Found live
    # by the statledger canary, 2026-08-14 (F-1, blocker).
    for m in re.finditer(r"(?<![\\$])\$(?=[0-9])", body):
        ln = body[:m.start()].count("\n") + 1
        issues.append(("HIGH", f"unescaped $N at body line {ln} — harness substitutes invocation args; escape as \\$ (T37)")); score -= 1.5
        break  # one flag per file is enough

    # --- guardrail honesty (T36): a skill that CLAIMS to be read-only must
    # enforce it via disallowed-tools. Prose is not a control. Advisory
    # recurring-mode guardrails (labeled "advisory") are exempt by design.
    claims_readonly = bool(re.search(r"read.only", desc, re.I)) or \
        bool(re.search(r"^Read-only skill", body, re.M))
    if claims_readonly and "disallowed-tools" not in fm:
        issues.append(("HIGH", "claims read-only but no disallowed-tools — prose is not a control (T36)")); score -= 1.5

    # --- prose coherence (T34): a list-introducing gather header must be
    # followed by at least one bullet. Catches the T20-migration corruption
    # class where "Additionally gather (domain-specific):" was left dangling
    # and spliced straight into unrelated body prose.
    body_lines_list = body.splitlines()
    for i, line in enumerate(body_lines_list):
        if re.match(r"^(Additionally gather|Before starting.*gather).*:\s*$", line.strip()):
            j = i + 1
            while j < len(body_lines_list) and not body_lines_list[j].strip():
                j += 1
            nxt = body_lines_list[j].strip() if j < len(body_lines_list) else ""
            if not re.match(r"^([-*]|\d+\.|`)", nxt):
                issues.append(("HIGH", f"dangling gather header at body line {i+1}: no bullet list follows (prose splice)")); score -= 1.5

    # --- T52 runtime-portability lints: strict YAML, path + cross-skill refs,
    # >=7d loops, stale script paths (CRIT, hard-fail); description trigger
    # position (WARN, advisory, no score effect).
    for iss in t42_skill_issues(text, fm, body, path.parent):
        issues.append(iss)
        if iss[0] == "CRIT":
            score -= 4 if iss[1].startswith("invalid YAML") else 1.0

    # --- currency: metadata.verified staleness (advisory until enforced) ---
    for iss in currency_issues(text, path.parent):
        issues.append(iss)
        if STALENESS_ENFORCED:
            score -= 1.5 if iss[0] == "HIGH" else 0.1

    # --- nested references (deeper than one level) heuristic ---
    md_links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", body)
    # Not penalized automatically (needs graph walk) — reported as info.

    return {
        "name": name or path.parent.name,
        "path": str(path.relative_to(ROOT)),
        "domain": path.relative_to(SKILLS_DIR).parts[0] if SKILLS_DIR in path.parents else "?",
        "body_lines": body_lines,
        "desc_len": len(desc),
        "combined_meta_len": combined,
        "score": round(max(0.0, score), 1),
        "issues": issues,
        "ref_count": len(md_links),
    }


def real_skill_index():
    """Map skill-name -> body line count, for preload validation."""
    idx = {}
    for p in SKILLS_DIR.rglob("SKILL.md"):
        fm, body = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        idx[fm.get("name", p.parent.name)] = len(body.splitlines())
        idx[p.parent.name] = len(body.splitlines())
    return idx


def score_agent(path, skill_idx):
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)
    name = fm.get("name", "")
    desc = fm.get("description", "")
    body_lines = len(body.splitlines())
    issues = []
    score = 10.0

    if not name:
        issues.append(("CRIT", "missing `name`")); score -= 4
    elif not NAME_RE.match(name):
        issues.append(("CRIT", "name not lowercase/hyphens")); score -= 2

    if not desc:
        issues.append(("CRIT", "missing `description`")); score -= 4
    else:
        # subagent description should describe WHEN to delegate
        if not re.search(r"\b(use|when|delegat|for )\b", desc, re.I):
            issues.append(("MED", "description lacks delegation trigger ('use when…')")); score -= 1
        if len(desc) < 40:
            issues.append(("LOW", "description very short (<40 chars) — weak auto-delegation")); score -= 0.5

    model = fm.get("model", "")
    if model and model not in VALID_MODELS and not model.startswith("claude-"):
        issues.append(("MED", f"model='{model}' not a valid value")); score -= 1

    if fm.get("effort") and fm["effort"] not in VALID_EFFORT:
        issues.append(("HIGH", f"invalid effort `{fm['effort']}` (valid: {sorted(VALID_EFFORT)})")); score -= 1.0
    if fm.get("isolation") and fm["isolation"] not in VALID_ISOLATION:
        issues.append(("HIGH", f"invalid isolation `{fm['isolation']}` (valid: {sorted(VALID_ISOLATION)})")); score -= 1.0

    if "tools" not in fm:
        issues.append(("LOW", "no `tools` (inherits ALL tools — consider least privilege)")); score -= 0.5

    # skills preload: validate references exist + weigh context cost
    if fm.get("skills"):
        refs = [s for s in re.split(r"[,\s]+", fm["skills"]) if s]
        preload_lines = 0
        for r in refs:
            if r not in skill_idx:
                issues.append(("CRIT", f"preloads non-existent skill '{r}' (broken reference)")); score -= 1.5
            else:
                preload_lines += skill_idx[r]
        if preload_lines > 1500:
            issues.append(("HIGH", f"preloads ~{preload_lines} lines into context every run (right-size with disable-model-invocation or fewer skills)")); score -= 1.0
        elif preload_lines > 800:
            issues.append(("MED", f"preloads ~{preload_lines} lines every run (policy: ≤~{PRELOAD_POLICY_LINES}; move to on-demand body references)")); score -= 0.5
        elif len(refs) >= 4:
            issues.append(("MED", f"preloads {len(refs)} full skills (~{preload_lines} lines) every run")); score -= 0.5

    for k in fm:
        if k not in AGENT_FIELDS:
            issues.append(("LOW", f"unknown frontmatter field `{k}`")); score -= 0.25

    # T52: strict YAML + slash-command references (agents are not slash commands)
    for e in frontmatter_yaml_errors(text):
        issues.append(("CRIT", f"invalid YAML frontmatter: {e} (T52)")); score -= 4
    for e in cross_ref_issues(body, name_sets(), check_slash=False):
        issues.append(("CRIT", f"{e} (T52)")); score -= 1.0

    return {
        "name": name or path.stem,
        "path": str(path.relative_to(ROOT)),
        "body_lines": body_lines,
        "score": round(max(0.0, score), 1),
        "issues": issues,
    }


def eval_deltas():
    """T30 calibration: measured on/off pass-rate delta per skill, from the
    newest skill-mode eval results. Empty dict if no eval data exists yet."""
    results_dir = ROOT / "evals" / "results"
    files = sorted(results_dir.glob("*-skill.json")) if results_dir.exists() else []
    if not files:
        return {}
    res = json.loads(files[-1].read_text())
    by_task = {}
    for k, v in res.get("summary", {}).items():
        task, _backend, arm = k.split("|")
        if v.get("n", 0) < 3:
            continue  # T39: single-rep results never drive calibration (t07 lesson)
        by_task.setdefault(task, {})[arm] = v["pass_rate"]
    idx_path = ROOT / "evals" / "index.json"
    if not idx_path.exists():
        return {}
    idx = json.loads(idx_path.read_text())["skill_to_tasks"]
    deltas = {}
    for skill, tids in idx.items():
        pairs = [(by_task[t]["on"], by_task[t]["off"]) for t in tids
                 if t in by_task and "on" in by_task[t] and "off" in by_task[t]]
        if pairs:
            deltas[skill] = sum(on - off for on, off in pairs) / len(pairs)
    return deltas


def collect():
    skills = sorted(SKILLS_DIR.rglob("SKILL.md"))
    agents = sorted(AGENTS_DIR.glob("*.md"))
    idx = real_skill_index()
    scored = [score_skill(p) for p in skills]
    # T30 calibration: conformance alone cannot exceed B when the skill has
    # eval coverage and its measured on/off delta is <= 0 — a skill that does
    # not demonstrably help is not an A skill, however clean its frontmatter.
    deltas = eval_deltas()
    for it in scored:
        d = deltas.get(it["name"])
        if d is not None:
            it["eval_delta"] = round(d, 3)
            if d <= 0 and it["score"] > 8.0:
                it["issues"].append(("HIGH", f"eval-calibrated: measured on/off delta {d:+.0%} <= 0 — score capped at 8.0"))
                it["score"] = 8.0
    return scored, [score_agent(p, idx) for p in agents]


def manifest_unlisted_domains():
    """Domains whose skills the plugin loader would silently skip.

    The Claude Code plugin loader only scans one level deep (<name>/SKILL.md),
    so every skills/<domain> directory must be listed in the plugin.json
    `skills` array or none of its skills register in consuming projects.
    """
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    declared = manifest.get("skills", [])
    if isinstance(declared, str):
        declared = [declared]
    declared = {Path(p).name for p in declared}
    domains = {p.relative_to(SKILLS_DIR).parts[0] for p in SKILLS_DIR.rglob("SKILL.md")}
    return sorted(domains - declared)


def flat_name_conflicts():
    """Skill `name` values that break a flattened export.

    Antigravity discovers skills only as a flat <root>/<name>/SKILL.md and keys
    off the directory name, so a name that disagrees with its directory, or a
    name reused across domains, silently resolves to the wrong skill there.
    Returns (mismatches, duplicates).
    """
    seen, mismatches, duplicates = {}, [], []
    for path in sorted(SKILLS_DIR.rglob("SKILL.md")):
        d = path.parent.name
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))[0] or {}
        name = (fm.get("name") or "").strip()
        if name and name != d:
            mismatches.append(f"skills/{path.parent.relative_to(SKILLS_DIR)} declares name: {name}")
        key = name or d
        if key in seen:
            duplicates.append(f"{key} in both {seen[key]} and {path.parent.relative_to(SKILLS_DIR).parts[0]}")
        else:
            seen[key] = path.parent.relative_to(SKILLS_DIR).parts[0]
    return mismatches, duplicates


def self_test():
    """T52 regression fixtures. Each BAD fixture must trip its lint; the GOOD
    fixture must trip none. Returns a process exit code."""
    import tempfile
    names = {"skills": {"finops", "security-review"}, "agents": {"code-reviewer"},
             "workflows": {"cure-code-audit"}, "styles": {"runbook"},
             "domains": {"business", "security"}}
    failures = []

    def expect(label, got, want):
        if bool(got) != want:
            failures.append(f"{label}: expected {'a hit' if want else 'no hit'}, got {got!r}")

    # 1. strict YAML — the stitch-design shape (orphan keys under a scalar)
    stitch = ('---\nname: x\ndescription: "d"\nargument-hint: "[a]"\n'
              '  tools: [stitch-mcp]\n  env: [KEY]\n---\nbody\n')
    expect("yaml/orphan-keys (stdlib)", frontmatter_yaml_errors(stitch, force_stdlib=True), True)
    expect("yaml/orphan-keys", frontmatter_yaml_errors(stitch), True)
    expect("yaml/duplicate-key", frontmatter_yaml_errors('---\nname: a\nname: b\n---\n', force_stdlib=True), True)
    expect("yaml/colon-in-plain", frontmatter_yaml_errors('---\ndescription: NOT for x: use y\n---\n', force_stdlib=True), True)
    expect("yaml/unclosed", frontmatter_yaml_errors('---\nname: a\n', force_stdlib=True), True)
    good_fm = ('---\nname: x\ndescription: "Does x. Use when y: z."\nhooks:\n  Stop:\n    - a\n'
               'paths: [a, b]\nwhen_to_use: >\n  folded\n  text\n---\n')
    expect("yaml/good (stdlib)", frontmatter_yaml_errors(good_fm, force_stdlib=True), False)
    expect("yaml/good", frontmatter_yaml_errors(good_fm), False)

    # 3. cross-skill references
    expect("xref/plugin-slash", cross_ref_issues("run /cure-product-engineering:nope", names), True)
    expect("xref/agent-as-slash", cross_ref_issues("`/code-reviewer` for x", names), True)
    expect("xref/see", cross_ref_issues("see `retirement-plan` and", names), True)
    expect("xref/when-available", cross_ref_issues("use `corp-finance-ops` (when available)", names), True)
    expect("xref/routing", routing_ref_issues_with(names, "NOT for NIL (use nil-contracts when available)"), True)
    expect("xref/routing-agent", routing_ref_issues_with(names, "NOT for rules (use rules-auditor agent)"), True)
    expect("xref/good", cross_ref_issues(
        "`/finops`, /cure-product-engineering:cure-code-audit, see `runbook` output style, "
        "the `security-review` skill, `/api-v1/users`, use `aria-live`, `/add-dir`", names), False)
    expect("xref/routing-good", routing_ref_issues_with(names, "(use finops, then security-review) (use code-reviewer agent) (use 1-2 max)"), False)

    # 4. loop interval
    expect("loop/1w", loop_interval_issues("/loop 1w /x"), True)
    expect("loop/7d", loop_interval_issues("/loop 7d /x"), True)
    expect("loop/1d", loop_interval_issues("/loop 1d /x and /loop 30m y and /loop.md"), False)

    # 2 + 5. paths (needs a real dir)
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "reference").mkdir()
        (d / "reference" / "ok.md").write_text("x")
        global _NAME_SETS
        saved, _NAME_SETS = _NAME_SETS, names
        try:
            expect("path/missing-ref", path_ref_issues("see `reference/missing.md`", d), True)
            expect("path/missing-link", path_ref_issues("[x](reference/nope.md)", d), True)
            expect("path/missing-py", path_ref_issues("run `scripts/gone.py`", d), True)
            expect("path/stale-python", path_ref_issues("python3 skills/finops/scripts/a.py", d), True)
            expect("path/good", path_ref_issues(
                "[x](reference/ok.md) `reference/ok.md` [u](https://e.com) [a](#top) "
                "`irc-lookup/reference/z.md` `scripts/deploy.sh` `$STUDIO/scripts/q.py`", d), False)
        finally:
            _NAME_SETS = saved

    # metadata map: must be valid YAML, parse one level, and drive currency
    import datetime
    meta_fm = ('---\nname: x\ndescription: "d"\nmetadata:\n  verified: 2026-09-23\n'
               '  requires-env: [A, B]\nargument-hint: "[a]"\n---\nbody\n')
    expect("metadata/yaml (stdlib)", frontmatter_yaml_errors(meta_fm, force_stdlib=True), False)
    expect("metadata/yaml", frontmatter_yaml_errors(meta_fm), False)
    if parse_metadata(meta_fm) != {"verified": "2026-09-23", "requires-env": "[A, B]"}:
        failures.append(f"metadata/parse: got {parse_metadata(meta_fm)!r}")
    if parse_metadata('---\nmetadata: {verified: 2026-01-01}\n---\n').get("verified") != "2026-01-01":
        failures.append("metadata/parse-flow")
    tax_dir, eng_dir = SKILLS_DIR / "tax" / "x", SKILLS_DIR / "engineering" / "x"
    fresh = datetime.date(2026, 10, 1)
    expect("currency/fresh", currency_issues(meta_fm, eng_dir, fresh), False)
    expect("currency/absent", currency_issues("---\nname: x\n---\n", eng_dir, fresh), True)
    old = datetime.date(2027, 10, 1)  # 373 days after verified
    sev = [s for s, _ in currency_issues(meta_fm, tax_dir, old)]
    if sev != ["HIGH"]:
        failures.append(f"currency/strict-stale: expected HIGH, got {sev}")
    sev = [s for s, _ in currency_issues(meta_fm, eng_dir, old)]
    if sev != ["LOW"]:
        failures.append(f"currency/stale: expected LOW, got {sev}")

    # 6. description trigger window (advisory)
    late = "x" * 120 + " Use when y"
    expect("trigger/late", not DESC_TRIGGER_RE.search(late[:DESC_TRIGGER_WINDOW]), True)
    expect("trigger/early", not DESC_TRIGGER_RE.search("Does x. Use when y."[:DESC_TRIGGER_WINDOW]), False)

    for f in failures:
        print(f"SELF-TEST FAIL: {f}", file=sys.stderr)
    print(f"T52 self-test: {'FAIL' if failures else 'OK'} "
          f"(PyYAML {'present' if _yaml else 'absent — stdlib checker only'})")
    return 1 if failures else 0


def routing_ref_issues_with(names, meta):
    global _NAME_SETS
    saved, _NAME_SETS = _NAME_SETS, names
    try:
        return routing_ref_issues(meta)
    finally:
        _NAME_SETS = saved


def grade(score):
    if score >= 9: return "A"
    if score >= 8: return "B"
    if score >= 7: return "C"
    if score >= 6: return "D"
    return "F"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--fail-under", type=float, default=None, help="exit 1 if mean score below threshold (CI gate)")
    ap.add_argument("--min-item", type=float, default=None, help="exit 1 if any single item scores below threshold")
    ap.add_argument("--self-test", action="store_true",
                    help="run the T52 lint regression fixtures (no library scan) and exit")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())

    skills, agents = collect()
    all_items = skills + agents
    mean = round(sum(i["score"] for i in all_items) / len(all_items), 2) if all_items else 0
    skill_mean = round(sum(i["score"] for i in skills) / len(skills), 2) if skills else 0
    agent_mean = round(sum(i["score"] for i in agents) / len(agents), 2) if agents else 0

    if args.json:
        print(json.dumps({
            "summary": {"items": len(all_items), "mean": mean,
                        "skill_mean": skill_mean, "agent_mean": agent_mean},
            "skills": skills, "agents": agents,
        }, indent=2))
    else:
        print(f"\n{'='*70}\n  CURE LIBRARY AUDIT — scored against official Anthropic spec\n{'='*70}")
        print(f"  Skills: {len(skills)}  mean {skill_mean}/10   "
              f"Agents: {len(agents)}  mean {agent_mean}/10   "
              f"Library mean: {mean}/10 ({grade(mean)})\n")
        print("  Worst 15 items:")
        for it in sorted(all_items, key=lambda x: x["score"])[:15]:
            crit = sum(1 for s, _ in it["issues"] if s in ("CRIT", "HIGH"))
            print(f"    {it['score']:>4}/10 {grade(it['score'])}  {it['name']:<28} "
                  f"({crit} hard issues)")
        # domain rollup
        print("\n  By domain:")
        doms = {}
        for s in skills:
            doms.setdefault(s["domain"], []).append(s["score"])
        for d, vals in sorted(doms.items()):
            print(f"    {d:<14} {round(sum(vals)/len(vals),2):>5}/10  ({len(vals)} skills)")
        # aggregate issue frequency
        print("\n  Most common issues (library-wide):")
        freq = {}
        for it in all_items:
            for sev, msg in it["issues"]:
                key = re.sub(r"\d+", "N", msg)
                freq[key] = freq.get(key, 0) + 1
        for msg, n in sorted(freq.items(), key=lambda x: -x[1])[:12]:
            print(f"    {n:>3}x  {msg}")
        print()

    fail = False
    # T52: runtime-portability CRITs hard-fail regardless of score — a skill
    # that Codex/agy silently drop, or that routes to a skill that does not
    # exist, is broken however clean the rest of it is.
    hard = [(it["path"], msg) for it in all_items for sev, msg in it["issues"] if is_t42_hard((sev, msg))]
    for p in sorted(PERSONAS_DIR.glob("*.md")) if PERSONAS_DIR.is_dir() else []:
        ptext = p.read_text(encoding="utf-8", errors="replace")
        for e in frontmatter_yaml_errors(ptext):
            hard.append((str(p.relative_to(ROOT)), f"invalid YAML frontmatter: {e} (T52)"))
        for e in cross_ref_issues(parse_frontmatter(ptext)[1], name_sets(), check_slash=False):
            hard.append((str(p.relative_to(ROOT)), f"{e} (T52)"))
    for path, msg in hard:
        print(f"FAIL: {path}: {msg}", file=sys.stderr)
    if hard:
        fail = True
    mismatches, duplicates = flat_name_conflicts()
    for m in mismatches:
        print(f"FAIL: skill name must equal its directory name — {m}", file=sys.stderr)
    for d in duplicates:
        print(f"FAIL: duplicate skill name across domains — {d} "
              f"(a flattened export would silently overwrite one)", file=sys.stderr)
    if mismatches or duplicates:
        fail = True
    unlisted = manifest_unlisted_domains()
    if unlisted:
        print(f"FAIL: skills/{{{','.join(unlisted)}}} not in plugin.json `skills` array — "
              f"the plugin loader scans one level deep, so these domains will not load "
              f"in consuming projects", file=sys.stderr)
        fail = True
    if args.fail_under is not None and mean < args.fail_under:
        print(f"FAIL: library mean {mean} < {args.fail_under}", file=sys.stderr); fail = True
    if args.min_item is not None:
        low = [i for i in all_items if i["score"] < args.min_item]
        if low:
            print(f"FAIL: {len(low)} items below {args.min_item}", file=sys.stderr); fail = True
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
