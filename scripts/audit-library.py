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
    "disallowed-tools", "model", "context",
}
# Tolerated-but-non-functional skill fields (no penalty beyond a note)
SKILL_FIELDS_INERT = {"version", "compatibility"}

AGENT_FIELDS = {
    "name", "description", "tools", "disallowedTools", "model", "permissionMode",
    "maxTurns", "skills", "mcpServers", "hooks", "memory", "background",
    "effort", "color", "isolation",
}
VALID_MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
NAME_RE = re.compile(r"^[a-z0-9-]+$")
FIRST_PERSON_RE = re.compile(r"\b(I can|I will|I'll|you can use this|let me)\b", re.I)
TIME_SENSITIVE_RE = re.compile(
    r"\b(as of (?:January|February|March|April|May|June|July|August|September|"
    r"October|November|December|20\d\d)|before 20\d\d|after 20\d\d|"
    r"in 20\d\d you|currently in 20\d\d)\b", re.I)


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
        elif len(refs) >= 4:
            issues.append(("MED", f"preloads {len(refs)} full skills (~{preload_lines} lines) every run")); score -= 0.5

    for k in fm:
        if k not in AGENT_FIELDS:
            issues.append(("LOW", f"unknown frontmatter field `{k}`")); score -= 0.25

    return {
        "name": name or path.stem,
        "path": str(path.relative_to(ROOT)),
        "body_lines": body_lines,
        "score": round(max(0.0, score), 1),
        "issues": issues,
    }


def collect():
    skills = sorted(SKILLS_DIR.rglob("SKILL.md"))
    agents = sorted(AGENTS_DIR.glob("*.md"))
    idx = real_skill_index()
    return [score_skill(p) for p in skills], [score_agent(p, idx) for p in agents]


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
    args = ap.parse_args()

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
    if args.fail_under is not None and mean < args.fail_under:
        print(f"FAIL: library mean {mean} < {args.fail_under}", file=sys.stderr); fail = True
    if args.min_item is not None:
        low = [i for i in all_items if i["score"] < args.min_item]
        if low:
            print(f"FAIL: {len(low)} items below {args.min_item}", file=sys.stderr); fail = True
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
