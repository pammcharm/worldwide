from django.contrib import admin
from .models import Review, ReviewImage


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "rating", "is_approved", "is_verified_purchase", "created_at"]
    list_filter = ["rating", "is_approved", "is_verified_purchase"]
    search_fields = ["product__name", "user__email", "body"]
    list_editable = ["is_approved"]
    inlines = [ReviewImageInline]
