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

ARMS = ("manual", "tri-lane", "advisor-only", "tri-lane-lean")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
INCLUDE_OVERLAPS = False  # T47: rows whose Claude window overlaps another task's are excluded from Claude medians unless asked
INCLUDE_BACKFILL = False  # backfilled rows carry no effort and an inferred model; they inform the dashboard, never the rule, unless asked


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
            r = json.loads(line)
            r.setdefault("_log", str(log))
            rows.append(r)
        except Exception:
            pass
    return rows


def load_all_projects() -> list:
    """Every benchmark.jsonl under the project roots (TRI_LANE_PROJECT_ROOTS or the defaults in lane_run)."""
    import lane_run  # noqa: E402
    seen, rows = set(), []
    for root in lane_run.project_roots():
        for log in Path(root).expanduser().glob("*/.git/tri-lane/benchmark.jsonl"):
            key = str(log.resolve())
            if key in seen:
                continue
            seen.add(key)
            for r in load(log):
                r["_project"] = log.resolve().parents[2].name
                rows.append(r)
    return rows


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return statistics.median(xs) if xs else None


def mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(statistics.fmean(xs), 2) if xs else None


def codex_tokens(r) -> int:
    """Billable analog: uncached input + output from the lane events. The account-wide figure from Codex session
    logs (codex_account, formerly codex_logs) is not per task; it stands in only for the manual arm, which has no lanes."""
    lane = r.get("codex_lane") or {}
    wt = r.get("codex_worktree") or {}
    acct = r.get("codex_account") or r.get("codex_logs") or {}
    # the rollout log keyed by worktree cwd sees implementer and reviewer sessions alike; the event stream sees only the implementer
    best = max(int(lane.get("billable_tokens") or 0), int(wt.get("billable_tokens") or 0))
    if best:
        return best
    if r.get("arm") == "manual":
        return int(acct.get("billable_tokens") or acct.get("total_tokens") or 0)
    return 0


def claude_rows(rs: list) -> list:
    """Rows eligible for Claude medians: measured, and not overlapping another task's window (unless INCLUDE_OVERLAPS)."""
    return [r for r in rs if (r.get("claude") or {}).get("billable_tokens") and (INCLUDE_OVERLAPS or not r.get("claude_overlap"))]


_ROWS: list = []


def rows_for(_s, arms):
    return [r for r in _ROWS if r.get("arm") in arms]


def window_open(r) -> bool:
    from datetime import datetime, timedelta, timezone
    try:
        return datetime.fromisoformat(r["ended_at"]) + timedelta(days=7) > datetime.now(timezone.utc)
    except Exception:
        return True


