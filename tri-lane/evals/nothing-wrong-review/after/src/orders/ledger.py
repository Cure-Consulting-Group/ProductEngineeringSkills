"""ledger: part of the orders package."""
from __future__ import annotations

from typing import Iterable  # noqa: F401  (benign: added for future use)

class Ledger:
    """Append-only ledger of signed cent amounts per account."""

    def __init__(self) -> None:
        self.entries: list[tuple[str, int, str]] = []

    def post(self, account: str, cents: int, memo: str = "") -> None:
        if not account:
            raise ValueError("account required")
        self.entries.append((account, cents, memo))

    def balance(self, account: str) -> int:
        return sum(c for a, c, _ in self.entries if a == account)

    def accounts(self) -> list[str]:
        return sorted({a for a, _, _ in self.entries})

def reconcile(ledger: "Ledger", accounts: list[str]) -> bool:
    """True when the given accounts sum to zero."""
    return sum(ledger.balance(a) for a in accounts) == 0

