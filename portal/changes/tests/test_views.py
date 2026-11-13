import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role
from changes import workflow
from changes.forms import detail_form
from changes.models import ChangeRequest, ChangeType, HistoryEntry, Stage, TRBDecision

from .helpers import make_request, make_user


def post_data(cr, user, action, **extra):
    """What the detail page would post: the stage, the editable fields as they stand, and the button."""
    data = {"stage": cr.stage, "action": action, "comment": ""}
    form = detail_form(cr, user)
    if form is not None:
        for name in form.fields:
            value = form[name].value()
            if value is None or value is False:
                continue
            if isinstance(value, datetime.datetime):
                value = timezone.localtime(value).strftime("%Y-%m-%dT%H:%M")
            data[name] = "on" if value is True else value
    data.update(extra)
    return data


NEW_REQUEST = {
    "requested_by": "Pat Requester", "requester_email": "pat@example.test",
    "title": "Patch the VDI servers", "category": "software", "change_type": "normal",
    "priority": "3", "risk": "3", "impact": "3", "location": "Bldg 400",
    "affected_systems": "VDI servers", "description": "Apply the monthly patches.",
}


class ViewTestCase(TestCase):
    def setUp(self):
        self.pat = make_user("pat")
        self.sam = make_user("sam")
        self.cm = make_user("cm", Role.CM)
        self.trb = make_user("trb", Role.TRB)

    def detail_url(self, cr):
        return reverse("detail", args=[cr.pk])


class SignInTests(ViewTestCase):
    def test_every_screen_needs_a_sign_in(self):
        cr = make_request(self.pat)
        for url in (reverse("board"), reverse("new_request"), reverse("schedule"), self.detail_url(cr)):
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_sign_in_page_renders(self):
        self.assertContains(self.client.get(reverse("login")), "Sign in")


class BoardTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        make_request(self.pat, title="Pat's patching")
        make_request(self.sam, title="Sam's switch", category="network", change_type=ChangeType.EMERGENCY)
        make_request(self.cm, title="Casey's own")

    def test_requester_sees_only_their_own_cards(self):
        self.client.force_login(self.pat)
        response = self.client.get(reverse("board"))
        self.assertContains(response, "Pat&#x27;s patching")
        self.assertNotContains(response, "Sam&#x27;s switch")
        self.assertNotContains(response, "Only my requests")

    def test_cm_sees_everything_and_can_filter(self):
        self.client.force_login(self.cm)
        board = reverse("board")
        self.assertContains(self.client.get(board), "Sam&#x27;s switch")
        for query, shown, hidden in (
            ("?q=switch", "Sam&#x27;s switch", "Pat&#x27;s patching"),
            ("?category=network", "Sam&#x27;s switch", "Pat&#x27;s patching"),
            ("?type=normal", "Pat&#x27;s patching", "Sam&#x27;s switch"),
            ("?mine=1", "Casey&#x27;s own", "Pat&#x27;s patching"),
        ):
            with self.subTest(query=query):
                response = self.client.get(board + query)
                self.assertContains(response, shown)
                self.assertNotContains(response, hidden)

    def test_old_closed_requests_drop_off_the_board(self):
        old = make_request(self.pat, ChangeType.STANDARD, title="Long gone")
        ChangeRequest.objects.filter(pk=old.pk).update(
            stage=Stage.CLOSE, closed_date=timezone.now() - datetime.timedelta(days=45))
        self.client.force_login(self.cm)
        self.assertNotContains(self.client.get(reverse("board")), "Long gone")


