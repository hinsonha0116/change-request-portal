import datetime

from django.test import TestCase
from django.utils import timezone

from accounts.models import Role
from changes import schedule, workflow
from changes.models import ChangeType

from .helpers import make_request, make_user


def at(day, hour):
    return timezone.make_aware(datetime.datetime(2026, 11, day, hour))


class ScheduleTests(TestCase):
    def setUp(self):
        self.pat = make_user("pat")
        self.sam = make_user("sam")
        self.cm = make_user("cm", Role.CM)
        self.trb = make_user("trb", Role.TRB)
        self.grid_start = schedule.grid_days(datetime.date(2026, 11, 1))[0]

    def entries(self, user):
        return {e.cr.title: e for e in schedule.load_entries(user, self.grid_start)}

    def test_grid_is_six_weeks_from_a_monday(self):
        days = schedule.grid_days(datetime.date(2026, 11, 1))
        self.assertEqual(len(days), 42)
        self.assertEqual(days[0], datetime.date(2026, 10, 26))
        self.assertEqual(days[0].weekday(), 0)

    def test_overlap_at_same_location_or_program_is_a_clash(self):
        make_request(self.pat, title="A", location="Bldg 400", a6_program="VDI",
                     planned_start=at(10, 9), planned_end=at(10, 12))
        make_request(self.pat, title="B", location="bldg 400 ", a6_program="Mail",
                     planned_start=at(10, 11), planned_end=at(10, 13))
        make_request(self.pat, title="C", location="Bldg 1", a6_program="vdi",
                     planned_start=at(10, 8), planned_end=at(10, 10))
        make_request(self.pat, title="D", location="Bldg 400", a6_program="VDI",
                     planned_start=at(10, 13), planned_end=at(10, 14))  # touches B's end, no overlap
        make_request(self.pat, title="E", location="Bldg 9", a6_program="Other",
                     planned_start=at(10, 9), planned_end=at(10, 12))  # overlaps, nothing in common
        found = self.entries(self.cm)
        self.assertEqual({t: e.has_conflict for t, e in found.items()},
                         {"A": True, "B": True, "C": True, "D": False, "E": False})

    def test_blank_program_or_unscheduled_never_clash(self):
        make_request(self.pat, title="A", location="Bldg 1", planned_start=at(10, 9), planned_end=at(10, 12))
        make_request(self.pat, title="B", location="Bldg 2", planned_start=at(10, 9), planned_end=at(10, 12))
        make_request(self.pat, title="No dates", location="Bldg 1")
        found = self.entries(self.cm)
        self.assertEqual(set(found), {"A", "B"})
        self.assertFalse(found["A"].has_conflict)

    def test_rejected_changes_are_left_out_and_do_not_clash(self):
        make_request(self.pat, title="A", planned_start=at(10, 9), planned_end=at(10, 12))
        rejected = make_request(self.pat, ChangeType.NORMAL, title="B",
                                planned_start=at(10, 9), planned_end=at(10, 12))
        rejected = workflow.advance(rejected, self.cm)
        workflow.reject(rejected, self.trb, "No")
        found = self.entries(self.cm)
        self.assertEqual(set(found), {"A"})
        self.assertFalse(found["A"].has_conflict)

    def test_requesters_see_only_their_own_but_still_learn_of_clashes(self):
        make_request(self.pat, title="Mine", planned_start=at(10, 9), planned_end=at(10, 12))
        make_request(self.sam, title="Theirs", planned_start=at(10, 10), planned_end=at(10, 11))
        found = self.entries(self.pat)
        self.assertEqual(set(found), {"Mine"})
        self.assertTrue(found["Mine"].has_conflict)

    def test_multi_day_change_shows_on_each_day(self):
        make_request(self.pat, title="Long", planned_start=at(10, 22), planned_end=at(12, 2))
        make_request(self.pat, title="No end", location="Bldg 2", a6_program="X", planned_start=at(11, 9))
        entries = schedule.load_entries(self.cm, self.grid_start)

        def titles(day):
            return [e.cr.title for e in schedule.entries_on(entries, datetime.date(2026, 11, day))]

        self.assertEqual(titles(9), [])
        self.assertEqual(titles(10), ["Long"])
        self.assertEqual(titles(11), ["Long", "No end"])
        self.assertEqual(titles(12), ["Long"])
        self.assertEqual(titles(13), [])

    def test_month_and_day_parsing_falls_back_safely(self):
        today = datetime.date(2026, 11, 13)
        self.assertEqual(schedule.parse_month("2027-02", today), datetime.date(2027, 2, 1))
        for bad in (None, "", "2026", "2026-13", "abc-de", "99999-01"):
            self.assertEqual(schedule.parse_month(bad, today), datetime.date(2026, 11, 1))
        self.assertEqual(schedule.parse_day("2026-11-20", today), datetime.date(2026, 11, 20))
        self.assertEqual(schedule.parse_day("nope", today), today)
