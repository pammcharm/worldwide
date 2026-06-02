from django.contrib import admin
from .models import Order, OrderItem, Coupon


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_name", "product_sku", "price", "quantity", "total"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "user", "total", "status", "payment_status", "created_at"]
    list_filter = ["status", "payment_status", "created_at"]
    search_fields = ["order_number", "user__email", "shipping_name"]
    list_editable = ["status", "payment_status"]
    readonly_fields = ["order_number", "created_at", "updated_at"]
    inlines = [OrderItemInline]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_type", "discount_value", "used_count", "max_uses", "is_active", "valid_until"]
    list_filter = ["discount_type", "is_active"]
    list_editable = ["is_active"]
