#!/usr/bin/env python3
"""PERT roll-up and Monte Carlo confidence levels for a three-point estimate (technical-estimation).

Reads the Step 2 table as CSV (req_id, component, optimistic, likely, pessimistic, in hours) and,
optionally, the Step 6 risk register (risk, probability, impact_hours). Reports per task the PERT
expected value (O + 4M + P) / 6 and sigma (P - O) / 6; the roll-up with sigma in quadrature, not
summed; the reference-class adjusted total (Step 3); the risk reserve as its own line (Step 6, never
folded into the multiplier); and the P50/P80/P90 of a Monte Carlo over Beta-PERT task durations plus
Bernoulli risks. A fixed seed makes the run reproducible, so the numbers in a bid can be re-derived.

Usage:
    python3 pert_estimate.py --tasks tasks.csv
    python3 pert_estimate.py --tasks tasks.csv --risks risks.csv --reference-class 1.4 --rate 165 --json
    python3 pert_estimate.py --tasks tasks.csv --runs 20000 --seed 7 --percentiles 50,80,90,95

Smoke: --tasks {fixtures}/tasks.csv --risks {fixtures}/risks.csv --reference-class 1.4 --rate 165 --json

Exit: 0 success, 2 bad input or missing file.
"""
import argparse
import csv
import json
import math
import random
import sys


