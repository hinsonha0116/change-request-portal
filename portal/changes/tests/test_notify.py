from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Role
from changes import workflow
from changes.models import Category, ChangeType, Decision, Notification, ReviewOutcome, Stage

from .helpers import make_request, make_user


class NotifyTestCase(TestCase):
    def setUp(self):
        self.pat = make_user("pat")
        self.sam = make_user("sam")
        self.cm = make_user("cm", Role.CM)
        self.cm2 = make_user("cm2", Role.CM)
        self.trb = make_user("trb", Role.TRB)
        self.cab = make_user("cab", Role.CAB)
        self.authority = make_user("authority", Role.AUTHORITY)
        self.swm = make_user("swm", Role.SW_MANAGER)
        self.hwm = make_user("hwm", Role.HW_MANAGER)

    def told(self, containing=""):
        """User names notified by subjects containing the text, then clear the list."""
        names = sorted(Notification.objects.filter(subject__contains=containing).values_list("user__username", flat=True))
        Notification.objects.all().delete()
        return names


class NewRequestNotifications(NotifyTestCase):
    def test_software_request_goes_to_cm_and_sw_managers(self):
        cr = make_request(self.pat, category=Category.SOFTWARE)
        subjects = set(Notification.objects.values_list("subject", flat=True))
        self.assertEqual(subjects, {
            f"New change request {cr.cr_number}: {cr.title}",
            f"New SOFTWARE change request {cr.cr_number}: {cr.title}",
        })
        self.assertEqual(self.told("New change request"), ["cm", "cm2"])

    def test_managers_by_category(self):
        make_request(self.pat, category=Category.SOFTWARE)
        self.assertEqual(self.told("SOFTWARE"), ["swm"])
        make_request(self.pat, category=Category.HARDWARE)
        self.assertEqual(self.told("HARDWARE"), ["hwm"])
        make_request(self.pat, category=Category.NETWORK)
        self.assertEqual(self.told(), ["cm", "cm2"])

    def test_submitter_is_not_told_about_their_own_request(self):
        make_request(self.cm, category=Category.NETWORK)
        self.assertEqual(self.told(), ["cm2"])

    def test_category_managers_can_open_requests_in_their_category_only(self):
        software = make_request(self.pat, category=Category.SOFTWARE)
        hardware = make_request(self.pat, category=Category.HARDWARE)
        self.assertTrue(workflow.can_view(software, self.swm))
        self.assertFalse(workflow.can_view(hardware, self.swm))
        self.assertEqual(list(workflow.visible_to(self.swm)), [software])
        self.assertEqual(list(workflow.visible_to(self.hwm)), [hardware])


class StageNotifications(NotifyTestCase):
    def test_normal_change_tells_the_right_people_at_each_stage(self):
        cr = make_request(self.pat, ChangeType.NORMAL, category=Category.NETWORK)
        self.told()

        cr = workflow.advance(cr, self.cm)
        self.assertEqual(self.told("is ready for TRB review"), ["trb"])

        cr = workflow.needs_changes(cr, self.trb, "Add the plan")
        self.assertEqual(self.told("needs changes before TRB review"), ["pat"])

        cr = workflow.advance(cr, self.cm)
        self.told()
        cr = workflow.apply_edits(cr, self.trb, {"trb_decision": Decision.APPROVED})
        self.assertEqual(self.told(), [])  # saving fields tells nobody

        cr = workflow.advance(cr, self.cm)
        self.assertEqual(self.told("is ready for CAB review"), ["cab"])

        cr = workflow.send_back(cr, self.cm)
        self.assertEqual(self.told("was sent back to Technical Review Board"), ["trb"])
        cr = workflow.advance(cr, self.cm)
        self.told()

        cr = workflow.apply_edits(cr, self.cab, {"cab_decision": Decision.APPROVED})
        cr = workflow.advance(cr, self.cm)
        self.assertEqual(self.told("is awaiting Change Authority approval"), ["authority"])

        cr = workflow.apply_edits(cr, self.authority, {"authority_decision": Decision.APPROVED})
        cr = workflow.advance(cr, self.cm)
        self.assertEqual(self.told("is approved for implementation"), ["cm2", "pat"])

        cr = workflow.apply_edits(cr, self.pat, {"implementation_notes": "Done."})
        cr = workflow.complete(cr, self.pat)
        self.assertEqual(self.told("has been completed by the implementer"), ["cm", "cm2"])

        cr = workflow.advance(cr, self.cm)
        self.assertEqual(self.told("is ready for PIR"), ["cm2"])

        cr = workflow.apply_edits(cr, self.cm, {"review_outcome": ReviewOutcome.SUCCESSFUL})
        cr = workflow.advance(cr, self.cm)
        self.assertEqual(self.told("is closed"), ["cm2", "pat"])
        self.assertEqual(cr.stage, Stage.CLOSE)

    def test_send_back_to_requester_and_reject(self):
        cr = workflow.advance(make_request(self.pat, ChangeType.EMERGENCY), self.cm)
        cr = workflow.send_back(cr, self.cm, "More detail please")
        self.assertEqual(self.told("was sent back to you"), ["pat"])
        cr = workflow.advance(cr, self.cm)
        self.told()
        workflow.reject(cr, self.cab, "Too risky")
        self.assertEqual(self.told("was rejected"), ["cm", "cm2", "pat"])

    def test_comments_tell_nobody(self):
        cr = make_request(self.pat)
        self.told()
        workflow.add_comment(cr, self.pat, "Any update?")
        self.assertEqual(self.told(), [])

    def test_requester_named_by_email_is_told_too(self):
        cr = make_request(self.pat, ChangeType.STANDARD, requester_email="SAM@example.test")
        self.told()
        workflow.advance(cr, self.cm)
        self.assertEqual(self.told("is approved for implementation"), ["cm2", "pat", "sam"])


