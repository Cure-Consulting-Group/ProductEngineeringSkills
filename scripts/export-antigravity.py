#!/usr/bin/env python3
"""Export the skill library as a flat Antigravity (agy) plugin, and optionally install it.

Antigravity does not load our Claude manifest (its `skills` array of domain dirs is ignored:
0 skills load) and does not scan `skills/<domain>/<name>/`. This builds the flat layout agy
does load, at a gitignored path (default dist/antigravity/cure/), never committed:

  plugin.json                     {"name": "cure", ...}
  skills/<name>/                  whole skill dir (SKILL.md, reference(s)/, scripts/, assets/, ...)
  agents/<persona>/agent.md       personas as agy custom agents (frontmatter: name, description, skills)
  rules/cure-rule-<x>.md          path rules, `trigger: glob` + `globs`
  rules/cure-style-<x>.md         output styles, `trigger: model_decision`
  EXPORT-MANIFEST.json            source SHA, library version, counts, rewrite totals

SKILL.md transforms: fold `when_to_use` into `description` (description text stays first);
rewrite inline !`cmd` context lines into run-first prose (asserts 0 remain); keep
`disable-model-invocation` (agy honors it); prepend a runtime note for skills whose
`allowed-tools` / `disallowed-tools` / `context: fork` / `disable-model-invocation` do not
travel, unless the body already carries a READ-ONLY or DESTRUCTIVE block; rewrite references
to repo files that do not travel (docs/, rules/, shared/, agents/, hooks/) to GitHub URLs on
main; drop Claude-only frontmatter keys.

Usage:
  python3 scripts/export-antigravity.py                   # build into dist/antigravity/cure
  python3 scripts/export-antigravity.py --json            # build, machine-readable summary
  python3 scripts/export-antigravity.py --check-collisions # build + refuse on name clashes in $HOME
  python3 scripts/export-antigravity.py --install         # build + collisions + agy plugin validate/install
  HOME=/tmp/agy-home python3 scripts/export-antigravity.py --install   # throwaway home

Exit codes: 0 ok, 1 an invariant or collision check failed, 2 bad input / agy missing on --install.
Python stdlib only.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GITHUB = "https://github.com/Cure-Consulting-Group/ProductEngineeringSkills/blob/main/"
PLUGIN_NAME = "cure"
KEEP_KEYS = {"name", "description", "disable-model-invocation", "license", "compatibility", "metadata"}
NON_TRAVELLING = ("docs", "rules", "shared", "agents", "hooks")
INJECT = re.compile(r"!`([^`\n]+)`")
INJECT_NOTE = re.compile(r"Values are injected inline below;[^\n]*?(?:run the shown commands instead\.|\n[^\n]*?instead\.)")
REPO_REF = re.compile(r"(?<![\w/.:-])((?:\.\./)*)((?:%s)/[\w./-]*\w)" % "|".join(NON_TRAVELLING))
RULE_FILE_MAX = 24_000     # agy per-file cap (bytes), from the builtin agy-customizations guide
RULES_TOKEN_BUDGET = 20_000  # agy aggregate rules budget (tokens); estimated at 4 bytes/token


class ExportError(Exception):
    pass


def split_frontmatter(text: str, where: str):
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m:
        raise ExportError(f"{where}: no YAML frontmatter")
    return m.group(1), text[m.end():]


def parse_fields(fm: str) -> list:
    """Top-level keys in order as (key, raw_block_lines). Minimal YAML: a key at column 0 owns the
    indented/continuation lines after it. Enough for our frontmatter; no pyyaml."""
    out = []
    for line in fm.splitlines():
        km = re.match(r"^([A-Za-z_][\w-]*):(.*)$", line)
        if km:
            out.append([km.group(1), [line]])
        elif out:
            out[-1][1].append(line)
    return out


def scalar(lines: list) -> str:
    first = lines[0].split(":", 1)[1].strip()
    rest = [l.strip() for l in lines[1:] if l.strip()]
    if first in (">", ">-", "|", "|-", ">+", "|+"):
        return (" " if first.startswith(">") else "\n").join(rest)
    joined = " ".join([first] + rest)
    if joined.startswith('"'):
        try:
            return json.loads(joined)
        except ValueError:
            return joined.strip('"').replace('\\"', '"')
    if joined.startswith("'"):
        return joined[1:-1].replace("''", "'")
    return joined


def rewrite_injections(body: str) -> tuple:
    n = len(INJECT.findall(body))
    if not n:
        return body, 0
    body = INJECT_NOTE.sub("Antigravity does not execute inline context commands: run each command below "
                           "in the workspace root first and use its output.", body)
    body = INJECT.sub(lambda m: "run `" + m.group(1) + "`", body)
    first = body.find("run `")
    lead_in = re.search(r"run (these|the shown|each)( context)? commands?", body[max(0, first - 400):first], re.I)
    if not lead_in:  # block without a lead-in sentence that already says "run these first"
        para = body.rfind("\n\n", 0, first)
        insert = 0 if para < 0 else para + 2
        body = body[:insert] + ("Before Step 1, run each context command below in the workspace root and use "
                                "its output (Antigravity does not execute them inline).\n\n") + body[insert:]
    return body, n


def rewrite_repo_refs(body: str, skill_dir: Path) -> tuple:
    count = 0

    def sub(m):
        nonlocal count
        ups, rel = m.group(1), m.group(2)
        cand = (skill_dir / (ups + rel)).resolve() if ups else (REPO / rel)
        try:
            relpath = cand.relative_to(REPO)
        except ValueError:
            return m.group(0)
        if not cand.is_file() or str(relpath).startswith("skills/"):
            return m.group(0)  # consumer-project paths (docs/prd/) and in-skill files stay as written
        count += 1
        return GITHUB + str(relpath)
    return REPO_REF.sub(sub, body), count


def runtime_note(fields: dict, body: str) -> str:
    if re.search(r"READ-ONLY|DESTRUCTIVE|Advisory skill|Nothing enforces this", body):
        return ""
    notes = []
    if "disable-model-invocation" in fields:
        notes.append("**DESTRUCTIVE — confirm before each mutating step.** Only run when the user asked for "
                     "this skill by name; ask for explicit confirmation before every file write or command "
                     "that changes state.")
    if "disallowed-tools" in fields:
        notes.append("**READ-ONLY SKILL.** Produce analysis only: do not edit files and do not run mutating "
                     "commands. (Claude Code enforces this; here it is advisory.)")
    elif "allowed-tools" in fields:
        tools = scalar(fields["allowed-tools"]).strip("[]").replace('"', "")
        notes.append(f"**Tool scope.** Designed around: {tools}. Ask before using tools outside this set "
                     "or running commands that change state.")
    if "context" in fields and scalar(fields["context"]) == "fork":
        notes.append("**Runs inline here.** Claude Code forks this skill into a separate context; in "
                     "Antigravity it shares the conversation, so summarise findings instead of pasting "
                     "large file dumps.")
    return "".join(f"> {n}\n>\n" for n in notes)[:-3] + "\n\n" if notes else ""


def transform_skill(src: Path, dst: Path, stats: dict) -> str:
    text = (src / "SKILL.md").read_text(encoding="utf-8")
    fm, body = split_frontmatter(text, str(src))
    ordered = parse_fields(fm)
    fields = {k: v for k, v in ordered}
    name = scalar(fields.get("name", ["name:"]))
    if not name or name != src.name:
        raise ExportError(f"{src}: name {name!r} does not match directory")
    desc = scalar(fields.get("description", ["description:"]))
    if not desc:
        raise ExportError(f"{src}: empty description")
    wtu = scalar(fields["when_to_use"]) if "when_to_use" in fields else ""
    if wtu and wtu.lower().rstrip(".") not in desc.lower():
        desc = desc.rstrip() + ("" if desc.rstrip().endswith((".", "!", "?")) else ".") + " " + wtu
        stats["folded"] += 1
    body, n_inj = rewrite_injections(body)
    body, n_ref = rewrite_repo_refs(body, src)
    note = runtime_note(fields, body)
    if note:
        stats["guardrail_notes"] += 1
        h1 = re.search(r"^# .*\n", body, re.M)
        body = body[:h1.end()] + "\n" + note + body[h1.end():].lstrip("\n") if h1 else note + body
    if INJECT.search(body):
        raise ExportError(f"{src}: inline context command survived the rewrite")
    out = ["---", f"name: {name}", "description: " + json.dumps(desc, ensure_ascii=False)]
    for k, lines in ordered:
        if k in KEEP_KEYS and k not in ("name", "description"):
            out.extend(lines)
    stats["dropped_keys"].update(k for k, _ in ordered if k not in KEEP_KEYS and k != "when_to_use")
    (dst / "SKILL.md").write_text("\n".join(out) + "\n---\n" + body, encoding="utf-8")
    stats["injections"] += n_inj
    stats["repo_refs"] += n_ref
    return name


def export_personas(out: Path, skill_names: set) -> int:
    n = 0
    for p in sorted((REPO / "personas").glob("*.md")):
        fm, body = split_frontmatter(p.read_text(encoding="utf-8"), str(p))
        f = {k: v for k, v in parse_fields(fm)}
        name, desc = scalar(f["name"]), scalar(f["description"])
        loadout = re.search(r"^## Skill Loadout\n(.*?)(?=^## )", body, re.S | re.M)
        skills = []
        for tok in re.findall(r"[a-z][a-z0-9-]+", loadout.group(1) if loadout else ""):
            if tok in skill_names and tok not in skills:
                skills.append(tok)
        body = body.replace("## Agent Loadout", "## Agent Loadout (Claude Code subagents — not available in "
                            "Antigravity; do this work inline)", 1)
        d = out / "agents" / name
        d.mkdir(parents=True)
        fm_out = ["---", f"name: {name}", "description: " + json.dumps(desc, ensure_ascii=False), "skills:"]
        fm_out += [f"  - {s}" for s in skills]
        (d / "agent.md").write_text("\n".join(fm_out) + "\n---\n" + body, encoding="utf-8")
        n += 1
    return n


def export_rules(out: Path) -> dict:
    rd = out / "rules"
    rd.mkdir()
    written, total = 0, 0
    for p in sorted((REPO / "rules").glob("*.md")):
        fm, body = split_frontmatter(p.read_text(encoding="utf-8"), str(p))
        globs = re.findall(r'^\s*-\s*"?([^"\n]+?)"?\s*$', fm, re.M)
        text = (f"---\ntrigger: glob\ndescription: {json.dumps('Cure standards for ' + p.stem + ' files')}\n"
                f"globs: {json.dumps(','.join(globs))}\n---\n" + body)
        (rd / f"cure-rule-{p.stem}.md").write_text(text, encoding="utf-8")
        written += 1
        total += len(text.encode())
    for p in sorted((REPO / "output-styles").glob("*/output-style.md")):
        raw = p.read_text(encoding="utf-8")
        if raw.startswith("---\n"):
            fm, body = split_frontmatter(raw, str(p))
            desc = scalar(dict((k, v) for k, v in parse_fields(fm)).get("description", ["description:"]))
        else:
            body = raw
            lead = [l for l in raw.splitlines() if l.strip() and not l.startswith("#")]
            desc = lead[0].rstrip(":") if lead else p.parent.name
        text = (f"---\ntrigger: model_decision\ndescription: {json.dumps('Output style: ' + desc, ensure_ascii=False)}\n"
                "---\n" + body)
        (rd / f"cure-style-{p.parent.name}.md").write_text(text, encoding="utf-8")
        written += 1
        total += len(text.encode())
    big = [f.name for f in rd.iterdir() if f.stat().st_size > RULE_FILE_MAX]
    if big:
        raise ExportError(f"rule files over {RULE_FILE_MAX} bytes: {big}")
    if total // 4 > RULES_TOKEN_BUDGET:
        raise ExportError(f"rules total ~{total // 4} tokens exceeds the {RULES_TOKEN_BUDGET}-token agy budget")
    return {"rules": written, "rules_bytes": total}


def git_sha() -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True,
                              timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def build(out: Path) -> dict:
    if out.exists():
        if not (out / "EXPORT-MANIFEST.json").exists():
            raise ExportError(f"{out} exists and is not a previous export; refusing to delete it")
        shutil.rmtree(out)
    (out / "skills").mkdir(parents=True)
    version = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())["version"]
    stats = {"folded": 0, "injections": 0, "repo_refs": 0, "guardrail_notes": 0, "dropped_keys": set()}
    names = {}
    for src in sorted(REPO.glob("skills/*/*/SKILL.md")):
        sdir = src.parent
        if sdir.name in names:
            raise ExportError(f"duplicate skill name {sdir.name}: {names[sdir.name]} and {sdir}")
        names[sdir.name] = sdir
        dst = out / "skills" / sdir.name
        shutil.copytree(sdir, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "openai.yaml"))
        transform_skill(sdir, dst, stats)
    personas = export_personas(out, set(names))
    rules = export_rules(out)
    (out / "plugin.json").write_text(json.dumps({
        "name": PLUGIN_NAME, "version": version,
        "description": "Cure Consulting Group product engineering skill library (Antigravity export of "
                       f"cure-product-engineering {version}). Generated by scripts/export-antigravity.py; do not edit."},
        indent=2) + "\n")
    summary = {"out": str(out), "version": version, "source_sha": git_sha(), "skills": len(names),
               "agents": personas, **rules, "descriptions_folded": stats["folded"],
               "injections_rewritten": stats["injections"], "injections_remaining": 0,
               "repo_refs_rewritten": stats["repo_refs"], "guardrail_notes_added": stats["guardrail_notes"],
               "frontmatter_keys_dropped": sorted(stats["dropped_keys"]),
               "hidden_by_disable_model_invocation": sorted(
                   n for n, d in names.items() if re.search(r"^disable-model-invocation:\s*true", (d / "SKILL.md").read_text(), re.M))}
    (out / "EXPORT-MANIFEST.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def existing_names(home: Path, exclude_plugin: str) -> dict:
    """Skill and agent names already visible to agy under `home`, mapped to where they live."""
    g = home / ".gemini"
    found = {}
    roots = [g / "config" / "skills", g / "antigravity-cli" / "builtin" / "skills", g / "antigravity-cli" / "skills",
             g / "skills"]
    for plugins in (g / "antigravity-cli" / "plugins", g / "config" / "plugins"):
        if plugins.is_dir():
            for p in plugins.iterdir():
                if p.name != exclude_plugin:
                    roots += [p / "skills", p / "agents"]
    for r in roots:
        if r.is_dir():
            for d in r.iterdir():
                if d.is_dir():
                    found.setdefault(d.name, str(d))
    return found


def check_collisions(out: Path, home: Path) -> list:
    ours = [d.name for d in (out / "skills").iterdir()] + [d.name for d in (out / "agents").iterdir()]
    have = existing_names(home, PLUGIN_NAME)
    return [{"name": n, "existing": have[n]} for n in sorted(ours) if n in have]


def agy(args: list, timeout: int = 180) -> tuple:
    p = subprocess.run(["agy"] + args, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Export the skill library as a flat Antigravity plugin and optionally install it.")
    ap.add_argument("--out", default=str(REPO / "dist" / "antigravity" / PLUGIN_NAME), help="output dir (default dist/antigravity/cure, gitignored)")
    ap.add_argument("--check-collisions", action="store_true", help="refuse if a skill/agent name already exists under $HOME/.gemini")
    ap.add_argument("--install", action="store_true", help="build, check collisions, then `agy plugin validate` + `agy plugin install` (uses $HOME)")
    ap.add_argument("--json", action="store_true", help="machine-readable summary on stdout")
    a = ap.parse_args()
    out = Path(a.out).expanduser().resolve()
    try:
        summary = build(out)
    except (ExportError, OSError, ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    rc = 0
    if a.check_collisions or a.install:
        clashes = check_collisions(out, Path(os.environ.get("HOME", str(Path.home()))))
        summary["collisions"] = clashes
        if clashes:
            rc = 1
    if a.install and rc == 0:
        if not shutil.which("agy"):
            print("error: agy not on PATH", file=sys.stderr)
            return 2
        try:
            vrc, vout = agy(["plugin", "validate", str(out)])
            summary["validate"] = {"exit": vrc, "output": vout[-2000:]}
            if vrc == 0:
                irc, iout = agy(["plugin", "install", str(out)])
                summary["install"] = {"exit": irc, "output": iout[-2000:]}
                rc = 0 if irc == 0 else 1
            else:
                rc = 1
        except (OSError, subprocess.SubprocessError) as e:
            print(f"error: agy failed: {e}", file=sys.stderr)
            return 2
    if a.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"exported {summary['skills']} skills, {summary['agents']} agents, {summary['rules']} rules -> {out}")
        print(f"  injections rewritten {summary['injections_rewritten']} (0 remain); repo refs -> GitHub "
              f"{summary['repo_refs_rewritten']}; descriptions folded {summary['descriptions_folded']}; "
              f"runtime notes {summary['guardrail_notes_added']}")
        for c in summary.get("collisions", []):
            print(f"  COLLISION {c['name']} already at {c['existing']}")
        for k in ("validate", "install"):
            if k in summary:
                print(f"  agy plugin {k}: exit {summary[k]['exit']}\n    " + summary[k]["output"].replace("\n", "\n    ")[:1500])
    return rc


if __name__ == "__main__":
    sys.exit(main())