def fail(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def read_csv(path: str, need: list) -> list:
    try:
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except OSError as err:
        fail(f"cannot read {path}: {err.strerror}")
    if not rows:
        fail(f"{path} has no rows")
    missing = [c for c in need if c not in rows[0]]
    if missing:
        fail(f"{path} is missing column(s): {', '.join(missing)} (need {', '.join(need)})")
    return rows


def num(row: dict, key: str, path: str) -> float:
    try:
        return float(str(row[key]).replace(",", "").replace("%", "").strip())
    except ValueError:
        fail(f"{path}: {key} '{row[key]}' is not a number")


def load_tasks(path: str) -> list:
    tasks = []
    for r in read_csv(path, ["req_id", "component", "optimistic", "likely", "pessimistic"]):
        o, m, p = num(r, "optimistic", path), num(r, "likely", path), num(r, "pessimistic", path)
        if not (0 <= o <= m <= p):
            fail(f"{path}: {r['req_id']} needs 0 <= optimistic <= likely <= pessimistic (got {o}, {m}, {p})")
        tasks.append({"req_id": r["req_id"], "component": r["component"], "o": o, "m": m, "p": p,
                      "pert": (o + 4 * m + p) / 6, "sigma": (p - o) / 6})
    return tasks


def load_risks(path: str) -> list:
    risks = []
    for r in read_csv(path, ["risk", "probability", "impact_hours"]):
        prob = num(r, "probability", path)
        prob = prob / 100 if prob > 1 or str(r["probability"]).strip().endswith("%") else prob
        if not 0 <= prob <= 1:
            fail(f"{path}: probability for '{r['risk']}' must be 0-1 or 0-100")
        impact = num(r, "impact_hours", path)
        risks.append({"risk": r["risk"], "probability": prob, "impact_hours": impact, "expected_hours": prob * impact})
    return risks


def beta_pert(rng: random.Random, o: float, m: float, p: float) -> float:
    if p == o:
        return o
    a = 1 + 4 * (m - o) / (p - o)
    b = 1 + 4 * (p - m) / (p - o)
    return o + rng.betavariate(a, b) * (p - o)


def percentile(sorted_xs: list, q: float) -> float:
    k = (len(sorted_xs) - 1) * q / 100
    lo, hi = math.floor(k), math.ceil(k)
    return sorted_xs[lo] if lo == hi else sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (k - lo)


def main() -> None:
    ap = argparse.ArgumentParser(description="PERT roll-up, reference-class adjustment, risk reserve and Monte Carlo P50/P80/P90 from a three-point estimate.")
    ap.add_argument("--tasks", required=True, help="CSV with req_id, component, optimistic, likely, pessimistic (hours)")
    ap.add_argument("--risks", help="CSV with risk, probability (0-1 or %%), impact_hours: risks absent from the reference class")
    ap.add_argument("--reference-class", type=float, default=1.0, help="outside-view multiplier on the bottom-up total (Step 3), e.g. 1.4; default 1.0 = none")
    ap.add_argument("--rate", type=float, help="blended hourly rate, to add cost columns")
    ap.add_argument("--runs", type=int, default=10000, help="Monte Carlo iterations (default 10000)")
    ap.add_argument("--seed", type=int, default=7, help="random seed, so the run is reproducible (default 7)")
    ap.add_argument("--percentiles", default="50,80,90", help="confidence levels to report (default 50,80,90)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()
    if a.reference_class <= 0:
        fail("--reference-class must be positive")
    if not 100 <= a.runs <= 1_000_000:
        fail("--runs must be between 100 and 1000000")
    try:
        qs = [float(x) for x in a.percentiles.split(",") if x.strip()]
    except ValueError:
        fail("--percentiles must be numbers, e.g. 50,80,90")
    if not qs or any(not 0 < q < 100 for q in qs):
        fail("--percentiles must be between 0 and 100")

    tasks = load_tasks(a.tasks)
    risks = load_risks(a.risks) if a.risks else []
    bottom_up = sum(t["pert"] for t in tasks)
    sigma = math.sqrt(sum(t["sigma"] ** 2 for t in tasks))
    adjusted = bottom_up * a.reference_class
    reserve = sum(r["expected_hours"] for r in risks)

    rng = random.Random(a.seed)
    totals = []
    for _ in range(a.runs):
        work = sum(beta_pert(rng, t["o"], t["m"], t["p"]) for t in tasks) * a.reference_class
        hit = sum(r["impact_hours"] for r in risks if rng.random() < r["probability"])
        totals.append(work + hit)
    totals.sort()
    levels = {f"P{q:g}": round(percentile(totals, q), 1) for q in qs}

    out = {
        "tasks": [{k: (round(v, 1) if isinstance(v, float) else v) for k, v in t.items()} for t in tasks],
        "bottom_up_pert_hours": round(bottom_up, 1),
        "sigma_hours": round(sigma, 1),
        "range_95_hours": [round(bottom_up - 2 * sigma, 1), round(bottom_up + 2 * sigma, 1)],
        "reference_class_multiplier": a.reference_class,
        "reference_class_adjusted_hours": round(adjusted, 1),
        "risks": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()} for r in risks],
        "risk_reserve_hours": round(reserve, 1),
        "point_estimate_hours": round(adjusted + reserve, 1),
        "monte_carlo": {"runs": a.runs, "seed": a.seed, "hours": levels},
    }
    if a.rate:
        out["rate"] = a.rate
        out["point_estimate_cost"] = round((adjusted + reserve) * a.rate, 2)
        out["monte_carlo"]["cost"] = {k: round(v * a.rate, 2) for k, v in levels.items()}
    if a.json:
        print(json.dumps(out, indent=2))
        return

    print(f"{'Req':<8} {'Component':<34} {'O':>7} {'M':>7} {'P':>7} {'PERT':>8} {'σ':>7}")
    for t in tasks:
        print(f"{t['req_id']:<8} {t['component'][:34]:<34} {t['o']:>7.0f} {t['m']:>7.0f} {t['p']:>7.0f} {t['pert']:>8.1f} {t['sigma']:>7.1f}")
    print(f"\nBottom-up PERT       {bottom_up:>10,.1f} h   σ {sigma:,.1f} h (in quadrature)   ~95%: {bottom_up - 2 * sigma:,.0f}–{bottom_up + 2 * sigma:,.0f} h")
    print(f"× reference class {a.reference_class:<4g}{adjusted:>10,.1f} h")
    print(f"+ risk reserve       {reserve:>10,.1f} h   ({len(risks)} named risk(s), outside the reference class)")
    print(f"= point estimate     {adjusted + reserve:>10,.1f} h" + (f"   ${(adjusted + reserve) * a.rate:,.0f}" if a.rate else ""))
    print(f"\nMonte Carlo ({a.runs:,} runs, seed {a.seed}): " + "   ".join(
        f"{k} {v:,.0f} h" + (f" (${v * a.rate:,.0f})" if a.rate else "") for k, v in levels.items()))


if __name__ == "__main__":
    main()
