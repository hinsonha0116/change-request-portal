"""Local development settings: debug on, SQLite, no secret key needed.

Use with: python manage.py runserver --settings config.settings_dev
Never use this in the cluster.
"""
import os

os.environ.setdefault("DJANGO_DEBUG", "1")

from .settings import *  # noqa: E402,F401,F403
