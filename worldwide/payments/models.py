from django.db import models
from django.conf import settings


class Payment(models.Model):
    """Payment record for orders."""
    PAYMENT_METHODS = [
        ("stripe", "Stripe (Card)"),
        ("paypal", "PayPal"),
        ("mtn_momo", "MTN Mobile Money"),
        ("airtel_money", "Airtel Money"),
        ("mpesa", "M-Pesa"),
        ("bank_transfer", "Bank Transfer"),
        ("cod", "Cash on Delivery"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_rwf = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, help_text="Mobile Money phone number")
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)
    payment_details = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment for {self.order.order_number} ({self.get_method_display()})"
