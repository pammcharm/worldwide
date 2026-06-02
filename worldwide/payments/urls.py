from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("<str:order_number>/", views.payment_view, name="pay"),
    path("<str:order_number>/stripe/", views.stripe_checkout, name="stripe_checkout"),
    path("<str:order_number>/momo-processing/", views.momo_processing, name="momo_processing"),
    path("api/check-status/<str:order_number>/", views.check_payment_status, name="check_status"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe_webhook"),
    path("webhook/momo/", views.momo_webhook, name="momo_webhook"),
]
