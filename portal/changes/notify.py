"""Who is told about what. Replaces the two Power Automate flows (DetailScreen-Fixes.md, Parts 4 and 7).

Every notification is saved for the in-app list. When email is set up
(EMAIL_HOST), the same message is also emailed once the change is safely saved.
The person who did the action is not notified about it.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format

from accounts.models import Role, User

from .models import Category, ChangeType, HistoryEntry, Notification, Stage

logger = logging.getLogger(__name__)

CATEGORY_MANAGERS = {Category.SOFTWARE: Role.SW_MANAGER, Category.HARDWARE: Role.HW_MANAGER}

# Moved to this stage -> (who is told, who is copied, what the subject says)
REQUESTER = "requester"
STAGE_RULES = {
    Stage.TRB: (Role.TRB, None, "is ready for TRB review"),
    Stage.CAB: (Role.CAB, None, "is ready for CAB review"),
    Stage.AUTHORITY: (Role.AUTHORITY, None, "is awaiting Change Authority approval"),
    Stage.IMPLEMENTATION: (REQUESTER, Role.CM, "is approved for implementation"),
    Stage.PIR: (Role.CM, None, "has been implemented and is ready for PIR"),
    Stage.CLOSE: (REQUESTER, Role.CM, "is closed"),
}


def _with_role(role):
    return set(User.objects.filter(is_active=True, role_assignments__role=role))


def _requester_users(cr):
    match = Q(pk=cr.submitted_by_id)
    if cr.requester_email:
        match |= Q(email__iexact=cr.requester_email)
    return set(User.objects.filter(match, is_active=True))


def _audience(cr, who):
    """Users to notify, plus any address that has no portal user behind it."""
    if who is None:
        return set(), set()
    if who != REQUESTER:
        return _with_role(who), set()
    users = _requester_users(cr)
    known = {u.email.lower() for u in users if u.email}
    extra = {cr.requester_email} if cr.requester_email and cr.requester_email.lower() not in known else set()
    return users, extra


def _when(value):
    return date_format(timezone.localtime(value), "j M Y H:i") if value else "Not set"


def _link(cr):
    if not settings.PORTAL_BASE_URL:
        return "Open the Change Request Portal to see the full request."
    return f"Open the request: {settings.PORTAL_BASE_URL}{reverse('detail', args=[cr.pk])}"


def _send(subject, body, to, cc, urgent):
    headers = {"Importance": "High", "X-Priority": "1"} if urgent else {}
    try:
        EmailMessage(subject, body, to=sorted(to), cc=sorted(cc), headers=headers).send()
    except Exception:  # a mail problem must never undo or block the change itself
        logger.exception("Could not send email: %s", subject)


def _deliver(cr, actor, subject, body, to, cc=None, urgent=False):
    to_users, to_extra = _audience(cr, to)
    cc_users, _ = _audience(cr, cc)
    to_users.discard(actor)
    cc_users -= to_users | {actor}

    Notification.objects.bulk_create(
        Notification(user=user, request=cr, subject=subject[:400]) for user in to_users | cc_users
    )

    if not settings.PORTAL_EMAIL_ENABLED:
        return
    to_addresses = {u.email for u in to_users if u.email} | to_extra
    cc_addresses = {u.email for u in cc_users if u.email} - to_addresses
    if not to_addresses:
        to_addresses, cc_addresses = cc_addresses, set()
    if to_addresses:
        transaction.on_commit(lambda: _send(subject, body, to_addresses, cc_addresses, urgent))


def new_request(cr):
    """A request was submitted: tell the CM team, and the SW or HW managers for their category."""
    outage = f"YES - {cr.outage_duration}" if cr.outage_expected else "No"
    body = "\n".join([
        "A new change request has been submitted.",
        "",
        f"CR number:        {cr.cr_number}",
        f"Title:            {cr.title}",
        f"Requested by:     {cr.requested_by} ({cr.requester_email})",
        f"A6 program:       {cr.a6_program}",
        f"Category / type:  {cr.get_category_display()} / {cr.get_change_type_display()}",
        f"Priority:         {cr.get_priority_display()}",
        f"Risk / Impact:    {cr.get_risk_display()} / {cr.get_impact_display()}",
        f"Planned:          {_when(cr.planned_start)} to {_when(cr.planned_end)}",
        f"Outage:           {outage}",
        f"Location:         {cr.location}",
        f"Affected systems: {cr.affected_systems}",
        "",
        "Description:",
        cr.description,
        "",
        "Impact details:",
        cr.impact_details or "-",
        "",
        "Justification:",
        cr.justification or "-",
        "",
        _link(cr),
    ])
    urgent = cr.change_type == ChangeType.EMERGENCY or cr.outage_expected
    actor = cr.submitted_by
    _deliver(cr, actor, f"New change request {cr.cr_number}: {cr.title}", body, Role.CM, urgent=urgent)
    manager_role = CATEGORY_MANAGERS.get(cr.category)
    if manager_role:
        label = cr.get_category_display().upper()
        _deliver(cr, actor, f"New {label} change request {cr.cr_number}: {cr.title}", body, manager_role, urgent=urgent)


def stage_event(entry):
    """A history row was written: tell the people who need to act on it or know about it."""
    kind, cr = entry.kind, entry.request
    if kind in (HistoryEntry.Kind.CREATED, HistoryEntry.Kind.COMMENT):
        return

    to, cc = None, None
    if kind == HistoryEntry.Kind.COMPLETED:
        to, what = Role.CM, "has been completed by the implementer"
    elif entry.to_stage == Stage.REQUESTED:
        to = REQUESTER
        what = "needs changes before TRB review" if kind == HistoryEntry.Kind.NEEDS_CHANGES else "was sent back to you"
    else:
        to, cc, what = STAGE_RULES[entry.to_stage]
        if kind == HistoryEntry.Kind.REJECTED:
            what = "was rejected"
        elif kind == HistoryEntry.Kind.SENT_BACK:
            what = f"was sent back to {entry.get_to_stage_display()}"

    actor = entry.actor
    body = "\n".join([
        f"{cr.cr_number} - {cr.title}",
        # Plain ASCII, so the text survives any mail relay or console.
        "Marked as implementation complete." if kind == HistoryEntry.Kind.COMPLETED
        else f"Moved from {entry.get_from_stage_display()} to {entry.get_to_stage_display()}.",
        "",
        f"By:              {actor.get_full_name() or actor.username}",
        f"Comment:         {entry.comment or '-'}",
        f"Requested by:    {cr.requested_by}",
        f"Category / type: {cr.get_category_display()} / {cr.get_change_type_display()}",
        f"Priority:        {cr.get_priority_display()}",
        f"Location:        {cr.location}",
        "",
        _link(cr),
    ])
    _deliver(cr, actor, f"{cr.cr_number} {what}: {cr.title}", body, to, cc)
