#!/usr/bin/env python3
"""lane_run: the run directory is the task's record. Everything the benchmark needs is read from files
the lanes already leave there, so `lane-log end` and `lane-worktree remove` need no flags (Wave 4, T42).

Files under $(git rev-parse --git-common-dir)/tri-lane/run/<task>/:
  meta.json          written once by `ensure()` (worktree add, route suggest/declare): started_at, base, kind, project, head
  route.json         append-only list of route declarations (`lane-route.py declare`); the last one is the route
  spec.md, spec-2.md …   one file per dispatch; rework = files - 1 (the implementer never overwrites)
  events*.jsonl      codex --json streams; dispatches = thread.started events
  report.json        the latest lane-report (report-<n>.json are earlier ones)
  verify.jsonl       one record per VERIFY command (T43)
  advisor.md         first line `VERDICT   ship|fix-first|rethink`
  agy*.json          Antigravity output
Python stdlib only. Importable and runnable: `python3 lane_run.py summary --task <slug>`.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

AUDIT_TRIGGERS = re.compile(
    r"(^|/)(firestore|storage|database)\.rules$|(^|/)migrations?/|(^|/)functions/|(^|/)\.github/workflows/|"
    r"(^|/)(auth|billing|payments?|stripe)[^/]*\.|/(auth|billing|payments?)/", re.I)
MANDATORY_DIFF_LINES = 150
DEFAULT_PROJECT_ROOTS = ("~/Documents/Cure-Consulting-Group", "~/CureVault/projects", "/Volumes/CureVault/projects")


def project_roots() -> list:
    """Directories whose immediate children are project checkouts. TRI_LANE_PROJECT_ROOTS (colon-separated) overrides."""
    env = os.environ.get("TRI_LANE_PROJECT_ROOTS", "")
    roots = [Path(x).expanduser() for x in (env.split(":") if env else DEFAULT_PROJECT_ROOTS) if x.strip()]
    seen, out = set(), []
    for r in roots:
        if r.exists():
            k = str(r.resolve())
            if k not in seen:
                seen.add(k); out.append(r.resolve())
    return out


def iter_run_dirs(all_projects: bool = False, cwd=None):
    """Yield (project_root, run_dir) for every task run dir: this repo's, or every project under the roots."""
    if not all_projects:
        gcd = git_common_dir(cwd)
        if gcd and (gcd / "tri-lane" / "run").exists():
            root = gcd.parent
            for d in sorted((gcd / "tri-lane" / "run").iterdir()):
                if d.is_dir():
                    yield root, d
        return
    for root in project_roots():
        for proj in sorted(root.iterdir()):
            runs = proj / ".git" / "tri-lane" / "run"
            if proj.is_dir() and runs.exists():
                for d in sorted(runs.iterdir()):
                    if d.is_dir():
                        yield proj, d


def sh(cmd, cwd=None, timeout=60, env=None) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL, env=env)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return 1, str(e)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_common_dir(cwd=None) -> Path | None:
    rc, out = sh(["git", "rev-parse", "--git-common-dir"], cwd=cwd)
    if rc != 0 or not out.strip():
        return None
    p = Path(out.strip())
    if not p.is_absolute():
        p = Path(cwd or os.getcwd()) / p
    return p.resolve()


def tri_lane_dir(cwd=None) -> Path:
    gcd = git_common_dir(cwd)
    base = gcd if gcd else Path(cwd or os.getcwd())
    d = base / "tri-lane"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_dir(task: str, cwd=None) -> Path:
    d = tri_lane_dir(cwd) / "run" / task
    (d / "tmp").mkdir(parents=True, exist_ok=True)
    return d


def task_from_worktree(wt: str | Path) -> str | None:
    """lane/<task> branch name, else the worktree directory name without a -ro suffix."""
    rc, out = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(wt))
    b = out.strip()
    if rc == 0 and b.startswith("lane/"):
        return b[5:].removesuffix("-salvage")
    name = Path(wt).name
    return name[:-3] if name.endswith("-ro") else (name or None)


