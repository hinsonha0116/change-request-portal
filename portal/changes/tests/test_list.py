import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role
from changes import workflow
from changes.models import Category, ChangeType, Decision, Priority, Stage

from .helpers import make_request, make_user


class ListTestCase(TestCase):
    def setUp(self):
        self.pat = make_user("pat")
        self.sam = make_user("sam")
        self.cm = make_user("cm", Role.CM)
        self.trb = make_user("trb", Role.TRB)
        self.url = reverse("request_list")

    def titles(self, user, query=""):
        self.client.force_login(user)
        response = self.client.get(self.url + query)
        self.assertEqual(response.status_code, 200)
        return [cr.title for cr in response.context["page"]]


class ListScreenTests(ListTestCase):
    def test_needs_a_sign_in(self):
        self.assertRedirects(self.client.get(self.url), f"{reverse('login')}?next={self.url}")

    def test_requesters_see_only_their_own_rows(self):
        make_request(self.pat, title="Pat one")
        make_request(self.sam, title="Sam one")
        self.assertEqual(self.titles(self.pat), ["Pat one"])
        self.assertEqual(sorted(self.titles(self.cm)), ["Pat one", "Sam one"])

    def test_rows_link_to_the_request_and_back_again(self):
        cr = make_request(self.pat, outage_expected=True, outage_duration="1 hour")
        self.client.force_login(self.pat)
        page = self.client.get(self.url)
        detail = reverse("detail", args=[cr.pk]) + "?from=list"
        self.assertContains(page, detail)
        self.assertContains(page, cr.cr_number)
        self.assertContains(page, "Outage")
        self.assertContains(self.client.get(detail), "← List")

    def test_views_split_open_closed_and_mine(self):
        make_request(self.pat, title="Open one")
        make_request(self.cm, title="Casey's")
        closed = make_request(self.pat, ChangeType.STANDARD, title="Closed one")
        type(closed).objects.filter(pk=closed.pk).update(stage=Stage.CLOSE)
        self.assertEqual(sorted(self.titles(self.cm)), ["Casey's", "Open one"])  # Open is the default
        self.assertEqual(self.titles(self.cm, "?view=closed"), ["Closed one"])
        self.assertEqual(self.titles(self.cm, "?view=mine"), ["Casey's"])
        self.assertEqual(len(self.titles(self.cm, "?view=all")), 3)
        self.assertEqual(len(self.titles(self.cm, "?view=nonsense")), 2)

    def test_filters_and_search(self):
        make_request(self.pat, title="Switch swap", category=Category.NETWORK, priority=Priority.CRITICAL,
                     change_type=ChangeType.EMERGENCY, a6_program="Backbone")
        make_request(self.pat, title="Patch servers")
        for query, expected in (
            ("?q=switch", ["Switch swap"]),
            ("?q=backbone", ["Switch swap"]),
            ("?q=CR-", ["Patch servers", "Switch swap"]),
            ("?category=network", ["Switch swap"]),
            ("?type=normal", ["Patch servers"]),
            ("?priority=1", ["Switch swap"]),
            ("?stage=requested&type=emergency", ["Switch swap"]),
            ("?stage=close", []),
            ("?category=bogus&priority=9", ["Patch servers", "Switch swap"]),
        ):
            with self.subTest(query=query):
                self.assertEqual(sorted(self.titles(self.cm, query)), expected)

    def test_starting_in_seven_days(self):
        now = timezone.now()
        make_request(self.pat, title="Soon", planned_start=now + datetime.timedelta(days=2))
        make_request(self.pat, title="Later", planned_start=now + datetime.timedelta(days=20))
        make_request(self.pat, title="Unscheduled")
        self.assertEqual(self.titles(self.cm, "?starting=7"), ["Soon"])

    def test_sorting_by_column_in_both_directions(self):
        make_request(self.pat, title="Bravo", priority=Priority.LOW)
        make_request(self.pat, title="Alpha", priority=Priority.CRITICAL)
        charlie = make_request(self.pat, title="Charlie", priority=Priority.HIGH)
        workflow.advance(charlie, self.cm)
        self.assertEqual(self.titles(self.cm, "?sort=title"), ["Alpha", "Bravo", "Charlie"])
        self.assertEqual(self.titles(self.cm, "?sort=-title"), ["Charlie", "Bravo", "Alpha"])
        self.assertEqual(self.titles(self.cm, "?sort=priority"), ["Alpha", "Charlie", "Bravo"])
        self.assertEqual(self.titles(self.cm, "?sort=number"), ["Bravo", "Alpha", "Charlie"])
        self.assertEqual(self.titles(self.cm, "?sort=-stage")[0], "Charlie")  # TRB comes after Requested
        self.assertEqual(self.titles(self.cm)[0], "Charlie")  # default: most recently updated first
        self.assertEqual(len(self.titles(self.cm, "?sort=password")), 3)  # unknown column is ignored

    def test_sort_links_flip_direction_and_keep_filters(self):
        self.client.force_login(self.cm)
        columns = {c["key"]: c for c in self.client.get(self.url + "?sort=title&type=normal").context["columns"]}
        self.assertEqual(columns["title"]["aria"], "ascending")
        self.assertIn("sort=-title", columns["title"]["url"])
        self.assertIn("type=normal", columns["title"]["url"])
        self.assertIn("sort=priority", columns["priority"]["url"])

    def test_pages_of_25(self):
        for number in range(27):
            make_request(self.pat, title=f"Request {number:02d}")
        self.assertEqual(len(self.titles(self.cm, "?sort=title")), 25)
        self.assertEqual(self.titles(self.cm, "?sort=title&page=2"), ["Request 25", "Request 26"])
        self.assertEqual(len(self.titles(self.cm, "?sort=title&page=99")), 2)  # past the end shows the last page
        self.client.force_login(self.cm)
        self.assertContains(self.client.get(self.url), "1–25 of 27")

    def test_tiles_count_what_the_user_can_see(self):
        make_request(self.pat, ChangeType.EMERGENCY)
        make_request(self.sam)
        self.client.force_login(self.pat)
        counts = {t["label"]: t["count"] for t in self.client.get(self.url).context["tiles"]}
        self.assertEqual(counts, {"Open": 1, "Needs my action": 0, "Open emergencies": 1,
                                  "Starting in 7 days": 0, "Closed": 0})


