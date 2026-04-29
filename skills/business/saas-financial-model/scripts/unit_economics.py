#!/usr/bin/env python3
"""SaaS unit economics — ARR, ARPU, LTV, LTV:CAC ratio, payback period.

Usage:
  python3 unit_economics.py --mrr 50000 --customers 200 --churn-rate 0.03 --cac 800
  python3 unit_economics.py --mrr 50000 --customers 200 --churn-rate 0.03 --cac 800 \\
      --gross-margin 0.75 --json

Inputs:
  --mrr            Monthly Recurring Revenue ($).
  --customers      Active paying customers.
  --churn-rate     Monthly customer churn rate (0-1, e.g. 0.03 = 3%).
  --cac            Customer Acquisition Cost ($).
  --gross-margin   Gross margin as fraction (default 0.75 = 75%). Used for margin-adjusted LTV.

Output: ARR, ARPU, LTV (revenue + margin-adjusted), LTV:CAC, payback months,
        avg lifespan, plus health flag (Healthy/Warning/Danger).
"""
from __future__ import annotations

import argparse
import json
import sys


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


def health(ratio: float) -> str:
    if ratio >= 3.0:
        return "Healthy"
    if ratio >= 1.0:
        return "Warning"
    return "Danger"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Compute SaaS unit economics: ARR, LTV, LTV:CAC, payback period.")
    p.add_argument("--mrr", type=float, required=True, help="Monthly Recurring Revenue (USD)")
    p.add_argument("--customers", type=float, required=True, help="Active paying customers")
    p.add_argument("--churn-rate", type=float, required=True,
                   help="Monthly churn rate as fraction (0-1)")
    p.add_argument("--cac", type=float, required=True,
                   help="Customer Acquisition Cost (USD)")
    p.add_argument("--gross-margin", type=float, default=0.75,
                   help="Gross margin as fraction (default 0.75)")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args()

    if args.mrr < 0:
        err("--mrr must be >= 0"); return 2
    if args.customers <= 0:
        err("--customers must be > 0"); return 2
    if not (0 < args.churn_rate < 1):
        err("--churn-rate must be between 0 and 1 (exclusive)"); return 2
    if args.cac < 0:
        err("--cac must be >= 0"); return 2
    if not (0 < args.gross_margin <= 1):
        err("--gross-margin must be in (0, 1]"); return 2

    arpu = args.mrr / args.customers
    arr = args.mrr * 12
    avg_lifespan_months = 1.0 / args.churn_rate
    ltv_revenue = arpu / args.churn_rate
    ltv_margin = ltv_revenue * args.gross_margin
    ratio_revenue = ltv_revenue / args.cac if args.cac > 0 else float("inf")
    ratio_margin = ltv_margin / args.cac if args.cac > 0 else float("inf")
    payback_months = args.cac / (arpu * args.gross_margin) if arpu > 0 else float("inf")

    flag = health(ratio_margin)

    def round_or_inf(x: float, digits: int = 2) -> float | str:
        if x == float("inf"):
            return "inf"
        return round(x, digits)

    result = {
        "arpu": round(arpu, 2),
        "arr": round(arr, 2),
        "avg_customer_lifespan_months": round(avg_lifespan_months, 2),
        "ltv_revenue": round(ltv_revenue, 2),
        "ltv_margin_adjusted": round(ltv_margin, 2),
        "ltv_cac_ratio_revenue": round_or_inf(ratio_revenue),
        "ltv_cac_ratio_margin": round_or_inf(ratio_margin),
        "payback_months": round_or_inf(payback_months),
        "gross_margin": args.gross_margin,
        "health": flag,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        def fmt(x: float) -> str:
            return "inf" if x == float("inf") else f"{x:,.2f}"
        print("SAAS UNIT ECONOMICS")
        print("=" * 46)
        print(f"ARPU:                 ${fmt(arpu)}")
        print(f"ARR:                  ${fmt(arr)}")
        print(f"Avg lifespan:         {avg_lifespan_months:.1f} months")
        print(f"LTV (revenue):        ${fmt(ltv_revenue)}")
        print(f"LTV (margin-adj.):    ${fmt(ltv_margin)} @ {args.gross_margin*100:g}% GM")
        print(f"LTV:CAC (revenue):    {fmt(ratio_revenue)}")
        print(f"LTV:CAC (margin-adj): {fmt(ratio_margin)}")
        print(f"Payback period:       {fmt(payback_months)} months")
        print(f"Health:               {flag}")
        print()
        print("Targets: LTV:CAC >= 3:1; payback < 12 months")
    return 0


if __name__ == "__main__":
    sys.exit(main())
