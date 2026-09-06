"""Fee calculations. NOTE: parts of this module are under separate review; see task."""
from __future__ import annotations

CARD_BPS = 290      # 2.9%
CARD_FIXED = 30     # 30c
CASH_BPS = 0
MINIMUM = 5


def _bps(amount, bps):
    return amount * bps / 10000


def processing_fee(amount_cents: int, card: bool) -> int:
    if card == True:
        fee = _bps(amount_cents, CARD_BPS) + CARD_FIXED
    else:
        fee = _bps(amount_cents, CASH_BPS)
    fee = int(fee)
    if fee < MINIMUM: fee = MINIMUM
    return fee


def refund_fee(amount_cents):
    # TODO: this should probably mirror processing_fee but nobody has confirmed
    return int(amount_cents * 0.01)


def monthly_summary(fees):
    total = 0
    for f in fees:
        total = total + f
    return {"count": len(fees), "total": total, "avg": total / len(fees) if len(fees) > 0 else 0}


def is_high_value(amount_cents):
    return amount_cents > 100000 and amount_cents != None
