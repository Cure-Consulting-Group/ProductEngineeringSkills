#!/usr/bin/env python3
"""lane-route: suggest a lane model and effort for a task from the capability table (models.json).

Shadow mode by design: the suggestion is written to the task's run dir as route-suggestion.json and
picked up by `lane-log end`, so the log records what the table would have chosen next to what the
architect actually chose. The architect still declares the route. Activate the table only after the
shadow log shows it would have done better.

Inputs: role, kind, risk flags, attempt number, expected diff size. The table's public-benchmark prior
is overridden by the project's own benchmark.jsonl once a model has `own_data_threshold` tasks of that
kind with a lower rework or higher precision. Python stdlib only.

Examples:
  python3 lane-route.py suggest --role implement --kind payments --risk payments,concurrency --task a4
  python3 lane-route.py suggest --role review --kind android --risk auth
  python3 lane-route.py table
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TABLE = HERE.parent / "models.json"


def load_table() -> dict:
    return json.loads(TABLE.read_text())


def git_common_dir() -> Path | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, timeout=30).stdout.strip()
        return Path(out).resolve() if out else None
    except Exception:
        return None


def own_data(kind: str, lane: str) -> dict:
    """Count logged tasks for this lane+kind and summarise rework and confirmed findings."""
    gcd = git_common_dir()
    log = (gcd / "tri-lane" / "benchmark.jsonl") if gcd else None
    if not log or not log.exists():
        return {"tasks": 0}
    n, rework, conf = 0, 0, 0
    for line in log.read_text().splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if (r.get("kind") or "") != kind or lane.split(" ")[0] not in (r.get("lane") or ""):
            continue
        n += 1
        rework += int(r.get("rework") or 0)
        conf += sum(int(v.get("confirmed") or 0) for v in (r.get("findings") or {}).values())
    return {"tasks": n, "rework_mean": round(rework / n, 2) if n else None, "confirmed_mean": round(conf / n, 2) if n else None}


def match(rule: dict, role: str, kind: str, risk: set, diff_lines: int) -> bool:
    if rule["role"] != role:
        return False
    if rule["kinds"] != ["*"] and kind not in rule["kinds"]:
        return False
    if rule["risk"] and not (risk & set(rule["risk"])):
        return False
    if not rule["risk"] and risk and rule["role"] == "implement" and rule.get("kinds") == ["*"]:
        return False
    if rule.get("min_diff_lines") and diff_lines < rule["min_diff_lines"]:
        return False
    return True


def suggest(role: str, kind: str, risk: set, attempt: int, diff_lines: int) -> dict:
    t = load_table()
    if role == "implement" and attempt >= 3:
        e = t["escalation"]["attempt_3"]
        return {"rule": "escalation.attempt_3", **e, "shadow": False}
    if role == "implement" and attempt == 2:
        e = t["escalation"]["attempt_2"]
        return {"rule": "escalation.attempt_2", **e, "shadow": False}
    # risk rules first, then size, then kind, then defaults: order in the table encodes precedence for ties
    candidates = [r for r in t["rules"] if match(r, role, kind, risk, diff_lines)]
    if not candidates:
        return {"rule": None, "lane": None, "effort": None, "basis": "no rule matched; architect decides", "shadow": False}
    def score(r):
        return (1 if r["risk"] else 0, 1 if r.get("min_diff_lines") else 0, 0 if r["kinds"] == ["*"] else 1)
    best = sorted(candidates, key=score, reverse=True)[0]
    out = {"rule": best["id"], "lane": best["lane"], "effort": best["effort"], "basis": best["basis"], "shadow": bool(best.get("shadow"))}
    od = own_data(kind, best["lane"])
    out["own_data"] = od
    cn = canary_data(kind, best["lane"], role)
    out["canary"] = cn
    posterior = od.get("tasks", 0) >= best.get("own_data_threshold", 5) or cn.get("runs", 0) >= 2
    out["prior_or_posterior"] = "posterior" if posterior else "prior"
    return out


def canary_data(kind: str, lane: str, role: str) -> dict:
    """Mean canary score for this lane on fixtures of the same kind or role (evals.jsonl)."""
    gcd = git_common_dir()
    log = (gcd / "tri-lane" / "evals.jsonl") if gcd else None
    if not log or not log.exists():
        return {"runs": 0}
    scores = []
    for line in log.read_text().splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("lane") != lane:
            continue
        if e.get("kind") == kind or e.get("role") == role:
            scores.append(float(e.get("score") or 0))
    return {"runs": len(scores), "mean_score": round(sum(scores) / len(scores), 3) if scores else None}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("suggest")
    s.add_argument("--role", required=True, choices=["implement", "review", "system-review", "whole-repo", "triage"])
    s.add_argument("--kind", default="impl", help="impl | feature | strings | docs | config | android | ios | web | tests | ci | sre | infra | migration | build | debug | payments | ...")
    s.add_argument("--risk", default="", help="comma list: payments,auth,rules,security,concurrency,billing,api,migration,ci")
    s.add_argument("--attempt", type=int, default=1)
    s.add_argument("--diff-lines", type=int, default=0, help="expected size of the change")
    s.add_argument("--task", help="write route-suggestion.json into this task's run dir (shadow mode)")
    s.add_argument("--json", action="store_true")
    sub.add_parser("table")
    a = ap.parse_args()
    if a.cmd == "table":
        t = load_table()
        print(f"updated {t['updated']}")
        for r in t["rules"]:
            print(f"{r['id']:28} {r['role']:14} {','.join(r['kinds']):40} risk={','.join(r['risk']) or '-':40} -> {r['lane']} @ {r['effort']}{'  [shadow]' if r.get('shadow') else ''}")
        return 0
    risk = {x.strip() for x in a.risk.split(",") if x.strip()}
    out = suggest(a.role, a.kind, risk, a.attempt, a.diff_lines)
    out.update({"role": a.role, "kind": a.kind, "risk": sorted(risk), "attempt": a.attempt, "diff_lines": a.diff_lines})
    if a.task:
        gcd = git_common_dir()
        if gcd:
            rd = gcd / "tri-lane" / "run" / a.task
            rd.mkdir(parents=True, exist_ok=True)
            (rd / "route-suggestion.json").write_text(json.dumps(out, indent=2))
            out["written"] = str(rd / "route-suggestion.json")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
