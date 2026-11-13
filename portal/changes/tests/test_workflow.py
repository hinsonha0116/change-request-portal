"""Covers the Part 9 test table in DetailScreen-Fixes.md, plus the permission rules."""
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from accounts.models import Role
from changes import workflow
from changes.models import (
    ChangeType,
    Decision,
    HistoryEntry,
    ReviewOutcome,
    Stage,
    TRBDecision,
)
from changes.workflow import WorkflowError

from .helpers import make_request, make_user


class WorkflowTestCase(TestCase):
    def setUp(self):
        self.requester = make_user("pat")
        self.other = make_user("sam")
        self.cm = make_user("cm", Role.CM)
        self.trb = make_user("trb", Role.TRB)
        self.cab = make_user("cab", Role.CAB)
        self.authority = make_user("authority", Role.AUTHORITY)

    def approve(self, cr):
        """Record Approved as the board member for the request's current stage."""
        role, decision_field, _ = workflow.BOARDS[cr.stage]
        member = {Role.TRB: self.trb, Role.CAB: self.cab, Role.AUTHORITY: self.authority}[role]
        return workflow.apply_edits(cr, member, {decision_field: Decision.APPROVED})

    def move_to(self, cr, stage):
        """Walk the request forward along its route until it reaches the given stage."""
        while cr.stage != stage:
            if cr.stage in workflow.BOARDS:
                cr = self.approve(cr)
            elif cr.stage == Stage.IMPLEMENTATION:
                cr = workflow.apply_edits(cr, self.requester, {"implementation_notes": "Done as planned."})
            elif cr.stage == Stage.PIR:
                cr = workflow.apply_edits(cr, self.cm, {"review_outcome": ReviewOutcome.SUCCESSFUL})
            cr = workflow.advance(cr, self.cm)
        return cr


class RouteTests(WorkflowTestCase):
    def test_route_per_change_type(self):
        self.assertEqual(
            workflow.route_for(ChangeType.NORMAL),
            [Stage.REQUESTED, Stage.TRB, Stage.CAB, Stage.AUTHORITY, Stage.IMPLEMENTATION, Stage.PIR, Stage.CLOSE],
        )
        self.assertEqual(
            workflow.route_for(ChangeType.EMERGENCY),
            [Stage.REQUESTED, Stage.CAB, Stage.AUTHORITY, Stage.IMPLEMENTATION, Stage.PIR, Stage.CLOSE],
        )
        self.assertEqual(
            workflow.route_for(ChangeType.STANDARD),
            [Stage.REQUESTED, Stage.IMPLEMENTATION, Stage.CLOSE],
        )

    def test_unknown_change_type_is_an_error(self):
        with self.assertRaises(ValueError):
            workflow.route_for("informational")

    def test_normal_change_walks_all_seven_stages(self):
        cr = make_request(self.requester, ChangeType.NORMAL)
        visited = [cr.stage]
        while cr.stage != Stage.CLOSE:
            cr = self.move_to(cr, workflow.next_stage(cr))
            visited.append(cr.stage)
        self.assertEqual(visited, workflow.route_for(ChangeType.NORMAL))
        self.assertIsNotNone(cr.closed_date)
        self.assertEqual(cr.history.filter(kind=HistoryEntry.Kind.MOVED).count(), 6)

    def test_emergency_skips_the_trb(self):
        cr = make_request(self.requester, ChangeType.EMERGENCY)
        cr = workflow.advance(cr, self.cm)
        self.assertEqual(cr.stage, Stage.CAB)

    def test_standard_goes_straight_to_implementation_then_close(self):
        cr = make_request(self.requester, ChangeType.STANDARD)
        cr = workflow.advance(cr, self.cm)
        self.assertEqual(cr.stage, Stage.IMPLEMENTATION)
        cr = self.move_to(cr, Stage.CLOSE)
        self.assertEqual(cr.stage, Stage.CLOSE)
        self.assertIsNotNone(cr.closed_date)


