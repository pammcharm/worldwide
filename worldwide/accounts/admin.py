from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["email", "username", "first_name", "last_name", "is_vendor", "is_verified", "is_active", "created_at"]
    list_filter = ["is_vendor", "is_verified", "is_active", "is_staff", "created_at"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-created_at"]
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("phone", "avatar", "bio", "date_of_birth", "is_vendor", "is_verified")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "label", "city", "country", "is_default"]
    list_filter = ["country", "is_default"]
    search_fields = ["user__email", "city", "country"]
