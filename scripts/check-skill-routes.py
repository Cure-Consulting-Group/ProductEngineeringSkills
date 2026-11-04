#!/usr/bin/env python3
"""Check the T93 routing table (hooks/skill_routes.json) against every eval prompt.

Every route must name a real skill, compile, and match only prompts whose case is tagged with that
skill. A case with a `not-<skill>` grader (a boundary case) must never be routed to <skill>, and a
case tagged for one skill must not be routed to a different one. Prompts no route matches are fine:
the nudge is for skills the model measurably skips, not for every skill.

Usage:
    python3 scripts/check-skill-routes.py           # report, exit 1 on any wrong route
    python3 scripts/check-skill-routes.py --json

Exit: 0 clean, 1 a route misfires or names a missing skill, 2 bad table.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def guard():
    spec = importlib.util.spec_from_file_location("cure_guard", REPO / "hooks" / "cure_guard.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cases():
    for d in sorted((REPO / "plugin-evals").iterdir()):
        p = d / "prompt.md"
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
        if not m:
            continue
        tags = re.search(r"^tags:\s*\[(.*?)\]", m.group(1), re.M)
        tagset = {t.strip().strip("'\"") for t in tags.group(1).split(",")} if tags else set()
        banned = {g.stem[4:] for g in (d / "graders").glob("not-*.md")} if (d / "graders").is_dir() else set()
        yield d.name, m.group(2).strip(), tagset, banned


def main() -> int:
    ap = argparse.ArgumentParser(description="Check the skill-routing table against every eval prompt.")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        table = json.loads((REPO / "hooks" / "skill_routes.json").read_text())["routes"]
        for r in table:
            re.compile(r["when"]); r.get("unless") and re.compile(r["unless"])
    except (OSError, ValueError, KeyError, re.error) as err:
        print(f"error: bad routing table: {err}", file=sys.stderr)
        return 2
    skills = {p.parent.name for p in REPO.glob("skills/*/*/SKILL.md")}
    problems = [f"route names a missing skill: {r['skill']}" for r in table if r["skill"] not in skills]
    g = guard()
    hits, rows = {}, []
    for name, prompt, tags, banned in cases():
        hit = g.route_skill(prompt)
        skill = hit[0] if hit else None
        rows.append({"case": name, "routed": skill, "tags": sorted(tags), "banned": sorted(banned)})
        if skill:
            hits.setdefault(skill, []).append(name)
            if skill in banned:
                problems.append(f"{name}: routed to {skill}, which its not-{skill} grader forbids")
            elif skill not in tags:
                problems.append(f"{name}: routed to {skill}, but the case is for {', '.join(sorted(tags - {'routing', 'negative', 'ported'})) or '?'}")
    for r in table:
        if r["skill"] not in hits:
            problems.append(f"route {r['skill']} matches no eval prompt (add a case or drop the route)")
    if a.json:
        print(json.dumps({"routed": hits, "problems": problems, "cases": rows}, indent=2))
    else:
        for skill, names in sorted(hits.items()):
            print(f"{skill}: {', '.join(names)}")
        for p in problems:
            print(f"FAIL {p}")
        print(f"\nroutes: {len(table)}, cases routed: {sum(map(len, hits.values()))} of {len(rows)}, problems: {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
