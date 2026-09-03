#!/usr/bin/env python3
"""benchmark-report: compare arms in a benchmark.jsonl and apply the pre-registered decision rule.

Reads the log written by lane-log.py, groups tasks by arm (manual, tri-lane, advisor-only),
and reports medians per arm for Claude billable tokens, Claude cache reads, Codex tokens,
Antigravity tokens, elapsed time, rework, confirmed findings per reviewer, and escaped
defects. Then evaluates the decision rule from BENCHMARK.md:

  adopt tri-lane  if  Claude billable tokens/task drop >= --claude-drop (default 0.33)
                  and escaped defects/task do not rise
                  and elapsed/task <= --max-slowdown x manual (default 1.5)

Outputs Markdown by default; --json for machine use; --html PATH writes a one-page report.
Python stdlib only.

Example:
  python3 benchmark-report.py                       # log from $(git rev-parse --git-common-dir)/tri-lane/benchmark.jsonl
  python3 benchmark-report.py --log ./benchmark.jsonl --html report.html
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

ARMS = ("manual", "tri-lane", "advisor-only")


def default_log() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, timeout=30).stdout.strip()
        return Path(out).resolve() / "tri-lane" / "benchmark.jsonl"
    except Exception:
        return Path("benchmark.jsonl")


def load(log: Path) -> list:
    rows = []
    if not log.exists():
        return rows
    for line in log.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return statistics.median(xs) if xs else None


def mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(statistics.fmean(xs), 2) if xs else None


def codex_tokens(r) -> int:
    """Billable analog: uncached input + output, from the lane events if present, else from Codex session logs."""
    lane, logs = r.get("codex_lane") or {}, r.get("codex_logs") or {}
    return int(lane.get("billable_tokens") or logs.get("billable_tokens") or lane.get("total_tokens") or logs.get("total_tokens") or 0)


def summarise(rows: list) -> dict:
    out = {}
    for arm in ARMS:
        rs = [r for r in rows if r.get("arm") == arm]
        if not rs:
            continue
        reviewers = {}
        for r in rs:
            for who, f in (r.get("findings") or {}).items():
                d = reviewers.setdefault(who, {"confirmed": 0, "disputed": 0, "unverified": 0, "tasks": 0})
                d["tasks"] += 1
                for k in ("confirmed", "disputed", "unverified"):
                    d[k] += int(f.get(k) or 0)
        for who, d in reviewers.items():
            tot = d["confirmed"] + d["disputed"] + d["unverified"]
            d["precision"] = round(d["confirmed"] / tot, 2) if tot else None
            d["confirmed_per_task"] = round(d["confirmed"] / d["tasks"], 2) if d["tasks"] else None
        pool = {}
        for r in rs:
            for k, v in (r.get("pool_deltas") or {}).items():
                pool.setdefault(k, []).append(v)
        out[arm] = {
            "tasks": len(rs),
            "kinds": sorted({r.get("kind") or "" for r in rs}),
            "routes": {k: sum(1 for r in rs if r.get("route") == k) for k in sorted({r.get("route") or "" for r in rs})},
            "status": {k: sum(1 for r in rs if r.get("status") == k) for k in sorted({r.get("status") or "" for r in rs})},
            "claude_billable_median": med([(r.get("claude") or {}).get("billable_tokens") for r in rs]),
            "claude_cache_read_median": med([(r.get("claude") or {}).get("cache_read_input_tokens") for r in rs]),
            "claude_messages_median": med([(r.get("claude") or {}).get("messages") for r in rs]),
            "codex_tokens_median": med([codex_tokens(r) for r in rs]),
            "agy_tokens_median": med([(r.get("agy") or {}).get("total_tokens") for r in rs]),
            "elapsed_min_median": med([round((r.get("elapsed_seconds") or 0) / 60, 1) for r in rs]),
            "rework_mean": mean([r.get("rework") for r in rs]),
            "escalated_rate": mean([1 if r.get("escalated") else 0 for r in rs]),
            "escaped_defects_mean": mean([r.get("escaped_defects") for r in rs]),
            "advisor_verdicts": {k: sum(1 for r in rs if r.get("advisor") == k) for k in sorted({r.get("advisor") or "" for r in rs}) if k},
            "reviewers": reviewers,
            "pool_delta_mean": {k: mean(v) for k, v in pool.items()},
        }
    return out


def decide(s: dict, claude_drop: float, max_slowdown: float) -> dict:
    m, t = s.get("manual"), s.get("tri-lane")
    if not m or not t:
        return {"verdict": "insufficient data", "reason": "need at least one task in both manual and tri-lane arms"}
    checks = {}
    if m["claude_billable_median"] and t["claude_billable_median"] is not None:
        drop = 1 - t["claude_billable_median"] / m["claude_billable_median"]
        checks["claude_tokens_drop"] = {"value": round(drop, 2), "target": claude_drop, "pass": drop >= claude_drop}
    if m["escaped_defects_mean"] is not None and t["escaped_defects_mean"] is not None:
        checks["escaped_defects_not_up"] = {"manual": m["escaped_defects_mean"], "tri_lane": t["escaped_defects_mean"], "pass": t["escaped_defects_mean"] <= m["escaped_defects_mean"]}
    if m["elapsed_min_median"] and t["elapsed_min_median"] is not None:
        ratio = t["elapsed_min_median"] / m["elapsed_min_median"]
        checks["slowdown"] = {"value": round(ratio, 2), "max": max_slowdown, "pass": ratio <= max_slowdown}
    n_ok = min(m["tasks"], t["tasks"]) >= 8
    checks["sample_size"] = {"manual": m["tasks"], "tri_lane": t["tasks"], "pass": n_ok, "note": "8+ per arm before trusting medians"}
    all_pass = all(c.get("pass") for c in checks.values())
    verdict = "adopt tri-lane" if all_pass else ("keep measuring" if not n_ok else "do not adopt as-is")
    extra = {}
    a = s.get("advisor-only")
    if a and t:
        tc = sum(v.get("confirmed", 0) for k, v in t["reviewers"].items() if k != "advisor")
        extra["cross_vendor_confirmed_per_task"] = round(tc / t["tasks"], 2) if t["tasks"] else None
        extra["note"] = "below 1.0 means the Codex and Antigravity reviews add little over the advisor alone"
    if t and t["reviewers"].get("agy") and t["reviewers"].get("codex"):
        extra["agy_vs_codex_confirmed_per_task"] = {"agy": t["reviewers"]["agy"]["confirmed_per_task"], "codex": t["reviewers"]["codex"]["confirmed_per_task"]}
    return {"verdict": verdict, "checks": checks, **extra}


def md_table(s: dict) -> str:
    cols = [("tasks", "Tasks"), ("claude_billable_median", "Claude billable (med)"), ("claude_cache_read_median", "Claude cache read (med)"),
            ("codex_tokens_median", "Codex billable (med)"), ("agy_tokens_median", "Antigravity tokens (med)"), ("elapsed_min_median", "Elapsed min (med)"),
            ("rework_mean", "Rework (mean)"), ("escaped_defects_mean", "Escaped defects (mean)")]
    arms = [a for a in ARMS if a in s]
    lines = ["| Metric | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for k, label in cols:
        lines.append(f"| {label} | " + " | ".join(str(s[a].get(k) if s[a].get(k) is not None else "—") for a in arms) + " |")
    return "\n".join(lines)


def render_md(s: dict, d: dict, log: Path) -> str:
    out = [f"# Tri-Lane benchmark report", f"Log: `{log}`", "", md_table(s), ""]
    for arm in ARMS:
        if arm not in s:
            continue
        a = s[arm]
        out.append(f"## {arm}")
        out.append(f"- routes: {a['routes']}  status: {a['status']}  advisor: {a['advisor_verdicts']}")
        out.append(f"- escalated rate: {a['escalated_rate']}  pool delta mean: {a['pool_delta_mean']}")
        if a["reviewers"]:
            out.append("- reviewers (confirmed / disputed / unverified, precision, confirmed per task):")
            for who, r in a["reviewers"].items():
                out.append(f"  - {who}: {r['confirmed']} / {r['disputed']} / {r['unverified']}, precision {r['precision']}, {r['confirmed_per_task']} per task")
        out.append("")
    out.append("## Decision")
    out.append(f"**{d['verdict']}**")
    for k, v in d.get("checks", {}).items():
        out.append(f"- {k}: {v}")
    for k in ("cross_vendor_confirmed_per_task", "agy_vs_codex_confirmed_per_task", "note", "reason"):
        if k in d:
            out.append(f"- {k}: {d[k]}")
    return "\n".join(out)


def render_html(md: str) -> str:
    import html
    body = html.escape(md)
    return ("<title>Tri-Lane Benchmark</title><style>body{font-family:ui-monospace,Menlo,monospace;max-width:900px;margin:40px auto;"
            "padding:0 20px;background:#F3F5F7;color:#16202A;line-height:1.5}pre{white-space:pre-wrap}</style><pre>" + body + "</pre>")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", help="benchmark.jsonl path")
    ap.add_argument("--claude-drop", type=float, default=0.33, help="required fractional drop in Claude billable tokens per task")
    ap.add_argument("--max-slowdown", type=float, default=1.5, help="max elapsed ratio tri-lane / manual")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--html", help="write a one-page HTML report to this path")
    args = ap.parse_args()
    log = Path(args.log) if args.log else default_log()
    rows = load(log)
    if not rows:
        print(f"no rows in {log}", file=sys.stderr)
        return 1
    s = summarise(rows)
    d = decide(s, args.claude_drop, args.max_slowdown)
    if args.json:
        print(json.dumps({"log": str(log), "arms": s, "decision": d}, indent=2))
    else:
        md = render_md(s, d, log)
        print(md)
        if args.html:
            Path(args.html).write_text(render_html(md))
            print(f"\nwrote {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
