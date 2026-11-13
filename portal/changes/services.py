"""Submitting a request and handing out its CR number."""
from django.db import transaction
from django.utils import timezone

from . import notify
from .models import ChangeRequest, CRCounter, HistoryEntry, Stage


def next_cr_number(today=None):
    """Return the next number for this year, e.g. CR-2026-001. Restarts at 001 each 1 January.

    Must run inside a transaction: the year's counter row stays locked until the
    caller commits, so two submissions at the same moment get different numbers.
    """
    year = (today or timezone.localdate()).year
    counter, _ = CRCounter.objects.select_for_update().get_or_create(year=year)
    counter.last_number += 1
    counter.save(update_fields=["last_number"])
    return f"CR-{year}-{counter.last_number:03d}"


@transaction.atomic
def submit_request(user, today=None, **fields):
    """Create a change request in the Requested stage and log it in the history."""
    cr = ChangeRequest(submitted_by=user, stage=Stage.REQUESTED, **fields)
    # Validate before taking a number, so a rejected form never uses one up.
    cr.full_clean(exclude=["cr_number"])
    cr.cr_number = next_cr_number(today)
    cr.save()
    HistoryEntry.objects.create(
        request=cr, kind=HistoryEntry.Kind.CREATED, to_stage=Stage.REQUESTED, actor=user
    )
    notify.new_request(cr)
    return cr
