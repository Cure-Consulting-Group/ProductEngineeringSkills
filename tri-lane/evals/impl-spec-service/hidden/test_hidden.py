import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from refund_policy import compute_refund  # noqa: E402

L = lambda sku, qty, cents, ok=True: {"sku": sku, "qty": qty, "unit_cents": cents, "refundable": ok}


class Hidden(unittest.TestCase):
    def test_day_14_is_full(self):
        self.assertEqual(compute_refund([L("a", 1, 1000)], 1000, 0, 14)["total_cents"], 1000)

    def test_day_15_is_half(self):
        self.assertEqual(compute_refund([L("a", 1, 1000)], 1000, 0, 15)["total_cents"], 500)

    def test_day_30_is_half_day_31_is_zero(self):
        self.assertEqual(compute_refund([L("a", 1, 1000)], 1000, 0, 30)["total_cents"], 500)
        self.assertEqual(compute_refund([L("a", 1, 1000)], 1000, 0, 31)["total_cents"], 0)

    def test_floor_per_line_not_total(self):
        r = compute_refund([L("a", 1, 333), L("b", 1, 333)], 666, 0, 20)
        self.assertEqual([x["eligible_cents"] for x in r["lines"]], [166, 166])
        self.assertEqual(r["total_cents"], 332)

    def test_cap_by_captured_minus_refunded(self):
        r = compute_refund([L("a", 2, 500)], 1000, 800, 1)
        self.assertEqual(r["total_cents"], 200)
        r = compute_refund([L("a", 2, 500)], 1000, 1000, 1)
        self.assertEqual(r["total_cents"], 0)

    def test_order_and_zero_lines_preserved(self):
        r = compute_refund([L("z", 1, 100, False), L("a", 1, 100)], 200, 0, 1)
        self.assertEqual([x["sku"] for x in r["lines"]], ["z", "a"])
        self.assertEqual(r["lines"][0]["eligible_cents"], 0)

    def test_negative_days_raises(self):
        with self.assertRaises(ValueError):
            compute_refund([L("a", 1, 100)], 100, 0, -1)

    def test_negative_refunded_raises(self):
        with self.assertRaises(ValueError):
            compute_refund([L("a", 1, 100)], 100, -5, 1)

    def test_integer_types(self):
        r = compute_refund([L("a", 3, 333)], 999, 0, 16)
        self.assertIsInstance(r["total_cents"], int)
        self.assertTrue(all(isinstance(x["eligible_cents"], int) for x in r["lines"]))
        self.assertEqual(r["total_cents"], 499)


if __name__ == "__main__":
    unittest.main()
