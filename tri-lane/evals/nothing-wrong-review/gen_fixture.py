#!/usr/bin/env python3
"""Generates base/ and after/ for the nothing-wrong review fixture: the same orders package and the same
kind of refactor as needle-in-diff-review, but every change is behaviour-preserving. Deterministic."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEEDLE = HERE.parent / "needle-in-diff-review" / "gen_fixture.py"

# Reuse the needle generator's function tables but replace the three planted bodies with correct ones.
spec = importlib.util.spec_from_file_location("needle_gen", NEEDLE)
src = NEEDLE.read_text()
# Do not execute the needle generator's file writes: strip them by loading only the data section.
data_src = src.split("for name, fns in")[0]
ns = {"__file__": str(NEEDLE), "Path": Path}
exec(data_src.replace("HERE = Path(__file__).resolve().parent", "HERE = Path('.')").replace("for d in (BASE, AFTER):\n    d.mkdir(parents=True, exist_ok=True)", ""), ns)

pricing, webhooks, delivery, ledger, reports, module = ns["pricing"], ns["webhooks"], ns["delivery"], ns["ledger"], ns["reports"], ns["module"]


def fix(table, fname, after_body):
    return [(n, b, after_body if n == fname else a) for n, b, a in table]


pricing = fix(pricing, "total_cents", '''def total_cents(lines: list[dict], discount_pct: float, tax_bps: int) -> int:
    """Grand total: (subtotal - discount) + tax on the discounted amount."""
    sub = subtotal_cents(lines)
    disc = discount_cents(sub, discount_pct)
    taxable = sub - disc
    tax = tax_cents(taxable, tax_bps)
    return taxable + tax''')
webhooks = fix(webhooks, "Inbox", '''class Inbox:
    """Idempotent webhook inbox: each event id is handled once."""

    def __init__(self) -> None:
        self.seen: set[str] = set()
        self.handled: list[dict] = []

    def handle(self, event_id: str, payload: dict) -> bool:
        """Return True if the event was handled, False if it was a duplicate."""
        if event_id in self.seen:
            return False
        self.seen.add(event_id)
        self.handled.append(payload)
        return True''')
delivery = fix(delivery, "send_with_retry", '''def send_with_retry(send, payload: dict, attempts: int = 3) -> dict | None:
    """Send, retrying on timeout up to `attempts` times; return the first non-timeout response."""
    last = None
    for _ in range(attempts):
        resp = send(payload)
        if resp.get("timeout"):
            last = resp
            continue
        return resp
    return last''')

BASE, AFTER = HERE / "base" / "src" / "orders", HERE / "after" / "src" / "orders"
for d in (BASE, AFTER):
    d.mkdir(parents=True, exist_ok=True)
for name, fns in (("pricing", pricing), ("webhooks", webhooks), ("delivery", delivery), ("ledger", ledger), ("reports", reports)):
    (BASE / f"{name}.py").write_text(module(name, fns, after=False))
    (AFTER / f"{name}.py").write_text(module(name, fns, after=True))
(BASE / "__init__.py").write_text("")
(AFTER / "__init__.py").write_text('"""orders package"""\n')
print("generated clean base/ and after/")