def summarise(rows: list) -> dict:
    global _ROWS
    _ROWS = rows
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
        for r in rs:
            for who, n in (r.get("findings_reported") or {}).items():
                d = reviewers.setdefault(who, {"confirmed": 0, "disputed": 0, "unverified": 0, "tasks": 0})
                d["reported"] = d.get("reported", 0) + int(n or 0)
                d["tasks_reported"] = d.get("tasks_reported", 0) + 1
        for who, d in reviewers.items():
            tot = d["confirmed"] + d["disputed"] + d["unverified"]
            d["precision"] = round(d["confirmed"] / tot, 2) if tot else None
            d["confirmed_per_task"] = round(d["confirmed"] / d["tasks"], 2) if d["tasks"] else None
        pool = {}
        for r in rs:
            for k, v in (r.get("pool_deltas") or {}).items():
                pool.setdefault(k, []).append(v)
        sugg = [r for r in rs if r.get("suggested")]
        out[arm] = {
            "tasks": len(rs),
            "projects": sorted({r.get("_project") for r in rs if r.get("_project")}),
            "models": sorted({f"{r.get('model')}@{r.get('effort')}" for r in rs}),
            "router_shadow": {"suggested": len(sugg), "followed": sum(1 for r in sugg if r.get("suggestion_followed")),
                               "rework_when_followed": mean([r.get("rework") for r in sugg if r.get("suggestion_followed")]),
                               "rework_when_not": mean([r.get("rework") for r in sugg if r.get("suggestion_followed") is False])},
            "kinds": sorted({r.get("kind") or "" for r in rs}),
            "routes": {k: sum(1 for r in rs if r.get("route") == k) for k in sorted({r.get("route") or "" for r in rs})},
            "status": {k: sum(1 for r in rs if r.get("status") == k) for k in sorted({r.get("status") or "" for r in rs})},
            "claude_billable_median": med([(r.get("claude") or {}).get("billable_tokens") for r in claude_rows(rs)]),
            "claude_cache_read_median": med([(r.get("claude") or {}).get("cache_read_input_tokens") for r in claude_rows(rs)]),
            "claude_messages_median": med([(r.get("claude") or {}).get("messages") for r in claude_rows(rs)]),
            "claude_measured": len(claude_rows(rs)), "claude_overlapped": sum(1 for r in rs if r.get("claude_overlap")),
            "backfilled": sum(1 for r in rs if r.get("backfilled")),
            "advisor_coverage": {"reviewed": sum(1 for r in rs if r.get("advisor") and r.get("advisor") != "none"), "skipped": sum(1 for r in rs if r.get("advisor") == "none"), "missing": sum(1 for r in rs if not r.get("advisor"))},
            "dispatches_mean": mean([r.get("dispatches") for r in rs]),
            "causes": {k: sum(1 for r in rs if r.get("cause") == k) for k in sorted({r.get("cause") or "" for r in rs}) if k},
            "codex_tokens_median": med([codex_tokens(r) for r in rs]),
            "agy_tokens_median": med([(r.get("agy") or {}).get("total_tokens") for r in rs]),
            "elapsed_min_median": med([round((r.get("elapsed_seconds") or 0) / 60, 1) for r in rs]),
            "rework_mean": mean([r.get("rework") for r in rs]),
            "escalated_rate": mean([1 if r.get("escalated") else 0 for r in rs]),
            "escaped_defects_mean": mean([r.get("escaped_defects") for r in rs]),
            "advisor_verdicts": {k: sum(1 for r in rs if r.get("advisor") == k) for k in sorted({r.get("advisor") or "" for r in rs}) if k},
            "agy_verdicts": {k: sum(1 for r in rs if r.get("agy_verdict") == k) for k in sorted({r.get("agy_verdict") or "" for r in rs}) if k},
            "codex_worktree_measured": sum(1 for r in rs if (r.get("codex_worktree") or {}).get("billable_tokens")),
            "reviewers": reviewers,
            "pool_delta_mean": {k: mean(v) for k, v in pool.items()},
        }
    return out


def decide(s: dict, claude_drop: float, max_slowdown: float) -> dict:
    """The pre-registered rule over lifecycle-logged rows. Backfilled rows are excluded unless INCLUDE_BACKFILL:
    they have no recorded effort and an inferred model, so they can never satisfy the fixed-model gate honestly."""
    if not INCLUDE_BACKFILL and any(r.get("backfilled") for r in _ROWS):
        live = [r for r in _ROWS if not r.get("backfilled")]
        excluded = len(_ROWS) - len(live)
        s = summarise(live) if live else {}
        d = _decide(s, claude_drop, max_slowdown)
        d["backfilled_excluded"] = excluded
        d["note_backfill"] = f"{excluded} backfilled row(s) excluded from the rule (no effort recorded, model inferred); pass --include-backfill to count them"
        return d
    return _decide(s, claude_drop, max_slowdown)


