#!/usr/bin/env python3
"""Change Failure Rate calculator — reads deployments CSV and reports CFR %.

Usage:
  python3 change_failure_rate.py --csv deployments.csv
  python3 change_failure_rate.py --csv deployments.csv --json

CSV columns required: id, deployed_at, caused_incident
  caused_incident is parsed as bool: true/false, 1/0, yes/no (case-insensitive).
  deployed_at is ISO8601; rows with unparseable timestamps are skipped.

Output: total deployments, failed deployments, CFR %, DORA tier.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


TRUTHY = {"true", "1", "yes", "y", "t"}
FALSY = {"false", "0", "no", "n", "f", ""}


def parse_bool(s: str) -> bool | None:
    v = (s or "").strip().lower()
    if v in TRUTHY:
        return True
    if v in FALSY:
        return False
    return None


def parse_ts(s: str) -> datetime | None:
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    if "T" not in s and " " in s:
        s = s.replace(" ", "T", 1)
    try:
        ts = datetime.fromisoformat(s)
    except ValueError:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def dora_tier(cfr_pct: float) -> str:
    if cfr_pct <= 15:
        return "Elite"
    if cfr_pct <= 30:
        return "High"
    if cfr_pct <= 45:
        return "Medium"
    return "Low"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Calculate Change Failure Rate from a deployments CSV.")
    p.add_argument("--csv", type=Path, required=True,
                   help="Path to deployments CSV (id, deployed_at, caused_incident)")
    p.add_argument("--since", help="Inclusive start date YYYY-MM-DD (optional)")
    p.add_argument("--until", help="Inclusive end date YYYY-MM-DD (optional)")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args()

    if not args.csv.exists():
        err(f"file not found: {args.csv}")
        return 2

    def parse_bound(s: str | None) -> datetime | None:
        if not s:
            return None
        ts = parse_ts(s)
        if ts is None:
            raise SystemExit(f"error: bad date '{s}' (expected YYYY-MM-DD)")
        return ts

    since_ts = parse_bound(args.since)
    until_ts = parse_bound(args.until)

    total = 0
    failed = 0
    skipped = 0

    try:
        with args.csv.open(newline="") as fh:
            reader = csv.DictReader(fh)
            required = {"id", "deployed_at", "caused_incident"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                err(f"CSV missing required columns: {sorted(required)}; "
                    f"found: {reader.fieldnames}")
                return 2
            for row in reader:
                ts = parse_ts(row["deployed_at"])
                if ts is None:
                    skipped += 1
                    continue
                if since_ts and ts < since_ts:
                    continue
                if until_ts and ts > until_ts:
                    continue
                b = parse_bool(row["caused_incident"])
                if b is None:
                    skipped += 1
                    continue
                total += 1
                if b:
                    failed += 1
    except OSError as e:
        err(f"cannot read {args.csv}: {e}")
        return 2

    if total == 0:
        err("no valid deployment rows in window")
        return 1

    cfr = (failed / total) * 100.0
    result = {
        "deployments_total": total,
        "deployments_failed": failed,
        "rows_skipped": skipped,
        "cfr_percent": round(cfr, 2),
        "dora_tier": dora_tier(cfr),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Deployments:        {total}")
        print(f"Failed deployments: {failed}")
        if skipped:
            print(f"Skipped rows:       {skipped}")
        print(f"Change Failure Rate: {cfr:.2f}%")
        print(f"DORA tier:           {result['dora_tier']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
