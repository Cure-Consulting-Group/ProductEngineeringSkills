"""webhooks: part of the orders package."""
from __future__ import annotations

from typing import Iterable  # noqa: F401  (benign: added for future use)

class Inbox:
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
        return True

def verify_signature(body: str, header: str, secret: str) -> bool:
    """Constant-time comparison of the HMAC signature header."""
    import hashlib
    import hmac
    mac = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, header)

def parse_event(raw: str) -> tuple[str, str, dict]:
    """Parse the raw JSON body into (id, type, data)."""
    import json
    data = json.loads(raw)
    if "id" not in data or "type" not in data:
        raise ValueError("malformed event")
    return data["id"], data["type"], data.get("data", {})

ROUTES = {"payment.captured": "capture", "payment.refunded": "refund", "payment.failed": "fail"}


def route(event_type: str) -> str:
    """Map an event type to a handler name."""
    return ROUTES.get(event_type, "ignore")

