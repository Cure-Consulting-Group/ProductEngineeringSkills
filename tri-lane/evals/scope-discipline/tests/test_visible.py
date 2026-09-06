import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from fees import processing_fee  # noqa: E402


class Visible(unittest.TestCase):
    def test_small_card_fee_unchanged(self):
        self.assertEqual(processing_fee(1000, True), 59)

    def test_cap(self):
        self.assertEqual(processing_fee(1000000, True), 500)


if __name__ == "__main__":
    unittest.main()
