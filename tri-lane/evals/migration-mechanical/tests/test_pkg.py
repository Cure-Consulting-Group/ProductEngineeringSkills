import importlib, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class PkgTests(unittest.TestCase):
    def test_scale_and_describe_all_modules(self):
        for i in range(1, 31):
            m = importlib.import_module(f"pkg.mod{i:02d}")
            self.assertEqual(m.scale(2), 2 * i)
            self.assertEqual(m.describe([1]), [f"mod{i:02d}:1"])


if __name__ == "__main__":
    unittest.main()