class NeedsMyActionTests(ListTestCase):
    def waiting_on(self, user):
        return sorted(self.titles(user, "?view=action"))

    def test_follows_a_normal_change_through_review(self):
        cr = make_request(self.pat, ChangeType.NORMAL, title="Change")
        self.assertEqual(self.waiting_on(self.cm), ["Change"])  # new request to send on
        self.assertEqual(self.waiting_on(self.trb), [])
        self.assertEqual(self.waiting_on(self.pat), [])

        cr = workflow.advance(cr, self.cm)
        self.assertEqual(self.waiting_on(self.trb), ["Change"])  # decision pending
        self.assertEqual(self.waiting_on(self.cm), [])

        cr = workflow.apply_edits(cr, self.trb, {"trb_decision": Decision.APPROVED})
        self.assertEqual(self.waiting_on(self.trb), [])
        self.assertEqual(self.waiting_on(self.cm), ["Change"])  # approved, ready to move

    def test_needs_changes_waits_on_the_requester(self):
        cr = workflow.advance(make_request(self.pat, ChangeType.NORMAL, title="Change"), self.cm)
        workflow.needs_changes(cr, self.trb, "Add the plan")
        self.assertEqual(self.waiting_on(self.pat), ["Change"])
        self.assertEqual(self.waiting_on(self.sam), [])

    def test_implementation_waits_on_the_assignee_then_cm(self):
        cr = workflow.advance(make_request(self.pat, ChangeType.STANDARD, title="Change"), self.cm)
        cr = workflow.apply_edits(cr, self.cm, {"assignee": self.sam, "implementation_notes": "Done."})
        self.assertEqual(self.waiting_on(self.sam), ["Change"])
        self.assertEqual(self.waiting_on(self.cm), [])
        workflow.complete(cr, self.sam)
        self.assertEqual(self.waiting_on(self.sam), [])
        self.assertEqual(self.waiting_on(self.cm), ["Change"])
