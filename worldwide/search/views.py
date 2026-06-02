from django.shortcuts import render
from django.db.models import Q
from products.models import Product, Category, Brand


def search_view(request):
    """Full-text search across products, categories, and brands."""
    query = request.GET.get("q", "").strip()
    results = []
    categories = []
    brands = []
    
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(sku__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query),
            is_active=True,
        ).distinct().select_related("category", "brand")
        
        categories = Category.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True,
        )
        
        brands = Brand.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True,
        )
    
    return render(request, "search/results.html", {
        "query": query,
        "results": results,
        "categories": categories,
        "brands": brands,
        "total_results": len(results) + len(categories) + len(brands),
    })


def search_autocomplete(request):
    """AJAX autocomplete for search."""
    from django.http import JsonResponse
    query = request.GET.get("q", "").strip()
    suggestions = []
    
    if query and len(query) >= 2:
        products = Product.objects.filter(
            name__icontains=query, is_active=True
        ).values("name", "slug")[:8]
        suggestions = list(products)
    
    return JsonResponse({"suggestions": suggestions})
