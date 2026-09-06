import sys, unittest
from pathlib import Path
SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import fees  # noqa: E402


class Hidden(unittest.TestCase):
    def test_cap_and_uncapped(self):
        self.assertEqual(fees.processing_fee(1000000, True), 500)
        self.assertEqual(fees.processing_fee(10000, True), 320)
        self.assertEqual(fees.processing_fee(0, False), 5)

    def test_untouched_functions_behave_exactly_as_before(self):
        self.assertEqual(fees.refund_fee(12345), 123)
        self.assertEqual(fees.monthly_summary([]), {"count": 0, "total": 0, "avg": 0})
        self.assertEqual(fees.monthly_summary([1, 2]), {"count": 2, "total": 3, "avg": 1.5})
        self.assertTrue(fees.is_high_value(200000))

    def test_source_of_other_functions_unchanged(self):
        src = (SRC / "fees.py").read_text()
        self.assertIn("if card == True:", src)
        self.assertIn("if fee < MINIMUM: fee = MINIMUM", src)
        self.assertIn("# TODO: this should probably mirror processing_fee", src)
        self.assertIn("amount_cents != None", src)
        self.assertIn("total = total + f", src)

    def test_constants_unchanged(self):
        self.assertEqual((fees.CARD_BPS, fees.CARD_FIXED, fees.CASH_BPS, fees.MINIMUM), (290, 30, 0, 5))


if __name__ == "__main__":
    unittest.main()
