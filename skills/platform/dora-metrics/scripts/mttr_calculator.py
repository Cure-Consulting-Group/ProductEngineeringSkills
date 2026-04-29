#!/usr/bin/env python3
"""MTTR calculator — computes mean, median, and p90 from an incidents CSV.

Usage:
  python3 mttr_calculator.py --csv incidents.csv
  python3 mttr_calculator.py --csv incidents.csv --json
  python3 mttr_calculator.py --csv incidents.csv --severity SEV1,SEV2

CSV columns required: id, opened_at, resolved_at
  Timestamps must be ISO8601 (e.g. 2025-04-01T13:45:00Z or 2025-04-01 13:45:00).
  Optional column: severity. Optional: resolved_at may be empty (incident open — skipped).

Output: count, mean, median, p90, p95 in hours; DORA MTTR tier.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


def parse_ts(s: str) -> datetime | None:
    if not s or not s.strip():
        return None
    s = s.strip().replace("Z", "+00:00")
    # Allow space separator
    if "T" not in s and " " in s:
        s = s.replace(" ", "T", 1)
    try:
        ts = datetime.fromisoformat(s)
    except ValueError:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * p
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return sorted_vals[int(k)]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def dora_tier(median_hours: float) -> str:
    if median_hours < 1:
        return "Elite"
    if median_hours < 24:
        return "High"
    if median_hours < 24 * 7:
        return "Medium"
    return "Low"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Calculate MTTR (mean / median / p90) from an incidents CSV.")
    p.add_argument("--csv", type=Path, required=True,
                   help="Path to incidents CSV (id, opened_at, resolved_at[, severity])")
    p.add_argument("--severity", default="",
                   help="Comma-separated severities to include (default: all)")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args()

    if not args.csv.exists():
        err(f"file not found: {args.csv}")
        return 2

    sev_filter = {s.strip() for s in args.severity.split(",") if s.strip()}

    durations_h: list[float] = []
    skipped_open = 0
    skipped_bad = 0
    total_rows = 0

    try:
        with args.csv.open(newline="") as fh:
            reader = csv.DictReader(fh)
            required = {"id", "opened_at", "resolved_at"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                err(f"CSV missing required columns: {sorted(required)}; "
                    f"found: {reader.fieldnames}")
                return 2
            for row in reader:
                total_rows += 1
                if sev_filter and row.get("severity", "").strip() not in sev_filter:
                    continue
                opened = parse_ts(row["opened_at"])
                resolved = parse_ts(row["resolved_at"])
                if opened is None:
                    skipped_bad += 1
                    continue
                if resolved is None:
                    skipped_open += 1
                    continue
                delta = (resolved - opened).total_seconds() / 3600.0
                if delta < 0:
                    skipped_bad += 1
                    continue
                durations_h.append(delta)
    except OSError as e:
        err(f"cannot read {args.csv}: {e}")
        return 2

    n = len(durations_h)
    if n == 0:
        err("no resolved incidents matched filters")
        return 1

    sorted_h = sorted(durations_h)
    result = {
        "incidents_resolved": n,
        "rows_total": total_rows,
        "skipped_open": skipped_open,
        "skipped_invalid": skipped_bad,
        "mean_hours": round(mean(sorted_h), 3),
        "median_hours": round(median(sorted_h), 3),
        "p90_hours": round(percentile(sorted_h, 0.90), 3),
        "p95_hours": round(percentile(sorted_h, 0.95), 3),
        "min_hours": round(sorted_h[0], 3),
        "max_hours": round(sorted_h[-1], 3),
        "dora_tier": dora_tier(median(sorted_h)),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Resolved incidents: {n} (of {total_rows} rows)")
        if skipped_open:
            print(f"Skipped (still open): {skipped_open}")
        if skipped_bad:
            print(f"Skipped (invalid timestamps): {skipped_bad}")
        print(f"Mean MTTR:   {result['mean_hours']} hours")
        print(f"Median MTTR: {result['median_hours']} hours")
        print(f"p90 MTTR:    {result['p90_hours']} hours")
        print(f"p95 MTTR:    {result['p95_hours']} hours")
        print(f"DORA tier:   {result['dora_tier']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
