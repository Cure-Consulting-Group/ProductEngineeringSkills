"""Roster line parser: splits CSV-ish lines into raw fields. Correct as shipped."""
from __future__ import annotations


def parse_lines(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            continue
        rows.append({"name": parts[0], "height_raw": parts[1], "pos": parts[2]})
    return rows
