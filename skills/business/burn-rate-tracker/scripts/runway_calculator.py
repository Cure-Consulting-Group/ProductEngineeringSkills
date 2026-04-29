#!/usr/bin/env python3
"""Runway calculator — months of runway with best/expected/worst scenarios.

Usage:
  python3 runway_calculator.py --cash 1500000 --monthly-burn 120000
  python3 runway_calculator.py --cash 1500000 --monthly-burn 120000 \\
      --monthly-revenue 30000 --revenue-growth 0.10 --burn-growth 0.02 --json

Inputs:
  --cash               Cash on hand (USD).
  --monthly-burn       Gross monthly expenses (USD).
  --monthly-revenue    Current monthly revenue (default 0).
  --revenue-growth     Monthly revenue growth rate as fraction (default 0).
  --burn-growth        Monthly burn growth rate as fraction (default 0).
  --max-months         Cap projection at N months (default 60).

Scenarios:
  Best:     revenue grows at 1.5x given rate, burn flat.
  Expected: revenue and burn grow at given rates.
  Worst:    revenue flat (no growth), burn grows at 1.5x given rate.

Output: runway months for each scenario plus status flag.
"""
from __future__ import annotations

import argparse
import json
import sys


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


def project_runway(cash: float, burn0: float, rev0: float,
                   rev_growth: float, burn_growth: float,
                   max_months: int) -> dict:
    """Step month-by-month until cash exhausted or break-even."""
    bal = cash
    burn = burn0
    rev = rev0
    months = 0
    breakeven_month: int | None = None
    while months < max_months:
        net = burn - rev
        if net <= 0 and breakeven_month is None:
            breakeven_month = months + 1
        if net <= 0:
            return {
                "runway_months": "inf",
                "ending_cash": round(bal, 2),
                "breakeven_month": breakeven_month,
            }
        if bal < net:
            # Partial month
            frac = bal / net
            return {
                "runway_months": round(months + frac, 2),
                "ending_cash": 0.0,
                "breakeven_month": breakeven_month,
            }
        bal -= net
        months += 1
        burn *= (1 + burn_growth)
        rev *= (1 + rev_growth)
    return {
        "runway_months": f">{max_months}",
        "ending_cash": round(bal, 2),
        "breakeven_month": breakeven_month,
    }


def status(runway: float | str) -> str:
    if isinstance(runway, str):  # "inf" or ">60"
        return "Healthy"
    if runway >= 12:
        return "Healthy"
    if runway >= 9:
        return "Monitor"
    if runway >= 6:
        return "Danger"
    if runway >= 3:
        return "Critical"
    return "Existential"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Compute cash runway in months with best/expected/worst scenarios.")
    p.add_argument("--cash", type=float, required=True, help="Cash on hand (USD)")
    p.add_argument("--monthly-burn", type=float, required=True,
                   help="Current monthly expenses (USD)")
    p.add_argument("--monthly-revenue", type=float, default=0.0,
                   help="Current monthly revenue (USD, default 0)")
    p.add_argument("--revenue-growth", type=float, default=0.0,
                   help="Monthly revenue growth as fraction (default 0)")
    p.add_argument("--burn-growth", type=float, default=0.0,
                   help="Monthly burn growth as fraction (default 0)")
    p.add_argument("--max-months", type=int, default=60,
                   help="Projection cap in months (default 60)")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args()

    if args.cash < 0:
        err("--cash must be >= 0"); return 2
    if args.monthly_burn <= 0:
        err("--monthly-burn must be > 0"); return 2
    if args.monthly_revenue < 0:
        err("--monthly-revenue must be >= 0"); return 2
    if args.max_months <= 0:
        err("--max-months must be > 0"); return 2

    base = dict(cash=args.cash, burn0=args.monthly_burn, rev0=args.monthly_revenue,
                max_months=args.max_months)

    best = project_runway(**base, rev_growth=args.revenue_growth * 1.5,
                          burn_growth=0.0)
    expected = project_runway(**base, rev_growth=args.revenue_growth,
                              burn_growth=args.burn_growth)
    worst = project_runway(**base, rev_growth=0.0,
                           burn_growth=max(args.burn_growth, 0.0) * 1.5
                                       if args.burn_growth > 0 else 0.0)

    # Static net burn at month 0 for context
    net_burn_now = args.monthly_burn - args.monthly_revenue
    static_runway = (args.cash / net_burn_now) if net_burn_now > 0 else float("inf")

    def runway_status_for(s: dict) -> str:
        r = s["runway_months"]
        if isinstance(r, str):
            return "Healthy"
        return status(r)

    result = {
        "inputs": {
            "cash": args.cash,
            "monthly_burn": args.monthly_burn,
            "monthly_revenue": args.monthly_revenue,
            "revenue_growth": args.revenue_growth,
            "burn_growth": args.burn_growth,
        },
        "static_net_burn": round(net_burn_now, 2),
        "static_runway_months": "inf" if net_burn_now <= 0 else round(static_runway, 2),
        "scenarios": {
            "best": {**best, "status": runway_status_for(best)},
            "expected": {**expected, "status": runway_status_for(expected)},
            "worst": {**worst, "status": runway_status_for(worst)},
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("RUNWAY ANALYSIS")
        print("=" * 60)
        print(f"Cash:          ${args.cash:,.2f}")
        print(f"Monthly burn:  ${args.monthly_burn:,.2f}")
        print(f"Monthly rev:   ${args.monthly_revenue:,.2f}")
        print(f"Net burn now:  ${net_burn_now:,.2f}")
        sr = result["static_runway_months"]
        print(f"Static runway: {sr if isinstance(sr, str) else f'{sr:.1f}'} months "
              "(no growth assumed)")
        print()
        print(f"{'Scenario':<10} {'Runway (mo)':>14} {'Status':>14} {'Break-even mo':>16}")
        for name in ("best", "expected", "worst"):
            s = result["scenarios"][name]
            r = s["runway_months"]
            r_s = r if isinstance(r, str) else f"{r:.2f}"
            be = s["breakeven_month"] if s["breakeven_month"] is not None else "-"
            print(f"{name:<10} {r_s:>14} {s['status']:>14} {str(be):>16}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
