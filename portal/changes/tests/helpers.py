from accounts.models import RoleAssignment, User
from changes.models import Category, ChangeType, Priority, Severity
from changes.services import submit_request


def make_user(name, *roles):
    user = User.objects.create_user(username=name, email=f"{name}@example.test")
    for role in roles:
        RoleAssignment.objects.create(user=user, role=role)
    return user


def make_request(user, change_type=ChangeType.NORMAL, **overrides):
    fields = dict(
        title="Patch the VDI servers",
        requested_by="Pat Requester",
        requester_email=user.email,
        category=Category.SOFTWARE,
        change_type=change_type,
        priority=Priority.MODERATE,
        risk=Severity.MODERATE,
        impact=Severity.MODERATE,
        description="Apply the monthly patches.",
        location="Bldg 400",
        affected_systems="VDI servers",
    )
    fields.update(overrides)
    return submit_request(user, **fields)
