from datetime import date, timedelta
from django.core.management.base import BaseCommand
from refunds.models import Customer, Order

CUSTOMERS = [
    ("Amara Okafor", "amara@example.com"), ("Liam Carter", "liam@example.com"),
    ("Sofia Reyes", "sofia@example.com"), ("Noah Kim", "noah@example.com"),
    ("Chidi Eze", "chidi@example.com"), ("Emma Wilson", "emma@example.com"),
    ("Yusuf Bello", "yusuf@example.com"), ("Olivia Brown", "olivia@example.com"),
    ("Mateo Silva", "mateo@example.com"), ("Zara Ahmed", "zara@example.com"),
    ("Ethan Clark", "ethan@example.com"), ("Ngozi Adeyemi", "ngozi@example.com"),
    ("Ava Martin", "ava@example.com"), ("Lucas Weber", "lucas@example.com"),
    ("Grace Lee", "grace@example.com"),
]

# (order_id, email, item, amount, days_ago, final_sale, refunded)
ORDERS = [
    ("ORD-1001", "amara@example.com", "Wireless Earbuds", 89.99, 5, False, False),
    ("ORD-1002", "amara@example.com", "Phone Case", 19.99, 60, False, False),
    ("ORD-1003", "liam@example.com", "Clearance Sneakers", 45.00, 10, True, False),
    ("ORD-1004", "liam@example.com", "Running Socks", 12.00, 8, False, False),
    ("ORD-1005", "sofia@example.com", "4K Monitor", 649.00, 7, False, False),
    ("ORD-1006", "noah@example.com", "Desk Lamp", 34.50, 45, False, False),
    ("ORD-1007", "noah@example.com", "Mechanical Keyboard", 129.00, 12, False, False),
    ("ORD-1008", "chidi@example.com", "Blender", 79.00, 3, False, False),
    ("ORD-1009", "chidi@example.com", "Coffee Maker", 110.00, 20, False, True),
    ("ORD-1010", "emma@example.com", "Laptop", 1299.00, 14, False, False),
    ("ORD-1011", "yusuf@example.com", "Yoga Mat", 25.00, 2, False, False),
    ("ORD-1012", "olivia@example.com", "Final Sale Jacket", 150.00, 6, True, False),
    ("ORD-1013", "mateo@example.com", "Bluetooth Speaker", 59.00, 29, False, False),
    ("ORD-1014", "mateo@example.com", "Backpack", 70.00, 31, False, False),
    ("ORD-1015", "zara@example.com", "Smart Watch", 199.00, 9, False, False),
    ("ORD-1016", "zara@example.com", "Headphones", 89.00, 40, False, True),
    ("ORD-1017", "zara@example.com", "Tablet Stand", 30.00, 50, False, True),
    ("ORD-1018", "zara@example.com", "Webcam", 60.00, 70, False, True),
    ("ORD-1019", "ethan@example.com", "Gaming Mouse", 55.00, 4, False, False),
    ("ORD-1020", "ngozi@example.com", "Air Fryer", 120.00, 15, False, False),
    ("ORD-1021", "ava@example.com", "Perfume Set", 85.00, 11, True, False),
    ("ORD-1022", "lucas@example.com", "Office Chair", 520.00, 18, False, False),
    ("ORD-1023", "grace@example.com", "Notebook Bundle", 22.00, 1, False, False),
]


class Command(BaseCommand):
    help = "Seed customers and orders"

    def handle(self, *args, **options):
        today = date.today()
        by_email = {}
        for name, email in CUSTOMERS:
            customer, _ = Customer.objects.update_or_create(
                email=email,
                defaults={"name": name},
            )
            by_email[email] = customer

        for oid, email, item, amount, days_ago, final, refunded in ORDERS:
            Order.objects.update_or_create(
                id=oid,
                defaults={
                    "customer": by_email[email],
                    "item": item,
                    "amount": amount,
                    "order_date": today - timedelta(days=days_ago),
                    "final_sale": final,
                    "refunded": refunded,
                    "refunded_date": today - timedelta(days=max(days_ago - 3, 0)) if refunded else None,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(CUSTOMERS)} customers, {len(ORDERS)} orders"))