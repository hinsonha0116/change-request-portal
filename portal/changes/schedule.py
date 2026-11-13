"""Forward Schedule of Change: the month grid and clash detection."""
import datetime
from dataclasses import dataclass

from django.utils import timezone

from . import workflow
from .models import ChangeRequest, ReviewOutcome


@dataclass
class Entry:
    cr: ChangeRequest
    start: datetime.datetime
    end: datetime.datetime  # the planned end, or the planned start if no end was entered
    has_conflict: bool


def parse_month(text, today):
    """'2026-11' -> date(2026, 11, 1). Anything else gives the current month."""
    try:
        year, month = (int(part) for part in (text or "").split("-"))
        if not 2000 <= year <= 2100:
            raise ValueError
        return datetime.date(year, month, 1)
    except ValueError:
        return today.replace(day=1)


def parse_day(text, default):
    try:
        return datetime.date.fromisoformat(text or "")
    except ValueError:
        return default


def grid_days(month):
    """The 42 days shown for a month: six weeks, starting on a Monday."""
    start = month - datetime.timedelta(days=month.weekday())
    return [start + datetime.timedelta(days=i) for i in range(42)]


def _day_start(day):
    return timezone.make_aware(datetime.datetime.combine(day, datetime.time.min))


def _same(a, b):
    a, b = a.strip().lower(), b.strip().lower()
    return bool(a) and a == b


def load_entries(user, grid_start):
    """Scheduled changes this user may see, on or near the grid, each flagged if it clashes.

    A clash is another change that overlaps in time at the same location or for the
    same A6 program. Clashes are checked against every scheduled change, including
    ones the user can't open, so a requester still learns their slot is contested.
    Rejected changes are left out.
    """
    scheduled = ChangeRequest.objects.filter(
        planned_start__gte=_day_start(grid_start - datetime.timedelta(days=30)),
        planned_start__lt=_day_start(grid_start + datetime.timedelta(days=42)),
    ).exclude(review_outcome=ReviewOutcome.REJECTED)
    spans = [(cr, cr.planned_start, cr.planned_end or cr.planned_start) for cr in scheduled]
    visible = set(workflow.visible_to(user).values_list("pk", flat=True))

    entries = []
    for cr, start, end in spans:
        if cr.pk not in visible:
            continue
        clash = any(
            other.pk != cr.pk
            and other_start < end
            and other_end > start
            and (_same(cr.location, other.location) or _same(cr.a6_program, other.a6_program))
            for other, other_start, other_end in spans
        )
        entries.append(Entry(cr, start, end, clash))
    return sorted(entries, key=lambda e: e.start)


def entries_on(entries, day):
    """Changes that touch this day. One that runs across several days shows on each."""
    day_begins = _day_start(day)
    next_day_begins = _day_start(day + datetime.timedelta(days=1))
    return [e for e in entries if e.start < next_day_begins and e.end >= day_begins]
