#!/usr/bin/env python3
"""session-report.py — Session observability report (T38).

Reads ~/.cure/telemetry/sessions.jsonl (session_start / session_stop /
tool_failure events, written by quiet fail-open hooks on cold events only —
no hot-path tracing, per Token Economy rules) plus skill-usage.jsonl, and
answers: where is agent time going, which projects fail most, what does a
typical session use?

v1 is session-level, not per-tool tracing — deliberate. Upgrade path if this
proves insufficient: OTel-style spans, which need harness support, not hooks.

Stdlib only. --help / --json.
"""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

TDIR = Path.home() / ".cure" / "telemetry"


def load(name, days):
    rows, f = [], TDIR / name
    if not f.exists():
        return rows
    cutoff = datetime.now() - timedelta(days=days)
    for line in f.read_text().splitlines():
        try:
            r = json.loads(line)
            if datetime.fromisoformat(r["ts"]) >= cutoff:
                rows.append(r)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ev = load("sessions.jsonl", args.days)
    sk = load("skill-usage.jsonl", args.days)

    starts = Counter(r["project"] for r in ev if r["event"] == "session_start")
    fails = Counter()
    fail_tools = Counter()
    for r in ev:
        if r["event"] == "tool_failure":
            fails[r["project"]] += 1
            fail_tools[r.get("detail") or "unknown"] += 1
    skills_by_proj = Counter(r.get("project", "?") for r in sk)

    report = {
        "window_days": args.days,
        "sessions_by_project": dict(starts.most_common()),
        "tool_failures_by_project": dict(fails.most_common()),
        "failing_tools": dict(fail_tools.most_common(10)),
        "skill_invocations_by_project": dict(skills_by_proj.most_common()),
        "skills_per_session": {p: round(skills_by_proj[p] / starts[p], 1)
                               for p in starts if starts[p]},
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Sessions — trailing {args.days}d\n")
        print(f"{'project':<30}{'sessions':<10}{'failures':<10}{'skills':<8}{'skills/session'}")
        for p, n in starts.most_common():
            print(f"{p:<30}{n:<10}{fails.get(p,0):<10}{skills_by_proj.get(p,0):<8}"
                  f"{report['skills_per_session'].get(p, 0)}")
        if fail_tools:
            print("\nFailing tools:", ", ".join(f"{t}×{n}" for t, n in fail_tools.most_common(5)))
        if not ev:
            print("(no session events yet — hooks ship with the next plugin release; data accrues from then)")
    return 0


if __name__ == "__main__":
    main()
