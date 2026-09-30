from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # e.g. ORD-1001
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    item = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateField()
    final_sale = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    refunded_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.id


class RefundRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    idempotency_key = models.UUIDField(unique=True, null=True, blank=True)
    customer_email = models.EmailField(blank=True)
    order_id = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    reason = models.CharField(max_length=30, blank=True)
    decision = models.CharField(max_length=20)  # Approved | Denied | Escalated
    rule = models.CharField(max_length=40, blank=True)
    reasons = models.JSONField(default=list)
    injection_flag = models.BooleanField(default=False)
    ai_status = models.CharField(max_length=24, default="not_used")
    ai_notes = models.TextField(blank=True)
    reply = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]