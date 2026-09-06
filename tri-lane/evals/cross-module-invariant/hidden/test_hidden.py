import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from shop import inventory, ledger, orders, reconcile  # noqa: E402


class Hidden(unittest.TestCase):
    def setUp(self):
        orders.reset()
        inventory.receive("ball", 10)
        inventory.receive("net", 4)

    def test_release_restores_available_without_touching_stock(self):
        orders.place("o1", [{"sku": "ball", "qty": 3, "unit_cents": 500}])
        self.assertEqual(inventory.available("ball"), 7)
        orders.cancel("o1")
        self.assertEqual(inventory.available("ball"), 10)
        self.assertEqual(inventory._stock["ball"], 10)

    def test_ledger_reverses_both_accounts(self):
        orders.place("o1", [{"sku": "ball", "qty": 2, "unit_cents": 500}])
        orders.cancel("o1")
        self.assertEqual(ledger.balance("receivable"), 0)
        self.assertEqual(ledger.balance("revenue"), 0)

    def test_reconcile_zero_after_cancel_multi_line(self):
        orders.place("o1", [{"sku": "ball", "qty": 2, "unit_cents": 500}, {"sku": "net", "qty": 1, "unit_cents": 2000}])
        orders.cancel("o1")
        self.assertEqual(reconcile.report("o1"), {"stock_delta": 0, "ledger_delta": 0})

    def test_ship_still_decrements_stock(self):
        orders.place("o1", [{"sku": "ball", "qty": 4, "unit_cents": 500}])
        orders.ship("o1")
        self.assertEqual(inventory.available("ball"), 6)
        self.assertEqual(inventory._stock["ball"], 6)
        self.assertEqual(ledger.balance("receivable"), 2000)

    def test_cancel_twice_rejected_and_idempotent_books(self):
        orders.place("o1", [{"sku": "ball", "qty": 1, "unit_cents": 500}])
        orders.cancel("o1")
        with self.assertRaises(ValueError):
            orders.cancel("o1")
        self.assertEqual(ledger.balance("receivable"), 0)
        self.assertEqual(inventory.available("ball"), 10)

    def test_second_order_unaffected_by_first_cancel(self):
        orders.place("o1", [{"sku": "ball", "qty": 3, "unit_cents": 500}])
        orders.place("o2", [{"sku": "ball", "qty": 2, "unit_cents": 500}])
        orders.cancel("o1")
        self.assertEqual(inventory.available("ball"), 8)
        self.assertEqual(reconcile.report("o1"), {"stock_delta": 0, "ledger_delta": 0})
        self.assertEqual(ledger.balance("receivable"), 1000)   # o2's books untouched by o1's cancel
        self.assertEqual(orders.status("o2"), "placed")


if __name__ == "__main__":
    unittest.main()
