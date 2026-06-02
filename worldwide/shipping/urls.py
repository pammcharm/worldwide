from django.urls import path
from . import views

app_name = "shipping"

urlpatterns = [
    path("methods/", views.shipping_methods_view, name="methods"),
]
