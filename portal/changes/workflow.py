"""Stage rules: who can do what to a request, and where it goes next.

This replaces the Stages table in App.Formulas and the frmDetail.OnSuccess
formula (DetailScreen-Fixes.md, Part 9). Every rule is enforced here, on the
server, whatever the screens show.

Each action takes the request, the acting user and a comment, and returns the
updated request. It raises PermissionDenied if the user may not do it, and
WorkflowError if the request is not ready for it.
"""
import os

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from accounts.models import Role

from . import notify
from .models import (
    Attachment,
    Category,
    ChangeRequest,
    ChangeType,
    Decision,
    HistoryEntry,
    ReviewOutcome,
    Stage,
    TRBDecision,
)


class WorkflowError(Exception):
    """The request isn't in a state that allows the action. The message is shown to the user."""


# ---------------------------------------------------------------- routes

_ALL = frozenset(ChangeType.values)
_REVIEWED = frozenset({ChangeType.NORMAL, ChangeType.EMERGENCY})

# Which change types pass through each stage. This one table controls every route.
# To change a route (e.g. when the Emergency process is finalised), edit it here.
STAGE_TYPES = (
    (Stage.REQUESTED, _ALL),
    (Stage.TRB, frozenset({ChangeType.NORMAL})),
    (Stage.CAB, _REVIEWED),
    (Stage.AUTHORITY, _REVIEWED),
    (Stage.IMPLEMENTATION, _ALL),
    (Stage.PIR, _REVIEWED),
    (Stage.CLOSE, _ALL),
)


def route_for(change_type):
    """The stages a change of this type passes through, in order."""
    route = [stage for stage, types in STAGE_TYPES if change_type in types]
    if not route:
        raise ValueError(f"Unknown change type: {change_type!r}")
    return route


def next_stage(cr):
    route = route_for(cr.change_type)
    i = route.index(cr.stage)
    return route[i + 1] if i + 1 < len(route) else None


def previous_stage(cr):
    route = route_for(cr.change_type)
    i = route.index(cr.stage)
    return route[i - 1] if i > 0 else None


# ---------------------------------------------------------------- who is who

# The board that decides at each review stage, and the fields it owns.
BOARDS = {
    Stage.TRB: (Role.TRB, "trb_decision", "trb_notes"),
    Stage.CAB: (Role.CAB, "cab_decision", "cab_notes"),
    Stage.AUTHORITY: (Role.AUTHORITY, "authority_decision", "authority_notes"),
}

SEE_ALL_ROLES = (Role.CM, Role.TRB, Role.CAB, Role.AUTHORITY)
# SW and HW managers are told about new requests in their category, so they can open those too.
MANAGER_CATEGORIES = {Role.SW_MANAGER: Category.SOFTWARE, Role.HW_MANAGER: Category.HARDWARE}

REQUEST_FIELDS = frozenset({
    "title", "a6_program", "dsn", "requested_by", "requester_email", "category",
    "change_type", "priority", "risk", "impact", "description", "impact_details",
    "justification", "location", "affected_systems", "outage_expected",
    "outage_duration", "planned_start", "planned_end",
})
TRB_FIELDS = frozenset({
    "trb_decision", "trb_notes", "trb_rollback_reviewed", "trb_tested", "trb_security_reviewed",
})
IMPLEMENTATION_FIELDS = frozenset({"assignee", "implementation_notes", "actual_start", "actual_end"})
PIR_FIELDS = frozenset({"review_outcome", "review_notes"})


def is_requester(cr, user):
    if cr.submitted_by_id == user.pk:
        return True
    return bool(user.email) and user.email.lower() == cr.requester_email.lower()


def can_view(cr, user):
    """Board members and the CM team see everything; everyone else sees their own requests."""
    if not user.is_active:
        return False
    if is_requester(cr, user) or cr.assignee_id == user.pk or user.has_any_role(*SEE_ALL_ROLES):
        return True
    return cr.category in managed_categories(user)


def managed_categories(user):
    return [category for role, category in MANAGER_CATEGORIES.items() if user.has_role(role)]


def own_requests(user):
    """Requests this user submitted, was named on as requester, or is assigned to."""
    mine = Q(submitted_by=user) | Q(assignee=user)
    if user.email:
        mine |= Q(requester_email__iexact=user.email)
    return ChangeRequest.objects.filter(mine)


