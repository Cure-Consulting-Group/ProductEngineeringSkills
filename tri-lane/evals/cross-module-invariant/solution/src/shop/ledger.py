"""Double-entry ledger in integer cents. Reference: reverse every account, once."""
from __future__ import annotations

_entries: list[tuple[str, str, int]] = []  # (order_id, account, cents)


def reset() -> None:
    _entries.clear()


def post(order_id: str, account: str, cents: int) -> None:
    _entries.append((order_id, account, cents))


def balance(account: str) -> int:
    return sum(c for _, a, c in _entries if a == account)


def entries_for(order_id: str) -> list[tuple[str, int]]:
    return [(a, c) for o, a, c in _entries if o == order_id]


def reverse(order_id: str) -> None:
    """Post the opposite of every entry for the order, so it nets to zero."""
    for account, cents in list(entries_for(order_id)):
        post(order_id, account, -cents)
