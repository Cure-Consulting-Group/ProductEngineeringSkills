#!/usr/bin/env python3
"""export-portable.py — package the skills for claude.ai uploads and the Claude API Skills endpoint (T88).

Claude Code reads keys those surfaces reject. Per code.claude.com/docs/en/skills ("Using skill
frontmatter outside Claude Code") and platform.claude.com/docs (Agent Skills overview, skills guide),
verified 2026-11-04, a SKILL.md uploaded to claude.ai or POST /v1/skills may carry only
`name`, `description`, `license`, `compatibility`, `metadata` (string to string) and `allowed-tools`;
any other key is an upload error. `name` is lowercase/digits/hyphens, at most 64 chars, without
"claude" or "anthropic"; `description` is non-empty, at most 1,024 chars, with no XML tags; an
upload is at most 30 MB; the zip's root is a folder named after the skill, holding SKILL.md.

For each skill this writes dist/portable/<name>/ and dist/portable/zips/<name>.zip:
  * frontmatter: name, description (with `when_to_use` folded in when it fits the 1,024 cap),
    license, metadata (scalars only, stringified). Claude Code's `allowed-tools` grammar
    ("Bash(git log:*)") is not the open spec's, so it is dropped, not translated.
  * every other file in the skill folder (references, scripts, fixtures, templates), minus
    Codex sidecars (agents/openai.yaml) and caches.
  * a report of what does not travel: Claude Code-only body features (the plugin's `cure-*`
    commands on PATH, ${CLAUDE_PLUGIN_ROOT}, $ARGUMENTS) and skills that rely on
    disable-model-invocation (there is no such control on claude.ai or the API).

Usage:
    python3 scripts/export-portable.py                    # all skills -> dist/portable
    python3 scripts/export-portable.py --only finops      # one skill
    python3 scripts/export-portable.py --check --json     # validate only, write nothing

Exit: 0 ok, 1 a skill cannot be made portable (named in the report), 2 bad input.
"""
import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PORTABLE_KEYS = ("name", "description", "license", "compatibility", "metadata")
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
DESC_MAX = 1024
UPLOAD_MAX = 30 * 1024 * 1024
SKIP_PARTS = {"__pycache__", ".DS_Store"}
SKIP_FILES = {Path("agents/openai.yaml")}
CC_ONLY = [
    (re.compile(r"\$\{?CLAUDE_PLUGIN_ROOT\}?"), "${CLAUDE_PLUGIN_ROOT} (plugin install path)"),
    (re.compile(r"\$ARGUMENTS\b"), "$ARGUMENTS substitution"),
    (re.compile(r"(?<![\w/-])cure-[a-z-]+(?= --|\s+--| \S+\.csv)"), "a `cure-*` command the plugin puts on PATH"),
    (re.compile(r"/cure-product-engineering:"), "a Claude Code slash-command reference"),
]


def split(text):
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    return (m.group(1), text[m.end():]) if m else (None, text)


def fields(fm):
    out = []
    for line in fm.splitlines():
        km = re.match(r"^([A-Za-z_][\w-]*):(.*)$", line)
        if km:
            out.append([km.group(1), [line]])
        elif out:
            out[-1][1].append(line)
    return {k: v for k, v in out}


def scalar(lines):
    first = lines[0].split(":", 1)[1].strip()
    rest = [l.strip() for l in lines[1:] if l.strip()]
    if first in (">", ">-", "|", "|-", ">+", "|+"):
        return (" " if first.startswith(">") else "\n").join(rest)
    v = " ".join([first] + rest).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def metadata(lines):
    """Indented `key: value` pairs under metadata:, scalars only, as strings."""
    out = {}
    for l in lines[1:]:
        m = re.match(r"^\s+([A-Za-z_][\w.-]*):\s*(.+?)\s*$", l)
        if m and not m.group(2).startswith(("[", "{", "|", ">")):
            out[m.group(1)] = m.group(2).strip("\"'")
    return out


def q(s):
    return json.dumps(s, ensure_ascii=False)