def visible_to(user):
    """The requests this user may see, for the board and the calendar."""
    if not user.is_active:
        return ChangeRequest.objects.none()
    if user.has_any_role(*SEE_ALL_ROLES):
        return ChangeRequest.objects.all()
    return own_requests(user) | ChangeRequest.objects.filter(category__in=managed_categories(user))


def editable_fields(cr, user):
    """The fields this user may change on this request at its current stage."""
    if not can_view(cr, user):
        return frozenset()
    if cr.stage == Stage.REQUESTED:
        return REQUEST_FIELDS if is_requester(cr, user) or user.has_role(Role.CM) else frozenset()
    if cr.stage in BOARDS:
        role, decision_field, notes_field = BOARDS[cr.stage]
        if not user.has_role(role):
            return frozenset()
        return TRB_FIELDS if cr.stage == Stage.TRB else frozenset({decision_field, notes_field})
    if cr.stage == Stage.IMPLEMENTATION:
        return IMPLEMENTATION_FIELDS
    if cr.stage == Stage.PIR:
        return PIR_FIELDS if user.has_role(Role.CM) else frozenset()
    return frozenset()


# ---------------------------------------------------------------- helpers

def _lock(cr):
    """Re-read the request with a row lock, so two people acting at once can't both move it."""
    return ChangeRequest.objects.select_for_update().get(pk=cr.pk)


def _require(allowed, message):
    if not allowed:
        raise PermissionDenied(message)


def _log(cr, user, kind, from_stage, to_stage, comment):
    entry = HistoryEntry.objects.create(
        request=cr, kind=kind, from_stage=from_stage, to_stage=to_stage,
        comment=comment.strip(), actor=user,
    )
    notify.stage_event(entry)


def _append_note(existing, label, comment):
    return "\n".join(part for part in (existing.strip(), f"{label}: {comment.strip()}") if part)


def advance_blocker(cr):
    """Why this request can't move on yet, or None if it can."""
    if cr.stage == Stage.CLOSE:
        return "This request is already closed."
    if cr.stage == Stage.TRB and cr.trb_decision != TRBDecision.APPROVED:
        return "The TRB decision must be Approved before this change can move on."
    if cr.stage == Stage.CAB and cr.cab_decision != Decision.APPROVED:
        return "The CAB decision must be Approved before this change can move on."
    if cr.stage == Stage.AUTHORITY and cr.authority_decision != Decision.APPROVED:
        return "The Change Authority decision must be Approved before this change can move on."
    if cr.stage == Stage.IMPLEMENTATION and not cr.implementation_notes.strip():
        return "Add implementation notes before moving on."
    if cr.stage == Stage.PIR and not cr.review_outcome:
        return "Choose a PIR outcome before closing."
    return None


# ---------------------------------------------------------------- actions

@transaction.atomic
def advance(cr, user, comment=""):
    """CM team: move the request to the next stage on its route."""
    cr = _lock(cr)
    _require(user.has_role(Role.CM), "Only the Change Management team can move a request on.")
    blocker = advance_blocker(cr)
    if blocker:
        raise WorkflowError(blocker)

    current, target = cr.stage, next_stage(cr)
    cr.stage = target
    if target == Stage.TRB:
        cr.trb_decision = TRBDecision.PENDING  # a fresh review each time it reaches the TRB
    if target == Stage.CLOSE:
        cr.closed_date = timezone.now()
    cr.save()
    _log(cr, user, HistoryEntry.Kind.MOVED, current, target, comment)
    return cr


@transaction.atomic
def send_back(cr, user, comment=""):
    """CM team: return the request to the previous stage on its route."""
    cr = _lock(cr)
    _require(user.has_role(Role.CM), "Only the Change Management team can send a request back.")
    if cr.stage in (Stage.REQUESTED, Stage.CLOSE):
        raise WorkflowError("A request can't be sent back from this stage.")

    current, target = cr.stage, previous_stage(cr)
    cr.stage = target
    cr.implementation_complete = False
    cr.save()
    _log(cr, user, HistoryEntry.Kind.SENT_BACK, current, target, comment)
    return cr


