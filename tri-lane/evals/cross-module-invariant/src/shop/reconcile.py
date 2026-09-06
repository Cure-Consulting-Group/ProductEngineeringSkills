"""Reconciliation: does a cancelled order leave any trace in stock or books?"""
from __future__ import annotations

from . import inventory, ledger, orders


def report(order_id: str) -> dict:
    o = orders._orders[order_id]
    stock_delta = 0
    for l in o["lines"]:
        stock_delta += inventory._reserved.get(l["sku"], 0)
    ledger_delta = sum(c for _, c in ledger.entries_for(order_id))
    return {"stock_delta": stock_delta, "ledger_delta": ledger_delta}
