from .cart import Cart


def cart_count(request):
    """Make cart item count available in all templates."""
    cart = Cart(request)
    return {"cart_count": cart.get_item_count()}