class NewRequestTests(ViewTestCase):
    def test_submit_creates_a_numbered_request_with_attachments(self):
        self.client.force_login(self.pat)
        plan = SimpleUploadedFile("rollback.pdf", b"%PDF-1.4 plan", content_type="application/pdf")
        response = self.client.post(reverse("new_request"), {**NEW_REQUEST, "attachments": [plan]})
        cr = ChangeRequest.objects.get()
        self.assertRedirects(response, self.detail_url(cr))
        self.assertRegex(cr.cr_number, r"^CR-\d{4}-001$")
        self.assertEqual((cr.submitted_by, cr.stage), (self.pat, Stage.REQUESTED))
        attachment = cr.attachments.get()
        self.assertEqual((attachment.filename, bytes(attachment.data)), ("rollback.pdf", b"%PDF-1.4 plan"))

    def test_missing_fields_are_reported_and_nothing_is_saved(self):
        self.client.force_login(self.pat)
        data = {**NEW_REQUEST, "location": "", "outage_expected": "on"}
        response = self.client.post(reverse("new_request"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("location", response.context["form"].errors)
        self.assertIn("outage_duration", response.context["form"].errors)
        self.assertFalse(ChangeRequest.objects.exists())

    @override_settings(PORTAL_MAX_UPLOAD_MB=0)
    def test_oversized_attachment_is_refused(self):
        self.client.force_login(self.pat)
        big = SimpleUploadedFile("big.bin", b"x" * 10)
        response = self.client.post(reverse("new_request"), {**NEW_REQUEST, "attachments": [big]})
        self.assertIn("attachments", response.context["form"].errors)
        self.assertFalse(ChangeRequest.objects.exists())


class DetailTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.cr = make_request(self.pat, ChangeType.NORMAL)

    def post(self, user, action, cr=None, **extra):
        cr = cr or self.cr
        self.client.force_login(user)
        return self.client.post(self.detail_url(cr), post_data(cr, user, action, **extra))

    def test_outsiders_get_not_found(self):
        self.client.force_login(self.sam)
        self.assertEqual(self.client.get(self.detail_url(self.cr)).status_code, 404)
        self.assertEqual(self.post(self.sam, "comment", comment="Hi").status_code, 404)

    def test_buttons_match_the_role(self):
        self.client.force_login(self.pat)
        page = self.client.get(self.detail_url(self.cr))
        self.assertNotContains(page, "Move to")
        self.assertContains(page, 'value="save"')
        self.client.force_login(self.cm)
        self.assertContains(self.client.get(self.detail_url(self.cr)), "Move to Technical Review Board")

    def test_cm_moves_the_request_on(self):
        response = self.post(self.cm, "advance", comment="Ready")
        self.assertRedirects(response, self.detail_url(self.cr))
        self.cr.refresh_from_db()
        self.assertEqual(self.cr.stage, Stage.TRB)
        self.assertEqual(self.cr.history.last().comment, "Ready")

    def test_requester_cannot_move_it_even_by_posting_the_action(self):
        self.assertEqual(self.post(self.pat, "advance").status_code, 403)
        self.cr.refresh_from_db()
        self.assertEqual(self.cr.stage, Stage.REQUESTED)

    def test_requester_edits_are_saved(self):
        self.post(self.pat, "save", title="Better title")
        self.cr.refresh_from_db()
        self.assertEqual(self.cr.title, "Better title")

    def test_invalid_edit_saves_nothing_and_runs_no_action(self):
        response = self.post(self.cm, "advance", location="")
        self.assertEqual(response.status_code, 200)
        self.assertIn("location", response.context["form"].errors)
        self.cr.refresh_from_db()
        self.assertEqual((self.cr.stage, self.cr.location), (Stage.REQUESTED, "Bldg 400"))

    def test_trb_member_approves_then_cm_moves_on(self):
        cr = workflow.advance(self.cr, self.cm)
        blocked = self.post(self.cm, "advance", cr=cr)
        self.assertRedirects(blocked, self.detail_url(cr))
        cr.refresh_from_db()
        self.assertEqual(cr.stage, Stage.TRB)

        self.post(self.trb, "save", cr=cr, trb_decision="approved", trb_tested="on", trb_notes="Looks fine")
        cr.refresh_from_db()
        self.assertEqual((cr.trb_decision, cr.trb_tested, cr.trb_notes), (TRBDecision.APPROVED, True, "Looks fine"))

        self.post(self.cm, "advance", cr=cr)
        cr.refresh_from_db()
        self.assertEqual(cr.stage, Stage.CAB)

    def test_rejected_cannot_be_picked_in_the_drop_down(self):
        cr = workflow.advance(self.cr, self.cm)
        response = self.post(self.trb, "save", cr=cr, trb_decision="rejected")
        self.assertIn("trb_decision", response.context["form"].errors)

    def test_needs_changes_and_reject_need_a_comment(self):
        cr = workflow.advance(self.cr, self.cm)
        for action in ("needschanges", "reject"):
            self.post(self.trb, action, cr=cr)
            cr.refresh_from_db()
            self.assertEqual(cr.stage, Stage.TRB)
        self.post(self.trb, "needschanges", cr=cr, comment="Add the rollback plan")
        cr.refresh_from_db()
        self.assertEqual((cr.stage, cr.trb_decision), (Stage.REQUESTED, TRBDecision.NEEDS_CHANGES))

    def test_stale_page_saves_nothing(self):
        stale = post_data(self.cr, self.pat, "save", title="Too late")
        workflow.advance(self.cr, self.cm)
        self.client.force_login(self.pat)
        self.client.post(self.detail_url(self.cr), stale)
        self.cr.refresh_from_db()
        self.assertEqual(self.cr.title, "Patch the VDI servers")

    def test_comment_and_unknown_action(self):
        self.post(self.pat, "comment", comment="Any update?")
        self.assertEqual(self.cr.history.last().kind, HistoryEntry.Kind.COMMENT)
        self.assertEqual(self.post(self.pat, "explode").status_code, 400)

    def test_standard_change_never_shows_review_sections(self):
        cr = make_request(self.pat, ChangeType.STANDARD)
        cr = workflow.advance(cr, self.cm)
        self.client.force_login(self.cm)
        page = self.client.get(self.detail_url(cr))
        self.assertContains(page, "✔ Completed")
        self.assertNotContains(page, "Change Advisory Board")
        self.assertNotContains(page, "TRB decision")
        self.assertContains(page, "Move to Close")


class AttachmentTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.cr = make_request(self.pat, ChangeType.STANDARD)
        self.upload_url = reverse("upload_attachment", args=[self.cr.pk])

    def upload(self, user, name="notes.html", body=b"<script>alert(1)</script>"):
        self.client.force_login(user)
        return self.client.post(self.upload_url, {"files": [SimpleUploadedFile(name, body, content_type="text/html")]})

    def test_upload_and_download(self):
        self.upload(self.pat)
        attachment = self.cr.attachments.get()
        response = self.client.get(reverse("download_attachment", args=[attachment.pk]))
        self.assertEqual(b"".join(response.streaming_content), b"<script>alert(1)</script>")
        self.assertEqual(response["Content-Type"], "application/octet-stream")
        self.assertIn("attachment", response["Content-Disposition"])

    def test_outsiders_cannot_upload_or_download(self):
        self.upload(self.pat)
        attachment = self.cr.attachments.get()
        self.assertEqual(self.upload(self.sam).status_code, 404)
        self.assertEqual(self.client.get(reverse("download_attachment", args=[attachment.pk])).status_code, 404)
        self.assertEqual(self.cr.attachments.count(), 1)

    def test_no_uploads_once_closed(self):
        ChangeRequest.objects.filter(pk=self.cr.pk).update(stage=Stage.CLOSE)
        self.upload(self.pat)
        self.assertEqual(self.cr.attachments.count(), 0)

    def test_path_is_stripped_from_the_file_name(self):
        self.upload(self.pat, name="..\\..\\evil.txt")
        self.assertEqual(self.cr.attachments.get().filename, "evil.txt")


class ScheduleViewTests(ViewTestCase):
    def test_month_shows_chips_and_the_day_panel(self):
        start = timezone.make_aware(datetime.datetime(2026, 11, 10, 9))
        cr = make_request(self.pat, a6_program="VDI", planned_start=start,
                          planned_end=start + datetime.timedelta(hours=2))
        make_request(self.sam, a6_program="VDI", title="Hidden from Pat", planned_start=start,
                     planned_end=start + datetime.timedelta(hours=2))
        self.client.force_login(self.pat)
        response = self.client.get(reverse("schedule") + "?month=2026-11&day=2026-11-10")
        self.assertContains(response, "November 2026")
        self.assertContains(response, f"{cr.cr_number} VDI")
        self.assertContains(response, "Possible clash")
        self.assertNotContains(response, "Hidden from Pat")

    def test_bad_parameters_fall_back_to_this_month(self):
        self.client.force_login(self.pat)
        response = self.client.get(reverse("schedule") + "?month=nonsense&day=never")
        self.assertEqual(response.status_code, 200)
