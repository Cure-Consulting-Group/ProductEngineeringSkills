#!/usr/bin/env python3
"""Deployment frequency calculator — counts deployments per day and per week.

Usage:
  python3 deployment_frequency.py --repo /path/to/repo --since 2025-01-01 --until 2025-03-31
  python3 deployment_frequency.py --git-log-json deployments.json
  python3 deployment_frequency.py --repo . --since 2025-01-01 --pattern "^v[0-9]" --json

Inputs:
  --repo PATH        Path to a git repo. Tags or commits matching --pattern count as deployments.
  --git-log-json F   JSON file: list of objects with "timestamp" (ISO8601) field.
  --since YYYY-MM-DD Inclusive lower bound. Defaults to 90 days ago.
  --until YYYY-MM-DD Inclusive upper bound. Defaults to today.
  --pattern REGEX    Only count tags/commits matching pattern (default: v* tags).
  --source tags|commits  Source for repo mode (default: tags).

Output: deployments/day, deployments/week, total, DORA tier.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


def parse_date(s: str) -> date:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError as e:
        raise SystemExit(f"error: bad date '{s}' (expected YYYY-MM-DD)") from e


def git_deployments(repo: Path, since: date, until: date, pattern: str, source: str) -> list[datetime]:
    if not (repo / ".git").exists() and not (repo / "HEAD").exists():
        raise SystemExit(f"error: {repo} is not a git repo")

    if source == "tags":
        cmd = ["git", "-C", str(repo), "for-each-ref",
               "--sort=creatordate",
               "--format=%(creatordate:iso-strict)\t%(refname:short)",
               "refs/tags"]
    else:
        cmd = ["git", "-C", str(repo), "log",
               f"--since={since.isoformat()}",
               f"--until={(until + timedelta(days=1)).isoformat()}",
               "--pretty=format:%aI\t%s"]

    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"error: git command failed: {e.stderr.strip()}") from e
    except FileNotFoundError:
        raise SystemExit("error: 'git' not found on PATH")

    rx = re.compile(pattern)
    timestamps: list[datetime] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        ts_str, _, name = line.partition("\t")
        if not rx.search(name):
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        d = ts.date()
        if since <= d <= until:
            timestamps.append(ts)
    return timestamps


def json_deployments(path: Path, since: date, until: date) -> list[datetime]:
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"error: cannot read JSON: {e}")
    if not isinstance(data, list):
        raise SystemExit("error: JSON must be a list of objects")
    out: list[datetime] = []
    for i, row in enumerate(data):
        if not isinstance(row, dict) or "timestamp" not in row:
            raise SystemExit(f"error: row {i} missing 'timestamp' field")
        try:
            ts = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            raise SystemExit(f"error: row {i} has invalid timestamp '{row['timestamp']}'")
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        d = ts.date()
        if since <= d <= until:
            out.append(ts)
    return out


def dora_tier(per_day: float) -> str:
    if per_day >= 1.0:
        return "Elite"
    if per_day >= 1.0 / 7:
        return "High"
    if per_day >= 1.0 / 30:
        return "Medium"
    return "Low"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Calculate DORA deployment frequency from a git repo or JSON log.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--repo", type=Path, help="Path to git repo")
    src.add_argument("--git-log-json", type=Path,
                     help="JSON file: list of {timestamp: ISO8601}")
    p.add_argument("--since", type=parse_date,
                   default=date.today() - timedelta(days=90),
                   help="Inclusive start date YYYY-MM-DD (default: 90 days ago)")
    p.add_argument("--until", type=parse_date, default=date.today(),
                   help="Inclusive end date YYYY-MM-DD (default: today)")
    p.add_argument("--pattern", default=r"^v\d",
                   help="Regex for tag/commit name (default: ^v\\d)")
    p.add_argument("--source", choices=["tags", "commits"], default="tags",
                   help="Repo mode source (default: tags)")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args()

    if args.until < args.since:
        err("--until is before --since")
        return 2

    if args.repo:
        events = git_deployments(args.repo, args.since, args.until,
                                 args.pattern, args.source)
    else:
        if not args.git_log_json.exists():
            err(f"file not found: {args.git_log_json}")
            return 2
        events = json_deployments(args.git_log_json, args.since, args.until)

    days = max((args.until - args.since).days + 1, 1)
    weeks = days / 7.0
    total = len(events)
    per_day = total / days
    per_week = total / weeks
    tier = dora_tier(per_day)

    result = {
        "since": args.since.isoformat(),
        "until": args.until.isoformat(),
        "days_in_window": days,
        "deployments_total": total,
        "deployments_per_day": round(per_day, 4),
        "deployments_per_week": round(per_week, 2),
        "dora_tier": tier,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Window:        {args.since} to {args.until} ({days} days)")
        print(f"Total deploys: {total}")
        print(f"Per day:       {per_day:.3f}")
        print(f"Per week:      {per_week:.2f}")
        print(f"DORA tier:     {tier}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
