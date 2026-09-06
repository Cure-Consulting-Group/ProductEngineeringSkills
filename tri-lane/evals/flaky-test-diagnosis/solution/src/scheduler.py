"""Reference solution: full-precision timestamps from an injectable clock; insertion order via dict order."""
from __future__ import annotations

import time
from typing import Callable


class Scheduler:
    def __init__(self, clock: Callable[[], float] = time.time):
        self._clock = clock
        self._jobs: dict[str, float] = {}
        self._added: dict[str, float] = {}

    def add(self, job_id: str, run_at: float) -> None:
        self._jobs[job_id] = run_at
        self._added[job_id] = self._clock()

    def due(self, now: float) -> list[str]:
        return [j for j, t in self._jobs.items() if t <= now]

    def collect_expired(self, now: float, ttl: float) -> list[str]:
        expired = [j for j, added in self._added.items() if now - added > ttl]
        for j in expired:
            self._jobs.pop(j, None)
            self._added.pop(j, None)
        return expired
