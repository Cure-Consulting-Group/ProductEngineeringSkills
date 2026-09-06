#!/usr/bin/env python3
"""Generates base/ and after/ for the needle-in-diff review fixture: a small order-processing package,
then a refactor commit with ~40 legitimate changes and 3 planted defects. Deterministic; run once when editing."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE, AFTER = HERE / "base" / "src" / "orders", HERE / "after" / "src" / "orders"
for d in (BASE, AFTER):
    d.mkdir(parents=True, exist_ok=True)


def module(name: str, functions: list[tuple[str, str, str]], after: bool) -> str:
    """functions: (fname, body_before, body_after). Adds docstrings/type hints in `after` as benign churn."""
    out = [f'"""{name}: part of the orders package."""', "from __future__ import annotations", ""]
    if after:
        out.append("from typing import Iterable  # noqa: F401  (benign: added for future use)")
        out.append("")
    for fname, before, aft in functions:
        out.append((aft if after else before).rstrip() + "\n")
    return "\n".join(out) + "\n"


# ---- pricing.py: 10 functions; benign edits everywhere; B1 tax-on-subtotal bug in total_cents ------------
pricing = [
    ("round_half_up", '''def round_half_up(cents: float) -> int:
    return int(cents + 0.5)''', '''def round_half_up(cents: float) -> int:
    """Round to the nearest cent, half up."""
    return int(cents + 0.5)'''),
    ("line_cents", '''def line_cents(qty, unit_cents):
    return qty * unit_cents''', '''def line_cents(qty: int, unit_cents: int) -> int:
    """Extended price of one line in integer cents."""
    return qty * unit_cents'''),
    ("subtotal_cents", '''def subtotal_cents(lines):
    total = 0
    for l in lines:
        total += line_cents(l["qty"], l["unit_cents"])
    return total''', '''def subtotal_cents(lines: list[dict]) -> int:
    """Sum of line prices before discount and tax."""
    return sum(line_cents(l["qty"], l["unit_cents"]) for l in lines)'''),
    ("discount_cents", '''def discount_cents(subtotal, pct):
    return round_half_up(subtotal * pct / 100.0)''', '''def discount_cents(subtotal: int, pct: float) -> int:
    """Discount as integer cents; pct is a percentage (10 means 10%)."""
    if pct < 0 or pct > 100:
        raise ValueError("pct out of range")
    return round_half_up(subtotal * pct / 100.0)'''),
    ("tax_cents", '''def tax_cents(taxable, bps):
    return round_half_up(taxable * bps / 10000.0)''', '''def tax_cents(taxable: int, bps: int) -> int:
    """Tax in cents; bps is basis points (825 means 8.25%)."""
    return round_half_up(taxable * bps / 10000.0)'''),
    ("total_cents", '''def total_cents(lines, discount_pct, tax_bps):
    sub = subtotal_cents(lines)
    disc = discount_cents(sub, discount_pct)
    taxable = sub - disc
    tax = tax_cents(taxable, tax_bps)
    return taxable + tax''', '''def total_cents(lines: list[dict], discount_pct: float, tax_bps: int) -> int:
    """Grand total: (subtotal - discount) + tax on the discounted amount."""
    sub = subtotal_cents(lines)
    disc = discount_cents(sub, discount_pct)
    taxable = sub - disc
    tax = tax_cents(sub, tax_bps)
    return taxable + tax'''),
    ("split_evenly", '''def split_evenly(cents, n):
    base = cents // n
    rem = cents - base * n
    return [base + (1 if i < rem else 0) for i in range(n)]''', '''def split_evenly(cents: int, n: int) -> list[int]:
    """Split cents into n parts that differ by at most one cent."""
    if n <= 0:
        raise ValueError("n must be positive")
    base, rem = divmod(cents, n)
    return [base + (1 if i < rem else 0) for i in range(n)]'''),
    ("apply_credit", '''def apply_credit(total, credit):
    if credit > total:
        credit = total
    return total - credit''', '''def apply_credit(total: int, credit: int) -> int:
    """Apply a store credit, never below zero."""
    return max(0, total - min(credit, total))'''),
    ("format_cents", '''def format_cents(cents):
    return "%d.%02d" % (cents // 100, cents % 100)''', '''def format_cents(cents: int) -> str:
    """Render integer cents as a decimal string."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"'''),
    ("percent_of", '''def percent_of(part, whole):
    if whole == 0:
        return 0.0
    return 100.0 * part / whole''', '''def percent_of(part: int, whole: int) -> float:
    """Percentage, safe for a zero denominator."""
    return 0.0 if whole == 0 else 100.0 * part / whole'''),
]

# ---- webhooks.py: B2 idempotency check after the write ----------------------------------------------
webhooks = [
    ("Inbox", '''class Inbox:
    def __init__(self):
        self.seen = set()
        self.handled = []

    def handle(self, event_id, payload):
        if event_id in self.seen:
            return False
        self.seen.add(event_id)
        self.handled.append(payload)
        return True''', '''class Inbox:
    """Idempotent webhook inbox: each event id is handled once."""

    def __init__(self) -> None:
        self.seen: set[str] = set()
        self.handled: list[dict] = []

    def handle(self, event_id: str, payload: dict) -> bool:
        """Return True if the event was handled, False if it was a duplicate."""
        self.seen.add(event_id)
        if event_id in self.seen:
            return False
        self.handled.append(payload)
        return True'''),
    ("verify_signature", '''def verify_signature(body, header, secret):
    import hmac, hashlib
    mac = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return mac == header''', '''def verify_signature(body: str, header: str, secret: str) -> bool:
    """Constant-time comparison of the HMAC signature header."""
    import hashlib
    import hmac
    mac = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, header)'''),
    ("parse_event", '''def parse_event(raw):
    import json
    data = json.loads(raw)
    return data["id"], data["type"], data.get("data", {})''', '''def parse_event(raw: str) -> tuple[str, str, dict]:
    """Parse the raw JSON body into (id, type, data)."""
    import json
    data = json.loads(raw)
    if "id" not in data or "type" not in data:
        raise ValueError("malformed event")
    return data["id"], data["type"], data.get("data", {})'''),
    ("route", '''def route(event_type):
    if event_type == "payment.captured":
        return "capture"
    if event_type == "payment.refunded":
        return "refund"
    return "ignore"''', '''ROUTES = {"payment.captured": "capture", "payment.refunded": "refund", "payment.failed": "fail"}


