import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pricing import apply_discount  # noqa: E402


class Visible(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(apply_discount(1000, 10), 900)

    def test_clamped_returns_int(self):
        self.assertIsInstance(apply_discount(1000, 150), int)


if __name__ == "__main__":
    unittest.main()
