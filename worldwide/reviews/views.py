from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from products.models import Product


from django.db import models


@login_required
def review_create_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user already reviewed
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, "You have already reviewed this product.")
        return redirect("products:detail", slug=product.slug)
    
    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        title = request.POST.get("title", "")
        body = request.POST.get("body", "")
        
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            title=title,
            body=body,
            is_approved=True,  # Auto-approve for now
        )
        
        # Update product rating
        reviews = Review.objects.filter(product=product, is_approved=True)
        product.rating_count = reviews.count()
        product.rating_avg = reviews.aggregate(avg=models.Avg("rating"))["avg"] or 0
        product.save()
        
        messages.success(request, "Review submitted successfully!")
        return redirect("products:detail", slug=product.slug)
    
    return render(request, "reviews/create.html", {"product": product})
