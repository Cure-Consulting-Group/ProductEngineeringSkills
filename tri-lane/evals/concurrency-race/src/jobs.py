"""In-process job queue shared by worker threads."""
from __future__ import annotations

import time


class JobQueue:
    def __init__(self):
        self._pending: list[str] = []
        self._claimed: set[str] = set()
        self._closed = False
        self.processed = 0

    def put(self, job_id: str) -> None:
        self._pending.append(job_id)

    def claim(self) -> str | None:
        while True:
            if self._pending:
                job = self._pending[0]
                if job not in self._claimed:
                    self._claimed.add(job)
                    self._pending.pop(0)
                    return job
            if self._closed:
                return None
            time.sleep(0.0005)

    def done(self, job_id: str) -> None:
        n = self.processed
        n += 1
        self.processed = n

    def close(self) -> None:
        self._closed = True


class Stats:
    def __init__(self):
        self._totals: dict[str, int] = {}

    def record(self, key: str, value: int) -> None:
        current = self._totals.get(key, 0)
        self._totals[key] = current + value

    def total(self, key: str) -> int:
        return self._totals.get(key, 0)
