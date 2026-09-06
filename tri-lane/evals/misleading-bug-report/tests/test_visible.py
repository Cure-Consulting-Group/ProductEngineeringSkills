import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from importer import import_roster  # noqa: E402


class Visible(unittest.TestCase):
    def test_feet_inches_with_quotes_is_dropped_today(self):
        rows = import_roster("Ava Stone, 6'2\", G\n")
        self.assertEqual(rows, [{"name": "Ava Stone", "height_in": 74, "pos": "G"}])


if __name__ == "__main__":
    unittest.main()
