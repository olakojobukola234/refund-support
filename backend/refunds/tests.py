from django.core.management import call_command
from django.test import TestCase
from refunds.models import Order
from refunds.services.policy import evaluate, count_recent_refunds


class PolicyTests(TestCase):
    def setUp(self):
        call_command("seed", verbosity=0)

    def run_case(self, oid, email, reason):
        order = Order.objects.filter(id=oid).first()
        return evaluate(order, email, reason, count_recent_refunds(email))

    def test_approved(self):
        self.assertEqual(self.run_case("ORD-1001", "amara@example.com", "changed_mind").status, "Approved")

    def test_final_sale_denied(self):
        self.assertEqual(self.run_case("ORD-1003", "liam@example.com", "changed_mind").rule, "FINAL_SALE")

    def test_final_sale_damaged_approved(self):
        self.assertEqual(self.run_case("ORD-1003", "liam@example.com", "damaged").status, "Approved")

    def test_too_old(self):
        self.assertEqual(self.run_case("ORD-1002", "amara@example.com", "damaged").rule, "RETURN_WINDOW")

    def test_window_boundary(self):
        self.assertEqual(self.run_case("ORD-1013", "mateo@example.com", "changed_mind").status, "Approved")
        self.assertEqual(self.run_case("ORD-1014", "mateo@example.com", "changed_mind").status, "Denied")

    def test_high_value(self):
        self.assertEqual(self.run_case("ORD-1005", "sofia@example.com", "damaged").rule, "HIGH_VALUE")

    def test_already_refunded(self):
        self.assertEqual(self.run_case("ORD-1009", "chidi@example.com", "damaged").rule, "ALREADY_REFUNDED")

    def test_wrong_owner(self):
        self.assertEqual(self.run_case("ORD-1001", "liam@example.com", "damaged").rule, "OWNER_MISMATCH")

    def test_unknown_order(self):
        self.assertEqual(self.run_case("ORD-9999", "amara@example.com", "damaged").rule, "ORDER_NOT_FOUND")

    def test_refund_pattern(self):
        self.assertEqual(self.run_case("ORD-1015", "zara@example.com", "damaged").rule, "REFUND_PATTERN")

    def test_unclear_reason(self):
        self.assertEqual(self.run_case("ORD-1011", "yusuf@example.com", "other").rule, "UNCLEAR_REASON")