def export_skill(skill_md: Path, out_root: Path, write: bool) -> dict:
    src = skill_md.parent
    rel = str(src.relative_to(REPO))
    text = skill_md.read_text(encoding="utf-8")
    fm, body = split(text)
    rep = {"skill": src.name, "path": rel, "errors": [], "warnings": [], "dropped_keys": []}
    if fm is None:
        rep["errors"].append("no YAML frontmatter")
        return rep
    f = fields(fm)
    name = scalar(f["name"]) if "name" in f else ""
    desc = scalar(f["description"]) if "description" in f else ""
    when = scalar(f["when_to_use"]) if "when_to_use" in f else ""
    if not NAME_RE.match(name or ""):
        rep["errors"].append(f"name '{name}' is not lowercase letters, digits and hyphens (1-64)")
    if re.search(r"claude|anthropic", name or ""):
        rep["errors"].append(f"name '{name}' contains a reserved word")
    if name != src.name:
        rep["errors"].append(f"name '{name}' does not match its folder '{src.name}'")
    folded = f"{desc} {when}".strip() if when else desc
    if len(folded) <= DESC_MAX:
        desc = folded
    else:
        rep["warnings"].append(f"when_to_use not folded: description + when_to_use is {len(folded)} chars (cap {DESC_MAX})")
    if not desc or len(desc) > DESC_MAX:
        rep["errors"].append(f"description is {len(desc)} chars (need 1-{DESC_MAX})")
    if re.search(r"<[A-Za-z/][^>]*>", desc):
        rep["errors"].append("description contains an XML/HTML tag")
    rep["dropped_keys"] = sorted(k for k in f if k not in PORTABLE_KEYS)
    if "disable-model-invocation" in f and scalar(f["disable-model-invocation"]).lower() == "true":
        rep["warnings"].append("disable-model-invocation: true has no equivalent there; the skill can be chosen automatically")
    for pat, what in CC_ONLY:
        if pat.search(body):
            rep["warnings"].append(f"body uses {what}")

    lines = ["---", f"name: {name}", f"description: {q(desc)}"]
    if "license" in f:
        lines.append(f"license: {q(scalar(f['license']))}")
    if "compatibility" in f:
        lines.append(f"compatibility: {q(scalar(f['compatibility'])[:500])}")
    meta = metadata(f["metadata"]) if "metadata" in f else {}
    meta["source"] = f"Cure-Consulting-Group/ProductEngineeringSkills {rel}"
    lines.append("metadata:")
    lines += [f"  {k}: {q(str(v))}" for k, v in sorted(meta.items())]
    lines.append("---")
    portable = "\n".join(lines) + "\n" + body

    files = [p for p in sorted(src.rglob("*")) if p.is_file() and p != skill_md
             and not (set(p.relative_to(src).parts) & SKIP_PARTS) and p.relative_to(src) not in SKIP_FILES]
    size = len(portable.encode("utf-8")) + sum(p.stat().st_size for p in files)
    rep["files"], rep["bytes"] = len(files) + 1, size
    if size > UPLOAD_MAX:
        rep["errors"].append(f"{size} bytes exceeds the 30 MB upload limit")
    if rep["errors"] or not write:
        return rep

    dst = out_root / name
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    (dst / "SKILL.md").write_text(portable, encoding="utf-8")
    for p in files:
        target = dst / p.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
    zips = out_root / "zips"
    zips.mkdir(exist_ok=True)
    with zipfile.ZipFile(zips / f"{name}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(dst.rglob("*")):
            if p.is_file():
                z.write(p, Path(name) / p.relative_to(dst))
    rep["zip"] = str((zips / f"{name}.zip").relative_to(REPO))
    return rep


def main() -> int:
    ap = argparse.ArgumentParser(description="Package skills for claude.ai uploads and the Claude API Skills endpoint (portable keys only).")
    ap.add_argument("--out", default=str(REPO / "dist" / "portable"), help="output folder (default dist/portable, gitignored)")
    ap.add_argument("--only", help="one skill by name")
    ap.add_argument("--check", action="store_true", help="validate only; write nothing")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    skills = sorted(REPO.glob("skills/*/*/SKILL.md"))
    if a.only:
        skills = [s for s in skills if s.parent.name == a.only]
        if not skills:
            print(f"error: no skill named {a.only}", file=sys.stderr)
            return 2
    if not a.check:
        out.mkdir(parents=True, exist_ok=True)
    reports = [export_skill(s, out, not a.check) for s in skills]
    bad = [r for r in reports if r["errors"]]
    warned = [r for r in reports if r["warnings"]]
    if a.json:
        print(json.dumps({"skills": reports, "failed": len(bad), "with_warnings": len(warned), "out": str(out)}, indent=2))
    else:
        for r in reports:
            for e in r["errors"]:
                print(f"FAIL {r['skill']}: {e}")
        for r in warned:
            print(f"warn {r['skill']}: " + "; ".join(r["warnings"]))
        print(f"\nportable: {len(reports) - len(bad)} ok, {len(bad)} failed, {len(warned)} with warnings"
              + ("" if a.check else f" -> {out.relative_to(REPO) if out.is_relative_to(REPO) else out}"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
