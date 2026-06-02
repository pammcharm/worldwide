"""
Context processors for products app
"""
from django.conf import settings


def media_settings(request):
    """Add media settings to template context"""
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
        'USE_S3_STORAGE': settings.USE_S3_STORAGE,
    }
