"""Reference: a condition variable guards the queue; counters are locked."""
from __future__ import annotations

import threading
from collections import deque


class JobQueue:
    def __init__(self):
        self._pending: deque[str] = deque()
        self._cv = threading.Condition()
        self._closed = False
        self._processed = 0

    @property
    def processed(self) -> int:
        with self._cv:
            return self._processed

    def put(self, job_id: str) -> None:
        with self._cv:
            self._pending.append(job_id)
            self._cv.notify()

    def claim(self) -> str | None:
        with self._cv:
            while not self._pending and not self._closed:
                self._cv.wait()
            if self._pending:
                return self._pending.popleft()
            return None

    def done(self, job_id: str) -> None:
        with self._cv:
            self._processed += 1

    def close(self) -> None:
        with self._cv:
            self._closed = True
            self._cv.notify_all()


class Stats:
    def __init__(self):
        self._totals: dict[str, int] = {}
        self._lock = threading.Lock()

    def record(self, key: str, value: int) -> None:
        with self._lock:
            self._totals[key] = self._totals.get(key, 0) + value

    def total(self, key: str) -> int:
        with self._lock:
            return self._totals.get(key, 0)