class AdvanceTests(WorkflowTestCase):
    def test_only_cm_can_advance(self):
        cr = make_request(self.requester)
        for user in (self.requester, self.trb, self.cab, self.authority):
            with self.assertRaises(PermissionDenied):
                workflow.advance(cr, user)
        cr.refresh_from_db()
        self.assertEqual(cr.stage, Stage.REQUESTED)

    def test_each_board_must_approve_before_the_request_moves_on(self):
        cr = make_request(self.requester, ChangeType.NORMAL)
        for stage in (Stage.TRB, Stage.CAB, Stage.AUTHORITY):
            cr = workflow.advance(cr, self.cm)
            self.assertEqual(cr.stage, stage)
            with self.assertRaisesMessage(WorkflowError, "must be Approved"):
                workflow.advance(cr, self.cm)
            cr = self.approve(cr)
        cr = workflow.advance(cr, self.cm)
        self.assertEqual(cr.stage, Stage.IMPLEMENTATION)

    def test_implementation_needs_notes(self):
        cr = self.move_to(make_request(self.requester, ChangeType.STANDARD), Stage.IMPLEMENTATION)
        with self.assertRaisesMessage(WorkflowError, "implementation notes"):
            workflow.advance(cr, self.cm)

    def test_pir_needs_an_outcome(self):
        cr = self.move_to(make_request(self.requester, ChangeType.EMERGENCY), Stage.PIR)
        with self.assertRaisesMessage(WorkflowError, "PIR outcome"):
            workflow.advance(cr, self.cm)

    def test_closed_request_cannot_advance(self):
        cr = self.move_to(make_request(self.requester, ChangeType.STANDARD), Stage.CLOSE)
        with self.assertRaisesMessage(WorkflowError, "already closed"):
            workflow.advance(cr, self.cm)

    def test_comment_is_saved_in_history(self):
        cr = workflow.advance(make_request(self.requester), self.cm, "Ready for review")
        entry = cr.history.last()
        self.assertEqual(
            (entry.kind, entry.from_stage, entry.to_stage, entry.comment, entry.actor),
            (HistoryEntry.Kind.MOVED, Stage.REQUESTED, Stage.TRB, "Ready for review", self.cm),
        )


class SendBackTests(WorkflowTestCase):
    def test_normal_goes_back_from_cab_to_trb_then_requested(self):
        cr = self.move_to(make_request(self.requester, ChangeType.NORMAL), Stage.CAB)
        cr = workflow.send_back(cr, self.cm)
        self.assertEqual(cr.stage, Stage.TRB)
        cr = workflow.send_back(cr, self.cm)
        self.assertEqual(cr.stage, Stage.REQUESTED)

    def test_emergency_goes_back_from_cab_to_requested(self):
        cr = self.move_to(make_request(self.requester, ChangeType.EMERGENCY), Stage.CAB)
        cr = workflow.send_back(cr, self.cm)
        self.assertEqual(cr.stage, Stage.REQUESTED)

    def test_standard_goes_back_from_implementation_and_clears_complete(self):
        cr = self.move_to(make_request(self.requester, ChangeType.STANDARD), Stage.IMPLEMENTATION)
        cr = workflow.apply_edits(cr, self.requester, {"implementation_notes": "Done."})
        cr = workflow.complete(cr, self.requester)
        cr = workflow.send_back(cr, self.cm, "Not finished")
        self.assertEqual(cr.stage, Stage.REQUESTED)
        self.assertFalse(cr.implementation_complete)
        self.assertEqual(cr.history.last().kind, HistoryEntry.Kind.SENT_BACK)

    def test_cannot_send_back_from_requested_or_close(self):
        cr = make_request(self.requester, ChangeType.STANDARD)
        with self.assertRaises(WorkflowError):
            workflow.send_back(cr, self.cm)
        cr = self.move_to(cr, Stage.CLOSE)
        with self.assertRaises(WorkflowError):
            workflow.send_back(cr, self.cm)

    def test_only_cm_can_send_back(self):
        cr = self.move_to(make_request(self.requester, ChangeType.NORMAL), Stage.CAB)
        with self.assertRaises(PermissionDenied):
            workflow.send_back(cr, self.cab)


