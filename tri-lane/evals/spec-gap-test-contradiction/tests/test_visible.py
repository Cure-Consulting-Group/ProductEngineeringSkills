import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dedupe import dedupe_emails  # noqa: E402


class Visible(unittest.TestCase):
    def test_case_insensitive_keep_first(self):
        self.assertEqual(dedupe_emails(["A@x.com", " a@X.com", "b@x.com"]), ["A@x.com", "b@x.com"])

    def test_empty_list_returns_empty(self):
        self.assertEqual(dedupe_emails([]), [])


if __name__ == "__main__":
    unittest.main()
