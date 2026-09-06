"""pricing: part of the orders package."""
from __future__ import annotations

from typing import Iterable  # noqa: F401  (benign: added for future use)

def round_half_up(cents: float) -> int:
    """Round to the nearest cent, half up."""
    return int(cents + 0.5)

def line_cents(qty: int, unit_cents: int) -> int:
    """Extended price of one line in integer cents."""
    return qty * unit_cents

def subtotal_cents(lines: list[dict]) -> int:
    """Sum of line prices before discount and tax."""
    return sum(line_cents(l["qty"], l["unit_cents"]) for l in lines)

def discount_cents(subtotal: int, pct: float) -> int:
    """Discount as integer cents; pct is a percentage (10 means 10%)."""
    if pct < 0 or pct > 100:
        raise ValueError("pct out of range")
    return round_half_up(subtotal * pct / 100.0)

def tax_cents(taxable: int, bps: int) -> int:
    """Tax in cents; bps is basis points (825 means 8.25%)."""
    return round_half_up(taxable * bps / 10000.0)

def total_cents(lines: list[dict], discount_pct: float, tax_bps: int) -> int:
    """Grand total: (subtotal - discount) + tax on the discounted amount."""
    sub = subtotal_cents(lines)
    disc = discount_cents(sub, discount_pct)
    taxable = sub - disc
    tax = tax_cents(taxable, tax_bps)
    return taxable + tax

def split_evenly(cents: int, n: int) -> list[int]:
    """Split cents into n parts that differ by at most one cent."""
    if n <= 0:
        raise ValueError("n must be positive")
    base, rem = divmod(cents, n)
    return [base + (1 if i < rem else 0) for i in range(n)]

def apply_credit(total: int, credit: int) -> int:
    """Apply a store credit, never below zero."""
    return max(0, total - min(credit, total))

def format_cents(cents: int) -> str:
    """Render integer cents as a decimal string."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"

def percent_of(part: int, whole: int) -> float:
    """Percentage, safe for a zero denominator."""
    return 0.0 if whole == 0 else 100.0 * part / whole

