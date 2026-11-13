"""Single sign-on through any OpenID Connect provider.

People are matched to portal users by user name, then by email. Someone signing
in for the first time gets a portal user with no roles, so they can submit and
follow their own requests straight away.
"""
from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from .models import Role, RoleAssignment, User


class PortalOIDCBackend(OIDCAuthenticationBackend):
    def _username(self, claims):
        name = claims.get(settings.PORTAL_OIDC_USERNAME_CLAIM) or claims.get("email") or claims.get("sub") or ""
        return str(name)[:150]

    def verify_claims(self, claims):
        return bool(self._username(claims))

    def filter_users_by_claims(self, claims):
        users = User.objects.filter(username__iexact=self._username(claims))
        if not users and claims.get("email"):
            users = User.objects.filter(email__iexact=claims["email"])
        return users

    def create_user(self, claims):
        user = User(username=self._username(claims))
        user.set_unusable_password()
        return self.update_user(user, claims)

    def update_user(self, user, claims):
        user.email = claims.get("email") or user.email
        user.first_name = (claims.get("given_name") or user.first_name)[:150]
        user.last_name = (claims.get("family_name") or user.last_name)[:150]
        user.save()
        self._sync_roles(user, claims)
        return user

    def _sync_roles(self, user, claims):
        """Set each role named in PORTAL_OIDC_ROLE_GROUPS from the provider's groups."""
        groups = claims.get(settings.PORTAL_OIDC_GROUPS_CLAIM) or []
        if isinstance(groups, str):
            groups = [groups]
        for role, group in settings.PORTAL_OIDC_ROLE_GROUPS.items():
            if role not in Role.values:
                continue
            if group in groups:
                RoleAssignment.objects.get_or_create(user=user, role=role)
            else:
                RoleAssignment.objects.filter(user=user, role=role).delete()
