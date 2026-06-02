import json
import re
import urllib.error
import urllib.request

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AddressForm
from .models import Address, User


def supabase_auth_context():
    return {
        "supabase_auth_enabled": settings.SUPABASE_AUTH_ENABLED,
        "supabase_url": settings.SUPABASE_URL,
        "supabase_anon_key": settings.SUPABASE_ANON_KEY,
        "supabase_providers": settings.SUPABASE_OAUTH_PROVIDERS,
    }


def unique_username_from_email(email):
    base = re.sub(r"[^a-zA-Z0-9_]+", "_", email.split("@")[0]).strip("_") or "user"
    username = base[:140]
    candidate = username
    counter = 1
    while User.objects.filter(username=candidate).exists():
        suffix = f"_{counter}"
        candidate = f"{username[:150 - len(suffix)]}{suffix}"
        counter += 1
    return candidate


def fetch_supabase_user(access_token):
    api_key = settings.SUPABASE_ANON_KEY or settings.SUPABASE_SECRET_KEY
    if not settings.SUPABASE_URL or not api_key:
        raise ValueError("Supabase is not configured.")

    request = urllib.request.Request(
        f"{settings.SUPABASE_URL}/auth/v1/user",
        headers={
            "apikey": api_key,
            "Authorization": f"Bearer {access_token}",
        },
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to WorldWide, {user.username}!")
            return redirect("core:home")
    else:
        form = UserRegistrationForm()
    context = {"form": form}
    context.update(supabase_auth_context())
    return render(request, "accounts/register.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next", "core:home")
            return redirect(next_url)
    else:
        form = UserLoginForm()
    context = {"form": form}
    context.update(supabase_auth_context())
    return render(request, "accounts/login.html", context)


def supabase_callback_view(request):
    if not settings.SUPABASE_AUTH_ENABLED:
        messages.error(request, "Supabase login is not configured yet.")
        return redirect("accounts:login")
    return render(request, "accounts/supabase_callback.html", supabase_auth_context())


@require_POST
def supabase_token_login_view(request):
    if not settings.SUPABASE_AUTH_ENABLED:
        return JsonResponse({"success": False, "error": "Supabase login is not configured."}, status=400)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        access_token = payload.get("access_token", "").strip()
        if not access_token:
            return JsonResponse({"success": False, "error": "Missing access token."}, status=400)
        supabase_user = fetch_supabase_user(access_token)
    except (json.JSONDecodeError, urllib.error.URLError, urllib.error.HTTPError, ValueError) as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=400)

    email = (supabase_user.get("email") or "").strip().lower()
    if not email:
        return JsonResponse({"success": False, "error": "Supabase account has no email address."}, status=400)

    metadata = supabase_user.get("user_metadata") or {}
    full_name = metadata.get("full_name") or metadata.get("name") or ""
    first_name = full_name.split(" ", 1)[0] if full_name else ""
    last_name = full_name.split(" ", 1)[1] if " " in full_name else ""

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": unique_username_from_email(email),
            "first_name": first_name,
            "last_name": last_name,
            "is_verified": True,
        },
    )
    if created:
        user.set_unusable_password()
        user.save()
    else:
        changed = False
        if not user.is_verified:
            user.is_verified = True
            changed = True
        if full_name and not user.first_name:
            user.first_name = first_name
            user.last_name = last_name
            changed = True
        if changed:
            user.save()

    login(request, user)
    redirect_url = settings.LOGIN_REDIRECT_URL
    if not str(redirect_url).startswith("/"):
        redirect_url = reverse(redirect_url)
    return JsonResponse({"success": True, "redirect_url": redirect_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("core:home")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("accounts:profile")
    else:
        form = UserProfileForm(instance=request.user)
    addresses = request.user.addresses.all()
    return render(request, "accounts/profile.html", {"form": form, "addresses": addresses})


@login_required
def address_create_view(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                Address.objects.filter(user=request.user).update(is_default=False)
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect("accounts:profile")
    else:
        form = AddressForm()
    return render(request, "accounts/address_form.html", {"form": form, "title": "Add Address"})


@login_required
def address_edit_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            if form.cleaned_data["is_default"]:
                Address.objects.filter(user=request.user).exclude(pk=pk).update(is_default=False)
            form.save()
            messages.success(request, "Address updated!")
            return redirect("accounts:profile")
    else:
        form = AddressForm(instance=address)
    return render(request, "accounts/address_form.html", {"form": form, "title": "Edit Address"})


@login_required
def address_delete_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Address deleted.")
    return redirect("accounts:profile")
