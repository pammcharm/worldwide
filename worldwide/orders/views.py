from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem, Coupon
from cart.cart import Cart


@login_required
def checkout_view(request):
    """Checkout page - create order from cart."""
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty!")
        return redirect("cart:detail")
    
    if request.method == "POST":
        # Create order
        order = Order(
            user=request.user,
            email=request.POST.get("email", request.user.email),
            phone=request.POST.get("phone", request.user.phone),
            shipping_name=request.POST.get("shipping_name", ""),
            shipping_street=request.POST.get("shipping_street", ""),
            shipping_city=request.POST.get("shipping_city", ""),
            shipping_state=request.POST.get("shipping_state", ""),
            shipping_postal_code=request.POST.get("shipping_postal_code", ""),
            shipping_country=request.POST.get("shipping_country", "Rwanda"),
            subtotal=cart.get_total_price(),
            shipping_cost=0,
            tax=0,
            total=cart.get_total_price(),
        )
        
        # Apply coupon
        coupon_code = request.POST.get("coupon_code", "").strip()
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.is_valid:
                    if coupon.discount_type == "percent":
                        order.discount = order.subtotal * (coupon.discount_value / 100)
                    else:
                        order.discount = coupon.discount_value
                    order.total = order.subtotal - order.discount
                    coupon.used_count += 1
                    coupon.save()
                else:
                    messages.warning(request, "Coupon is not valid.")
            except Coupon.DoesNotExist:
                messages.warning(request, "Invalid coupon code.")
        
        order.save()
        
        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product_name=item["product"].name,
                product_sku=item["product"].sku,
                price=item["price"],
                quantity=item["quantity"],
                total=item["total_price"],
            )
        
        cart.clear()
        messages.success(request, f"Order {order.order_number} created. Choose how you want to pay in Rwanda.")
        return redirect("payments:pay", order_number=order.order_number)
    
    return render(request, "orders/checkout.html", {
        "cart": cart,
        "addresses": request.user.addresses.all(),
    })


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, "orders/detail.html", {"order": order})


@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "orders/list.html", {"orders": orders})


@login_required
def order_cancel_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.status in ["pending", "confirmed"]:
        order.status = "cancelled"
        order.save()
        messages.success(request, "Order cancelled successfully.")
    else:
        messages.error(request, "This order cannot be cancelled.")
    return redirect("orders:detail", order_number=order.order_number)
