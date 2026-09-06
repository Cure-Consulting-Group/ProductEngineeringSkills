import sys, unittest
from pathlib import Path
SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from importer import import_roster  # noqa: E402
from parser import parse_lines  # noqa: E402


class Hidden(unittest.TestCase):
    def test_all_height_forms(self):
        text = "A, 6'2\", G\nB, 6' 2\", F\nC, 6-2, C\nD, 74, G\nE, 6ft 2in, F\n"
        self.assertEqual([r["height_in"] for r in import_roster(text)], [74] * 5)

    def test_names_keep_apostrophes(self):
        rows = import_roster("Shaquille O'Neal, 7'1\", C\n")
        self.assertEqual(rows[0]["name"], "Shaquille O'Neal")
        self.assertEqual(rows[0]["height_in"], 85)

    def test_parser_unchanged_behaviour(self):
        rows = parse_lines("# comment\n\nX, 6'0\", G\nbad line\n")
        self.assertEqual(rows, [{"name": "X", "height_raw": "6'0\"", "pos": "G"}])

    def test_unparseable_height_still_dropped(self):
        self.assertEqual(import_roster("Z, tall, G\n"), [])

    def test_no_row_lost_in_bulk(self):
        text = "".join(f"P{i}, 6'{i % 10}\", G\n" for i in range(40))
        self.assertEqual(len(import_roster(text)), 40)


if __name__ == "__main__":
    unittest.main()
