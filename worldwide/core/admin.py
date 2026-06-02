from django.contrib import admin
from .models import Banner, ProductLinkRequest, SiteSettings


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "order", "created_at"]
    list_editable = ["is_active", "order"]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProductLinkRequest)
class ProductLinkRequestAdmin(admin.ModelAdmin):
    list_display = ["product_url", "platform", "contact_name", "contact_phone", "status", "created_at"]
    list_filter = ["status", "platform", "created_at"]
    search_fields = ["product_url", "contact_name", "contact_phone", "notes", "admin_note"]
    list_editable = ["status"]
    readonly_fields = ["user", "product_url", "platform", "contact_name", "contact_phone", "notes", "created_at", "updated_at"]
    fieldsets = (
        ("Request", {
            "fields": ("user", "product_url", "platform", "contact_name", "contact_phone", "notes")
        }),
        ("Admin Workflow", {
            "fields": ("status", "admin_note")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )
