#!/usr/bin/env python3
"""Engineering cost estimator — dev hours x rate + infra spend over duration.

Usage:
  python3 cost_estimator.py --hours 400 --rate 175 --infra-monthly 250 --duration-months 6
  python3 cost_estimator.py --hours 400 --rate 175 --infra-monthly 250 \\
      --duration-months 6 --pm-pct 10 --qa-pct 15 --contingency-pct 15 --json

Inputs (all numbers):
  --hours              Estimated development hours.
  --rate               Hourly rate ($/hr).
  --infra-monthly      Monthly infra/services cost ($/month).
  --duration-months    Project duration (months).
  --pm-pct             Project management overhead % (default 10).
  --qa-pct             Testing/QA overhead % (default 15).
  --contingency-pct    Contingency on top of subtotal % (default 0).

Output: development cost, overhead, infra total, contingency, grand total.
"""
from __future__ import annotations

import argparse
import json
import sys


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


def nonneg(name: str, v: float) -> float:
    if v < 0:
        raise SystemExit(f"error: --{name} must be >= 0 (got {v})")
    return v


def main() -> int:
    p = argparse.ArgumentParser(
        description="Estimate total engineering project cost: hours x rate + overhead + infra.")
    p.add_argument("--hours", type=float, required=True, help="Development hours")
    p.add_argument("--rate", type=float, required=True, help="Hourly rate in USD")
    p.add_argument("--infra-monthly", type=float, required=True,
                   help="Monthly infra/services cost in USD")
    p.add_argument("--duration-months", type=float, required=True,
                   help="Project duration in months")
    p.add_argument("--pm-pct", type=float, default=10.0,
                   help="Project management overhead %% of dev cost (default 10)")
    p.add_argument("--qa-pct", type=float, default=15.0,
                   help="QA/testing overhead %% of dev cost (default 15)")
    p.add_argument("--contingency-pct", type=float, default=0.0,
                   help="Contingency %% on subtotal (default 0)")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args()

    for name in ("hours", "rate", "infra_monthly", "duration_months",
                 "pm_pct", "qa_pct", "contingency_pct"):
        nonneg(name.replace("_", "-"), getattr(args, name))

    dev_cost = args.hours * args.rate
    pm_cost = dev_cost * (args.pm_pct / 100.0)
    qa_cost = dev_cost * (args.qa_pct / 100.0)
    infra_total = args.infra_monthly * args.duration_months
    subtotal = dev_cost + pm_cost + qa_cost + infra_total
    contingency = subtotal * (args.contingency_pct / 100.0)
    total = subtotal + contingency
    blended_hours = args.hours * (1 + args.pm_pct / 100.0 + args.qa_pct / 100.0)

    result = {
        "inputs": {
            "hours": args.hours,
            "rate": args.rate,
            "infra_monthly": args.infra_monthly,
            "duration_months": args.duration_months,
            "pm_pct": args.pm_pct,
            "qa_pct": args.qa_pct,
            "contingency_pct": args.contingency_pct,
        },
        "development_cost": round(dev_cost, 2),
        "pm_overhead": round(pm_cost, 2),
        "qa_overhead": round(qa_cost, 2),
        "infra_total": round(infra_total, 2),
        "subtotal": round(subtotal, 2),
        "contingency": round(contingency, 2),
        "grand_total": round(total, 2),
        "blended_hours": round(blended_hours, 1),
        "monthly_burn": round(total / args.duration_months, 2) if args.duration_months > 0 else 0.0,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        def line(label: str, val: float) -> str:
            return f"{label:<28}{'$':>1}{val:>14,.2f}"
        print("ENGINEERING COST ESTIMATE")
        print("=" * 46)
        print(line("Development", dev_cost))
        print(line(f"PM overhead ({args.pm_pct:g}%)", pm_cost))
        print(line(f"QA overhead ({args.qa_pct:g}%)", qa_cost))
        print(line(f"Infra ({args.duration_months:g} mo @ ${args.infra_monthly:g}/mo)", infra_total))
        print("-" * 46)
        print(line("Subtotal", subtotal))
        if args.contingency_pct:
            print(line(f"Contingency ({args.contingency_pct:g}%)", contingency))
        print("=" * 46)
        print(line("GRAND TOTAL", total))
        print()
        print(f"Blended hours (incl. overhead): {blended_hours:,.0f}")
        if args.duration_months > 0:
            print(f"Effective monthly burn:         ${total / args.duration_months:,.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