# ---- meta / start ---------------------------------------------------------------------------------

def read_json(p: Path, default=None):
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def meta(task: str, cwd=None) -> dict:
    return read_json(run_dir(task, cwd) / "meta.json", {}) or {}


def write_meta(task: str, cwd=None, **updates) -> dict:
    p = run_dir(task, cwd) / "meta.json"
    m = read_json(p, {}) or {}
    m.update(updates)
    p.write_text(json.dumps(m, indent=2))
    return m


def ensure(task: str, kind: str | None = None, base: str | None = None, cwd=None, log: str | None = None, arm: str = "tri-lane") -> dict:
    """Create the run dir and meta.json on first sight of a task, and open its benchmark record.
    Idempotent: a second call changes nothing (kind/base fill in only if empty). Never raises."""
    rd = run_dir(task, cwd)
    p = rd / "meta.json"
    m = read_json(p, {}) or {}
    created = not m
    env_arm = os.environ.get("TRI_LANE_ARM", "").strip()
    if env_arm in ("manual", "tri-lane", "advisor-only", "tri-lane-lean"):
        arm = env_arm  # a lean-architect session logs itself apart from the arm under test (BENCHMARK.md)
    if created:
        rc, head = sh(["git", "rev-parse", "--short", "HEAD"], cwd=cwd)
        rc2, top = sh(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
        m = {"task": task, "started_at": now_iso(), "kind": kind or "", "base": base or "", "arm": arm,
             "project": (top.strip() if rc2 == 0 else str(Path(cwd or os.getcwd()).resolve())), "head": head.strip() if rc == 0 else ""}
    else:
        if kind and not m.get("kind"):
            m["kind"] = kind
        if base and not m.get("base"):
            m["base"] = base
    p.write_text(json.dumps(m, indent=2))
    # open the benchmark record; lane-log refuses a duplicate start, which is the idempotence we want
    try:
        args = [sys.executable, str(HERE / "lane-log.py")]
        if log:
            args += ["--log", log]
        args += ["start", "--task", task, "--arm", arm, "--kind", m.get("kind") or ""]
        rc, out = sh(args, cwd=m["project"] if Path(m["project"]).exists() else cwd, timeout=180)
        m["_log_started"] = rc == 0 or "already started" in out
    except Exception as e:  # never block a dispatch on bookkeeping
        m["_log_started"] = False
        m["_log_error"] = str(e)[:200]
    return {"run_dir": str(rd), "created": created, **{k: v for k, v in m.items()}}


# ---- discovery ------------------------------------------------------------------------------------

VERDICT_RX = re.compile(r"verdict\s*[:\-—]*\s*\**\s*(ship|fix-first|fix first|rethink)\b", re.I)


def advisor_verdict(rd: Path) -> str | None:
    """ship | fix-first | rethink from advisor.md; the first verdict word wins. Tolerates headings,
    code fences, and bold (every variant seen in production, 2026-09-13)."""
    p = Path(rd) / "advisor.md"
    if not p.exists():
        return None
    for line in p.read_text(errors="ignore").splitlines()[:40]:
        m = VERDICT_RX.search(line)
        if m:
            return m.group(1).lower().replace("fix first", "fix-first")
    return None


def route_history(rd: Path) -> list:
    v = read_json(Path(rd) / "route.json", [])
    return v if isinstance(v, list) else []


def latest_route(rd: Path) -> dict | None:
    h = route_history(rd)
    return h[-1] if h else None


def latest_report(rd: Path) -> dict | None:
    return read_json(Path(rd) / "report.json")


def verify_records(rd: Path) -> list:
    p = Path(rd) / "verify.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text(errors="ignore").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def spec_versions(rd: Path) -> list:
    rd = Path(rd)
    return sorted([p for p in rd.glob("spec*.md")], key=lambda p: (p.name != "spec.md", p.name))


def rework(rd: Path) -> int:
    return max(0, len(spec_versions(rd)) - 1)


def dispatches(rd: Path) -> int:
    n = 0
    for f in Path(rd).glob("*events*.jsonl"):
        try:
            n += sum(1 for l in open(f, errors="ignore") if '"thread.started"' in l)
        except OSError:
            pass
    return n


def diff_lines(report: dict | None) -> int:
    """insertions + deletions from the report's CHANGES stat line."""
    if not report:
        return 0
    m = re.findall(r"(\d+) (?:insertion|deletion)", report.get("CHANGES") or "")
    return sum(int(x) for x in m)


def mandatory_advisor(report: dict | None) -> list:
    """Why an advisor review may not be skipped for this diff (T45 tier). Empty list = skippable with a reason."""
    if not report:
        return []
    why = []
    if "sol" in (report.get("LANE") or "").lower():
        why.append("lane is Sol")
    n = diff_lines(report)
    if n > MANDATORY_DIFF_LINES:
        why.append(f"diff is {n} lines (> {MANDATORY_DIFF_LINES})")
    if report.get("OUT_OF_SCOPE"):
        why.append("lane touched files outside FILES")
    if report.get("EXEC_CONFIG_TOUCHED"):
        why.append("lane touched executable config")
    hits = [p for p in (report.get("TOUCHED") or []) if AUDIT_TRIGGERS.search(p)]
    if hits:
        why.append("audit-trigger paths: " + ", ".join(hits[:4]))
    return why


def has_lane_diff(report: dict | None) -> bool:
    return bool(report) and report.get("STATUS") in ("complete", "partial", "timeout") and bool(report.get("TOUCHED"))


def summary(task: str, cwd=None, rd=None) -> dict:
    """Everything the benchmark row can learn from the run dir without a human. `rd` overrides the run dir
    (lane-log passes the one next to its --log so the two never disagree)."""
    rd = Path(rd) if rd else run_dir(task, cwd)
    (rd / "tmp").mkdir(parents=True, exist_ok=True)
    m = read_json(rd / "meta.json", {}) or {}
    rep = latest_report(rd)
    rt = latest_route(rd)
    hist = route_history(rd)
    vr = verify_records(rd)
    return {
        "run_dir": str(rd),
        "meta": m,
        "route": (rt or {}).get("route"),
        "route_reason": (rt or {}).get("reason"),
        "route_history": [{"route": h.get("route"), "at": h.get("at")} for h in hist],
        "escalated": len({h.get("route") for h in hist}) > 1,
        "kind": m.get("kind") or (rt or {}).get("kind") or "",
        "lane": (rep or {}).get("LANE"),
        "status": (rep or {}).get("STATUS"),
        "gaps": (rep or {}).get("GAPS") or [],
        "commit": (rep or {}).get("COMMIT"),
        "touched": (rep or {}).get("TOUCHED") or [],
        "diff_lines": diff_lines(rep),
        "advisor": advisor_verdict(rd),
        "advisor_skip_reason": m.get("advisor_skip_reason"),
        "rework": rework(rd),
        "dispatches": dispatches(rd),
        "verify": {"commands": len(vr), "failed": sum(1 for v in vr if v.get("exit") not in (0, None)),
                    "timed_out": sum(1 for v in vr if v.get("timed_out")), "filtered": sum(1 for v in vr if v.get("filtered"))},
        "has_report": rep is not None,
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summary", help="what the run dir says about a task")
    s.add_argument("--task", required=True)
    e = sub.add_parser("ensure", help="create meta.json and open the benchmark record (idempotent)")
    e.add_argument("--task", required=True)
    e.add_argument("--kind", default="")
    e.add_argument("--base", default="")
    a = ap.parse_args()
    if a.cmd == "summary":
        print(json.dumps(summary(a.task), indent=2))
    else:
        print(json.dumps(ensure(a.task, a.kind or None, a.base or None), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