def _decide(s: dict, claude_drop: float, max_slowdown: float) -> dict:
    m, t = s.get("manual"), s.get("tri-lane")
    if not m or not t:
        return {"verdict": "insufficient data", "reason": "need at least one lifecycle-logged task in both manual and tri-lane arms"}
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
    # fixed-model rule: both arms must have run under one session model + effort
    models = sorted({f"{r.get('model')}@{r.get('effort')}" for r in rows_for(s, ("manual", "tri-lane"))})
    checks["model_frozen"] = {"models_seen": models, "pass": len(models) == 1 and models[0] != "None@None", "note": "recorded by lane-log start; None means the task predates 1.3.0"}
    # defect windows: every task in both arms must have had its 7-day window checked or closed
    open_w = [r["task"] for r in rows_for(s, ("manual", "tri-lane")) if not r.get("window_checked_at") and window_open(r)]
    checks["defect_windows_closed"] = {"open": open_w, "pass": not open_w, "note": "escaped_defects_not_up passes on 0 vs 0 by construction while windows are open"}
    all_pass = all(c.get("pass") for c in checks.values())
    blockers = [k for k in ("sample_size", "model_frozen", "defect_windows_closed") if not checks[k]["pass"]]
    verdict = "adopt tri-lane" if all_pass else ("keep measuring: " + ", ".join(blockers) if blockers else "do not adopt as-is")
    extra = {}
    a = s.get("advisor-only")
    if a and t:
        tc = sum(v.get("confirmed", 0) for k, v in t["reviewers"].items() if k != "advisor")
        extra["cross_vendor_confirmed_per_task"] = round(tc / t["tasks"], 2) if t["tasks"] else None
        extra["note"] = "below 1.0 means the Codex and Antigravity reviews add little over the advisor alone"
    if t and t["reviewers"].get("agy") and t["reviewers"].get("codex"):
        extra["agy_vs_codex_confirmed_per_task"] = {"agy": t["reviewers"]["agy"]["confirmed_per_task"], "codex": t["reviewers"]["codex"]["confirmed_per_task"]}
    return {"verdict": verdict, "checks": checks, **extra}


def proxy(pre: str, post: str, projects: list, until: str | None = None) -> dict:
    """T49 part 1: Claude billable per merged commit per repository across two windows, from transcripts and
    `git log --all`. A proxy for the pre-registered rule, never a substitute for the manual arm: work mix differs
    between windows, review sessions inflate the post window, and commits count every branch."""
    import importlib.util
    from datetime import datetime, timezone
    spec_u = importlib.util.spec_from_file_location("usage_window", HERE / "usage-window.py")
    uw = importlib.util.module_from_spec(spec_u); spec_u.loader.exec_module(uw)
    t_pre, t_post = uw.parse_ts(pre), uw.parse_ts(post)
    t_end = uw.parse_ts(until) if until else datetime.now(timezone.utc)
    out = {"windows": {"pre": [t_pre.isoformat(), t_post.isoformat()], "post": [t_post.isoformat(), t_end.isoformat()]}, "projects": {}, "confounds": [
        "work mix differs between windows", "the post window includes review and documentation sessions",
        "commits are counted on every branch (--all) and include lane and salvage commits", "Claude billable includes cache creation, which scales with context size",
        "this is not the pre-registered rule; only the manual arm can return a verdict"]}
    for proj in projects:
        pj = Path(proj).expanduser()
        u_pre, u_post = uw.claude_usage_multi(str(pj), [(t_pre, t_post), (t_post, t_end)])
        def commits(a, b, scope):
            # scope "all": every branch, which after adoption includes one commit per lane run and salvage;
            # scope "branch": first-parent history of the checked-out branch, closer to "changes that landed"
            args = ["git", "log", "--oneline", f"--since={a.isoformat()}", f"--until={b.isoformat()}"] + (["--all"] if scope == "all" else ["--first-parent", "HEAD"])
            try:
                r = subprocess.run(args, cwd=str(pj), capture_output=True, text=True, timeout=60)
                return len([l for l in r.stdout.splitlines() if l.strip()])
            except Exception:
                return 0
        def side(u, a, b):
            ca, cb = commits(a, b, "all"), commits(a, b, "branch")
            return {"claude_billable": u["billable_tokens"], "messages": u["messages"], "commits_all": ca, "commits_branch": cb,
                    "per_commit_all": round(u["billable_tokens"] / ca) if ca else None, "per_commit_branch": round(u["billable_tokens"] / cb) if cb else None}
        row = {"pre": side(u_pre, t_pre, t_post), "post": side(u_post, t_post, t_end)}
        for k in ("all", "branch"):
            a, b = row["pre"][f"per_commit_{k}"], row["post"][f"per_commit_{k}"]
            if a and b:
                row[f"per_commit_change_{k}"] = round(b / a - 1, 2)
        out["projects"][pj.name] = row
    return out


