#!/usr/bin/env python3
"""lane-export: the per-task dataset, reproducibly, from benchmark.jsonl (Wave 4, T47).

The 13 Sep 2026 production review was built from a hand-made JSON of 142 tasks. This script produces the
same shape from the logs the lifecycle now writes (and from `lane-log.py backfill` for older run dirs), so
every figure in a review can be regenerated with one command.

  python3 lane-export.py --all-projects --out tri-lane/data/benchmark-tasks-2026-09-20.json
  python3 lane-export.py --out tasks.json                # this repo only
Python stdlib only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_report_module():
    spec = importlib.util.spec_from_file_location("benchmark_report", HERE / "benchmark-report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def export_row(r: dict) -> dict:
    c = r.get("claude") or {}
    x = r.get("codex_lane") or {}
    a = r.get("agy") or {}
    sp = r.get("spec") or {}
    lane = r.get("lane") or ""
    model = lane.split(" @ ")[0] if lane else sp.get("lane")
    rung = lane.split(" @ ")[1] if " @ " in lane else sp.get("reasoning")
    return {
        "project": r.get("_project") or Path(r.get("project") or "").name,
        "task_id": r.get("task"),
        "arm": r.get("arm"),
        "kind": r.get("kind") or "",
        "started_at": r.get("started_at"), "ended_at": r.get("ended_at"), "elapsed_seconds": r.get("elapsed_seconds"),
        "route": r.get("route") or "", "route_inferred": bool(r.get("route_inferred")), "escalated": bool(r.get("escalated")),
        "lane": ("luna" if "luna" in (model or "") else "sol" if "sol" in (model or "") else model) if model else None,
        "model": model, "reasoning": rung,
        "objective": sp.get("objective"), "files": sp.get("files") or [], "verify_cmd": sp.get("verify"),
        "status": r.get("status") or "", "status_inferred": bool(r.get("status_inferred")), "cause": r.get("cause"),
        "gaps": r.get("gaps") or [],
        "dispatches": r.get("dispatches"), "rework": r.get("rework"),
        "codex_input": x.get("input_tokens", 0), "codex_cached": x.get("cached_input_tokens", 0), "codex_output": x.get("output_tokens", 0),
        "codex_billable": x.get("billable_tokens", 0), "codex_calls": x.get("calls", 0),
        # events.jsonl, events2.jsonl, events-<variant>.jsonl are implementer dispatches (one per attempt or spec variant);
        # review-events.jsonl is the codex-reviewer lane (its stream carries no turn.completed usage today)
        "codex_billable_implementer": sum(v for k, v in (x.get("by_file") or {}).items() if not k.startswith("review")) if x.get("by_file") else x.get("billable_tokens", 0),
        "codex_billable_reviewer": sum(v for k, v in (x.get("by_file") or {}).items() if k.startswith("review")),
        "agy_calls": a.get("calls", 0), "agy_total_tokens": a.get("total_tokens", 0),
        "advisor_verdict": r.get("advisor") or None, "advisor_skip_reason": r.get("advisor_skip_reason"),
        "findings": r.get("findings") or {}, "findings_labeled": bool(r.get("findings_labeled")),
        "claude_billable": c.get("billable_tokens"), "claude_cache_read": c.get("cache_read_input_tokens"), "claude_messages": c.get("messages"),
        "claude_overlap": r.get("claude_overlap") or [],
        "verify": r.get("verify"), "diff_lines": r.get("diff_lines"), "commit": r.get("commit"),
        "escaped_defects": r.get("escaped_defects"), "window_checked_at": r.get("window_checked_at"),
        "backfilled": bool(r.get("backfilled")), "evidence_grade": r.get("evidence_grade"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", help="benchmark.jsonl path (default: this repo's)")
    ap.add_argument("--all-projects", action="store_true", help="every project's benchmark.jsonl under the Cure project roots")
    ap.add_argument("--out", help="write JSON here (default stdout)")
    ap.add_argument("--summary", action="store_true", help="print the headline totals the production review used")
    a = ap.parse_args()
    br = load_report_module()
    rows = br.load_all_projects() if a.all_projects else br.load(Path(a.log) if a.log else br.default_log())
    out = [export_row(r) for r in rows]
    out.sort(key=lambda r: (r["project"], r["started_at"] or ""))
    text = json.dumps(out, indent=1)
    if a.out:
        Path(a.out).expanduser().write_text(text)
        print(f"wrote {a.out} ({len(out)} tasks)")
    else:
        print(text)
    if a.summary:
        s = {
            "tasks": len(out),
            "codex_runs": sum(1 for r in out if r["codex_calls"]),
            "codex_billable": sum(r["codex_billable"] for r in out), "codex_cached": sum(r["codex_cached"] for r in out),
            "codex_billable_implementer": sum(r["codex_billable_implementer"] for r in out), "codex_billable_reviewer": sum(r["codex_billable_reviewer"] for r in out),
            "agy_tokens": sum(r["agy_total_tokens"] for r in out), "agy_tasks": sum(1 for r in out if r["agy_calls"]),
            "advisor_reviews": sum(1 for r in out if r["advisor_verdict"] and r["advisor_verdict"] != "none"),
            "advisor_skipped": sum(1 for r in out if r["advisor_verdict"] == "none"),
            "claude_billable_measured": sum(1 for r in out if r["claude_billable"]),
            "claude_overlapped": sum(1 for r in out if r["claude_overlap"]),
            "routes": {k: sum(1 for r in out if r["route"] == k) for k in sorted({r["route"] for r in out})},
            "backfilled": sum(1 for r in out if r["backfilled"]),
        }
        print(json.dumps(s, indent=1), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
