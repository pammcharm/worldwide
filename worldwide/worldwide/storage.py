"""
Storage configuration for local development and production.
Supports local filesystem and S3/Supabase Storage.
"""
import os
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def get_storage_backend():
    """
    Determine storage backend:
    - Development: Local filesystem (django.core.files.storage.FileSystemStorage)
    - Production with S3: storages.backends.s3boto3.S3Boto3Storage
    - Production local: Local filesystem with media collection
    """
    use_s3 = config("USE_S3_STORAGE", default=False, cast=bool)
    
    if use_s3 and not config("DEBUG", default=True, cast=bool):
        # Production with S3
        return "storages.backends.s3boto3.S3Boto3Storage"
    
    # Development and local production
    return "django.core.files.storage.FileSystemStorage"


STORAGES = {
    "default": {
        "BACKEND": get_storage_backend(),
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# S3/Supabase Storage Configuration (optional)
if config("USE_S3_STORAGE", default=False, cast=bool):
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_S3_CUSTOM_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN", default="")
    AWS_S3_ACCESS_KEY_ID = config("AWS_S3_ACCESS_KEY_ID", default="")
    AWS_S3_SECRET_ACCESS_KEY = config("AWS_S3_SECRET_ACCESS_KEY", default="")
    AWS_S3_USE_SSL = config("AWS_S3_USE_SSL", default=True, cast=bool)
    AWS_S3_VERIFY = config("AWS_S3_VERIFY", default=True, cast=bool)
    AWS_DEFAULT_ACL = "public-read"
    AWS_QUERYSTRING_AUTH = False
    
    # URL for accessing S3 files
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    else:
        MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/media/"