class NeedsChangesTests(WorkflowTestCase):
    def setUp(self):
        super().setUp()
        self.cr = workflow.advance(make_request(self.requester, ChangeType.NORMAL), self.cm)

    def test_sends_the_request_back_to_the_requester(self):
        cr = workflow.needs_changes(self.cr, self.trb, "Add the rollback plan")
        self.assertEqual(cr.stage, Stage.REQUESTED)
        self.assertEqual(cr.trb_decision, TRBDecision.NEEDS_CHANGES)
        self.assertEqual(cr.trb_notes, "NEEDS CHANGES: Add the rollback plan")
        entry = cr.history.last()
        self.assertEqual((entry.kind, entry.to_stage), (HistoryEntry.Kind.NEEDS_CHANGES, Stage.REQUESTED))

    def test_decision_resets_when_it_reaches_the_trb_again(self):
        cr = workflow.needs_changes(self.cr, self.trb, "Add the rollback plan")
        cr = workflow.advance(cr, self.cm)
        self.assertEqual(cr.stage, Stage.TRB)
        self.assertEqual(cr.trb_decision, TRBDecision.PENDING)
        self.assertIn("NEEDS CHANGES", cr.trb_notes)

    def test_needs_a_comment(self):
        with self.assertRaisesMessage(WorkflowError, "what needs to change"):
            workflow.needs_changes(self.cr, self.trb, "   ")

    def test_only_trb_members_at_the_trb_stage(self):
        with self.assertRaises(PermissionDenied):
            workflow.needs_changes(self.cr, self.cm, "No")
        cab_stage = self.move_to(self.cr, Stage.CAB)
        with self.assertRaises(WorkflowError):
            workflow.needs_changes(cab_stage, self.trb, "No")


class RejectTests(WorkflowTestCase):
    def test_each_board_can_reject_at_its_own_stage(self):
        cases = (
            (Stage.TRB, self.trb, "trb_decision", "trb_notes"),
            (Stage.CAB, self.cab, "cab_decision", "cab_notes"),
            (Stage.AUTHORITY, self.authority, "authority_decision", "authority_notes"),
        )
        for stage, member, decision_field, notes_field in cases:
            with self.subTest(stage=stage):
                cr = self.move_to(make_request(self.requester, ChangeType.NORMAL), stage)
                cr = workflow.reject(cr, member, "Too risky")
                self.assertEqual(cr.stage, Stage.CLOSE)
                self.assertEqual(getattr(cr, decision_field), Decision.REJECTED)
                self.assertEqual(getattr(cr, notes_field), "REJECTED: Too risky")
                self.assertEqual(cr.review_outcome, ReviewOutcome.REJECTED)
                self.assertIsNotNone(cr.closed_date)
                entry = cr.history.last()
                self.assertEqual((entry.kind, entry.from_stage, entry.to_stage),
                                 (HistoryEntry.Kind.REJECTED, stage, Stage.CLOSE))

    def test_other_roles_cannot_reject(self):
        cr = self.move_to(make_request(self.requester, ChangeType.NORMAL), Stage.CAB)
        for user in (self.cm, self.trb, self.authority, self.requester):
            with self.assertRaises(PermissionDenied):
                workflow.reject(cr, user, "No")

    def test_reject_needs_a_comment_and_a_review_stage(self):
        cr = make_request(self.requester, ChangeType.NORMAL)
        with self.assertRaises(WorkflowError):
            workflow.reject(cr, self.trb, "No")  # still in Requested
        cr = workflow.advance(cr, self.cm)
        with self.assertRaisesMessage(WorkflowError, "why"):
            workflow.reject(cr, self.trb, "")


class CompleteTests(WorkflowTestCase):
    def setUp(self):
        super().setUp()
        self.cr = self.move_to(make_request(self.requester, ChangeType.STANDARD), Stage.IMPLEMENTATION)

    def test_needs_implementation_notes_first(self):
        with self.assertRaisesMessage(WorkflowError, "implementation notes"):
            workflow.complete(self.cr, self.requester)

    def test_marks_complete_once(self):
        cr = workflow.apply_edits(self.cr, self.requester, {"implementation_notes": "Done."})
        cr = workflow.complete(cr, self.requester, "All good")
        self.assertTrue(cr.implementation_complete)
        self.assertEqual(cr.stage, Stage.IMPLEMENTATION)
        self.assertEqual(cr.history.last().kind, HistoryEntry.Kind.COMPLETED)
        with self.assertRaisesMessage(WorkflowError, "already"):
            workflow.complete(cr, self.requester)

    def test_only_during_implementation_and_only_with_access(self):
        with self.assertRaises(PermissionDenied):
            workflow.complete(self.cr, self.other)
        fresh = make_request(self.requester)
        with self.assertRaises(WorkflowError):
            workflow.complete(fresh, self.requester)


