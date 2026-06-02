from django.shortcuts import render
from .models import ShippingMethod, ShippingZone


def shipping_methods_view(request):
    """Display available shipping methods."""
    methods = ShippingMethod.objects.filter(is_active=True).select_related("zone")
    return render(request, "shipping/methods.html", {"methods": methods})
