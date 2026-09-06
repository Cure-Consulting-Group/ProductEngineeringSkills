"""Export orchestration."""
from __future__ import annotations

from legacy_client import LegacyClient


def export_all(records: list[dict], transport) -> list[str]:
    client = LegacyClient(transport)
    if len(records) > 50:
        return client.batch(records)
    return [client.send(r) for r in records]
