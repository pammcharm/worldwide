"""
WorldWide URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path("admin/", include("core.admin_urls")),  # Custom admin URLs
    path("", include("core.urls", namespace="core")),
    path("products/", include("products.urls", namespace="products")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("cart/", include("cart.urls", namespace="cart")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("checkout/payments/", include("payments.urls", namespace="payments")),
    path("reviews/", include("reviews.urls", namespace="reviews")),
    path("wishlist/", include("wishlist.urls", namespace="wishlist")),
    path("search/", include("search.urls", namespace="search")),
    path("shipping/", include("shipping.urls", namespace="shipping")),
]

# Serve media files - works in both DEBUG and production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production: serve media files locally when not using S3 storage.
    if not settings.USE_S3_STORAGE:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
