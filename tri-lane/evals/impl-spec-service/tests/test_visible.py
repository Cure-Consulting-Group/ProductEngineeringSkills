import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from refund_policy import compute_refund  # noqa: E402


class Visible(unittest.TestCase):
    def test_full_refund_window(self):
        r = compute_refund([{"sku": "a", "qty": 2, "unit_cents": 500, "refundable": True}], 1000, 0, 3)
        self.assertEqual(r["total_cents"], 1000)
        self.assertEqual(r["rate"], 1.0)

    def test_non_refundable_line(self):
        r = compute_refund([{"sku": "a", "qty": 1, "unit_cents": 500, "refundable": False}], 500, 0, 1)
        self.assertEqual(r["total_cents"], 0)


if __name__ == "__main__":
    unittest.main()
