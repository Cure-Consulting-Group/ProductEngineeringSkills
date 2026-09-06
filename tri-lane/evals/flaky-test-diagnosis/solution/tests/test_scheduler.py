import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scheduler import Scheduler  # noqa: E402


class FakeClock:
    def __init__(self, t=100.0):
        self.t = t
    def __call__(self):
        return self.t
    def advance(self, dt):
        self.t += dt


class SchedulerTests(unittest.TestCase):
    def test_ordering_is_stable(self):
        s = Scheduler(clock=FakeClock())
        order = ["c", "a", "b", "d"]
        for j in order:
            s.add(j, 1.0)
        self.assertEqual(s.due(5.0), order)
        self.assertEqual(s.due(5.0), order)

    def test_expired_jobs_are_collected(self):
        clock = FakeClock()
        s = Scheduler(clock=clock)
        s.add("old", 1.0)
        clock.advance(0.005)
        s.add("new", 1.0)
        expired = s.collect_expired(clock(), ttl=0.003)
        self.assertEqual(expired, ["old"])


if __name__ == "__main__":
    unittest.main()
