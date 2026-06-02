from django.db import models
from django.conf import settings


class Wishlist(models.Model):
    """User wishlist."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField("products.Product", blank=True, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

    @property
    def count(self):
        return self.products.count()
