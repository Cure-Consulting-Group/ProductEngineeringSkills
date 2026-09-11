"""Commit history is dated and attributable, which makes it useful CORROBORATION for a time allocation. Author and commit dates are set by whoever commits, and history can be rewritten, so its weight rises with remote logs, protected branches, or signed commits. It does NOT establish the IRC §41 four-part test — pair it with the project-level uncertainty and experimentation narrative (see ../reference/qre-qualification.md). Point ROOT only at checkouts you trust.

Usage:
    python3 repo_activity.py [ROOT] [--year YYYY] [--json]
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional


FIELDS = [
    "repo",
    "commits",
    "authors",
    "first_commit",
    "last_commit",
    "active_months",
    "files_changed",
    "insertions",
    "deletions",
]


def safe_cell(value: str) -> str:
    """Prevent spreadsheet formulas from being interpreted as formulas."""
    if value.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


def _git(args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, capture_output=True, text=True)


def discover_repos(root: str, max_depth: int = 3) -> List[str]:
    """Find repositories at root and up to max_depth directory levels below it."""
    root_real = os.path.realpath(root)
    found = set()

    probe = _git(["-C", root_real, "rev-parse", "--show-toplevel"])
    if probe.returncode == 0 and os.path.realpath(probe.stdout.strip()) == root_real:
        found.add(root_real)

    for current, dirs, files in os.walk(root_real, topdown=True, followlinks=False):
        relative = os.path.relpath(current, root_real)
        depth = 0 if relative == "." else relative.count(os.sep) + 1
        git_entry = os.path.join(current, ".git")
        if os.path.isdir(git_entry) or os.path.isfile(git_entry):
            found.add(os.path.realpath(current))
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
        if depth > max_depth:
            dirs[:] = []
            continue
    return sorted(found)


def _warn(repo: str, error: str) -> None:
    detail = error.strip().splitlines()[0] if error.strip() else "unknown git error"
    print("warning: skipping {}: {}".format(repo, detail), file=sys.stderr)


def _log_records(repo: str, year: int, reverse: bool = False) -> Optional[List[List[str]]]:
    since = "{}-01-01 00:00:00".format(year)
    until = "{}-12-31 23:59:59".format(year)
    args = [
        "-C", repo, "log", "--since", since, "--until", until,
        "--format=%aN%x1f%ad%x1f%ad", "--date=format:%Y-%m-%d",
    ]
    if reverse:
        args.append("--reverse")
    result = _git(args)
    if result.returncode != 0:
        _warn(repo, result.stderr)
        return None
    records = []
    for line in result.stdout.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 3:
            records.append(parts)
    return records


def repo_stats(repo: str, year: int) -> Optional[Dict[str, object]]:
    """Return activity statistics for repo, or None when it has no commits."""
    records = _log_records(repo, year, reverse=False)
    if records is None or not records:
        return None

    shortstat = _git([
        "-C", repo, "log", "--since", "{}-01-01 00:00:00".format(year),
        "--until", "{}-12-31 23:59:59".format(year), "--no-ext-diff",
        "--no-textconv", "--shortstat", "--format=",
    ])
    if shortstat.returncode != 0:
        _warn(repo, shortstat.stderr)
        return None

    files_changed = insertions = deletions = 0
    for line in shortstat.stdout.splitlines():
        match = re.search(r"(\d+) files? changed", line)
        if match:
            files_changed += int(match.group(1))
        match = re.search(r"(\d+) insertions?\(\+\)", line)
        if match:
            insertions += int(match.group(1))
        match = re.search(r"(\d+) deletions?\(-\)", line)
        if match:
            deletions += int(match.group(1))

    dates = [record[1] for record in records]
    months = {record[2][:7] for record in records}
    authors = sorted({record[0] for record in records})
    return {
        "repo": os.path.basename(os.path.realpath(repo)),
        "commits": len(records),
        "authors": ";".join(authors),
        "first_commit": min(dates),
        "last_commit": max(dates),
        "active_months": len(months),
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract dated commit activity by repository.")
    parser.add_argument("root", nargs="?", default=os.getcwd(), help="directory to search (default: current directory)")
    parser.add_argument("--year", type=int, default=None, help="calendar year to inspect (default: current year)")
    parser.add_argument("--json", action="store_true", help="emit a JSON array instead of CSV")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(argv)
    if not os.path.isdir(args.root):
        print("error: ROOT is not a directory: {}".format(args.root), file=sys.stderr)
        return 2
    year = args.year if args.year is not None else datetime.date.today().year
    rows = []
    for repo in discover_repos(args.root):
        stats = repo_stats(repo, year)
        if stats is not None:
            rows.append(stats)
    if args.json:
        json.dump(rows, sys.stdout)
        sys.stdout.write("\n")
    else:
        writer = csv.writer(sys.stdout)
        writer.writerow(FIELDS)
        for row in rows:
            writer.writerow([safe_cell(str(row[field])) if isinstance(row[field], str) else row[field] for field in FIELDS])
    return 0


if __name__ == "__main__":
    sys.exit(main())
