from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_add(request):
    cart = Cart(request)
    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart.add(product=product, quantity=quantity)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart.get_item_count(),
            "message": f"{product.name} added to cart!",
        })
    return redirect("cart:detail")


@require_POST
def cart_remove(request):
    cart = Cart(request)
    product_id = request.POST.get("product_id") or request.GET.get("product_id")
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True, "cart_total": str(cart.get_total_price())})
    return redirect("cart:detail")


@require_POST
def cart_update(request):
    cart = Cart(request)
    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))
    product = get_object_or_404(Product, id=product_id)
    cart.update_quantity(product, quantity)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        item_total = product.price * quantity
        return JsonResponse({
            "success": True,
            "item_total": str(item_total),
            "cart_total": str(cart.get_total_price()),
            "cart_count": cart.get_item_count(),
        })
    return redirect("cart:detail")