class EmailTests(NotifyTestCase):
    def move_to_implementation(self, **fields):
        cr = make_request(self.pat, ChangeType.STANDARD, **fields)
        mail.outbox.clear()
        with self.captureOnCommitCallbacks(execute=True):
            workflow.advance(cr, self.cm, "Go ahead")
        return cr

    @override_settings(PORTAL_EMAIL_ENABLED=False)
    def test_no_email_unless_it_is_switched_on(self):
        with self.captureOnCommitCallbacks(execute=True):
            make_request(self.pat)
        self.assertEqual(mail.outbox, [])

    @override_settings(PORTAL_EMAIL_ENABLED=True, PORTAL_BASE_URL="https://changes.example")
    def test_stage_email_has_to_cc_and_a_link(self):
        cr = self.move_to_implementation()
        message = mail.outbox[0]
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(message.subject, f"{cr.cr_number} is approved for implementation: {cr.title}")
        self.assertEqual(message.to, ["pat@example.test"])
        self.assertEqual(message.cc, ["cm2@example.test"])
        self.assertIn("Go ahead", message.body)
        self.assertIn(f"https://changes.example{reverse('detail', args=[cr.pk])}", message.body)

    @override_settings(PORTAL_EMAIL_ENABLED=True)
    def test_requester_without_an_account_still_gets_the_email(self):
        self.move_to_implementation(requester_email="outside@example.test")
        self.assertEqual(mail.outbox[0].to, ["outside@example.test", "pat@example.test"])

    @override_settings(PORTAL_EMAIL_ENABLED=True)
    def test_new_emergency_request_is_flagged_urgent(self):
        with self.captureOnCommitCallbacks(execute=True):
            make_request(self.pat, ChangeType.EMERGENCY, category=Category.HARDWARE)
        self.assertEqual(len(mail.outbox), 2)
        cm_mail, hw_mail = sorted(mail.outbox, key=lambda m: m.subject, reverse=True)
        self.assertEqual(cm_mail.to, ["cm2@example.test", "cm@example.test"])
        self.assertEqual(hw_mail.to, ["hwm@example.test"])
        self.assertEqual(cm_mail.extra_headers["Importance"], "High")
        self.assertIn("Patch the VDI servers", cm_mail.body)

    @override_settings(PORTAL_EMAIL_ENABLED=True)
    def test_a_mail_failure_does_not_stop_the_change(self):
        with mock.patch("changes.notify.EmailMessage.send", side_effect=OSError("relay down")):
            with self.assertLogs("changes.notify", level="ERROR"):
                cr = self.move_to_implementation()
        cr.refresh_from_db()
        self.assertEqual(cr.stage, Stage.IMPLEMENTATION)
        self.assertTrue(Notification.objects.filter(user=self.pat, request=cr).exists())


class NotificationScreenTests(NotifyTestCase):
    def test_list_shows_unread_then_marks_them_read(self):
        cr = workflow.advance(make_request(self.pat, ChangeType.STANDARD), self.cm)
        self.client.force_login(self.pat)
        board = self.client.get(reverse("board"))
        self.assertContains(board, '<span class="badge">1</span>')
        page = self.client.get(reverse("notifications"))
        self.assertContains(page, f"{cr.cr_number} is approved for implementation")
        self.assertContains(page, "New")
        self.assertFalse(self.pat.notifications.filter(read_at__isnull=True).exists())
        self.assertNotContains(self.client.get(reverse("board")), 'class="badge"')

    def test_opening_the_request_marks_its_notifications_read(self):
        cr = workflow.advance(make_request(self.pat, ChangeType.STANDARD), self.cm)
        self.client.force_login(self.pat)
        self.client.get(reverse("detail", args=[cr.pk]))
        self.assertFalse(self.pat.notifications.filter(read_at__isnull=True).exists())

    def test_people_only_see_their_own_notifications(self):
        make_request(self.pat)
        self.client.force_login(self.sam)
        self.assertContains(self.client.get(reverse("notifications")), "Nothing yet")
