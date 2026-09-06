import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from shop import inventory, ledger, orders, reconcile  # noqa: E402


class Visible(unittest.TestCase):
    def setUp(self):
        orders.reset()
        inventory.receive("ball", 10)

    def test_cancel_restores_stock_and_books(self):
        before_avail = inventory.available("ball")
        before_recv = ledger.balance("receivable")
        orders.place("o1", [{"sku": "ball", "qty": 3, "unit_cents": 500}])
        orders.cancel("o1")
        self.assertEqual(inventory.available("ball"), before_avail)
        self.assertEqual(ledger.balance("receivable"), before_recv)
        self.assertEqual(reconcile.report("o1"), {"stock_delta": 0, "ledger_delta": 0})


if __name__ == "__main__":
    unittest.main()
