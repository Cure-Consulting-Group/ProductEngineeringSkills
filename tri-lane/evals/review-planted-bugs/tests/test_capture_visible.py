import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from capture import CaptureService, Gateway, Line, Sale, Store  # noqa: E402


class FakeGateway(Gateway):
    def __init__(self):
        self.n = 0
    def create_intent(self, amount_cents):
        self.n += 1
        return f"pi_{self.n}"
    def confirm(self, intent_id):
        return "requires_capture"
    def capture(self, intent_id):
        return 1000
    def cancel(self, intent_id):
        pass
    def retrieve(self, intent_id):
        return {"status": "requires_capture"}
    def refund(self, intent_id, amount_cents):
        pass


class Visible(unittest.TestCase):
    def test_card_happy_path(self):
        svc = CaptureService(FakeGateway(), Store())
        sale = Sale("s1", [Line("sku", 2, 5.0)])
        svc.begin_card(sale, "tok_x")
        self.assertEqual(svc.capture_card(sale), 1000)

    def test_cash_change(self):
        svc = CaptureService(FakeGateway(), Store())
        sale = Sale("s2", [Line("sku", 1, 4.0)])
        self.assertEqual(svc.cash_checkout(sale, 500), 100)


if __name__ == "__main__":
    unittest.main()
