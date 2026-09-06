"""delivery: part of the orders package."""
from __future__ import annotations

from typing import Iterable  # noqa: F401  (benign: added for future use)

def send_with_retry(send, payload: dict, attempts: int = 3) -> dict | None:
    """Send, retrying on timeout up to `attempts` times; return the first non-timeout response."""
    last = None
    for _ in range(attempts):
        resp = send(payload)
        if resp.get("timeout"):
            last = resp
            continue
        return resp
    return last

def backoff_seconds(attempt: int, cap: int = 30) -> int:
    """Exponential backoff with a cap."""
    return min(cap, 2 ** attempt)

def should_retry(status: int) -> bool:
    """Retry on server errors and rate limiting only."""
    return status >= 500 or status == 429

def build_headers(token: str, request_id: str | None = None) -> dict:
    """Standard headers; request id is optional."""
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    if request_id:
        h["X-Request-Id"] = request_id
    return h

