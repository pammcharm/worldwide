from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Category, Brand, Product, ProductImage, ProductVariant, ProductSpecification


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "icon_preview", "parent", "is_active", "featured", "product_count", "order"]
    list_filter = ["is_active", "featured"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["is_active", "featured", "order"]

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<span style="background:#eef2ff;padding:2px 8px;border-radius:999px;font-size:11px;">{}</span>', obj.icon)
        return "-"
    icon_preview.short_description = "Icon"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name", "sku", "get_price_display", "get_price_rwf_display",
        "product_type", "origin_platform", "source_link_preview",
        "category", "in_stock", "is_featured", "is_active", "created_at"
    ]
    list_filter = [
        "is_active", "is_featured", "is_new", "is_bestseller",
        "in_stock", "category", "brand", "product_type", "origin_platform"
    ]
    search_fields = ["name", "sku", "description", "source_url"]
    list_editable = ["in_stock", "is_featured", "is_active"]
    inlines = [ProductImageInline, ProductVariantInline, ProductSpecificationInline]
    readonly_fields = [
        "rating_avg", "rating_count", "created_at", "updated_at",
        "calculated_price_rwf", "trust_label_display", "full_source_link",
        "price_breakdown_display",
    ]

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "slug", "sku", "description", "short_description")
        }),
        ("Organization", {
            "fields": ("category", "brand", "tags")
        }),
        ("STEP 1: Product Source", {
            "description": "ALWAYS set the source URL first. Paste the original product link from Alibaba, Amazon, eBay, etc.",
            "fields": (
                "product_type", "origin_platform", "full_source_link", "source_url", "estimated_delivery_days",
            ),
        }),
        ("STEP 2: Import Pricing Engine", {
            "description": "Enter original USD price AND weight in kg. The system auto-calculates the final RWF price using the formula: [P + (W x $12) + (P x 10%)] x 1,350",
            "classes": ("wide",),
            "fields": (
                "original_price_usd", "weight",
                "shipping_cost_per_kg", "service_fee_percent",
                "usd_to_rwf_rate", "calculated_price_rwf",
                "price_breakdown_display", "trust_label_display",
            ),
        }),
        ("Display Price", {
            "description": "This is auto-set from the pricing engine. You can override manually if needed.",
            "fields": ("price", "compare_at_price", "cost_price")
        }),
        ("Stock", {
            "fields": ("in_stock", "stock_quantity", "low_stock_threshold")
        }),
        ("Attributes", {
            "fields": ("dimensions",)
        }),
        ("Status", {
            "fields": ("is_active", "is_featured", "is_new", "is_bestseller")
        }),
        ("Ratings", {
            "fields": ("rating_avg", "rating_count")
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def get_price_display(self, obj):
        if obj.original_price_usd:
            return f"${obj.original_price_usd} USD"
        return f"{obj.price}"
    get_price_display.short_description = "Orig. Price"

    def get_price_rwf_display(self, obj):
        if obj.calculated_price_rwf:
            return format_html(
                '<span style="color:#16a34a;font-weight:bold;">{} RWF</span>',
                f"{obj.calculated_price_rwf:,.0f}"
            )
        return format_html('<span style="color:#666;">{}</span>', obj.price)
    get_price_rwf_display.short_description = "Price (RWF)"

    def source_link_preview(self, obj):
        if obj.source_url:
            platform_icons = {
                "alibaba": "Alibaba",
                "amazon": "Amazon",
                "ebay": "eBay",
                "trendyol": "Trendyol",
                "aliexpress": "AliExpress",
            }
            platform = platform_icons.get(obj.origin_platform, "Source")
            return format_html(
                '<a href="{}" target="_blank" style="color:#4f46e5;font-size:11px;">{} - Open Source</a>',
                obj.source_url, platform
            )
        return mark_safe('<span style="color:#dc2626;font-size:11px;">No link</span>')
    source_link_preview.short_description = "Source"

    def full_source_link(self, obj):
        if obj.source_url:
            return format_html(
                '<div style="padding:8px 12px;background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;margin:4px 0;">'
                '<strong>Source URL:</strong> <a href="{}" target="_blank" style="color:#1d4ed8;word-break:break-all;">{}</a>'
                '</div>',
                obj.source_url, obj.source_url
            )
        return mark_safe(
            '<div style="padding:8px 12px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;margin:4px 0;">'
            '<strong style="color:#dc2626;">No source link set!</strong> Paste the product link above.'
            '</div>'
        )
    full_source_link.short_description = "Product Source Link"

    def trust_label_display(self, obj):
        if obj.is_import:
            return format_html(
                '<span style="background:#dbeafe;color:#1d4ed8;padding:4px 10px;border-radius:999px;font-size:12px;">Import - {}</span>',
                obj.trust_label
            )
        return format_html(
            '<span style="background:#dcfce7;color:#16a34a;padding:4px 10px;border-radius:999px;font-size:12px;">Local - {}</span>',
            obj.trust_label
        )
    trust_label_display.short_description = "Customer Trust Label"

    def price_breakdown_display(self, obj):
        pb = obj.price_breakdown
        if not pb:
            return mark_safe('<span style="color:#64748b;">Enter original price + weight above to see breakdown</span>')
        return format_html(
            '<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;font-family:monospace;font-size:12px;line-height:1.8;">'
            '<div style="display:flex;justify-content:space-between;"><span>Item Cost:</span><span style="font-weight:bold;">${}</span></div>'
            '<div style="display:flex;justify-content:space-between;"><span>Shipping ({}kg x ${}/kg):</span><span style="font-weight:bold;">${}</span></div>'
            '<div style="display:flex;justify-content:space-between;"><span>Service Fee ({}%):</span><span style="font-weight:bold;">${}</span></div>'
            '<div style="border-top:1px solid #e2e8f0;margin:4px 0;"></div>'
            '<div style="display:flex;justify-content:space-between;"><span>Total USD:</span><span style="font-weight:bold;">${}</span></div>'
            '<div style="display:flex;justify-content:space-between;"><span>Rate:</span><span>{} RWF/USD</span></div>'
            '<div style="border-top:2px solid #16a34a;margin:4px 0;"></div>'
            '<div style="display:flex;justify-content:space-between;font-size:14px;"><span style="color:#16a34a;">FINAL PRICE:</span><span style="color:#16a34a;font-weight:bold;">{} RWF</span></div>'
            '</div>',
            pb["item_cost_usd"],
            pb["weight_kg"], obj.shipping_cost_per_kg, pb["shipping_cost_usd"],
            obj.service_fee_percent, pb["service_fee_usd"],
            pb["total_usd"],
            pb["exchange_rate"],
            f"{obj.calculated_price_rwf:,.0f}" if obj.calculated_price_rwf else "0",
        )
    price_breakdown_display.short_description = "Price Calculation"

    def save_model(self, request, obj, form, change):
        if obj.product_type == "import" and obj.original_price_usd:
            obj._calculate_import_price()
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "is_primary", "order"]
    list_filter = ["is_primary"]
