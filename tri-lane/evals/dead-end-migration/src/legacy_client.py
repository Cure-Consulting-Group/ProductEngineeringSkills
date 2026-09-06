"""DEPRECATED legacy export client. Do not modify; scheduled for deletion."""
from __future__ import annotations


class LegacyClient:
    def __init__(self, transport):
        self._t = transport  # callable(path, body) -> dict

    def send(self, record: dict) -> str:
        resp = self._t("/v1/records", {"record": record})
        return resp["id"]

    def batch(self, records: list[dict]) -> list[str]:
        ids = []
        for i in range(0, len(records), 50):
            chunk = records[i:i + 50]
            resp = self._t("/v1/records/batch", {"records": chunk})
            ids.extend(resp["ids"])
        return ids
