#!/usr/bin/env python3
"""usage-report.py — Skill invocation telemetry report (T35).

Reads ~/.cure/telemetry/skill-usage.jsonl (written by the PreToolUse Skill
hook: local, append-only, no network) and reports per-skill invocation counts,
per-project spread, the never-invoked list, and a trailing-90-day view.

The never-invoked list feeds the PRUNE MANDATE: a library skill with zero
invocations across the fleet for 2 consecutive quarters is auto-filed as a
deprecation candidate at the next wave — keeping it requires a written why.

Stdlib only. --help / --json.
"""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = Path.home() / ".cure" / "telemetry" / "skill-usage.jsonl"


def library_skills():
    return sorted(p.parent.name for p in (ROOT / "skills").rglob("SKILL.md"))


def load(days=None):
    rows = []
    if not LOG.exists():
        return rows
    cutoff = datetime.now() - timedelta(days=days) if days else None
    for line in LOG.read_text().splitlines():
        try:
            r = json.loads(line)
            if cutoff and datetime.fromisoformat(r["ts"]) < cutoff:
                continue
            rows.append(r)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue  # a corrupt line never breaks the report
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=int, default=90, help="trailing window (default 90)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = load(args.days)
    lib = library_skills()
    # normalize plugin-prefixed invocations to bare names
    counts = Counter(r["skill"].split(":")[-1] for r in rows)
    projects = defaultdict(set)
    for r in rows:
        projects[r["skill"].split(":")[-1]].add(r.get("project", "?"))
    used = {s: c for s, c in counts.items() if s in lib}
    never = [s for s in lib if s not in counts]

    report = {
        "window_days": args.days,
        "total_invocations": len(rows),
        "skills_used": len(used),
        "skills_total": len(lib),
        "top": counts.most_common(15),
        "per_skill": {s: {"count": c, "projects": sorted(projects[s])}
                      for s, c in sorted(used.items(), key=lambda x: -x[1])},
        "never_invoked": never,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Skill usage — trailing {args.days}d: {len(rows)} invocations, "
              f"{len(used)}/{len(lib)} library skills used\n")
        for s, c in report["top"]:
            print(f"  {c:>5}  {s}  ({len(projects[s])} project(s))")
        print(f"\nNever invoked ({len(never)}): deprecation candidates after 2 dark quarters")
        for s in never[:20]:
            print(f"  - {s}")
        if len(never) > 20:
            print(f"  ... and {len(never)-20} more")
    return 0


if __name__ == "__main__":
    main()
