"""Field normalisation. Heights become integer inches."""
from __future__ import annotations

import re

_FEET_IN = re.compile(r"^(\d)\s*(?:ft|')\s*(\d{1,2})\s*(?:in|\")?$")
_DASH = re.compile(r"^(\d)-(\d{1,2})$")


def clean_text(s: str) -> str:
    """Strip stray quote characters that come from spreadsheet exports."""
    return s.replace('"', "").replace("'", "").strip()


def height_inches(raw: str) -> int | None:
    raw = clean_text(raw)
    if raw.isdigit():
        return int(raw)
    m = _FEET_IN.match(raw) or _DASH.match(raw)
    if not m:
        return None
    return int(m.group(1)) * 12 + int(m.group(2))
