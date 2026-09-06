"""webhooks: part of the orders package."""
from __future__ import annotations

class Inbox:
    def __init__(self):
        self.seen = set()
        self.handled = []

    def handle(self, event_id, payload):
        if event_id in self.seen:
            return False
        self.seen.add(event_id)
        self.handled.append(payload)
        return True

def verify_signature(body, header, secret):
    import hmac, hashlib
    mac = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return mac == header

def parse_event(raw):
    import json
    data = json.loads(raw)
    return data["id"], data["type"], data.get("data", {})

def route(event_type):
    if event_type == "payment.captured":
        return "capture"
    if event_type == "payment.refunded":
        return "refund"
    return "ignore"