class AccessTests(WorkflowTestCase):
    def test_requesters_see_only_their_own_requests(self):
        mine = make_request(self.requester)
        theirs = make_request(self.other)
        self.assertEqual(list(workflow.visible_to(self.requester)), [mine])
        self.assertTrue(workflow.can_view(mine, self.requester))
        self.assertFalse(workflow.can_view(theirs, self.requester))

    def test_board_members_and_cm_see_everything(self):
        make_request(self.requester)
        make_request(self.other)
        for user in (self.cm, self.trb, self.cab, self.authority):
            self.assertEqual(workflow.visible_to(user).count(), 2)

    def test_requester_email_and_assignee_give_access(self):
        cr = make_request(self.requester, requester_email="SAM@example.test")
        self.assertTrue(workflow.can_view(cr, self.other))
        self.assertIn(cr, workflow.visible_to(self.other))

        implementer = make_user("imp")
        cr = self.move_to(make_request(self.requester, ChangeType.STANDARD), Stage.IMPLEMENTATION)
        self.assertFalse(workflow.can_view(cr, implementer))
        cr = workflow.apply_edits(cr, self.cm, {"assignee": implementer})
        self.assertTrue(workflow.can_view(cr, implementer))
        self.assertIn(cr, workflow.visible_to(implementer))

    def test_inactive_users_see_nothing(self):
        cr = make_request(self.requester)
        self.cm.is_active = False
        self.cm.save()
        self.assertFalse(workflow.can_view(cr, self.cm))
        self.assertEqual(workflow.visible_to(self.cm).count(), 0)

    def test_comments_need_access_and_text(self):
        cr = make_request(self.requester)
        with self.assertRaises(PermissionDenied):
            workflow.add_comment(cr, self.other, "Hello")
        with self.assertRaises(WorkflowError):
            workflow.add_comment(cr, self.requester, " ")
        workflow.add_comment(cr, self.requester, "Any update?")
        entry = cr.history.last()
        self.assertEqual((entry.kind, entry.from_stage, entry.to_stage, entry.comment),
                         (HistoryEntry.Kind.COMMENT, Stage.REQUESTED, Stage.REQUESTED, "Any update?"))


class EditTests(WorkflowTestCase):
    def test_requester_can_edit_the_request_only_while_requested(self):
        cr = make_request(self.requester)
        cr = workflow.apply_edits(cr, self.requester, {"title": "New title"})
        self.assertEqual(cr.title, "New title")
        cr = workflow.advance(cr, self.cm)
        with self.assertRaises(PermissionDenied):
            workflow.apply_edits(cr, self.requester, {"title": "Sneaky"})

    def test_nobody_can_edit_the_stage_or_number_directly(self):
        cr = make_request(self.requester)
        for field, value in (("stage", Stage.CLOSE), ("cr_number", "CR-1"), ("cab_decision", Decision.APPROVED)):
            with self.assertRaises(PermissionDenied):
                workflow.apply_edits(cr, self.cm, {field: value})

    def test_only_the_board_at_its_stage_can_record_a_decision(self):
        cr = workflow.advance(make_request(self.requester, ChangeType.NORMAL), self.cm)
        for user in (self.cm, self.cab, self.requester):
            with self.assertRaises(PermissionDenied):
                workflow.apply_edits(cr, user, {"trb_decision": TRBDecision.APPROVED})
        cr = workflow.apply_edits(cr, self.trb, {"trb_decision": TRBDecision.APPROVED, "trb_tested": True})
        self.assertEqual(cr.trb_decision, TRBDecision.APPROVED)
        self.assertTrue(cr.trb_tested)
        with self.assertRaises(PermissionDenied):
            workflow.apply_edits(cr, self.trb, {"cab_decision": Decision.APPROVED})

    def test_rejected_and_needs_changes_must_use_their_actions(self):
        cr = workflow.advance(make_request(self.requester, ChangeType.NORMAL), self.cm)
        for value in (TRBDecision.REJECTED, TRBDecision.NEEDS_CHANGES):
            with self.assertRaises(WorkflowError):
                workflow.apply_edits(cr, self.trb, {"trb_decision": value})

    def test_pir_outcome_is_set_by_cm(self):
        cr = self.move_to(make_request(self.requester, ChangeType.EMERGENCY), Stage.PIR)
        with self.assertRaises(PermissionDenied):
            workflow.apply_edits(cr, self.requester, {"review_outcome": ReviewOutcome.SUCCESSFUL})
        cr = workflow.apply_edits(cr, self.cm, {"review_outcome": ReviewOutcome.SUCCESSFUL})
        self.assertEqual(cr.review_outcome, ReviewOutcome.SUCCESSFUL)

    def test_closed_requests_are_read_only(self):
        cr = self.move_to(make_request(self.requester, ChangeType.STANDARD), Stage.CLOSE)
        self.assertEqual(workflow.editable_fields(cr, self.cm), frozenset())
