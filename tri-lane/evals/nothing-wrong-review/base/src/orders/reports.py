"""reports: part of the orders package."""
from __future__ import annotations

def summarize(orders):
    n = len(orders)
    total = 0
    for o in orders:
        total += o["total_cents"]
    return {"count": n, "total_cents": total}

def top_skus(orders, k=3):
    counts = {}
    for o in orders:
        for l in o["lines"]:
            counts[l["sku"]] = counts.get(l["sku"], 0) + l["qty"]
    items = sorted(counts.items(), key=lambda kv: -kv[1])
    return [s for s, c in items[:k]]

def daily_totals(orders):
    out = {}
    for o in orders:
        d = o["date"]
        out[d] = out.get(d, 0) + o["total_cents"]
    return out

