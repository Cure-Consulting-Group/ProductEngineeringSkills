import sys, threading, time, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jobs import JobQueue, Stats  # noqa: E402

# Force frequent thread switches so check-then-act windows are actually exercised; the default 5 ms
# interval lets unsynchronised code pass by luck on a fast machine.
sys.setswitchinterval(1e-6)


def run_workers(q, n, sink, lock, stats=None):
    def worker():
        while True:
            j = q.claim()
            if j is None:
                return
            with lock:
                sink.append(j)
            if stats:
                stats.record("n", 1)
            q.done(j)
    ts = [threading.Thread(target=worker) for _ in range(n)]
    [t.start() for t in ts]
    return ts


class Hidden(unittest.TestCase):
    def test_exactly_once_under_contention_with_producer(self):
        q = JobQueue()
        seen, lock = [], threading.Lock()
        ts = run_workers(q, 8, seen, lock)
        for i in range(5000):
            q.put(f"j{i}")
        q.close()
        [t.join(timeout=15) for t in ts]
        self.assertTrue(all(not t.is_alive() for t in ts), "workers hung after close")
        self.assertEqual(sorted(seen), sorted(f"j{i}" for i in range(5000)))
        self.assertEqual(q.processed, 5000)

    def test_stats_exact(self):
        s = Stats()
        def w():
            for _ in range(20000):
                s.record("k", 1)
        ts = [threading.Thread(target=w) for _ in range(8)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(s.total("k"), 160000)

    def test_close_wakes_blocked_claimers_promptly(self):
        q = JobQueue()
        results = []
        def w():
            results.append(q.claim())
        ts = [threading.Thread(target=w) for _ in range(4)]
        [t.start() for t in ts]
        time.sleep(0.05)
        t0 = time.time()
        q.close()
        [t.join(timeout=2) for t in ts]
        self.assertLess(time.time() - t0, 1.0)
        self.assertEqual(results, [None] * 4)

    def test_processed_matches_done_calls(self):
        q = JobQueue()
        for i in range(3000):
            q.put(str(i))
        q.close()
        seen, lock = [], threading.Lock()
        s = Stats()
        ts = run_workers(q, 8, seen, lock, stats=s)
        [t.join(timeout=15) for t in ts]
        self.assertEqual(q.processed, 3000)
        self.assertEqual(s.total("n"), 3000)


if __name__ == "__main__":
    unittest.main()
