import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from leaderboard import top_three  # noqa: E402


class Visible(unittest.TestCase):
    def test_ties_have_an_order_the_spec_never_states(self):
        players = [{"name": "Zoe", "points": 10}, {"name": "Ava", "points": 10}, {"name": "Mia", "points": 12}, {"name": "Bo", "points": 10}]
        self.assertEqual(top_three(players), ["Mia", "Ava", "Bo"])

    def test_fewer_than_three_players(self):
        self.assertEqual(top_three([{"name": "Solo", "points": 1}]), ["Solo"])


if __name__ == "__main__":
    unittest.main()
