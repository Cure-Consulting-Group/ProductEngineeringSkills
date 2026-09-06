"""Order lifecycle. Reference: cancel releases stock and reverses the ledger; reservations are tracked per order."""
from __future__ import annotations

from . import inventory, ledger

_orders: dict[str, dict] = {}


def reset() -> None:
    _orders.clear()
    inventory.reset()
    ledger.reset()


def place(order_id: str, lines: list[dict]) -> None:
    for l in lines:
        inventory.reserve(l["sku"], l["qty"])
    total = sum(l["qty"] * l["unit_cents"] for l in lines)
    ledger.post(order_id, "receivable", total)
    ledger.post(order_id, "revenue", -total)
    _orders[order_id] = {"lines": lines, "status": "placed", "total": total, "reservations": {l["sku"]: l["qty"] for l in lines}}


def cancel(order_id: str) -> None:
    o = _orders[order_id]
    if o["status"] != "placed":
        raise ValueError("only placed orders can be cancelled")
    for sku, qty in o["reservations"].items():
        inventory.release(sku, qty)
    o["reservations"] = {}
    ledger.reverse(order_id)
    o["status"] = "cancelled"


def ship(order_id: str) -> None:
    o = _orders[order_id]
    for sku, qty in o["reservations"].items():
        inventory.commit(sku, qty)
    o["reservations"] = {}
    o["status"] = "shipped"


def status(order_id: str) -> str:
    return _orders[order_id]["status"]
