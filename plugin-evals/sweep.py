#!/usr/bin/env python3
"""sweep.py — n>=3 with/without-skill delta sweep over the top skills by traffic (T85).

Picks the top N plugin-evals-covered skills by observed traffic, runs every case tagged with
those skills through `claude plugin eval` in both arms (WITH plugin / W/OUT plugin) at n>=3
runs per arm under one total cost cap, then writes:

  evals/results/<stamp>-skill.json   run-evals.py's results format (key case|claude|on|off),
                                     plus `skill_deltas`, `selection`, `costUsd`, `partial`
  evals/RESULTS.md                   the existing scoreboard table + a per-skill delta table
                                     + the delta~0 list for T88

Traffic (see plugin-evals/SWEEP.md): per skill, the max of (a) T35 telemetry
~/.cure/telemetry/skill-usage.jsonl and (b) Skill tool calls found in local Claude Code
transcripts under ~/.claude/projects, within --days. Max, not sum, because the T35 hook and the
transcript record the same invocation. Ties (and every skill with no traffic) fall back to the
T85 risk list, then to case count. Only skills with at least one case can be swept; high-traffic
skills with no case are reported so a case can be written.

Every eval run is a real model call billed to the account. --dry-run spends nothing.
Stdlib only. --help / --json.
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS_DIR = ROOT / "evals" / "results"
RESULTS_MD = ROOT / "evals" / "RESULTS.md"
PLUGIN = "cure-product-engineering"

# T85 scope, in ticket order: where the risk is. Used to rank skills with equal traffic.
RISK_ORDER = [
    "security-review", "compliance-architect", "qsbs-compliance", "data-migration",
    "return-review", "tax-preparation", "public-sector-contracting", "engagement-automation",
    "cure-infra-bootstrap", "nextjs-feature-scaffold",
    # T81 rewritten triggers (routing cases)
    "firebase-architect", "database-architect", "finops", "performance-review",
    "product-manager", "project-manager", "legal-doctrine", "legal-research", "design-studio",
]
FLAT = 0.05  # |delta| below this is "delta ~ 0" (a T88 prune/rework candidate)


def load_checker():
    spec = importlib.util.spec_from_file_location("check_plugin_evals", ROOT / "scripts" / "check-plugin-evals.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def coverage():
    """skill -> [case names], from the same parser the CI validator uses."""
    chk = load_checker()
    errors, summary = chk.check(chk.eval_dir())
    if errors:
        sys.exit("plugin-evals invalid (run scripts/check-plugin-evals.py):\n  " + "\n  ".join(errors))
    cov = {}
    for s in summary:
        for t in s["tags"]:
            if t not in chk.NON_SKILL_TAGS:
                cov.setdefault(t, []).append(s["case"])
    return cov, chk.skill_names()


def norm(name, library):
    name = name.split(":", 1)[1] if name.startswith(PLUGIN + ":") else name
    return name if name in library else None


def telemetry_counts(path, since, library):
    c = Counter()
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    ts = datetime.fromisoformat(r.get("ts", "")).replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue
                s = norm(r.get("skill", ""), library)
                if s and ts >= since:
                    c[s] += 1
    except OSError:
        pass
    return c


SKILL_CALL = re.compile(r'"name"\s*:\s*"Skill"\s*,\s*"input"\s*:\s*\{\s*"skill"\s*:\s*"([^"]+)"')


def transcript_counts(base, since, library):
    c = Counter()
    if not base.is_dir():
        return c
    cutoff = since.timestamp()
    for p in base.rglob("*.jsonl"):
        try:
            if p.stat().st_mtime < cutoff:
                continue
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if '"Skill"' not in line:
                        continue
                    for m in SKILL_CALL.finditer(line):
                        s = norm(m.group(1), library)
                        if s:
                            c[s] += 1
        except OSError:
            continue
    return c


def select(args, cov, library):
    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    tel = telemetry_counts(Path(os.path.expanduser(args.telemetry)), since, library) if args.traffic in ("telemetry", "both") else Counter()
    trn = transcript_counts(Path(os.path.expanduser(args.transcripts)), since, library) if args.traffic in ("transcripts", "both") else Counter()
    traffic = {s: max(tel.get(s, 0), trn.get(s, 0)) for s in set(tel) | set(trn)}
    risk = {s: i for i, s in enumerate(RISK_ORDER)}
    ranked = sorted(cov, key=lambda s: (-traffic.get(s, 0), risk.get(s, len(RISK_ORDER)), -len(cov[s]), s))
    if args.skills:
        chosen = [s for s in args.skills.split(",") if s]
        missing = [s for s in chosen if s not in cov]
        if missing:
            sys.exit(f"no plugin-evals case is tagged with: {', '.join(missing)}")
    else:
        chosen = ranked[: args.top]
    uncovered = sorted(((s, n) for s, n in traffic.items() if s not in cov), key=lambda x: -x[1])
    rows = [{"skill": s, "traffic": traffic.get(s, 0), "telemetry": tel.get(s, 0), "transcripts": trn.get(s, 0),
             "risk_rank": risk.get(s), "cases": sorted(cov[s]),
             "basis": "traffic" if traffic.get(s, 0) else ("T85 risk list" if s in risk else "case count")}
            for s in chosen]
    return rows, uncovered


def build_cmd(args, skills, out_json):
    cmd = ["claude", "plugin", "eval", str(ROOT),
           "--runs", str(args.runs), "--ablation", "with-without",
           "--trust-plugin", "--scaffold", "--no-publish",
           "--threshold", "0",  # the sweep measures delta; it does not gate
           "-j", str(args.concurrency),
           "--max-cost-usd", str(args.max_cost_usd),
           "--output-dir", str(out_json.parent)]
    if args.model:
        cmd += ["--model", args.model]
    if args.judge_model:
        cmd += ["--judge-model", args.judge_model]
    # list-valued flags last so they can't swallow the target (docs: target before --tag/--allow-tools)
    cmd += ["--allow-tools", *args.allow_tools, "--tag", *skills]
    return cmd


def wilson(p, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (round(max(0, center - half), 3), round(min(1, center + half), 3))


def run_score(r):
    for k in ("score", "weightedScore"):
        if isinstance(r.get(k), (int, float)):
            return float(r[k])
    g = [x for x in (r.get("graders") or r.get("graderResults") or []) if x.get("scored", True)]
    if g:
        return sum(1.0 for x in g if x.get("passed")) / len(g)
    return 0.0


def convert(agg, rows):
    """aggregate-result.json -> run-evals.py results dict (+ skill_deltas)."""
    summary, runs, per_case = {}, [], {}
    for c in agg.get("cases", []):
        name = c.get("name")
        arms = c.get("arms") or {}
        means = {}
        for arm, label in (("with", "on"), ("without", "off")):
            rs = arms.get(arm) or []
            if not rs:
                continue
            scores = [run_score(r) for r in rs]
            p = sum(scores) / len(scores)
            means[label] = p
            summary[f"{name}|claude|{label}"] = {"pass_rate": round(p, 3), "n": len(scores), "ci95": wilson(p, len(scores)),
                                                 # flaky = run scores disagree across reps (the run-evals meaning)
                                                 "flaky": len(set(scores)) > 1}
            for r, s in zip(rs, scores):
                runs.append({"task": name, "backend": "claude", "skill": label == "on", "pass": s >= 1.0,
                             "score": s, "status": "error" if r.get("error") else "graded",
                             "error": r.get("error"), "skippedPaidGraders": bool(r.get("skippedPaidGraders"))})
        n_min = min((summary[f"{name}|claude|{l}"]["n"] for l in means), default=0)
        delta = (c.get("aggregates") or {}).get("delta")
        if delta is None and {"on", "off"} <= set(means):
            delta = means["on"] - means["off"]
        per_case[name] = {"delta": delta, "n_min": n_min}
    skill_deltas = {}
    for row in rows:
        ds = [per_case[c] for c in row["cases"] if c in per_case and per_case[c]["delta"] is not None]
        if ds:
            skill_deltas[row["skill"]] = {"delta": round(sum(d["delta"] for d in ds) / len(ds), 3),
                                          "cases": len(ds), "n_min": min(d["n_min"] for d in ds)}
    return summary, runs, skill_deltas


def render_md(res):
    md = ["# Eval Results (generated — do not edit)", "",
          f"Latest sweep: `{res['stamp']}` mode=`{res['mode']}` source=`claude plugin eval` (plugin-evals/sweep.py)"
          + (f" — **PARTIAL ({res.get('partialReason') or 'unknown'})**" if res.get("partial") else ""), "",
          "| key (task\\|backend\\|arm) | pass rate | n | 95% CI | flaky |", "|---|---|---|---|---|"]
    for k, v in sorted(res["summary"].items()):
        ci = v.get("ci95", ("—", "—"))
        md.append(f"| {k} | {v['pass_rate']:.0%} | {v['n']} | [{ci[0]}, {ci[1]}] | {'⚠️' if v.get('flaky') else ''} |")
    md += ["", "_Deltas require n≥3 per arm; single-rep results are directional only (t07, 2026-08-14)._",
           "_`pass rate` here is the mean run score (fraction of scored graders passed); `on` = WITH plugin, "
           "`off` = W/OUT. `tool_used: Skill` graders are indicators, not scored, in two-arm runs._"]
    sd = res.get("skill_deltas") or {}
    if sd:
        md += ["", "## Skill on/off deltas", "", "| skill | Δ pass rate | cases | min n/arm |", "|---|---|---|---|"]
        for s, d in sorted(sd.items(), key=lambda x: -x[1]["delta"]):
            low = "" if d["n_min"] >= 3 else " (n<3: directional)"
            md.append(f"| {s} | {d['delta']:+.0%}{low} | {d['cases']} | {d['n_min']} |")
        flat = sorted(s for s, d in sd.items() if abs(d["delta"]) < FLAT and d["n_min"] >= 3)
        neg = sorted(s for s, d in sd.items() if d["delta"] <= -FLAT and d["n_min"] >= 3)
        md += ["", f"### Δ≈0 (|Δ| < {FLAT:.0%}) — T88 candidates", ""]
        md += [f"- {s}" for s in flat] or ["- (none)"]
        if neg:
            md += ["", "### Δ < 0 — the plugin made these worse", ""] + [f"- {s}" for s in neg]
    md += ["", f"Cost: ${res.get('costUsd', 0):.2f} (list-price estimate) · claude {res.get('claudeVersion', '?')}"]
    return "\n".join(md) + "\n"


def write(res, results_dir, results_md):
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / f"{res['stamp']}-skill.json"
    path.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    results_md.write_text(render_md(res), encoding="utf-8")
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 epilog="Example: python3 plugin-evals/sweep.py --dry-run  |  "
                                        "python3 plugin-evals/sweep.py --max-cost-usd 150")
    ap.add_argument("--top", type=int, default=20, help="skills to sweep (default 20)")
    ap.add_argument("--skills", help="comma-separated skills to sweep instead of the traffic ranking")
    ap.add_argument("--runs", type=int, default=3, help="runs per arm (default 3; <3 refused without --allow-low-n)")
    ap.add_argument("--allow-low-n", action="store_true", help="permit --runs <3 (results are directional only)")
    ap.add_argument("--max-cost-usd", type=float, default=150.0, help="TOTAL cost ceiling for the whole sweep (default 150)")
    ap.add_argument("--est-run-usd", type=float, default=0.45, help="per-run cost used for the --dry-run estimate")
    ap.add_argument("-j", "--concurrency", type=int, default=4, help="parallel agent runs, 1-8 (default 4)")
    ap.add_argument("--model", help="pin the agent model (recommended so deltas compare across sweeps)")
    ap.add_argument("--judge-model", help="judge for llm graders (none ship today)")
    ap.add_argument("--allow-tools", nargs="+", default=["Write", "Edit", "Bash(python3 *)", "Bash(ls *)", "Bash(grep *)"],
                    help="tool grants passed to claude plugin eval")
    ap.add_argument("--traffic", choices=["both", "telemetry", "transcripts", "none"], default="both")
    ap.add_argument("--telemetry", default="~/.cure/telemetry/skill-usage.jsonl")
    ap.add_argument("--transcripts", default="~/.claude/projects")
    ap.add_argument("--days", type=int, default=90, help="traffic window (default 90)")
    ap.add_argument("--from-result", metavar="JSON", help="skip running; convert an existing aggregate-result.json")
    ap.add_argument("--results-dir", default=str(RESULTS_DIR), help="where <stamp>-skill.json goes (default evals/results)")
    ap.add_argument("--results-md", default=str(RESULTS_MD), help="scoreboard to regenerate (default evals/RESULTS.md)")
    ap.add_argument("--dry-run", action="store_true", help="print the selection, estimate, and command; spend nothing")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    if args.runs < 3 and not args.allow_low_n:
        sys.exit("--runs must be >=3 for a delta that counts (T85); pass --allow-low-n for a directional run")

    cov, library = coverage()
    rows, uncovered = select(args, cov, library)
    skills = [r["skill"] for r in rows]
    n_cases = len({c for r in rows for c in r["cases"]})
    est = n_cases * args.runs * 2 * args.est_run_usd
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    out_dir = HERE / "results" / f"sweep-{stamp}"
    cmd = build_cmd(args, skills, out_dir / "aggregate-result.json")
    plan = {"skills": rows, "cases": n_cases, "runs_per_arm": args.runs, "agent_runs": n_cases * args.runs * 2,
            "estimate_usd": round(est, 2), "max_cost_usd": args.max_cost_usd,
            "uncovered_traffic": uncovered[:10], "command": cmd}

    if args.dry_run:
        if args.json:
            print(json.dumps(plan, indent=2))
        else:
            print(f"{'skill':28} {'traffic':>7} {'basis':14} cases")
            for r in rows:
                print(f"{r['skill']:28} {r['traffic']:>7} {r['basis']:14} {len(r['cases'])}")
            print(f"\n{n_cases} cases x {args.runs} runs x 2 arms = {n_cases * args.runs * 2} agent runs; "
                  f"estimate ${est:.0f} at ${args.est_run_usd}/run; hard cap ${args.max_cost_usd:.0f}")
            if uncovered:
                print("High-traffic skills with no case (write one): "
                      + ", ".join(f"{s} ({n})" for s, n in uncovered[:10]))
            print("\n" + " ".join(f"'{c}'" if (" " in c or "*" in c) else c for c in cmd))
        return

    if args.from_result:
        agg_path = Path(args.from_result)
        code = 0
    else:
        if subprocess.run(["git", "--version"], capture_output=True).returncode == 0:
            v = re.search(r"(\d+)\.(\d+)", subprocess.run(["git", "--version"], capture_output=True, text=True).stdout)
            if v and (int(v.group(1)), int(v.group(2))) < (2, 31):
                sys.exit(f"git {v.group(0)} is too old: claude plugin eval needs git >=2.31")
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Sweeping {len(skills)} skills / {n_cases} cases, cap ${args.max_cost_usd:.0f} …", file=sys.stderr)
        code = subprocess.run(cmd, cwd=ROOT).returncode
        agg_path = out_dir / "aggregate-result.json"
        if code not in (0, 1, 2) or not agg_path.exists():
            sys.exit(f"claude plugin eval exited {code} and wrote no {agg_path}")
    agg = json.loads(agg_path.read_text(encoding="utf-8"))
    if args.from_result and agg.get("startedAt"):
        stamp = datetime.fromisoformat(agg["startedAt"].replace("Z", "+00:00")).strftime("%Y-%m-%d-%H%M")
    summary, runs, skill_deltas = convert(agg, rows)
    res = {"mode": "skill", "stamp": stamp, "source": "claude plugin eval (plugin-evals/sweep.py)",
           "summary": summary, "runs": runs, "skill_deltas": skill_deltas, "selection": rows,
           "partial": bool(agg.get("partial")), "partialReason": agg.get("partialReason"),
           "costUsd": agg.get("costUsd", 0), "claudeVersion": agg.get("claudeVersion"),
           "aggregate": str(agg_path)}
    results_md = Path(args.results_md)
    path = write(res, Path(args.results_dir), results_md)
    flat = sorted(s for s, d in skill_deltas.items() if abs(d["delta"]) < FLAT and d["n_min"] >= 3)
    if args.json:
        print(json.dumps({"results": str(path), "skill_deltas": skill_deltas, "flat_for_T88": flat,
                          "partial": res["partial"], "costUsd": res["costUsd"], "eval_exit": code}, indent=2))
    else:
        for s, d in sorted(skill_deltas.items(), key=lambda x: -x[1]["delta"]):
            print(f"{s:28} Δ {d['delta']:+.2f}  ({d['cases']} cases, n≥{d['n_min']})")
        print(f"\nWrote {path} and {results_md}; "
              f"Δ≈0 for T88: {', '.join(flat) or 'none'}; cost ${res['costUsd']:.2f}"
              + ("; PARTIAL" if res["partial"] else ""))
    sys.exit(2 if res["partial"] else 0)


if __name__ == "__main__":
    main()
