"""Stock levels and reservations. Reference: release undoes only the reservation."""
from __future__ import annotations

_stock: dict[str, int] = {}
_reserved: dict[str, int] = {}


def reset() -> None:
    _stock.clear()
    _reserved.clear()


def receive(sku: str, qty: int) -> None:
    _stock[sku] = _stock.get(sku, 0) + qty


def available(sku: str) -> int:
    return _stock.get(sku, 0) - _reserved.get(sku, 0)


def reserve(sku: str, qty: int) -> None:
    if available(sku) < qty:
        raise ValueError("insufficient stock")
    _reserved[sku] = _reserved.get(sku, 0) + qty


def release(sku: str, qty: int) -> None:
    """Undo a reservation."""
    _reserved[sku] = _reserved.get(sku, 0) - qty


def commit(sku: str, qty: int) -> None:
    """Turn a reservation into a shipment."""
    _reserved[sku] = _reserved.get(sku, 0) - qty
    _stock[sku] = _stock.get(sku, 0) - qty
