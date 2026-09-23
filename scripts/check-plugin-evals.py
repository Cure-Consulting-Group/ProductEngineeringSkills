#!/usr/bin/env python3
"""check-plugin-evals.py — zero-cost structural check of the `claude plugin eval` suite (T60).

Validates every case under the manifest's eval dir (experimental.evals, default
plugin-evals/) without calling a model:

  - each case dir has prompt.md or case.yaml, and >=1 grader (graders/*.md)
  - prompt.md frontmatter keys are ones the CLI accepts (an unknown key is a
    load error at run time), and `tags` names at least one real skill
  - every grader has a known `type`; `tool_used: Skill` graders name a real skill
  - a case.yaml scaffold_script exists in the case dir

Also the Ring-0 helper used by scripts/release.sh:

  --changed-tags REF   print the space-separated skill tags that (a) changed
                       under skills/ since REF and (b) have at least one case.
                       Empty output = nothing covered changed.

Stdlib only. --help / --json.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT_KEYS = {"schema_version", "name", "description", "tags", "plugins", "runs", "expected_outcome",
               "model", "max_turns", "timeout_seconds", "allowed_tools", "append_system_prompt", "env"}
GRADER_TYPES = {"regex", "tool_used", "tool_order", "file_exists", "llm", "baseline"}
NON_SKILL_TAGS = {"ported", "routing", "negative", "substitution", "pilot"}


def eval_dir():
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    return ROOT / (manifest.get("experimental", {}).get("evals") or "evals")


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            out[km.group(1)] = km.group(2).strip()
    return out


def parse_list(v):
    v = (v or "").strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
    return [v] if v else []


def skill_names():
    return {p.parent.name for p in (ROOT / "skills").glob("*/*/SKILL.md")}


def cases(edir):
    for p in sorted(edir.iterdir()):
        if p.is_dir() and p.name not in ("results", "mocks") and ((p / "prompt.md").exists() or (p / "case.yaml").exists()):
            yield p


def check(edir):
    skills = skill_names()
    errors, summary = [], []
    for c in cases(edir):
        tags = []
        pm = c / "prompt.md"
        if pm.exists():
            fm = frontmatter(pm)
            if fm is None:
                fm = {}
            bad = set(fm) - PROMPT_KEYS
            if bad:
                errors.append(f"{c.name}: unknown prompt.md frontmatter key(s) {sorted(bad)}")
            tags = parse_list(fm.get("tags"))
            body = re.sub(r"^---\n.*?\n---\n?", "", pm.read_text(encoding="utf-8"), count=1, flags=re.S)
            if not body.strip():
                errors.append(f"{c.name}: prompt.md has an empty body")
        cy = c / "case.yaml"
        if cy.exists():
            text = cy.read_text(encoding="utf-8")
            if 'schema_version: "1.1"' not in text or not re.search(r"^name:\s*\S", text, re.M):
                errors.append(f"{c.name}: case.yaml needs schema_version \"1.1\" and name")
            sm = re.search(r"scaffold_script:\s*(\S+)", text)
            if sm and not (c / sm.group(1)).exists():
                errors.append(f"{c.name}: scaffold_script {sm.group(1)} missing")
        graders = sorted((c / "graders").glob("*.md")) if (c / "graders").is_dir() else []
        if not graders and not (cy.exists() and re.search(r"^graders:", cy.read_text(encoding="utf-8"), re.M)):
            errors.append(f"{c.name}: no graders")
        fired = []
        for g in graders:
            gfm = frontmatter(g) or {}
            if gfm.get("type") not in GRADER_TYPES:
                errors.append(f"{c.name}/{g.name}: unknown grader type {gfm.get('type')!r}")
            if gfm.get("type") == "tool_used" and gfm.get("tool") == "Skill":
                sm = re.search(r"\?([a-z0-9-]+)\"", gfm.get("input_match", ""))
                if sm:
                    fired.append(sm.group(1))
                    if sm.group(1) not in skills and sm.group(1) != "subst-fixture":
                        errors.append(f"{c.name}/{g.name}: Skill grader names unknown skill {sm.group(1)!r}")
        skill_tags = [t for t in tags if t not in NON_SKILL_TAGS]
        for t in skill_tags:
            if t not in skills:
                errors.append(f"{c.name}: tag {t!r} is not a skill name")
        summary.append({"case": c.name, "tags": tags, "graders": len(graders), "skill_graders": fired})
    return errors, summary


def changed_tags(ref, summary):
    try:
        out = subprocess.run(["git", "diff", "--name-only", ref, "--", "skills/"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        sys.exit(f"git diff failed: {e.stderr.strip()}")
    changed = {Path(p).parts[2] for p in out.splitlines() if len(Path(p).parts) >= 4}
    covered = {t for s in summary for t in s["tags"] if t not in NON_SKILL_TAGS}
    return sorted(changed & covered)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--changed-tags", metavar="REF", help="print covered skill tags changed vs REF (Ring 0)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    edir = eval_dir()
    if not edir.is_dir():
        sys.exit(f"eval dir {edir} not found")
    errors, summary = check(edir)
    if args.changed_tags:
        if errors:
            sys.exit("plugin-evals invalid:\n  " + "\n  ".join(errors))
        print(" ".join(changed_tags(args.changed_tags, summary)))
        return
    covered = sorted({t for s in summary for t in s["tags"] if t not in NON_SKILL_TAGS})
    if args.json:
        print(json.dumps({"eval_dir": str(edir.relative_to(ROOT)), "cases": len(summary),
                          "skills_covered": covered, "errors": errors}, indent=2))
    else:
        for e in errors:
            print(f"FAIL: {e}")
        print(f"{len(summary)} cases, {len(covered)} skills covered, {len(errors)} error(s) in {edir.relative_to(ROOT)}/")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
