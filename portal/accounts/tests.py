from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Role, RoleAssignment, User
from .oidc import PortalOIDCBackend


def make_user(name, *roles, **extra):
    user = User.objects.create_user(username=name, email=f"{name}@example.test", **extra)
    for role in roles:
        RoleAssignment.objects.create(user=user, role=role)
    return user


def roles_of(user):
    return set(user.role_assignments.values_list("role", flat=True))


class PeopleScreenTests(TestCase):
    def setUp(self):
        self.pat = make_user("pat")
        self.cm = make_user("cm", Role.CM)
        self.url = reverse("people")

    def test_only_cm_and_superusers_can_open_it(self):
        self.client.force_login(self.pat)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, {f"role-{self.pat.pk}-cm": "on"}).status_code, 403)
        self.assertEqual(roles_of(self.pat), set())
        self.assertNotContains(self.client.get(reverse("board")), "People")

        self.client.force_login(make_user("root", is_superuser=True))
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_cm_sets_and_clears_roles(self):
        trb = make_user("trb", Role.TRB)
        self.client.force_login(self.cm)
        self.assertContains(self.client.get(self.url), "pat@example.test")
        self.client.post(self.url, {
            f"role-{self.cm.pk}-cm": "on",
            f"role-{self.pat.pk}-cab": "on",
            f"role-{self.pat.pk}-sw_manager": "on",
        })
        self.assertEqual(roles_of(self.pat), {Role.CAB, Role.SW_MANAGER})
        self.assertEqual(roles_of(trb), set())
        self.assertEqual(roles_of(self.cm), {Role.CM})

    def test_cm_cannot_remove_their_own_cm_role(self):
        self.client.force_login(self.cm)
        response = self.client.post(self.url, {}, follow=True)
        self.assertEqual(roles_of(self.cm), {Role.CM})
        self.assertContains(response, "can&#x27;t remove your own")


class PasswordTests(TestCase):
    def test_user_can_change_their_password(self):
        user = make_user("pat")
        user.set_password("old-password-123")
        user.save()
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("password_change")).status_code, 200)
        response = self.client.post(reverse("password_change"), {
            "old_password": "old-password-123",
            "new_password1": "a-much-better-phrase-9",
            "new_password2": "a-much-better-phrase-9",
        })
        self.assertRedirects(response, reverse("password_change_done"))
        user.refresh_from_db()
        self.assertTrue(user.check_password("a-much-better-phrase-9"))


@override_settings(
    OIDC_RP_CLIENT_ID="portal",
    OIDC_RP_CLIENT_SECRET="not-a-real-secret",
    OIDC_OP_AUTHORIZATION_ENDPOINT="https://idp.test/auth",
    OIDC_OP_TOKEN_ENDPOINT="https://idp.test/token",
    OIDC_OP_USER_ENDPOINT="https://idp.test/userinfo",
    OIDC_OP_JWKS_ENDPOINT="https://idp.test/keys",
    PORTAL_OIDC_ROLE_GROUPS={"cm": "change-managers", "trb": "trb-members"},
)
class SingleSignOnTests(TestCase):
    """The parts we own: matching people to users and mapping groups to roles."""

    def setUp(self):
        self.backend = PortalOIDCBackend()
        self.claims = {
            "sub": "abc-123", "preferred_username": "jdoe", "email": "jdoe@example.test",
            "given_name": "Jo", "family_name": "Doe", "groups": ["change-managers", "staff"],
        }

    def test_first_sign_in_creates_a_user_with_mapped_roles(self):
        user = self.backend.create_user(self.claims)
        self.assertEqual((user.username, user.email, user.get_full_name()), ("jdoe", "jdoe@example.test", "Jo Doe"))
        self.assertFalse(user.has_usable_password())
        self.assertEqual(roles_of(user), {Role.CM})

    def test_matches_existing_user_by_name_then_by_email(self):
        by_name = make_user("JDoe")
        self.assertEqual(list(self.backend.filter_users_by_claims(self.claims)), [by_name])
        by_name.delete()
        by_email = User.objects.create_user(username="someone", email="JDOE@example.test")
        self.assertEqual(list(self.backend.filter_users_by_claims(self.claims)), [by_email])

    def test_later_sign_in_updates_details_and_mapped_roles_only(self):
        user = self.backend.create_user(self.claims)
        RoleAssignment.objects.create(user=user, role=Role.CAB)  # set on the People screen, not mapped
        changed = {**self.claims, "family_name": "Smith", "groups": ["trb-members"]}
        self.backend.update_user(user, changed)
        user.refresh_from_db()
        self.assertEqual(user.last_name, "Smith")
        self.assertEqual(roles_of(user), {Role.TRB, Role.CAB})

    def test_falls_back_to_email_or_subject_for_the_user_name(self):
        self.assertEqual(self.backend.create_user({"sub": "x1", "email": "a@example.test"}).username, "a@example.test")
        self.assertEqual(self.backend.create_user({"sub": "x2"}).username, "x2")
        self.assertTrue(self.backend.verify_claims({"sub": "x2"}))
        self.assertFalse(self.backend.verify_claims({}))

    @override_settings(PORTAL_OIDC_ROLE_GROUPS={})
    def test_without_a_mapping_roles_are_left_alone(self):
        user = make_user("jdoe", Role.CAB)
        self.backend.update_user(user, self.claims)
        self.assertEqual(roles_of(user), {Role.CAB})
