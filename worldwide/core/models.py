from django.conf import settings
from django.db import models


class Banner(models.Model):
    """Homepage banners/carousel slides."""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to="banners/")
    button_text = models.CharField(max_length=50, default="Shop Now")
    button_url = models.CharField(max_length=500, default="#")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    """Global site configuration."""
    site_name = models.CharField(max_length=200, default="Worldwide e-shopping LTD")
    tagline = models.CharField(max_length=300, default="We help you buy products on Alibaba, Amazon, eBay, and many more...")
    logo = models.ImageField(upload_to="site/", blank=True)
    favicon = models.ImageField(upload_to="site/", blank=True)
    footer_text = models.TextField(default="&copy; 2026 Worldwide e-shopping LTD. All rights reserved.")

    # Social links
    facebook_url = models.URLField(blank=True, default="https://web.facebook.com/epurchaseworldwide/")
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)

    # Contact
    contact_email = models.EmailField(default="info@worldwideshopping.rw")
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_address = models.TextField(blank=True, default="Kigali, Rwanda")

    # Features
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    currency = models.CharField(max_length=10, default="RWF")
    currency_symbol = models.CharField(max_length=5, default="RWF")

    # Pricing engine defaults
    default_shipping_cost_per_kg = models.DecimalField(max_digits=8, decimal_places=2, default=12.00, help_text="Default international shipping cost per kg in USD")
    default_service_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Default service commission percentage")
    default_usd_to_rwf_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1350.00, help_text="Default USD to RWF exchange rate")

    # MoMo / Payment settings
    mtn_momo_enabled = models.BooleanField(default=True, help_text="Enable MTN Mobile Money payments")
    airtel_money_enabled = models.BooleanField(default=True, help_text="Enable Airtel Money payments")
    stripe_enabled = models.BooleanField(default=False, help_text="Enable Stripe card payments")
    cod_enabled = models.BooleanField(default=True, help_text="Enable Cash on Delivery")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name


class ProductLinkRequest(models.Model):
    """Customer request created from a pasted external product link."""
    STATUS_CHOICES = [
        ("new", "New"),
        ("reviewing", "Reviewing"),
        ("quoted", "Quoted"),
        ("converted", "Converted to Product"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_link_requests",
    )
    product_url = models.URLField(max_length=1000)
    contact_name = models.CharField(max_length=200, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    platform = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_platform_display_name()} request #{self.pk or 'new'}"

    def get_platform_display_name(self):
        return self.platform.title() if self.platform else "Product link"
