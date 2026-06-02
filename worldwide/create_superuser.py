#!/usr/bin/env python
"""Create a superuser for WorldWide."""
import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "worldwide.settings")
django.setup()

from accounts.models import User

if not User.objects.filter(email="admin@worldwide.com").exists():
    User.objects.create_superuser("admin@worldwide.com", "admin", "admin123")
    print("Superuser created: admin@worldwide.com / admin123")
else:
    print("Superuser already exists")
