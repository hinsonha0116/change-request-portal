"""Local development settings: debug on, SQLite, no secret key needed.

Use with: python manage.py runserver --settings config.settings_dev
Never use this in the cluster.
"""
import os

os.environ.setdefault("DJANGO_DEBUG", "1")

from .settings import *  # noqa: E402,F401,F403

# Print emails in the terminal instead of sending them.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
PORTAL_EMAIL_ENABLED = True
PORTAL_BASE_URL = PORTAL_BASE_URL or "http://localhost:8000"  # noqa: F405
