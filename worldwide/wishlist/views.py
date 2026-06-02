from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Wishlist
from products.models import Product


@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, "wishlist/detail.html", {"wishlist": wishlist})


@login_required
def wishlist_add(request, product_id):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlist.products.add(product)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True, "count": wishlist.count})
    messages.success(request, f"{product.name} added to wishlist!")
    return redirect("wishlist:detail")


@login_required
def wishlist_remove(request, product_id):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlist.products.remove(product)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True, "count": wishlist.count})
    messages.success(request, f"{product.name} removed from wishlist.")
    return redirect("wishlist:detail")
