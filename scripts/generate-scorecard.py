#!/usr/bin/env python3
"""generate-scorecard.py — One-page library health rollup (T35).

Writes SCORECARD.md: one row per metrics layer, each derived from its owning
tool. THIS is the headline quality number — the conformance audit is one row,
not the story. Layers without data yet say so honestly instead of vanishing.

  conformance   audit-library.py mean (spec + prose coherence + calibration)
  effectiveness latest skill-mode eval sweep (evals/results/*-skill.json)
  usage         usage-report.py trailing-90d coverage
  fleet         fleet-census.py (needs --projects-dir; cached last result)
  outcome       manual for now — wave cycle time from BACKLOG resolution tables

Stdlib only. --help / --json. Run by nightly drift + before releases.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLEET_CACHE = Path.home() / ".cure" / "telemetry" / "fleet-last.json"


def run_json(args):
    try:
        r = subprocess.run([sys.executable] + args, capture_output=True, text=True,
                           cwd=ROOT, timeout=120)
        return json.loads(r.stdout)
    except Exception:
        return None


def conformance():
    d = run_json(["scripts/audit-library.py", "--json"])
    if not d:
        return ("no data", "audit failed to run")
    m = d["summary"]["mean"]
    return (f"{m}/10", f"{d['summary']['items']} items; includes prose-coherence lint + eval calibration cap")


def effectiveness():
    files = sorted((ROOT / "evals" / "results").glob("*-skill.json"))
    if not files:
        return ("no data", "no skill-mode sweep yet — run scripts/run-evals.py --mode skill")
    res = json.loads(files[-1].read_text())
    rates = [v["pass_rate"] for k, v in res["summary"].items() if k.endswith("|on")]
    offr = [v["pass_rate"] for k, v in res["summary"].items() if k.endswith("|off")]
    if not rates:
        return ("no data", "sweep file has no on-arm results")
    delta = (sum(rates) / len(rates)) - (sum(offr) / len(offr) if offr else 0)
    return (f"{sum(rates)/len(rates):.0%} pass (Δ{delta:+.0%} vs skill-off)",
            f"sweep {res['stamp']}, {len(rates)} task-arms")


def usage():
    d = run_json(["scripts/usage-report.py", "--json"])
    if not d or d["total_invocations"] == 0:
        return ("no data", "telemetry hook just installed — data accrues with use")
    return (f"{d['skills_used']}/{d['skills_total']} skills used, {d['total_invocations']} invocations/90d",
            f"{len(d['never_invoked'])} never-invoked (prune candidates after 2 dark quarters)")


def fleet():
    if not FLEET_CACHE.exists():
        return ("no data", "run scripts/fleet-census.py --projects-dir <dir> (cached here)")
    d = json.loads(FLEET_CACHE.read_text())
    rows = d["projects"]
    plugin = sum(1 for r in rows if r["mode"] == "plugin")
    drift = sum(1 for r in rows if r["drifted_count"])
    return (f"{plugin}/{len(rows)} projects on plugin mode, {drift} with drift",
            f"censused vs v{d['library_version']}; canary: " +
            (", ".join(r["project"] for r in rows if r.get("channel") == "next") or "none"))


def outcome():
    return ("manual", "wave cycle time + rework rate — reviewed at quarterly re-eval")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    layers = {
        "Conformance": conformance(),
        "Effectiveness": effectiveness(),
        "Usage": usage(),
        "Fleet": fleet(),
        "Outcome": outcome(),
    }
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [
        "# SCORECARD (generated — do not edit)",
        "",
        f"_Regenerated {stamp} by `scripts/generate-scorecard.py`. This rollup is the",
        "headline quality signal; no single row (especially conformance) is the story._",
        "",
        "| Layer | Current | Notes |",
        "|---|---|---|",
    ]
    for name, (val, note) in layers.items():
        md.append(f"| {name} | {val} | {note} |")
    md += ["",
           "Definition of sound (Wave 3): every skill measured or marked for pruning;",
           "every project on a manifested current version; every guardrail enforced or",
           "labeled advisory; no load-bearing prose without a lint."]
    (ROOT / "SCORECARD.md").write_text("\n".join(md) + "\n")
    if args.json:
        print(json.dumps({k: {"value": v[0], "note": v[1]} for k, v in layers.items()}, indent=2))
    else:
        print("wrote SCORECARD.md")
    return 0


if __name__ == "__main__":
    main()
