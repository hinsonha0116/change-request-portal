from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("accounts.urls")),
    path("", include("changes.urls")),
]

if settings.PORTAL_SSO_ENABLED:
    urlpatterns.append(path("oidc/", include("mozilla_django_oidc.urls")))