def render_proxy_md(d: dict) -> str:
    out = ["# Tri-Lane cost proxy: Claude billable per merged commit", "",
           f"Windows: pre `{d['windows']['pre'][0][:10]}` to `{d['windows']['pre'][1][:10]}`; post `{d['windows']['post'][0][:10]}` to `{d['windows']['post'][1][:10]}`.", "",
           "**Proxy, not the rule.** " + " ".join(c[0].upper() + c[1:] + "." for c in d["confounds"]), "",
           "Two commit denominators, because the answer depends on it: *branch* counts first-parent commits on the checked-out branch (changes that landed); *all* counts every branch, which after adoption includes one commit per lane run and every salvage branch, so it flatters the post window.", "",
           "| Repository | Claude billable, pre | Claude billable, post | Per branch commit, pre → post | Change | Per commit (all branches), pre → post | Change |", "|---|---:|---:|---|---:|---|---:|"]
    f = lambda v: f"{v:,}" if isinstance(v, int) else ("—" if v is None else v)
    pct = lambda ch: ("+" if ch and ch > 0 else "") + str(round(ch * 100)) + "%" if ch is not None else "—"
    for name, r in d["projects"].items():
        out.append(f"| {name} | {f(r['pre']['claude_billable'])} | {f(r['post']['claude_billable'])} | {f(r['pre']['per_commit_branch'])} ({r['pre']['commits_branch']}) → {f(r['post']['per_commit_branch'])} ({r['post']['commits_branch']}) | {pct(r.get('per_commit_change_branch'))} | {f(r['pre']['per_commit_all'])} ({r['pre']['commits_all']}) → {f(r['post']['per_commit_all'])} ({r['post']['commits_all']}) | {pct(r.get('per_commit_change_all'))} |")
    return "\n".join(out)


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
        out.append(f"- projects: {a['projects']}  models: {a['models']}  router shadow: {a['router_shadow']}")
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
    ap.add_argument("--all-projects", action="store_true", help="aggregate every project's benchmark.jsonl under the Cure project roots")
    ap.add_argument("--claude-drop", type=float, default=0.33, help="required fractional drop in Claude billable tokens per task")
    ap.add_argument("--max-slowdown", type=float, default=1.5, help="max elapsed ratio tri-lane / manual")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--html", help="write a one-page HTML report to this path")
    ap.add_argument("--include-overlaps", action="store_true", help="count Claude tokens for tasks whose windows overlap another task's (double counts; default excludes them)")
    ap.add_argument("--include-backfill", action="store_true", help="let backfilled rows (no effort, inferred model) count toward the decision rule")
    ap.add_argument("--proxy", action="store_true", help="T49: Claude billable per merged commit per repo across two windows (--pre, --post); a proxy, not the rule")
    ap.add_argument("--pre", help="ISO start of the pre-adoption window (with --proxy)")
    ap.add_argument("--post", help="ISO start of the post-adoption window; the pre window ends here (with --proxy)")
    ap.add_argument("--until", help="ISO end of the post window (default now)")
    ap.add_argument("--projects", help="comma-separated repo paths (default: every project root child with a .git/tri-lane)")
    args = ap.parse_args()
    global INCLUDE_OVERLAPS, INCLUDE_BACKFILL
    INCLUDE_OVERLAPS = args.include_overlaps
    INCLUDE_BACKFILL = args.include_backfill
    if args.proxy:
        if not (args.pre and args.post):
            print("--proxy needs --pre and --post", file=sys.stderr)
            return 2
        import lane_run  # noqa: E402
        projects = [p.strip() for p in args.projects.split(",")] if args.projects else [str(pj) for root in lane_run.project_roots() for pj in sorted(root.iterdir()) if (pj / ".git" / "tri-lane").exists()]
        d = proxy(args.pre, args.post, projects, args.until)
        if args.json:
            print(json.dumps(d, indent=2))
        else:
            md = render_proxy_md(d)
            print(md)
            if args.html:
                Path(args.html).write_text(render_html(md))
        return 0
    log = Path(args.log) if args.log else default_log()
    rows = load_all_projects() if args.all_projects else load(log)
    if args.all_projects:
        log = Path("(all projects)")
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
