"""pricing: part of the orders package."""
from __future__ import annotations

def round_half_up(cents: float) -> int:
    return int(cents + 0.5)

def line_cents(qty, unit_cents):
    return qty * unit_cents

def subtotal_cents(lines):
    total = 0
    for l in lines:
        total += line_cents(l["qty"], l["unit_cents"])
    return total

def discount_cents(subtotal, pct):
    return round_half_up(subtotal * pct / 100.0)

def tax_cents(taxable, bps):
    return round_half_up(taxable * bps / 10000.0)

def total_cents(lines, discount_pct, tax_bps):
    sub = subtotal_cents(lines)
    disc = discount_cents(sub, discount_pct)
    taxable = sub - disc
    tax = tax_cents(taxable, tax_bps)
    return taxable + tax

def split_evenly(cents, n):
    base = cents // n
    rem = cents - base * n
    return [base + (1 if i < rem else 0) for i in range(n)]

def apply_credit(total, credit):
    if credit > total:
        credit = total
    return total - credit

def format_cents(cents):
    return "%d.%02d" % (cents // 100, cents % 100)

def percent_of(part, whole):
    if whole == 0:
        return 0.0
    return 100.0 * part / whole

