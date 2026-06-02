from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order", "method", "status", "amount_rwf", "phone_number", "transaction_id", "paid_at", "created_at"]
    list_filter = ["method", "status"]
    search_fields = ["order__order_number", "transaction_id", "phone_number"]
    readonly_fields = ["created_at", "updated_at", "payment_details"]
