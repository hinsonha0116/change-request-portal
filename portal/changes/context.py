from django.conf import settings

from accounts.views import can_manage_people


def portal(request):
    """Values the page header and the sign-in page need on every screen."""
    context = {"sso_enabled": settings.PORTAL_SSO_ENABLED, "local_login": settings.PORTAL_LOCAL_LOGIN}
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        context["unread_count"] = user.notifications.filter(read_at__isnull=True).count()
        context["can_manage_people"] = can_manage_people(user)
    return context
