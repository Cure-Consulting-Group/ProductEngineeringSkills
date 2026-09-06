"""delivery: part of the orders package."""
from __future__ import annotations

def send_with_retry(send, payload, attempts=3):
    last = None
    for i in range(attempts):
        resp = send(payload)
        if resp.get("timeout"):
            last = resp
            continue
        return resp
    return last

def backoff_seconds(attempt):
    return 2 ** attempt

def should_retry(status):
    return status >= 500 or status == 429

def build_headers(token):
    return {"Authorization": "Bearer " + token}

