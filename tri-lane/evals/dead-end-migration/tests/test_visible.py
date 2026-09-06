import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import app  # noqa: E402


class FakeTransport:
    """Speaks both v1 and v2 so the migration can be verified end to end."""
    def __init__(self):
        self.calls = []
        self.n = 0
    def __call__(self, path, body):
        self.calls.append((path, body))
        if path == "/v1/records":
            self.n += 1
            return {"id": f"id{self.n}"}
        if path == "/v1/records/batch":
            ids = []
            for _ in body["records"]:
                self.n += 1
                ids.append(f"id{self.n}")
            return {"ids": ids}
        if path == "/v2":
            op, payload = body["op"], body["payload"]
            if op == "record.create":
                self.n += 1
                return {"ok": True, "result": f"id{self.n}"}
            if op == "record.create_many":
                if len(payload["records"]) > 50:
                    return {"ok": False, "error": "too many records (max 50)"}
                ids = []
                for _ in payload["records"]:
                    self.n += 1
                    ids.append(f"id{self.n}")
                return {"ok": True, "result": ids}
            return {"ok": False, "error": f"unknown op {op}"}
        raise AssertionError(path)


class Visible(unittest.TestCase):
    def test_small_export(self):
        t = FakeTransport()
        self.assertEqual(app.export_all([{"a": 1}, {"a": 2}], t), ["id1", "id2"])


if __name__ == "__main__":
    unittest.main()
