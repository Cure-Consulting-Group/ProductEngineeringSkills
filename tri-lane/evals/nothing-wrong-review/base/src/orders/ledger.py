"""ledger: part of the orders package."""
from __future__ import annotations

class Ledger:
    def __init__(self):
        self.entries = []

    def post(self, account, cents, memo=""):
        self.entries.append((account, cents, memo))

    def balance(self, account):
        total = 0
        for a, c, m in self.entries:
            if a == account:
                total += c
        return total

def reconcile(ledger, accounts):
    return sum(ledger.balance(a) for a in accounts) == 0