def route(event_type: str) -> str:
    """Map an event type to a handler name."""
    return ROUTES.get(event_type, "ignore")'''),
]

# ---- delivery.py: B3 retry loop keeps sending after success --------------------------------------------
delivery = [
    ("send_with_retry", '''def send_with_retry(send, payload, attempts=3):
    last = None
    for i in range(attempts):
        resp = send(payload)
        if resp.get("timeout"):
            last = resp
            continue
        return resp
    return last''', '''def send_with_retry(send, payload: dict, attempts: int = 3) -> dict | None:
    """Send, retrying on timeout up to `attempts` times."""
    last = None
    for _ in range(attempts):
        resp = send(payload)
        if resp.get("timeout"):
            last = resp
            continue
        last = resp
    return last'''),
    ("backoff_seconds", '''def backoff_seconds(attempt):
    return 2 ** attempt''', '''def backoff_seconds(attempt: int, cap: int = 30) -> int:
    """Exponential backoff with a cap."""
    return min(cap, 2 ** attempt)'''),
    ("should_retry", '''def should_retry(status):
    return status >= 500 or status == 429''', '''def should_retry(status: int) -> bool:
    """Retry on server errors and rate limiting only."""
    return status >= 500 or status == 429'''),
    ("build_headers", '''def build_headers(token):
    return {"Authorization": "Bearer " + token}''', '''def build_headers(token: str, request_id: str | None = None) -> dict:
    """Standard headers; request id is optional."""
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    if request_id:
        h["X-Request-Id"] = request_id
    return h'''),
]

# ---- ledger.py and reports.py: benign churn only ---------------------------------------------------------
ledger = [
    ("Ledger", '''class Ledger:
    def __init__(self):
        self.entries = []

    def post(self, account, cents, memo=""):
        self.entries.append((account, cents, memo))

    def balance(self, account):
        total = 0
        for a, c, m in self.entries:
            if a == account:
                total += c
        return total''', '''class Ledger:
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
        return sorted({a for a, _, _ in self.entries})'''),
    ("reconcile", '''def reconcile(ledger, accounts):
    return sum(ledger.balance(a) for a in accounts) == 0''', '''def reconcile(ledger: "Ledger", accounts: list[str]) -> bool:
    """True when the given accounts sum to zero."""
    return sum(ledger.balance(a) for a in accounts) == 0'''),
]
reports = [
    ("summarize", '''def summarize(orders):
    n = len(orders)
    total = 0
    for o in orders:
        total += o["total_cents"]
    return {"count": n, "total_cents": total}''', '''def summarize(orders: list[dict]) -> dict:
    """Count and sum of order totals."""
    total = sum(o["total_cents"] for o in orders)
    return {"count": len(orders), "total_cents": total, "average_cents": (total // len(orders)) if orders else 0}'''),
    ("top_skus", '''def top_skus(orders, k=3):
    counts = {}
    for o in orders:
        for l in o["lines"]:
            counts[l["sku"]] = counts.get(l["sku"], 0) + l["qty"]
    items = sorted(counts.items(), key=lambda kv: -kv[1])
    return [s for s, c in items[:k]]''', '''def top_skus(orders: list[dict], k: int = 3) -> list[str]:
    """The k best-selling SKUs by quantity, ties broken by SKU."""
    counts: dict[str, int] = {}
    for o in orders:
        for l in o["lines"]:
            counts[l["sku"]] = counts.get(l["sku"], 0) + l["qty"]
    return [s for s, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]'''),
    ("daily_totals", '''def daily_totals(orders):
    out = {}
    for o in orders:
        d = o["date"]
        out[d] = out.get(d, 0) + o["total_cents"]
    return out''', '''def daily_totals(orders: list[dict]) -> dict[str, int]:
    """Total cents per ISO date."""
    out: dict[str, int] = {}
    for o in orders:
        out[o["date"]] = out.get(o["date"], 0) + o["total_cents"]
    return dict(sorted(out.items()))'''),
]

for name, fns in (("pricing", pricing), ("webhooks", webhooks), ("delivery", delivery), ("ledger", ledger), ("reports", reports)):
    (BASE / f"{name}.py").write_text(module(name, fns, after=False))
    (AFTER / f"{name}.py").write_text(module(name, fns, after=True))
(BASE / "__init__.py").write_text("")
(AFTER / "__init__.py").write_text('"""orders package"""\n')
print("generated base/ and after/")
