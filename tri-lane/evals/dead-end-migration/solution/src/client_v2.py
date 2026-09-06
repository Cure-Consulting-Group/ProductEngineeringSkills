"""Export client, version 2. Reference: batch added in the v2 wire format."""
from __future__ import annotations


class Client:
    def __init__(self, transport):
        self._t = transport

    def _post(self, op: str, payload) -> object:
        resp = self._t("/v2", {"op": op, "payload": payload})
        if not resp.get("ok"):
            raise RuntimeError(f"v2 {op} failed: {resp.get('error')}")
        return resp["result"]

    def send(self, record: dict) -> str:
        return self._post("record.create", {"record": record})

    def batch(self, records: list[dict]) -> list[str]:
        ids: list[str] = []
        for i in range(0, len(records), 50):
            ids.extend(self._post("record.create_many", {"records": records[i:i + 50]}))
        return ids
