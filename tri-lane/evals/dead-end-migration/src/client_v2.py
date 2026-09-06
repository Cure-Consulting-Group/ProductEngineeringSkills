"""Export client, version 2. Wire format: every request is {"op": ..., "payload": ...} and every
response is {"ok": bool, "result": ...}."""
from __future__ import annotations


class Client:
    def __init__(self, transport):
        self._t = transport  # callable(path, body) -> dict

    def _post(self, op: str, payload) -> object:
        resp = self._t("/v2", {"op": op, "payload": payload})
        if not resp.get("ok"):
            raise RuntimeError(f"v2 {op} failed: {resp.get('error')}")
        return resp["result"]

    def send(self, record: dict) -> str:
        return self._post("record.create", {"record": record})
