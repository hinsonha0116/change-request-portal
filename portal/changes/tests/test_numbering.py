import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from changes.models import ChangeRequest, HistoryEntry, Stage

from .helpers import make_request, make_user


class NumberingTests(TestCase):
    def setUp(self):
        self.user = make_user("pat")

    def test_numbers_count_up_within_a_year(self):
        day = datetime.date(2026, 11, 13)
        first = make_request(self.user, today=day)
        second = make_request(self.user, today=day)
        self.assertEqual(first.cr_number, "CR-2026-001")
        self.assertEqual(second.cr_number, "CR-2026-002")

    def test_numbers_restart_each_year(self):
        make_request(self.user, today=datetime.date(2026, 12, 31))
        new_year = make_request(self.user, today=datetime.date(2027, 1, 1))
        back_in_2026 = make_request(self.user, today=datetime.date(2026, 12, 31))
        self.assertEqual(new_year.cr_number, "CR-2027-001")
        self.assertEqual(back_in_2026.cr_number, "CR-2026-002")

    def test_numbers_keep_going_past_999(self):
        from changes.models import CRCounter

        CRCounter.objects.create(year=2026, last_number=999)
        cr = make_request(self.user, today=datetime.date(2026, 6, 1))
        self.assertEqual(cr.cr_number, "CR-2026-1000")

    def test_invalid_request_does_not_use_up_a_number(self):
        day = datetime.date(2026, 11, 13)
        with self.assertRaises(ValidationError):
            make_request(self.user, today=day, outage_expected=True, outage_duration="")
        self.assertEqual(ChangeRequest.objects.count(), 0)
        self.assertEqual(make_request(self.user, today=day).cr_number, "CR-2026-001")

    def test_submit_starts_in_requested_and_logs_history(self):
        cr = make_request(self.user)
        self.assertEqual(cr.stage, Stage.REQUESTED)
        self.assertEqual(cr.submitted_by, self.user)
        entry = cr.history.get()
        self.assertEqual(entry.kind, HistoryEntry.Kind.CREATED)
        self.assertEqual(entry.to_stage, Stage.REQUESTED)
        self.assertEqual(entry.actor, self.user)

    def test_planned_end_before_start_is_refused(self):
        with self.assertRaises(ValidationError):
            make_request(
                self.user,
                planned_start=datetime.datetime(2026, 12, 2, tzinfo=datetime.timezone.utc),
                planned_end=datetime.datetime(2026, 12, 1, tzinfo=datetime.timezone.utc),
            )
