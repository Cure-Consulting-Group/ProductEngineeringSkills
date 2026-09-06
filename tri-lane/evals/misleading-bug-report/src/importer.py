"""Roster import: parse, normalise, drop rows that cannot be normalised."""
from __future__ import annotations

from normalizer import clean_text, height_inches
from parser import parse_lines


def import_roster(text: str) -> list[dict]:
    out = []
    for row in parse_lines(text):
        h = height_inches(row["height_raw"])
        if h is None:
            continue
        out.append({"name": clean_text(row["name"]), "height_in": h, "pos": row["pos"]})
    return out
