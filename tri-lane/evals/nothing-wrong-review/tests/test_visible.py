import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from orders.pricing import subtotal_cents, split_evenly, format_cents  # noqa: E402
from orders.ledger import Ledger  # noqa: E402


class Visible(unittest.TestCase):
    def test_subtotal(self):
        self.assertEqual(subtotal_cents([{"qty": 2, "unit_cents": 150}]), 300)

    def test_split(self):
        self.assertEqual(split_evenly(10, 3), [4, 3, 3])

    def test_format(self):
        self.assertEqual(format_cents(1234), "12.34")

    def test_ledger(self):
        l = Ledger()
        l.post("a", 5)
        l.post("a", -2)
        self.assertEqual(l.balance("a"), 3)


if __name__ == "__main__":
    unittest.main()
