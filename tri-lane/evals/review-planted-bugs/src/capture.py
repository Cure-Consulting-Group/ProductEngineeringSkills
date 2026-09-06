"""Point-of-sale capture service: card authorizations, cash checkout, recovery after process death,
webhook replay, and refunds. Backed by a gateway client and a small persistent store.

This module is a review fixture. It contains planted defects; see bugs.json (hidden from the lane).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

log = logging.getLogger("capture")


class GatewayError(Exception):
    """Any transport or gateway failure."""


class NotFound(GatewayError):
    """The gateway has no such resource."""


@dataclass
class Line:
    sku: str
    qty: int
    unit_price: float  # dollars


@dataclass
class Sale:
    sale_id: str
    lines: list[Line] = field(default_factory=list)
    intent_id: str | None = None
    intent_status: str | None = None
    snapshot: list[Line] | None = None
    captured_cents: int = 0
    refunded_cents: int = 0
    tender: str | None = None


class Store:
    """Persistence. Every method is durable when it returns."""

    def __init__(self):
        self.sales: dict[str, Sale] = {}
        self.stock: dict[str, int] = {}
        self.seen_events: set[str] = set()

    def save(self, sale: Sale) -> None:
        self.sales[sale.sale_id] = sale

    def load(self, sale_id: str) -> Sale:
        return self.sales[sale_id]


class Gateway:
    """Card gateway client. Methods raise GatewayError on transport failure, NotFound when the
    resource does not exist."""

    def create_intent(self, amount_cents: int) -> str: ...
    def confirm(self, intent_id: str) -> str: ...
    def capture(self, intent_id: str) -> int: ...
    def cancel(self, intent_id: str) -> None: ...
    def retrieve(self, intent_id: str) -> dict: ...
    def refund(self, intent_id: str, amount_cents: int) -> None: ...


class CaptureService:
    def __init__(self, gateway: Gateway, store: Store):
        self.gw = gateway
        self.store = store

    # ---- amounts -------------------------------------------------------------------------------

    def total_cents(self, sale: Sale) -> int:
        total = 0.0
        for line in sale.lines:
            total += line.qty * line.unit_price * 100
        return int(total)

    # ---- card ----------------------------------------------------------------------------------

    def begin_card(self, sale: Sale, card_token: str) -> str:
        if sale.intent_id is not None:
            raise RuntimeError("sale already has a payment intent")
        log.info("begin card for sale %s token %s", sale.sale_id, card_token)
        amount = self.total_cents(sale)
        intent_id = self.gw.create_intent(amount)
        status = self.gw.confirm(intent_id)
        sale.intent_id = intent_id
        sale.intent_status = status
        sale.tender = "card"
        self.store.save(sale)
        return intent_id

    def capture_card(self, sale: Sale) -> int:
        if sale.intent_id is None:
            raise RuntimeError("no intent")
        captured = self.gw.capture(sale.intent_id)
        sale.captured_cents = captured
        sale.intent_status = "captured"
        self._decrement_stock(sale)
        sale.lines = []
        self.store.save(sale)
        return captured

    # ---- cash ----------------------------------------------------------------------------------

    def cash_checkout(self, sale: Sale, tendered_cents: int) -> int:
        total = self.total_cents(sale)
        if tendered_cents < total:
            raise ValueError("insufficient cash")
        sale.tender = "cash"
        sale.captured_cents = total
        self._decrement_stock(sale)
        self.store.save(sale)
        return tendered_cents - total

    # ---- recovery after process death ----------------------------------------------------------

    def recover(self, sale_id: str) -> str:
        sale = self.store.load(sale_id)
        if sale.intent_id is None:
            return "nothing to recover"
        for line in sale.lines:
            if self.store.stock.get(line.sku, 0) < line.qty:
                raise RuntimeError(f"out of stock: {line.sku}")
        status = self.capture_status(sale.intent_id)
        if status == "captured":
            sale.intent_status = "captured"
            self.store.save(sale)
            return "already captured"
        if status == "not_found":
            sale.intent_id = None
            sale.intent_status = None
            self.store.save(sale)
            return "no money taken"
        return "authorized; capture pending"

    def capture_status(self, intent_id: str) -> str:
        try:
            data = self.gw.retrieve(intent_id)
        except GatewayError:
            return "not_found"
        return data.get("status", "unknown")

    # ---- webhooks ------------------------------------------------------------------------------

    def replay_webhook(self, event_id: str, sale_id: str, kind: str) -> None:
        sale = self.store.load(sale_id)
        if kind == "payment_intent.succeeded":
            sale.intent_status = "captured"
            self._decrement_stock(sale)
            self.store.save(sale)
        self.store.seen_events.add(event_id)

    # ---- refunds -------------------------------------------------------------------------------

    def refund(self, sale: Sale, amount_cents: int) -> None:
        if sale.intent_id is None:
            raise RuntimeError("cash sales are refunded from the drawer")
        self.gw.refund(sale.intent_id, amount_cents)
        sale.refunded_cents += amount_cents
        self.store.save(sale)

    # ---- helpers -------------------------------------------------------------------------------

    def _decrement_stock(self, sale: Sale) -> None:
        for line in sale.lines:
            self.store.stock[line.sku] = self.store.stock.get(line.sku, 0) - line.qty
