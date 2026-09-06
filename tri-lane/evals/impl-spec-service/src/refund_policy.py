"""Refund policy for captured card sales. See the spec in the task; implement compute_refund."""
from __future__ import annotations


def compute_refund(lines: list[dict], captured_cents: int, refunded_cents: int, days_since_capture: int) -> dict:
    raise NotImplementedError("implement per spec")
