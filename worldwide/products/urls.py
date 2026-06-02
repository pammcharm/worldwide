from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list_view, name="list"),
    path("category/<slug:slug>/", views.category_view, name="category"),
    path("brand/<slug:slug>/", views.brand_view, name="brand"),
    path("<slug:slug>/", views.product_detail_view, name="detail"),
]
