"""Reference solution."""
from __future__ import annotations


def _rate(days: int) -> float:
    if days <= 14:
        return 1.0
    if days <= 30:
        return 0.5
    return 0.0


def compute_refund(lines: list[dict], captured_cents: int, refunded_cents: int, days_since_capture: int) -> dict:
    if days_since_capture < 0 or refunded_cents < 0:
        raise ValueError("negative input")
    rate = _rate(days_since_capture)
    num, den = (1, 1) if rate == 1.0 else (1, 2) if rate == 0.5 else (0, 1)
    out = []
    total = 0
    for line in lines:
        cents = (line["qty"] * line["unit_cents"] * num) // den if line.get("refundable") else 0
        out.append({"sku": line["sku"], "eligible_cents": int(cents)})
        total += int(cents)
    cap = max(0, captured_cents - refunded_cents)
    return {"lines": out, "total_cents": min(total, cap), "rate": rate}
