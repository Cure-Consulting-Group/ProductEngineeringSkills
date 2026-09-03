#!/usr/bin/env python3
"""lane-log: record one benchmark line per task, for any arm (manual, tri-lane, advisor-only).

  start   snapshot the clock and every quota pool before a task begins
  end     close the task: elapsed, Claude + Codex usage from logs, Antigravity usage from
          agy JSON files, pool deltas, route/lane/status, review labels; append to the log
  update  amend a logged task later (escaped defects found after merge, notes)
  list    print the log as a table

Log lives at $(git rev-parse --git-common-dir)/tri-lane/benchmark.jsonl (override with --log).
Python stdlib only; reads agy and codex logs, never spends quota except one free `agy -p /usage`.

Examples:
  python3 lane-log.py start --task v-042 --arm tri-lane --kind security
  python3 lane-log.py end --task v-042 --route audit --lane "gpt-5.6-sol @ max" --status complete \
      --codex-events /tmp/lane-events.xxx --agy-json /tmp/agy-out.json \
      --finding codex:2:0:1 --finding agy:1:2:0 --finding advisor:0:0:0 --advisor fix-first --rework 1
  python3 lane-log.py update --task v-042 --escaped-defects 1 --notes "null roster on empty team"
  python3 lane-log.py list
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sh(cmd, cwd=None, timeout=60):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return 1, str(e)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_path(override: str | None) -> Path:
    if override:
        return Path(override)
    rc, out = sh(["git", "rev-parse", "--git-common-dir"])
    base = Path(out.strip()).resolve() if rc == 0 else Path.cwd()
    p = base / "tri-lane"
    p.mkdir(parents=True, exist_ok=True)
    return p / "benchmark.jsonl"


def start_path(log: Path, task: str) -> Path:
    d = log.parent / "bench-open"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{task}.json"


def agy_pools() -> dict:
    rc, out = sh(["agy", "-p", "/usage", "--output-format", "json"], timeout=60)
    pools: dict = {}
    try:
        resp = json.loads(out.strip().splitlines()[-1]).get("response", "")
    except Exception:
        return pools
    for line in resp.splitlines():
        parts = [p.strip() for p in line.split("\t")]
        if len(parts) >= 3 and parts[2].endswith("%"):
            key = "google_gemini" if parts[0].lower().startswith("gemini") else "google_claude_gpt"
            window = "weekly" if "weekly" in parts[1].lower() else "five_hour"
            try:
                pools[f"{key}_{window}_remaining"] = int(parts[2].rstrip("%"))
            except ValueError:
                pass
    return pools


def codex_pool() -> dict:
    rc, out = sh([sys.executable, str(HERE / "usage-window.py"), "--since", "1970-01-01T00:00:00Z"], timeout=120)
    try:
        c = json.loads(out)["codex"]
        return {"codex_weekly_used_percent": c.get("weekly_used_percent"), "codex_weekly_resets_at": c.get("weekly_resets_at")}
    except Exception:
        return {"codex_weekly_used_percent": None}


def snapshot_pools() -> dict:
    d = agy_pools()
    d.update(codex_pool())
    d["captured_at"] = now_iso()
    return d


def read_log(log: Path) -> list:
    if not log.exists():
        return []
    rows = []
    for line in log.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def write_log(log: Path, rows: list) -> None:
    log.write_text("".join(json.dumps(r) + "\n" for r in rows))


def parse_agy_json(path: str) -> dict:
    try:
        d = json.loads(Path(path).read_text())
        u = d.get("usage") or {}
        return {k: int(u.get(k) or 0) for k in ("input_tokens", "output_tokens", "thinking_tokens", "cache_read_tokens", "total_tokens")} | {"duration_seconds": d.get("duration_seconds")}
    except Exception:
        return {}


def parse_codex_events(path: str) -> dict:
    tot = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0, "total_tokens": 0}
    try:
        for line in Path(path).read_text(errors="ignore").splitlines():
            if '"turn.completed"' not in line:
                continue
            d = json.loads(line)
            u = d.get("usage") or {}
            for k in tot:
                tot[k] += int(u.get(k) or 0)
    except Exception:
        pass
    tot["billable_tokens"] = tot["input_tokens"] - tot["cached_input_tokens"] + tot["output_tokens"]
    return tot


def cmd_start(a) -> int:
    log = log_path(a.log)
    sp = start_path(log, a.task)
    if sp.exists() and not a.force:
        print(f"task {a.task} already started at {json.loads(sp.read_text()).get('started_at')}; use --force to restart", file=sys.stderr)
        return 1
    rc, head = sh(["git", "rev-parse", "--short", "HEAD"])
    rec = {
        "task": a.task, "arm": a.arm, "kind": a.kind, "started_at": now_iso(),
        "project": str(Path.cwd().resolve()), "head": head.strip(), "notes": a.notes or "",
        "pools_before": snapshot_pools(),
    }
    sp.write_text(json.dumps(rec, indent=2))
    print(json.dumps({"started": a.task, "arm": a.arm, "pools_before": rec["pools_before"]}, indent=2))
    return 0


def cmd_end(a) -> int:
    log = log_path(a.log)
    sp = start_path(log, a.task)
    if not sp.exists():
        print(f"no open start record for task {a.task}; run `lane-log.py start --task {a.task}` first", file=sys.stderr)
        return 1
    rec = json.loads(sp.read_text())
    ended = now_iso()
    started = rec["started_at"]
    elapsed = (datetime.fromisoformat(ended) - datetime.fromisoformat(started)).total_seconds()

    rc, out = sh([sys.executable, str(HERE / "usage-window.py"), "--since", started, "--until", ended, "--project", rec["project"]], timeout=180)
    try:
        usage = json.loads(out)
    except Exception:
        usage = {"claude": {}, "codex": {}}

    agy = {"input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0, "cache_read_tokens": 0, "total_tokens": 0, "calls": 0}
    for f in a.agy_json or []:
        u = parse_agy_json(f)
        if u:
            agy["calls"] += 1
            for k in ("input_tokens", "output_tokens", "thinking_tokens", "cache_read_tokens", "total_tokens"):
                agy[k] += u.get(k, 0)
    codex_lane = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0, "total_tokens": 0, "billable_tokens": 0, "calls": 0}
    for f in a.codex_events or []:
        u = parse_codex_events(f)
        codex_lane["calls"] += 1
        for k in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens", "billable_tokens"):
            codex_lane[k] += u.get(k, 0)

    findings = {}
    for spec in a.finding or []:
        try:
            who, c, d, u = spec.split(":")
            findings[who] = {"confirmed": int(c), "disputed": int(d), "unverified": int(u)}
        except ValueError:
            print(f"bad --finding {spec!r}; expected reviewer:confirmed:disputed:unverified", file=sys.stderr)
            return 2

    pools_after = snapshot_pools()
    deltas = {}
    for k, v in pools_after.items():
        b = rec["pools_before"].get(k)
        if isinstance(v, (int, float)) and isinstance(b, (int, float)):
            deltas[k.replace("_remaining", "").replace("_used_percent", "")] = round(v - b, 2) if "remaining" in k else round(v - b, 2)

    row = {
        **{k: rec[k] for k in ("task", "arm", "kind", "project", "head")},
        "started_at": started, "ended_at": ended, "elapsed_seconds": round(elapsed),
        "route": a.route, "lane": a.lane, "status": a.status, "advisor": a.advisor,
        "rework": a.rework, "escalated": bool(a.escalated), "escaped_defects": 0,
        "claude": usage.get("claude", {}), "codex_logs": usage.get("codex", {}),
        "codex_lane": codex_lane, "agy": agy,
        "findings": findings, "pools_before": rec["pools_before"], "pools_after": pools_after, "pool_deltas": deltas,
        "notes": " ".join(x for x in (rec.get("notes"), a.notes) if x),
    }
    rows = read_log(log)
    rows = [r for r in rows if r.get("task") != a.task] + [row]
    write_log(log, rows)
    sp.unlink()
    summary = {
        "task": a.task, "arm": a.arm if hasattr(a, "arm") else rec["arm"], "elapsed_min": round(elapsed / 60, 1),
        "claude_billable": row["claude"].get("billable_tokens"), "claude_cache_read": row["claude"].get("cache_read_input_tokens"),
        "codex_billable": codex_lane["billable_tokens"] or row["codex_logs"].get("billable_tokens"), "codex_total": codex_lane["total_tokens"] or row["codex_logs"].get("total_tokens"), "agy_total": agy["total_tokens"],
        "pool_deltas": deltas, "log": str(log),
    }
    print(json.dumps(summary, indent=2))
    return 0


def cmd_update(a) -> int:
    log = log_path(a.log)
    rows = read_log(log)
    hit = [r for r in rows if r.get("task") == a.task]
    if not hit:
        print(f"task {a.task} not in {log}", file=sys.stderr)
        return 1
    r = hit[-1]
    if a.escaped_defects is not None:
        r["escaped_defects"] = a.escaped_defects
    if a.notes:
        r["notes"] = (r.get("notes", "") + " " + a.notes).strip()
    if a.set:
        for kv in a.set:
            k, v = kv.split("=", 1)
            try:
                r[k] = json.loads(v)
            except Exception:
                r[k] = v
    write_log(log, rows)
    print(json.dumps({"updated": a.task, "escaped_defects": r.get("escaped_defects"), "notes": r.get("notes")}))
    return 0


def cmd_list(a) -> int:
    log = log_path(a.log)
    rows = read_log(log)
    if a.json:
        print(json.dumps(rows, indent=2))
        return 0
    print(f"{'task':10} {'arm':13} {'kind':9} {'route':9} {'status':9} {'min':>6} {'claude_bill':>11} {'codex':>9} {'agy':>9} {'conf':>4} {'esc':>3}")
    for r in rows:
        conf = sum(v.get("confirmed", 0) for v in (r.get("findings") or {}).values())
        codex = (r.get("codex_lane") or {}).get("total_tokens") or (r.get("codex_logs") or {}).get("total_tokens") or 0
        print(f"{r.get('task',''):10} {r.get('arm',''):13} {(r.get('kind') or ''):9} {(r.get('route') or ''):9} {(r.get('status') or ''):9} "
              f"{round(r.get('elapsed_seconds',0)/60):>6} {(r.get('claude') or {}).get('billable_tokens',0):>11} {codex:>9} {(r.get('agy') or {}).get('total_tokens',0):>9} {conf:>4} {r.get('escaped_defects',0):>3}")
    print(f"{len(rows)} tasks in {log}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", help="override the benchmark.jsonl path")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="snapshot pools and clock before a task")
    s.add_argument("--task", required=True)
    s.add_argument("--arm", required=True, choices=["manual", "tri-lane", "advisor-only"])
    s.add_argument("--kind", default="", help="impl | security | infra | debug | refactor | docs")
    s.add_argument("--notes", default="")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_start)

    e = sub.add_parser("end", help="close a task and append the benchmark line")
    e.add_argument("--task", required=True)
    e.add_argument("--route", default="", help="solo | delegate | audit | full | manual")
    e.add_argument("--lane", default="", help='as executed, e.g. "gpt-5.6-luna @ high"')
    e.add_argument("--status", default="", help="complete | partial | refused | timeout | unavailable")
    e.add_argument("--advisor", default="", help="ship | fix-first | rethink | none")
    e.add_argument("--rework", type=int, default=0, help="spec corrections sent back")
    e.add_argument("--escalated", action="store_true", help="lane escalated (Luna to Sol, or to the architect)")
    e.add_argument("--codex-events", action="append", help="codex --json events file (repeatable)")
    e.add_argument("--agy-json", action="append", help="agy --output-format json file (repeatable)")
    e.add_argument("--finding", action="append", help="reviewer:confirmed:disputed:unverified (repeatable)")
    e.add_argument("--notes", default="")
    e.set_defaults(fn=cmd_end)

    u = sub.add_parser("update", help="amend a logged task")
    u.add_argument("--task", required=True)
    u.add_argument("--escaped-defects", type=int)
    u.add_argument("--notes", default="")
    u.add_argument("--set", action="append", help="key=json-value (repeatable)")
    u.set_defaults(fn=cmd_update)

    l = sub.add_parser("list", help="print the log")
    l.add_argument("--json", action="store_true")
    l.set_defaults(fn=cmd_list)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
