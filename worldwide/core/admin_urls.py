from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum

admin.site.site_header = "WorldWide Admin"
admin.site.site_title = "WorldWide Admin"
admin.site.index_title = "Store Command Center"


def dashboard_view(request):
    from accounts.models import User
    from orders.models import Order
    from products.models import Product

    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:5]
    context = {
        **admin.site.each_context(request),
        "title": "Dashboard",
        "total_orders": Order.objects.count(),
        "total_revenue": Order.objects.aggregate(total=Sum("total"))["total"] or 0,
        "total_products": Product.objects.count(),
        "total_customers": User.objects.filter(is_staff=False).count(),
        "recent_orders": recent_orders,
    }
    return render(request, "admin/dashboard.html", context)


urlpatterns = [
    path("", admin.site.admin_view(dashboard_view), name="index"),
    path("", admin.site.urls),
]
