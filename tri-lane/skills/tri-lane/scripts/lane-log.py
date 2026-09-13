#!/usr/bin/env python3
"""lane-log: record one benchmark line per task, for any arm (manual, tri-lane, advisor-only).

  start   snapshot the clock and every quota pool before a task begins
  end     close the task: elapsed, Claude + Codex usage from logs, Antigravity usage from
          agy JSON files, pool deltas, route/lane/status, review labels; append to the log
  update  amend a logged task later (escaped defects found after merge, notes); --escaped-defects 0 marks the window checked
  due     tasks whose 7-day defect window has closed and has not been checked
  list    print the log as a table

`start` records the session model and effort from ~/.claude/settings.json so the benchmark's fixed-model
rule is checkable. `end` auto-discovers everything the run dir holds ($(git rev-parse --git-common-dir)/tri-lane/run/<task>/):
events*.jsonl, agy*.json, route-suggestion.json, route.json (declared route), report.json (lane, status, gaps),
advisor.md (verdict), spec*.md (rework), so nothing is missed when flags are omitted; flags override.
Neither command needs typing any more: `lane-worktree.py add` runs `start` and `remove` runs `end` (Wave 4, T42).
`end` with no open start record falls back to meta.json's started_at, then --started-at. --ended-at backfills.
Set TRI_LANE_NO_POOLS=1 to skip the quota snapshots (tests, offline).

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
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ARMS = ["manual", "tri-lane", "advisor-only", "tri-lane-lean"]


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
    if os.environ.get("TRI_LANE_NO_POOLS"):
        return {"captured_at": now_iso(), "skipped": True}
    d = agy_pools()
    d.update(codex_pool())
    d["captured_at"] = now_iso()
    return d


def session_model() -> dict:
    """The Claude Code session model and effort, from ~/.claude/settings.json (overridable by flags).
    The benchmark protocol freezes these for both arms; recording them makes the freeze checkable."""
    out = {"model": None, "effort": None}
    try:
        s = json.loads((Path.home() / ".claude" / "settings.json").read_text())
        out["model"] = s.get("model")
        out["effort"] = s.get("effortLevel")
    except Exception:
        pass
    return out


def run_dir_for(log: Path, task: str) -> Path:
    return log.parent / "run" / task


def discover_run_files(log: Path, task: str) -> dict:
    """Events, agy JSON, and route suggestion the lanes left in the run dir, so `end` needs no flags."""
    rd = run_dir_for(log, task)
    found = {"codex_events": [], "agy_json": [], "suggestion": None}
    if not rd.exists():
        return found
    for f in sorted(rd.glob("*.jsonl")):
        if "events" in f.name:
            found["codex_events"].append(str(f))
    for f in sorted(rd.glob("*.json")):
        if f.name == "route-suggestion.json":
            try:
                found["suggestion"] = json.loads(f.read_text())
            except Exception:
                pass
        elif f.name.startswith("agy"):
            found["agy_json"].append(str(f))
    return found


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
    sm = session_model()
    rec = {
        "task": a.task, "arm": a.arm, "kind": a.kind, "started_at": now_iso(),
        "project": str(Path.cwd().resolve()), "head": head.strip(), "notes": a.notes or "",
        "model": a.model or sm["model"], "effort": a.effort or sm["effort"],
        "pools_before": snapshot_pools(),
    }
    sp.write_text(json.dumps(rec, indent=2))
    print(json.dumps({"started": a.task, "arm": a.arm, "model": rec["model"], "effort": rec["effort"], "pools_before": rec["pools_before"]}, indent=2))
    return 0


def cmd_end(a) -> int:
    log = log_path(a.log)
    sp = start_path(log, a.task)
    try:
        import lane_run  # noqa: E402
        disc = lane_run.summary(a.task, rd=run_dir_for(log, a.task))
        meta = disc.get("meta") or {}
    except Exception as e:
        disc, meta = {"_error": str(e)[:200]}, {}
    if not sp.exists():
        started_at = a.started_at or meta.get("started_at")
        if not started_at:
            print(f"no open start record for task {a.task} and no meta.json; `lane-worktree.py add` opens one, or pass --started-at ISO to backfill from logs", file=sys.stderr)
            return 1
        rc, head = sh(["git", "rev-parse", "--short", "HEAD"])
        rec = {"task": a.task, "arm": a.arm or meta.get("arm") or "tri-lane", "kind": a.kind or meta.get("kind") or "", "started_at": started_at,
               "project": meta.get("project") or str(Path.cwd().resolve()), "head": meta.get("head") or head.strip(),
               "notes": "backfilled from meta.json" if meta.get("started_at") and not a.started_at else "backfilled: no pools_before snapshot", "pools_before": {}}
        rec.update(session_model() if not (a.model_hint or a.effort_hint) else {"model": a.model_hint, "effort": a.effort_hint})
        sp.write_text(json.dumps(rec))
    rec = json.loads(sp.read_text())
    ended = a.ended_at or now_iso()
    started = rec["started_at"]
    if a.kind and not rec.get("kind"):
        rec["kind"] = a.kind
    if not rec.get("kind") and disc.get("kind"):
        rec["kind"] = disc["kind"]
    elapsed = (datetime.fromisoformat(ended) - datetime.fromisoformat(started)).total_seconds()

    rc, out = sh([sys.executable, str(HERE / "usage-window.py"), "--since", started, "--until", ended, "--project", rec["project"]], timeout=180)
    try:
        usage = json.loads(out)
    except Exception:
        usage = {"claude": {}, "codex": {}}

    found = discover_run_files(log, a.task)
    agy_files = list(a.agy_json or []) + [f for f in found["agy_json"] if f not in (a.agy_json or [])]
    codex_files = list(a.codex_events or []) + [f for f in found["codex_events"] if f not in (a.codex_events or [])]
    agy = {"input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0, "cache_read_tokens": 0, "total_tokens": 0, "calls": 0}
    for f in agy_files:
        u = parse_agy_json(f)
        if u:
            agy["calls"] += 1
            for k in ("input_tokens", "output_tokens", "thinking_tokens", "cache_read_tokens", "total_tokens"):
                agy[k] += u.get(k, 0)
    codex_lane = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0, "total_tokens": 0, "billable_tokens": 0, "calls": 0, "by_file": {}}
    for f in codex_files:
        u = parse_codex_events(f)
        codex_lane["calls"] += 1
        codex_lane["by_file"][Path(f).name] = u.get("billable_tokens", 0)
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

    route = a.route or disc.get("route") or ""
    lane = a.lane or disc.get("lane") or ""
    status = a.status or disc.get("status") or ""
    advisor = a.advisor or disc.get("advisor") or ("none" if disc.get("advisor_skip_reason") else "")
    rework_n = a.rework if a.rework is not None else int(disc.get("rework") or 0)
    escalated = bool(a.escalated or disc.get("escalated"))

    pools_after = snapshot_pools() if not a.ended_at else {"captured_at": ended, "skipped": True, "reason": "backfill"}
    deltas = {}
    for k, v in pools_after.items():
        b = rec["pools_before"].get(k)
        if isinstance(v, (int, float)) and isinstance(b, (int, float)):
            deltas[k.replace("_remaining", "").replace("_used_percent", "")] = round(v - b, 2) if "remaining" in k else round(v - b, 2)

    row = {
        **{k: rec[k] for k in ("task", "arm", "kind", "project", "head")},
        "started_at": started, "ended_at": ended, "elapsed_seconds": round(elapsed),
        "model": rec.get("model"), "effort": rec.get("effort"),
        "route": route, "route_reason": disc.get("route_reason"), "route_history": disc.get("route_history") or [],
        "lane": lane, "status": status, "advisor": advisor, "advisor_skip_reason": disc.get("advisor_skip_reason"),
        "suggested": found["suggestion"], "suggestion_followed": (bool(found["suggestion"]) and found["suggestion"].get("lane") and found["suggestion"]["lane"] in (lane or "")) or None,
        "rework": rework_n, "dispatches": disc.get("dispatches"), "escalated": escalated, "escaped_defects": 0, "window_checked_at": None,
        "gaps": disc.get("gaps") or [], "diff_lines": disc.get("diff_lines"), "verify": disc.get("verify"), "commit": disc.get("commit"),
        "claude": usage.get("claude", {}), "codex_account": usage.get("codex", {}),
        "codex_lane": codex_lane, "agy": agy,
        "findings": findings, "findings_labeled": bool(findings),
        "pools_before": rec["pools_before"], "pools_after": pools_after, "pool_deltas": deltas,
        "backfilled": bool(a.ended_at), "run_dir": disc.get("run_dir"),
        "notes": " ".join(x for x in (rec.get("notes"), a.notes) if x),
    }
    rows = read_log(log)
    rows = [r for r in rows if r.get("task") != a.task] + [row]
    write_log(log, rows)
    sp.unlink()
    summary = {
        "task": a.task, "arm": rec["arm"], "model": rec.get("model"), "elapsed_min": round(elapsed / 60, 1),
        "route": route, "lane": lane, "status": status, "advisor": advisor, "rework": rework_n, "dispatches": disc.get("dispatches"),
        "findings": "labeled" if findings else "unlabeled (pass --finding reviewer:C:D:U to lane-worktree remove or lane-log update)",
        "auto_discovered": {"codex_events": len(found["codex_events"]), "agy_json": len(found["agy_json"]), "suggestion": bool(found["suggestion"]),
                             "report": bool(disc.get("has_report")), "route": bool(disc.get("route")), "advisor": bool(disc.get("advisor"))},
        "claude_billable": row["claude"].get("billable_tokens"), "claude_cache_read": row["claude"].get("cache_read_input_tokens"),
        "codex_billable": codex_lane["billable_tokens"] or (row["codex_account"].get("billable_tokens") if rec["arm"] == "manual" else 0),
        "codex_total": codex_lane["total_tokens"], "agy_total": agy["total_tokens"],
        "defect_window_closes": (datetime.fromisoformat(ended) + timedelta(days=7)).date().isoformat(),
        "pool_deltas": deltas, "log": str(log),
    }
    print(json.dumps(summary, indent=2))
    return 0


def parse_spec(rd: Path) -> dict:
    """LANE / REASONING / OBJECTIVE / FILES / VERIFY from spec.md (the first version), for rows that predate report.json."""
    p = rd / "spec.md"
    if not p.exists():
        return {}
    out, section, files = {}, None, []
    import re
    for line in p.read_text(errors="ignore").splitlines():
        m = re.match(r"^\s*(LANE|REASONING|OBJECTIVE|FILES|INTERFACES|CONSTRAINTS|VERIFY)\b\s*[:\-—]?\s*(.*)$", line)
        if m:
            section = m.group(1)
            rest = m.group(2).strip()
            if section == "LANE":
                out["lane"] = (rest.split() or [""])[0].lower()
            elif section == "REASONING":
                out["reasoning"] = (rest.split() or [""])[0].lower()
            elif section == "OBJECTIVE":
                out["objective"] = rest[:240]
            elif section == "VERIFY":
                out["verify"] = rest.strip("`")
            elif section == "FILES" and rest:
                files.append(rest.strip("`- "))
            continue
        if section == "FILES" and line.strip():
            s = line.strip().lstrip("-*• ").strip("`")
            if s and " " not in s.split("(")[0].strip():
                files.append(s.split("(")[0].strip())
        elif section == "VERIFY" and line.strip() and not out.get("verify"):
            out["verify"] = line.strip().strip("`")
        elif section == "OBJECTIVE" and line.strip() and len(out.get("objective", "")) < 240:
            out["objective"] = (out.get("objective", "") + " " + line.strip())[:240].strip()
    if files:
        out["files"] = files[:40]
    return out


def infer_route(rd: Path, disc: dict, codex_calls: int, agy_calls: int) -> str:
    if disc.get("route"):
        return disc["route"]
    if codex_calls and agy_calls:
        return "full"
    if agy_calls:
        return "audit"
    if codex_calls:
        return "delegate"
    if disc.get("advisor"):
        return "advisor-only"
    return "docs"


def cmd_backfill(a) -> int:
    """T47: one benchmark row per run dir that has none, from what the run dir holds. Inferred fields are marked.
    Never overwrites a row the lifecycle wrote; re-runs replace only rows it wrote itself."""
    import importlib.util
    import lane_run  # noqa: E402
    from lane_failures import classify_run  # noqa: E402
    spec_u = importlib.util.spec_from_file_location("usage_window", HERE / "usage-window.py")
    uw = importlib.util.module_from_spec(spec_u); spec_u.loader.exec_module(uw)
    projects: dict = {}
    for proj, rd in lane_run.iter_run_dirs(all_projects=a.all_projects):
        projects.setdefault(proj, []).append(rd)
    total_written, report = 0, {}
    for proj, rds in projects.items():
        log = Path(a.log) if (a.log and not a.all_projects) else (proj / ".git" / "tri-lane" / "benchmark.jsonl")
        existing = read_log(log)
        live = {r["task"] for r in existing if not r.get("backfilled")}
        drafts, windows = [], []
        for rd in rds:
            task = rd.name
            if task in live:
                continue
            files = [p for p in rd.rglob("*") if p.is_file() and "tmp" not in p.relative_to(rd).parts]
            if not files:
                continue
            mt = {p: datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc) for p in files}
            spec_files = [p for p in files if p.name.startswith("spec")]
            started = min(mt[p] for p in (spec_files or files))
            end_files = [p for p in files if p.name.split(".")[0] in ("final", "review", "advisor", "agy", "report", "verify") or p.name.startswith(("final", "review", "advisor", "agy", "report", "events"))]
            ended = max(mt[p] for p in (end_files or files))
            if ended - started < timedelta(minutes=1):
                ended = started + timedelta(minutes=1)  # file mtimes can sit microseconds apart; a task is never shorter than a minute
            disc = lane_run.summary(task, rd=rd)
            found = {"codex_events": sorted(str(p) for p in rd.glob("*events*.jsonl")), "agy_json": sorted(str(p) for p in rd.glob("agy*.json"))}
            agy = {"input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0, "cache_read_tokens": 0, "total_tokens": 0, "calls": 0}
            for f in found["agy_json"]:
                u = parse_agy_json(f)
                if u:
                    agy["calls"] += 1
                    for k in ("input_tokens", "output_tokens", "thinking_tokens", "cache_read_tokens", "total_tokens"):
                        agy[k] += u.get(k, 0)
            codex_lane = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0, "total_tokens": 0, "billable_tokens": 0, "calls": 0, "by_file": {}}
            for f in found["codex_events"]:
                u = parse_codex_events(f)
                codex_lane["calls"] += 1
                codex_lane["by_file"][Path(f).name] = u.get("billable_tokens", 0)  # events.jsonl = implementer; review-events.jsonl = reviewer
                for k in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens", "billable_tokens"):
                    codex_lane[k] += u.get(k, 0)
            spec = parse_spec(rd)
            cls = classify_run(rd)
            lane = disc.get("lane") or (f"gpt-5.6-{spec['lane']} @ {spec.get('reasoning') or '?'}" if spec.get("lane") in ("luna", "sol") else (f"gemini-3.8-flash-high" if agy["calls"] and not codex_lane["calls"] else ""))
            status = disc.get("status") or (cls["state"] if cls.get("cause") else ("complete" if codex_lane["calls"] and cls["state"] == "unclassified" else (cls["state"] or "")))
            sugg = None
            try:
                sugg = json.loads((rd / "route-suggestion.json").read_text())
            except Exception:
                pass
            row = {
                "task": task, "arm": (disc.get("meta") or {}).get("arm") or "tri-lane", "kind": disc.get("kind") or "", "project": str(proj), "head": (disc.get("meta") or {}).get("head") or "",
                "started_at": started.isoformat(), "ended_at": ended.isoformat(), "elapsed_seconds": round((ended - started).total_seconds()),
                "model": None, "effort": None,
                "route": infer_route(rd, disc, codex_lane["calls"], agy["calls"]), "route_inferred": not disc.get("route"), "route_history": disc.get("route_history") or [],
                "lane": lane, "status": status, "status_inferred": not disc.get("status"), "cause": cls.get("cause"), "evidence_grade": cls.get("evidence_grade"),
                "advisor": disc.get("advisor") or "", "advisor_skip_reason": disc.get("advisor_skip_reason"),
                "suggested": sugg, "suggestion_followed": (bool(sugg) and sugg.get("lane") and sugg["lane"] in lane) or None,
                "rework": disc.get("rework") or 0, "dispatches": disc.get("dispatches") or 0, "escalated": bool(disc.get("escalated")),
                "escaped_defects": 0, "window_checked_at": None,
                "gaps": disc.get("gaps") or [], "diff_lines": disc.get("diff_lines"), "verify": disc.get("verify"), "commit": disc.get("commit"),
                "spec": spec, "codex_lane": codex_lane, "agy": agy, "codex_account": {},
                "findings": {}, "findings_labeled": False, "pools_before": {}, "pools_after": {}, "pool_deltas": {},
                "backfilled": True, "run_dir": str(rd), "notes": "backfilled from run dir; timestamps from file mtimes",
            }
            drafts.append(row)
            windows.append((started, ended))
        if not drafts:
            report[proj.name] = {"written": 0, "kept_live": len(live)}
            continue
        usages = uw.claude_usage_multi(str(proj), windows)
        for row, u in zip(drafts, usages):
            row["claude"] = u
        for i, row in enumerate(drafts):
            s1, e1 = windows[i]
            row["claude_overlap"] = sorted(d["task"] for j, d in enumerate(drafts) if j != i and windows[j][0] <= e1 and s1 <= windows[j][1])
        if not a.dry_run:
            keep = [r for r in existing if not r.get("backfilled") or r["task"] not in {d["task"] for d in drafts}]
            write_log(log, keep + drafts)
        total_written += len(drafts)
        report[proj.name] = {"written": len(drafts), "kept_live": len(live), "overlapped": sum(1 for d in drafts if d["claude_overlap"]),
                             "claude_measured": sum(1 for d in drafts if d["claude"].get("billable_tokens")), "log": str(log)}
    print(json.dumps({"rows": total_written, "dry_run": bool(a.dry_run), "projects": report}, indent=2))
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
        r["window_checked_at"] = now_iso()
    if a.notes:
        r["notes"] = (r.get("notes", "") + " " + a.notes).strip()
    for spec in a.finding or []:
        try:
            who, c, d, u = spec.split(":")
            r.setdefault("findings", {})[who] = {"confirmed": int(c), "disputed": int(d), "unverified": int(u)}
            r["findings_labeled"] = True
        except ValueError:
            print(f"bad --finding {spec!r}; expected reviewer:confirmed:disputed:unverified", file=sys.stderr)
            return 2
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


def cmd_due(a) -> int:
    """Tasks whose 7-day escaped-defect window has closed (or closes within --within days) and that
    have not been checked with `update --escaped-defects N` (0 counts as checked)."""
    log = log_path(a.log)
    now = datetime.now(timezone.utc)
    rows = []
    for r in read_log(log):
        if r.get("window_checked_at") or not r.get("ended_at"):
            continue
        closes = datetime.fromisoformat(r["ended_at"]) + timedelta(days=7)
        days = (closes - now).total_seconds() / 86400
        if days <= a.within:
            rows.append({"task": r["task"], "arm": r.get("arm"), "window_closes": closes.date().isoformat(), "days": round(days, 1)})
    if a.json:
        print(json.dumps(rows, indent=2))
    elif a.quiet:
        # SessionStart hook form (T51): one line per due window, nothing at all when none are due
        for r in rows:
            state = "closed" if r["days"] <= 0 else f"closes in {r['days']}d"
            print(f"tri-lane: defect window for {r['task']} {state}: lane-log.py update --task {r['task']} --escaped-defects N")
    else:
        for r in rows:
            state = "CLOSED" if r["days"] <= 0 else f"closes in {r['days']}d"
            print(f"{r['task']:24} {r['arm'] or '':13} {r['window_closes']}  {state}   -> lane-log.py update --task {r['task']} --escaped-defects N")
        print(f"{len(rows)} task(s) need a defect check")
    return 0


def cmd_list(a) -> int:
    log = log_path(a.log)
    rows = read_log(log)
    if a.json:
        print(json.dumps(rows, indent=2))
        return 0
    print(f"{'task':22} {'arm':13} {'model':16} {'kind':9} {'route':9} {'status':9} {'min':>6} {'claude_bill':>11} {'codex':>9} {'agy':>9} {'conf':>4} {'esc':>3}")
    for r in rows:
        conf = sum(v.get("confirmed", 0) for v in (r.get("findings") or {}).values())
        acct = r.get("codex_account") or r.get("codex_logs") or {}
        codex = (r.get("codex_lane") or {}).get("billable_tokens") or (acct.get("billable_tokens") if r.get("arm") == "manual" else 0) or 0
        print(f"{r.get('task',''):22} {r.get('arm',''):13} {(r.get('model') or '?')[:16]:16} {(r.get('kind') or ''):9} {(r.get('route') or ''):9} {(r.get('status') or ''):9} "
              f"{round(r.get('elapsed_seconds',0)/60):>6} {(r.get('claude') or {}).get('billable_tokens',0):>11} {codex:>9} {(r.get('agy') or {}).get('total_tokens',0):>9} {conf:>4} {r.get('escaped_defects',0):>3}")
    print(f"{len(rows)} tasks in {log}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", help="override the benchmark.jsonl path")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="snapshot pools and clock before a task")
    s.add_argument("--task", required=True)
    s.add_argument("--arm", required=True, choices=ARMS)
    s.add_argument("--kind", default="", help="impl | security | infra | debug | refactor | docs")
    s.add_argument("--model", help="override the session model recorded (default: ~/.claude/settings.json)")
    s.add_argument("--effort", help="override the session effort recorded")
    s.add_argument("--notes", default="")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_start)

    d = sub.add_parser("due", help="tasks whose 7-day defect window needs checking")
    d.add_argument("--within", type=float, default=0, help="also list windows closing within N days")
    d.add_argument("--json", action="store_true")
    d.add_argument("--quiet", action="store_true", help="hook form: one line per due window, silent when none")
    d.set_defaults(fn=cmd_due)

    e = sub.add_parser("end", help="close a task and append the benchmark line")
    e.add_argument("--task", required=True)
    e.add_argument("--started-at", help="backfill: ISO timestamp the task began (when neither `start` nor `lane-worktree add` ran). Pools_before will be empty")
    e.add_argument("--ended-at", help="backfill: ISO timestamp the task ended (default now). Marks the row backfilled and skips the pool snapshot")
    e.add_argument("--arm", choices=ARMS, help="only with --started-at")
    e.add_argument("--kind", help="only with --started-at")
    e.add_argument("--model-hint", help="backfill: session model to record when no start record exists")
    e.add_argument("--effort-hint", help="backfill: session effort to record when no start record exists")
    e.add_argument("--route", default="", help="solo | delegate | audit | full | manual (default: run dir route.json)")
    e.add_argument("--lane", default="", help='as executed, e.g. "gpt-5.6-luna @ high" (default: run dir report.json)')
    e.add_argument("--status", default="", help="complete | partial | refused | timeout | unavailable (default: run dir report.json)")
    e.add_argument("--advisor", default="", help="ship | fix-first | rethink | none (default: run dir advisor.md)")
    e.add_argument("--rework", type=int, default=None, help="spec corrections sent back (default: spec*.md count - 1)")
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
    u.add_argument("--finding", action="append", help="reviewer:confirmed:disputed:unverified (repeatable); label a row after the fact")
    u.set_defaults(fn=cmd_update)

    b = sub.add_parser("backfill", help="T47: one row per run dir with none, inferred fields marked; never overwrites lifecycle rows")
    b.add_argument("--from-run-dirs", action="store_true", required=True, help="the only source today")
    b.add_argument("--all-projects", action="store_true", help="every project under the Cure project roots (each writes its own benchmark.jsonl)")
    b.add_argument("--dry-run", action="store_true")
    b.set_defaults(fn=cmd_backfill)

    l = sub.add_parser("list", help="print the log")
    l.add_argument("--json", action="store_true")
    l.set_defaults(fn=cmd_list)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
