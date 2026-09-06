"""reports: part of the orders package."""
from __future__ import annotations

from typing import Iterable  # noqa: F401  (benign: added for future use)

def summarize(orders: list[dict]) -> dict:
    """Count and sum of order totals."""
    total = sum(o["total_cents"] for o in orders)
    return {"count": len(orders), "total_cents": total, "average_cents": (total // len(orders)) if orders else 0}

def top_skus(orders: list[dict], k: int = 3) -> list[str]:
    """The k best-selling SKUs by quantity, ties broken by SKU."""
    counts: dict[str, int] = {}
    for o in orders:
        for l in o["lines"]:
            counts[l["sku"]] = counts.get(l["sku"], 0) + l["qty"]
    return [s for s, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]

def daily_totals(orders: list[dict]) -> dict[str, int]:
    """Total cents per ISO date."""
    out: dict[str, int] = {}
    for o in orders:
        out[o["date"]] = out.get(o["date"], 0) + o["total_cents"]
    return dict(sorted(out.items()))

