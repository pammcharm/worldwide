from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("supabase/callback/", views.supabase_callback_view, name="supabase_callback"),
    path("supabase/token-login/", views.supabase_token_login_view, name="supabase_token_login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("address/add/", views.address_create_view, name="address_add"),
    path("address/<int:pk>/edit/", views.address_edit_view, name="address_edit"),
    path("address/<int:pk>/delete/", views.address_delete_view, name="address_delete"),
]
