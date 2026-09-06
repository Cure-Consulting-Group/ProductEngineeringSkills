"""Reconciliation. Reference: per-order reservations, signed ledger sum."""
from __future__ import annotations

from . import ledger, orders


def report(order_id: str) -> dict:
    o = orders._orders[order_id]
    stock_delta = sum(o.get("reservations", {}).values())
    ledger_delta = sum(c for _, c in ledger.entries_for(order_id))
    return {"stock_delta": stock_delta, "ledger_delta": ledger_delta}
