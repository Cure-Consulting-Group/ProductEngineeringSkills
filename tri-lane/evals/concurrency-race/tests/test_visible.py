import sys, threading, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jobs import JobQueue, Stats  # noqa: E402

sys.setswitchinterval(1e-6)  # frequent thread switches so races actually show


class Visible(unittest.TestCase):
    def test_single_thread(self):
        q = JobQueue()
        q.put("a")
        q.put("b")
        self.assertEqual(q.claim(), "a")
        q.done("a")
        self.assertEqual(q.claim(), "b")
        q.close()
        self.assertIsNone(q.claim())
        self.assertEqual(q.processed, 1)

    def test_workers_claim_each_job_once(self):
        q = JobQueue()
        for i in range(2000):
            q.put(f"j{i}")
        q.close()
        seen = []
        lock = threading.Lock()

        def worker():
            while True:
                j = q.claim()
                if j is None:
                    return
                with lock:
                    seen.append(j)
                q.done(j)
        ts = [threading.Thread(target=worker) for _ in range(8)]
        [t.start() for t in ts]
        [t.join(timeout=10) for t in ts]
        self.assertEqual(len(seen), 2000)
        self.assertEqual(len(set(seen)), 2000)
        self.assertEqual(q.processed, 2000)


if __name__ == "__main__":
    unittest.main()
