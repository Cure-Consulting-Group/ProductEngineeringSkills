import ast, sys, unittest
from pathlib import Path
SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import app  # noqa: E402


class Transport:
    def __init__(self, v1_enabled=False):
        self.calls = []
        self.n = 0
        self.v1 = v1_enabled
    def __call__(self, path, body):
        self.calls.append((path, body))
        if path.startswith("/v1"):
            if not self.v1:
                raise AssertionError("legacy v1 endpoint called after migration")
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


class Hidden(unittest.TestCase):
    def test_no_legacy_import(self):
        tree = ast.parse((SRC / "app.py").read_text())
        names = [n.names[0].name if isinstance(n, ast.Import) else n.module for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertNotIn("legacy_client", names)

    def test_large_export_order_and_chunking(self):
        t = Transport()
        recs = [{"i": i} for i in range(120)]
        ids = app.export_all(recs, t)
        self.assertEqual(ids, [f"id{i}" for i in range(1, 121)])
        many = [c for c in t.calls if c[1].get("op") == "record.create_many"]
        self.assertEqual([len(c[1]["payload"]["records"]) for c in many], [50, 50, 20])

    def test_exactly_fifty_is_one_round_trip(self):
        t = Transport()
        ids = app.export_all([{"i": i} for i in range(50)], t)
        self.assertEqual(len(ids), 50)
        self.assertLessEqual(len(t.calls), 50)

    def test_v2_error_surfaces(self):
        class Broken(Transport):
            def __call__(self, path, body):
                return {"ok": False, "error": "down"}
        with self.assertRaises(RuntimeError):
            app.export_all([{"i": 1}] * 60, Broken())

    def test_legacy_file_untouched(self):
        text = (SRC / "legacy_client.py").read_text()
        self.assertIn("DEPRECATED legacy export client. Do not modify", text)
        self.assertIn("def batch(self, records", text)


if __name__ == "__main__":
    unittest.main()
