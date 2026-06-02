from django.db import models


class ShippingZone(models.Model):
    """Geographic shipping zones."""
    name = models.CharField(max_length=200)
    countries = models.CharField(max_length=500, help_text="Comma-separated country names")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ShippingMethod(models.Model):
    """Shipping methods per zone."""
    ZONE_TYPES = [
        ("local", "Local Delivery"),
        ("national", "National Shipping"),
        ("international", "International Shipping"),
        ("express", "Express Delivery"),
        ("free", "Free Shipping"),
    ]

    name = models.CharField(max_length=200)
    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name="methods")
    method_type = models.CharField(max_length=20, choices=ZONE_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_above = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Free shipping above this amount")
    estimated_days = models.CharField(max_length=50, default="3-5 business days")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} - {self.zone.name}"
