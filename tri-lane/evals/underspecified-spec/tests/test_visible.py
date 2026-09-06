import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quote import quote_cents  # noqa: E402


class Visible(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(quote_cents(2, 500, 0), 1000)

    def test_discount_rounding(self):
        # 3 * 333 = 999; 10% off = 899.1 -> the rounding rule is not in the spec
        self.assertEqual(quote_cents(3, 333, 10), 899)


if __name__ == "__main__":
    unittest.main()
