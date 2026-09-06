"""Order lifecycle: place, cancel, ship."""
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
    _orders[order_id] = {"lines": lines, "status": "placed", "total": total}


def cancel(order_id: str) -> None:
    o = _orders[order_id]
    if o["status"] != "placed":
        raise ValueError("only placed orders can be cancelled")
    for l in o["lines"]:
        inventory.release(l["sku"], l["qty"])
    o["status"] = "cancelled"


def ship(order_id: str) -> None:
    o = _orders[order_id]
    for l in o["lines"]:
        inventory.commit(l["sku"], l["qty"])
    o["status"] = "shipped"


def status(order_id: str) -> str:
    return _orders[order_id]["status"]
