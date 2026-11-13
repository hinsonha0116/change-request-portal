"""Demo users and requests for local work. Refuses to run unless DJANGO_DEBUG is on."""
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from accounts.models import Role, RoleAssignment, User
from changes import workflow
from changes.models import Category, ChangeRequest, ChangeType, Decision, Priority, Severity
from changes.services import submit_request

# Local demo accounts only. Never used outside DEBUG.
DEMO_PASSWORD = "demo-portal-local"
DEMO_USERS = [
    ("pat", "Pat", "Requester", []),
    ("sam", "Sam", "Implementer", []),
    # cm holds every role and is a superuser, so one account can walk a request through every step.
    ("cm", "Casey", "Change-Manager", list(Role)),
    ("trb", "Terry", "Review-Board", [Role.TRB]),
    ("cab", "Cameron", "Advisory-Board", [Role.CAB]),
    ("authority", "Alex", "Authority", [Role.AUTHORITY]),
]


class Command(BaseCommand):
    help = "Create demo users (password in this file) and a few sample change requests."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo only runs with DJANGO_DEBUG=1.")
        if ChangeRequest.objects.exists():
            raise CommandError("There are already change requests here; not adding demo data.")

        users = {}
        for username, first, last, roles in DEMO_USERS:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "email": f"{username}@example.test"},
            )
            user.set_password(DEMO_PASSWORD)
            user.is_staff = user.is_superuser = username == "cm"
            user.save()
            for role in roles:
                RoleAssignment.objects.get_or_create(user=user, role=role)
            users[username] = user

        pat, sam, cm = users["pat"], users["sam"], users["cm"]
        now = timezone.now().replace(minute=0, second=0, microsecond=0)

        def request(owner, title, change_type, days, hours=2, **extra):
            start = now + datetime.timedelta(days=days)
            fields = dict(
                title=title, requested_by=owner.get_full_name(), requester_email=owner.email,
                category=Category.SOFTWARE, change_type=change_type, priority=Priority.MODERATE,
                risk=Severity.MODERATE, impact=Severity.MODERATE,
                description="Demo request.", location="Bldg 400", affected_systems="VDI servers",
                a6_program="VDI", planned_start=start, planned_end=start + datetime.timedelta(hours=hours),
            )
            fields.update(extra)
            return submit_request(owner, **fields)

        request(pat, "Patch the VDI servers", ChangeType.NORMAL, 2)
        request(sam, "Replace core switch in the comms room", ChangeType.NORMAL, 2, hours=4,
                category=Category.NETWORK, priority=Priority.HIGH, risk=Severity.HIGH,
                a6_program="Network", outage_expected=True, outage_duration="30 minutes")
        request(pat, "Restart the print server", ChangeType.STANDARD, 5, hours=1,
                a6_program="Print", location="Bldg 210", priority=Priority.LOW)

        emergency = request(pat, "Emergency firewall rule for the mail gateway", ChangeType.EMERGENCY, 1,
                            category=Category.NETWORK, priority=Priority.CRITICAL, risk=Severity.CRITICAL,
                            impact=Severity.HIGH, a6_program="Mail", location="Bldg 100",
                            justification="Blocking an active phishing campaign.")
        emergency = workflow.advance(emergency, cm, "Straight to the CAB")
        emergency = workflow.apply_edits(emergency, users["cab"], {"cab_decision": Decision.APPROVED})
        workflow.advance(emergency, cm)

        in_trb = request(sam, "Upgrade the backup software", ChangeType.NORMAL, 9, hours=6,
                         a6_program="Backup", location="Bldg 210")
        workflow.advance(in_trb, cm)

        standard = request(sam, "Add memory to the file server", ChangeType.STANDARD, 12, hours=1,
                           category=Category.HARDWARE, a6_program="Files", location="Bldg 210")
        standard = workflow.advance(standard, cm)
        standard = workflow.apply_edits(standard, cm, {"assignee": sam, "implementation_notes": "Memory fitted and tested."})
        workflow.complete(standard, sam, "Finished early")

        self.stdout.write(self.style.SUCCESS(
            "Demo data created. Users: " + ", ".join(name for name, *_ in DEMO_USERS)
            + ". The password is DEMO_PASSWORD in changes/management/commands/seed_demo.py."
        ))
