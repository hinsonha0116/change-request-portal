"""Settings for the standalone Change Request Portal.

Everything that differs between a laptop and the cluster comes from
environment variables, so the same image runs in both.
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


DEBUG = env_bool("DJANGO_DEBUG", False)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Set DJANGO_SECRET_KEY (or DJANGO_DEBUG=1 for local work).")
    SECRET_KEY = "local-development-only-not-a-secret"

ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "changes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "changes.context.portal",
            ],
        },
    },
]

# PostgreSQL when POSTGRES_HOST is set (the cluster); SQLite otherwise (laptop, tests).
if os.environ.get("POSTGRES_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "NAME": os.environ.get("POSTGRES_DB", "portal"),
            "USER": os.environ.get("POSTGRES_USER", "portal"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("PORTAL_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "board"
LOGOUT_REDIRECT_URL = "login"


def required_env(name):
    value = os.environ.get(name, "")
    if not value:
        raise ImproperlyConfigured(f"Single sign-on is on (OIDC_RP_CLIENT_ID is set), so {name} must be set too.")
    return value


# --- Sign-in -----------------------------------------------------------------
# Single sign-on (OpenID Connect) switches on when OIDC_RP_CLIENT_ID is set.
# It works with any provider that speaks OIDC (Keycloak, Dex, GitLab, ...).
OIDC_RP_CLIENT_ID = os.environ.get("OIDC_RP_CLIENT_ID", "")
PORTAL_SSO_ENABLED = bool(OIDC_RP_CLIENT_ID)
# Local user names and passwords. Always on when there is no single sign-on.
PORTAL_LOCAL_LOGIN = env_bool("PORTAL_LOCAL_LOGIN", True) or not PORTAL_SSO_ENABLED

AUTHENTICATION_BACKENDS = []
if PORTAL_SSO_ENABLED:
    INSTALLED_APPS.append("mozilla_django_oidc")
    AUTHENTICATION_BACKENDS.append("accounts.oidc.PortalOIDCBackend")
    OIDC_RP_CLIENT_SECRET = required_env("OIDC_RP_CLIENT_SECRET")
    OIDC_OP_AUTHORIZATION_ENDPOINT = required_env("OIDC_OP_AUTHORIZATION_ENDPOINT")
    OIDC_OP_TOKEN_ENDPOINT = required_env("OIDC_OP_TOKEN_ENDPOINT")
    OIDC_OP_USER_ENDPOINT = required_env("OIDC_OP_USER_ENDPOINT")
    OIDC_OP_JWKS_ENDPOINT = required_env("OIDC_OP_JWKS_ENDPOINT")
    OIDC_RP_SIGN_ALGO = os.environ.get("OIDC_RP_SIGN_ALGO", "RS256")
    OIDC_RP_SCOPES = os.environ.get("OIDC_RP_SCOPES", "openid email profile")
    OIDC_USE_PKCE = True
    OIDC_TIMEOUT = 10
if PORTAL_LOCAL_LOGIN:
    AUTHENTICATION_BACKENDS.append("django.contrib.auth.backends.ModelBackend")

# Which claim holds the user name, and which holds the user's groups.
PORTAL_OIDC_USERNAME_CLAIM = os.environ.get("PORTAL_OIDC_USERNAME_CLAIM", "preferred_username")
PORTAL_OIDC_GROUPS_CLAIM = os.environ.get("PORTAL_OIDC_GROUPS_CLAIM", "groups")
# Optional: take roles from the provider's groups, e.g. "cm=change-managers,trb=trb-members".
# A role listed here is set from the group at every sign-in. Roles not listed stay as set on the People screen.
PORTAL_OIDC_ROLE_GROUPS = dict(
    pair.strip().split("=", 1)
    for pair in os.environ.get("PORTAL_OIDC_ROLE_GROUPS", "").split(",")
    if "=" in pair
)

# --- Notifications and email ---------------------------------------------------
# Every notification shows in the app. Email is sent as well once EMAIL_HOST is set.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
PORTAL_EMAIL_ENABLED = bool(EMAIL_HOST)
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.environ.get("PORTAL_EMAIL_FROM", "change-management@localhost")
# The address people use to reach the portal, e.g. https://changes.example. Used for links in emails.
PORTAL_BASE_URL = os.environ.get("PORTAL_BASE_URL", "").rstrip("/")

# Largest single attachment, in megabytes. Attachments are stored in the database.
PORTAL_MAX_UPLOAD_MB = int(os.environ.get("PORTAL_MAX_UPLOAD_MB", "25"))

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
