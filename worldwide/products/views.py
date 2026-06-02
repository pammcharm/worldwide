from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from .models import Category, Product, Brand
from reviews.models import Review
from decimal import Decimal, InvalidOperation


def product_list_view(request):
    """Main product listing with filtering."""
    products = Product.objects.filter(is_active=True, in_stock=True).select_related("category", "brand").prefetch_related("images")
    
    # Product type filter
    product_type = request.GET.get("type")
    if product_type in ("local", "import"):
        products = products.filter(product_type=product_type)

    # Category filter
    category_slug = request.GET.get("category")
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)
    else:
        category = None
    
    # Brand filter
    brand_slug = request.GET.get("brand")
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
    else:
        brand = None
    
    # Price range
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except InvalidOperation:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except InvalidOperation:
            pass
    
    # Filtering by attributes
    featured = request.GET.get("featured")
    new = request.GET.get("new")
    bestseller = request.GET.get("bestseller")
    on_sale = request.GET.get("on_sale")
    
    if featured:
        products = products.filter(is_featured=True)
    if new:
        products = products.filter(is_new=True)
    if bestseller:
        products = products.filter(is_bestseller=True)
    if on_sale:
        products = products.exclude(compare_at_price__isnull=True).exclude(compare_at_price=0)
    
    # Sorting
    sort = request.GET.get("sort", "-created_at")
    sort_options = {
        "price_asc": "price",
        "price_desc": "-price",
        "name_asc": "name",
        "name_desc": "-name",
        "newest": "-created_at",
        "rating": "-rating_avg",
        "popular": "-rating_count",
    }
    products = products.order_by(sort_options.get(sort, "-created_at"))
    
    # Pagination
    paginator = Paginator(products, 24)
    page = request.GET.get("page")
    products_page = paginator.get_page(page)
    
    categories = Category.objects.filter(is_active=True, parent=None).order_by("order", "name")
    brands = Brand.objects.filter(is_active=True)
    
    return render(request, "products/list.html", {
        "products": products_page,
        "categories": categories,
        "brands": brands,
        "current_category": category,
        "current_brand": brand,
        "current_sort": sort,
    })


def product_detail_view(request, slug):
    """Detailed product page."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = Review.objects.filter(product=product, is_approved=True).select_related("user")
    related_products = Product.objects.filter(
        category=product.category, is_active=True, in_stock=True
    ).exclude(pk=product.pk)[:8]
    
    context = {
        "product": product,
        "reviews": reviews,
        "related_products": related_products,
        "primary_image": product.images.filter(is_primary=True).first() or product.images.first(),
    }
    return render(request, "products/detail.html", context)


def category_view(request, slug):
    """Category page with its products."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True, in_stock=True)
    subcategories = category.children.filter(is_active=True)
    
    paginator = Paginator(products, 24)
    page = request.GET.get("page")
    products_page = paginator.get_page(page)
    
    return render(request, "products/category.html", {
        "category": category,
        "products": products_page,
        "subcategories": subcategories,
    })


def brand_view(request, slug):
    """Brand page with its products."""
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products = Product.objects.filter(brand=brand, is_active=True, in_stock=True)
    
    paginator = Paginator(products, 24)
    page = request.GET.get("page")
    products_page = paginator.get_page(page)
    
    return render(request, "products/brand.html", {
        "brand": brand,
        "products": products_page,
    })
