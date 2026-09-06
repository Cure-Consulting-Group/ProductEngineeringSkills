"""Export orchestration. Reference: v2 only."""
from __future__ import annotations

from client_v2 import Client


def export_all(records: list[dict], transport) -> list[str]:
    client = Client(transport)
    if len(records) > 50:
        return client.batch(records)
    return [client.send(r) for r in records]
