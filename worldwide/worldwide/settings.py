#!/usr/bin/env python
"""WorldWide E-Commerce Platform - Main Settings"""
import os
from pathlib import Path
from urllib.parse import parse_qsl, urlparse, unquote
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent


def bool_config(name, default=False):
    value = config(name, default=default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in {"0", "false", "no", "off", "release", "production", "prod"}


SECRET_KEY = config("SECRET_KEY", default="django-insecure-dev-key-change-in-production")
DEBUG = bool_config("DEBUG", default=False)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,0.0.0.0,.onrender.com,worldwide-g58k.onrender.com",
    cast=Csv(),
)


def database_config(default_sqlite_path):
    database_url = config("DATABASE_URL", default="").strip()
    direct_url = config("DIRECT_URL", default="").strip()
    if bool_config("USE_DIRECT_DATABASE_URL", default=False) and direct_url:
        database_url = direct_url
    if not database_url or database_url.startswith("sqlite"):
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": default_sqlite_path,
        }

    parsed = urlparse(database_url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ValueError("DATABASE_URL must be a sqlite, postgres, or postgresql URL.")

    options = {
        key: value
        for key, value in parse_qsl(parsed.query)
        if key not in {"pgbouncer"}
    }
    netloc_auth = parsed.netloc.rsplit("@", 1)[0] if "@" in parsed.netloc else ""
    raw_username = netloc_auth.rsplit(":", 1)[0] if netloc_auth else (parsed.username or "")
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/")),
        "USER": unquote(raw_username),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or ""),
        "OPTIONS": options,
    }

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    # "debug_toolbar",  # Temporarily disabled - version conflict
]

LOCAL_APPS = [
    "core",
    "products",
    "accounts",
    "cart",
    "orders",
    "shipping",
    "payments",
    "reviews",
    "wishlist",
    "search",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Security settings (override in production via .env)
SECURE_BROWSER_XSS_FILTER = config("SECURE_BROWSER_XSS_FILTER", default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config("SECURE_CONTENT_TYPE_NOSNIFF", default=True, cast=bool)
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=False, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# HSTS (enable in production)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False, cast=bool)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=False, cast=bool)
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)

# Content Security Policy header
CSP_DEFAULT_SRC = config("CSP_DEFAULT_SRC", default="'self'")
CSP_SCRIPT_SRC = config("CSP_SCRIPT_SRC", default="'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net")
CSP_STYLE_SRC = config("CSP_STYLE_SRC", default="'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com")
CSP_FONT_SRC = config("CSP_FONT_SRC", default="'self' https://fonts.gstatic.com")
CSP_IMG_SRC = config("CSP_IMG_SRC", default="'self' data: https:")

ROOT_URLCONF = "worldwide.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",
                "cart.context_processors.cart_count",
                "products.context_processors.media_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "worldwide.wsgi.application"

# Database: Supabase Postgres via DATABASE_URL, SQLite fallback for local dev.
DATABASES = {"default": database_config(BASE_DIR / "db.sqlite3")}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Kigali"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# WhiteNoise configuration for serving media files
WHITENOISE_ROOT = BASE_DIR / 'media'
WHITENOISE_URL = '/media/'
WHITENOISE_INDEX_FILE = True

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Storage configuration
USE_S3_STORAGE = bool_config("USE_S3_STORAGE", default=False)

if USE_S3_STORAGE:
    # Configure S3/Supabase Storage backend
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "bucket_name": config("AWS_STORAGE_BUCKET_NAME", default=""),
                "region_name": config("AWS_S3_REGION_NAME", default="us-east-1"),
                "access_key": config("AWS_S3_ACCESS_KEY_ID", default=""),
                "secret_key": config("AWS_S3_SECRET_ACCESS_KEY", default=""),
                "use_ssl": bool_config("AWS_S3_USE_SSL", default=True),
                "verify": bool_config("AWS_S3_VERIFY", default=True),
                "default_acl": "public-read",
                "querystring_auth": False,
            }
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    # Update media URL for S3
    custom_domain = config("AWS_S3_CUSTOM_DOMAIN", default="")
    if custom_domain:
        MEDIA_URL = f"https://{custom_domain}/media/"
    else:
        bucket = config("AWS_STORAGE_BUCKET_NAME", default="")
        region = config("AWS_S3_REGION_NAME", default="us-east-1")
        MEDIA_URL = f"https://{bucket}.s3.{region}.amazonaws.com/media/"
else:
    # Use local filesystem storage
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Site
SITE_ID = 1

# Login redirects
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"
LOGIN_URL = "accounts:login"

# Supabase
SUPABASE_URL = config("SUPABASE_URL", default="").rstrip("/")
SUPABASE_ANON_KEY = config("SUPABASE_ANON_KEY", default="")
SUPABASE_SECRET_KEY = config("SUPABASE_SECRET_KEY", default="")
SUPABASE_AUTH_ENABLED = bool(SUPABASE_URL and SUPABASE_ANON_KEY)
SUPABASE_OAUTH_PROVIDERS = ["google", "github"]

# Stripe
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")

# Paypack Rwanda Mobile Money
PAYPACK_CLIENT_ID = config("PAYPACK_CLIENT_ID", default="")
PAYPACK_CLIENT_SECRET = config("PAYPACK_CLIENT_SECRET", default="")
PAYPACK_BASE_URL = config("PAYPACK_BASE_URL", default="https://payments.paypack.rw/api").rstrip("/")
PAYPACK_WEBHOOK_MODE = config("PAYPACK_WEBHOOK_MODE", default="production")
PAYPACK_WEBHOOK_SECRET = config("PAYPACK_WEBHOOK_SECRET", default="")
PAYPACK_TIMEOUT_SECONDS = config("PAYPACK_TIMEOUT_SECONDS", default=20, cast=int)

# Email
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

# Debug toolbar
INTERNAL_IPS = ["127.0.0.1"]

# Session
SESSION_COOKIE_AGE = 86400 * 30  # 30 days
CART_SESSION_ID = "cart"

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "payments": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
import os
logs_dir = BASE_DIR / "logs"
os.makedirs(logs_dir, exist_ok=True)
