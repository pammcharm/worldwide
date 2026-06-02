from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    """Hierarchical product category."""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Lucide icon name (e.g., laptop, shirt, home)")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:category", kwargs={"slug": self.slug})

    @property
    def product_count(self):
        return self.products.filter(is_active=True, in_stock=True).count()


class Brand(models.Model):
    """Product brand/manufacturer."""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Core product model - sells everything."""
    PRODUCT_TYPE_CHOICES = [
        ("local", "Local Stock (Instant Delivery)"),
        ("import", "Import On-Demand"),
    ]

    ORIGIN_PLATFORM_CHOICES = [
        ("alibaba", "Alibaba (China)"),
        ("amazon", "Amazon (USA)"),
        ("ebay", "eBay (Global)"),
        ("trendyol", "Trendyol (Turkey)"),
        ("aliexpress", "AliExpress (China)"),
        ("other", "Other"),
    ]

    # Basic info
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)

    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Organization
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")

    # Stock
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    # Physical attributes
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in kg (used for import price calc)")
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H in cm")

    # --- Import / Hybrid E-Commerce Fields ---
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default="import", help_text="Local = instant delivery, Import = sourced from overseas")
    origin_platform = models.CharField(max_length=20, choices=ORIGIN_PLATFORM_CHOICES, blank=True, help_text="Where this product is sourced from (Alibaba, Amazon, etc.)")
    source_url = models.URLField(max_length=1000, blank=True, help_text="Paste the original product link here (e.g., alibaba.com/item/...)")
    original_price_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Original item price in USD on the source platform")
    service_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Service commission percentage (e.g., 10.00 = 10%)")
    shipping_cost_per_kg = models.DecimalField(max_digits=8, decimal_places=2, default=12.00, help_text="International shipping cost per kg in USD (air cargo to Rwanda)")
    usd_to_rwf_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1350.00, help_text="Current USD to RWF exchange rate")
    calculated_price_rwf = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, editable=False, help_text="Auto-calculated final price in RWF")
    estimated_delivery_days = models.CharField(max_length=50, blank=True, default="10-14 days", help_text="Estimated delivery time for import items")

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)

    # Ratings (cached)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "in_stock"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["price"]),
            models.Index(fields=["product_type"]),
            models.Index(fields=["origin_platform"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            prefix = "IMP" if self.product_type == "import" else "LOC"
            import uuid
            self.sku = f"WW-{prefix}-{uuid.uuid4().hex[:8].upper()}"
        # Auto-calculate RWF price for import products
        if self.product_type == "import" and self.original_price_usd:
            self._calculate_import_price()
        super().save(*args, **kwargs)

    def _calculate_import_price(self):
        """
        Pricing Engine Formula:
        Final RWF = [P_original + (W × C_shipping) + (P_original × R_agency)] × E_rate

        Where:
        P_original = original item price in USD
        W = weight in kg
        C_shipping = shipping cost per kg (USD)
        R_agency = service fee percentage (as decimal)
        E_rate = USD to RWF exchange rate
        """
        from decimal import Decimal
        p = self.original_price_usd or Decimal("0")
        w = self.weight or Decimal("0")
        c = self.shipping_cost_per_kg or Decimal("12.00")
        r = (self.service_fee_percent or Decimal("10.00")) / Decimal("100")
        e = self.usd_to_rwf_rate or Decimal("1350.00")

        shipping_cost = w * c
        service_fee = p * r
        total_usd = p + shipping_cost + service_fee
        final_rwf = total_usd * e

        self.calculated_price_rwf = final_rwf.quantize(Decimal("0.01"))
        # Also set the display price to the RWF value
        self.price = final_rwf.quantize(Decimal("0.01"))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    @property
    def discount_percent(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return int((1 - self.price / self.compare_at_price) * 100)
        return 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    @property
    def is_import(self):
        return self.product_type == "import"

    @property
    def trust_label(self):
        if self.product_type == "import":
            platform_names = dict(self.ORIGIN_PLATFORM_CHOICES)
            platform = platform_names.get(self.origin_platform, "Overseas")
            return f"Import from {platform} (Arrives in {self.estimated_delivery_days})"
        return "Local Stock - Instant Delivery"

    @property
    def price_breakdown(self):
        """Return a dict showing how the price was calculated."""
        from decimal import Decimal
        if self.product_type != "import" or not self.original_price_usd:
            return None
        p = self.original_price_usd
        w = self.weight or Decimal("0")
        c = self.shipping_cost_per_kg or Decimal("12.00")
        r = (self.service_fee_percent or Decimal("10.00")) / Decimal("100")
        e = self.usd_to_rwf_rate or Decimal("1350.00")
        return {
            "item_cost_usd": p,
            "weight_kg": w,
            "shipping_cost_usd": w * c,
            "service_fee_usd": p * r,
            "total_usd": p + (w * c) + (p * r),
            "exchange_rate": e,
            "final_rwf": self.calculated_price_rwf,
        }


class ProductImage(models.Model):
    """Additional product images."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    """Product variants (size, color, etc.)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=100, unique=True)
    price_override = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/variants/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def price(self):
        return self.price_override or self.product.price


class ProductSpecification(models.Model):
    """Technical specifications for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specifications")
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.product.name}: {self.name} = {self.value}"