@transaction.atomic
def reject(cr, user, comment):
    """TRB, CAB or Change Authority member, at their own stage: reject and close."""
    cr = _lock(cr)
    if cr.stage not in BOARDS:
        raise WorkflowError("A request can only be rejected at the TRB, CAB or Change Authority stage.")
    role, decision_field, notes_field = BOARDS[cr.stage]
    _require(user.has_role(role), "Only a member of the board reviewing this request can reject it.")
    if not comment.strip():
        raise WorkflowError("Add a comment saying why the change is rejected.")

    current = cr.stage
    setattr(cr, decision_field, Decision.REJECTED)
    setattr(cr, notes_field, _append_note(getattr(cr, notes_field), "REJECTED", comment))
    cr.stage = Stage.CLOSE
    cr.review_outcome = ReviewOutcome.REJECTED
    cr.closed_date = timezone.now()
    cr.save()
    _log(cr, user, HistoryEntry.Kind.REJECTED, current, Stage.CLOSE, comment)
    return cr


@transaction.atomic
def needs_changes(cr, user, comment):
    """TRB member, at the TRB stage: send the request back to the requester."""
    cr = _lock(cr)
    if cr.stage != Stage.TRB:
        raise WorkflowError("Needs changes can only be used at the TRB stage.")
    _require(user.has_role(Role.TRB), "Only a TRB member can ask for changes.")
    if not comment.strip():
        raise WorkflowError("Add a comment saying what needs to change.")

    cr.stage = Stage.REQUESTED
    cr.trb_decision = TRBDecision.NEEDS_CHANGES
    cr.trb_notes = _append_note(cr.trb_notes, "NEEDS CHANGES", comment)
    cr.save()
    _log(cr, user, HistoryEntry.Kind.NEEDS_CHANGES, Stage.TRB, Stage.REQUESTED, comment)
    return cr


@transaction.atomic
def complete(cr, user, comment=""):
    """Anyone who can open the request, during Implementation: mark the work as done."""
    cr = _lock(cr)
    _require(can_view(cr, user), "You don't have access to this request.")
    if cr.stage != Stage.IMPLEMENTATION:
        raise WorkflowError("A request can only be marked complete during Implementation.")
    if cr.implementation_complete:
        raise WorkflowError("This request is already marked complete.")
    if not cr.implementation_notes.strip():
        raise WorkflowError("Add implementation notes before marking it complete.")

    cr.implementation_complete = True
    cr.save()
    _log(cr, user, HistoryEntry.Kind.COMPLETED, Stage.IMPLEMENTATION, Stage.IMPLEMENTATION, comment)
    return cr


@transaction.atomic
def add_comment(cr, user, comment):
    """Anyone who can open the request: add a comment to its history."""
    cr = _lock(cr)
    _require(can_view(cr, user), "You don't have access to this request.")
    if not comment.strip():
        raise WorkflowError("Type a comment first.")
    _log(cr, user, HistoryEntry.Kind.COMMENT, cr.stage, cr.stage, comment)
    return cr


@transaction.atomic
def attach(cr, user, upload):
    """Anyone who can open the request, until it is closed: add a file."""
    cr = _lock(cr)
    _require(can_view(cr, user), "You don't have access to this request.")
    if cr.stage == Stage.CLOSE:
        raise WorkflowError("Files can't be added to a closed request.")
    return Attachment.objects.create(
        request=cr,
        filename=os.path.basename(upload.name.replace("\\", "/"))[:255],
        content_type=(upload.content_type or "")[:100],
        size=upload.size,
        data=upload.read(),
        uploaded_by=user,
    )


@transaction.atomic
def apply_edits(cr, user, changes):
    """Save field changes, limited to what this user may edit at the current stage."""
    cr = _lock(cr)
    _require(can_view(cr, user), "You don't have access to this request.")
    blocked = set(changes) - editable_fields(cr, user)
    _require(not blocked, f"You can't change these fields at this stage: {', '.join(sorted(blocked))}.")

    # A board records Approved (or back to Pending) here. Rejected and Needs changes
    # also move the request, so they only happen through their own actions.
    if cr.stage in BOARDS:
        decision_field = BOARDS[cr.stage][1]
        if changes.get(decision_field, Decision.PENDING) not in (Decision.PENDING, Decision.APPROVED):
            raise WorkflowError("Use the Reject or Needs changes button for that decision.")

    for field, value in changes.items():
        setattr(cr, field, value)
    cr.full_clean()
    cr.save()
    return cr
