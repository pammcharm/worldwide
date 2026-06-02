from django.contrib import messages
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from products.models import Product, Category, Brand
from .models import Banner, ProductLinkRequest, SiteSettings


def home_view(request):
    """Homepage with featured products, banners, categories."""
    featured_products = Product.objects.filter(
        is_active=True, is_featured=True, in_stock=True
    ).select_related("category").prefetch_related("images")[:16]

    import_products = Product.objects.filter(
        is_active=True, is_featured=True, in_stock=True, product_type="import"
    ).select_related("category").prefetch_related("images")[:8]

    local_products = Product.objects.filter(
        is_active=True, is_featured=True, in_stock=True, product_type="local"
    ).select_related("category").prefetch_related("images")[:8]

    new_arrivals = Product.objects.filter(
        is_active=True, is_new=True, in_stock=True
    ).order_by("-created_at")[:8]

    bestsellers = Product.objects.filter(
        is_active=True, is_bestseller=True, in_stock=True
    ).order_by("-rating_count")[:8]

    on_sale = Product.objects.filter(
        is_active=True, in_stock=True
    ).exclude(compare_at_price__isnull=True).exclude(compare_at_price=0)[:8]

    categories = Category.objects.filter(
        is_active=True, featured=True, parent=None
    ).order_by("order")[:8]

    brands = Brand.objects.filter(is_active=True)[:12]

    banners = Banner.objects.filter(is_active=True).order_by("order")[:5]

    return render(request, "core/home.html", {
        "featured_products": featured_products,
        "import_products": import_products,
        "local_products": local_products,
        "new_arrivals": new_arrivals,
        "bestsellers": bestsellers,
        "on_sale": on_sale,
        "categories": categories,
        "brands": brands,
        "banners": banners,
    })


def product_link_request_view(request):
    """Store a customer pasted product link for admin follow-up."""
    if request.method != "POST":
        return redirect("core:home")

    product_url = request.POST.get("product_url", "").strip()
    contact_name = request.POST.get("contact_name", "").strip()
    contact_phone = request.POST.get("contact_phone", "").strip()
    notes = request.POST.get("notes", "").strip()

    validator = URLValidator()
    try:
        validator(product_url)
    except ValidationError:
        messages.error(request, "Please paste a valid product link starting with http:// or https://.")
        return redirect("core:home")

    lowered_url = product_url.lower()
    platform = "other"
    for key in ("alibaba", "amazon", "ebay", "trendyol", "aliexpress"):
        if key in lowered_url:
            platform = key
            break

    ProductLinkRequest.objects.create(
        user=request.user if request.user.is_authenticated else None,
        product_url=product_url,
        contact_name=contact_name or (request.user.full_name if request.user.is_authenticated else ""),
        contact_phone=contact_phone or (request.user.phone if request.user.is_authenticated else ""),
        notes=notes,
        platform=platform,
    )
    messages.success(request, "Product link received. We will calculate the RWF price and follow up.")
    return redirect("core:home")


def about_view(request):
    return render(request, "core/about.html")


def contact_view(request):
    return render(request, "core/contact.html")


def faq_view(request):
    return render(request, "core/faq.html")
