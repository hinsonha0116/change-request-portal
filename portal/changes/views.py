import datetime
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.text import capfirst
from django.views.decorators.http import require_POST

from accounts.models import Role

from . import schedule as fsc
from . import workflow
from .forms import REQUEST_FIELD_ORDER, AttachmentForm, NewRequestForm, detail_form
from .models import Attachment, Category, ChangeRequest, ChangeType, Stage
from .services import submit_request
from .workflow import WorkflowError

SHORT_STAGE = {Stage.TRB: "TRB", Stage.CAB: "CAB", Stage.AUTHORITY: "Authority"}
CLOSE_COLUMN_DAYS = 30

# Detail screen sections. Each shows once its stage is reached, if that stage is on the request's route.
SECTIONS = [
    ("Request", Stage.REQUESTED, REQUEST_FIELD_ORDER),
    ("Technical Review Board", Stage.TRB,
     ["trb_decision", "trb_rollback_reviewed", "trb_tested", "trb_security_reviewed", "trb_notes"]),
    ("Change Advisory Board", Stage.CAB, ["cab_decision", "cab_notes"]),
    ("Change Authority", Stage.AUTHORITY, ["authority_decision", "authority_notes"]),
    ("Implementation", Stage.IMPLEMENTATION, ["assignee", "actual_start", "actual_end", "implementation_notes"]),
    ("PIR", Stage.PIR, ["review_outcome", "review_notes"]),
]
WIDE_FIELDS = {
    "affected_systems", "description", "impact_details", "justification",
    "trb_notes", "cab_notes", "authority_notes", "implementation_notes", "review_notes",
}


def short_stage(stage):
    return SHORT_STAGE.get(stage, Stage(stage).label)


def _get_visible(request, pk):
    """Fetch a request, or 404 if it doesn't exist or this user may not see it."""
    cr = get_object_or_404(ChangeRequest, pk=pk)
    if not workflow.can_view(cr, request.user):
        raise Http404
    return cr


# ---------------------------------------------------------------- board

@login_required
def board(request):
    user = request.user
    sees_all = user.has_any_role(*workflow.SEE_ALL_ROLES)
    mine_only = request.GET.get("mine") == "1"
    search = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    change_type = request.GET.get("type", "")

    requests = workflow.own_requests(user) if (sees_all and mine_only) else workflow.visible_to(user)
    if search:
        requests = requests.filter(Q(title__icontains=search) | Q(cr_number__icontains=search))
    if category in Category.values:
        requests = requests.filter(category=category)
    if change_type in ChangeType.values:
        requests = requests.filter(change_type=change_type)
    cutoff = timezone.now() - datetime.timedelta(days=CLOSE_COLUMN_DAYS)
    requests = requests.exclude(stage=Stage.CLOSE, closed_date__lt=cutoff).order_by("-updated_at")

    cards = {stage: [] for stage in Stage.values}
    for cr in requests:
        cards[cr.stage].append(cr)
    columns = [
        {"number": n, "stage": stage, "label": short_stage(stage), "cards": cards[stage]}
        for n, stage in enumerate(Stage.values, start=1)
    ]
    return render(request, "changes/board.html", {
        "columns": columns,
        "sees_all": sees_all,
        "mine_only": mine_only,
        "search": search,
        "category": category,
        "change_type": change_type,
        "categories": Category.choices,
        "change_types": ChangeType.choices,
        "close_days": CLOSE_COLUMN_DAYS,
    })


# ---------------------------------------------------------------- new request

@login_required
def new_request(request):
    user = request.user
    if request.method == "POST":
        form = NewRequestForm(request.POST, request.FILES)
        if form.is_valid():
            fields = dict(form.cleaned_data)
            uploads = fields.pop("attachments")
            with transaction.atomic():
                cr = submit_request(user, **fields)
                for upload in uploads:
                    workflow.attach(cr, user, upload)
            messages.success(request, f"{cr.cr_number} submitted.")
            return redirect("detail", pk=cr.pk)
    else:
        form = NewRequestForm(initial={
            "requested_by": user.get_full_name() or user.username,
            "requester_email": user.email,
        })
    return render(request, "changes/new.html", {"form": form, "wide_fields": WIDE_FIELDS | {"attachments"}})


# ---------------------------------------------------------------- detail

def _display(cr, name):
    """A field's value as read-only text. Empty string means 'nothing to show'."""
    field = ChangeRequest._meta.get_field(name)
    value = getattr(cr, name)
    if isinstance(field, models.BooleanField):
        return "Yes" if value else "No"
    if value in (None, ""):
        return ""
    if field.choices:
        return getattr(cr, f"get_{name}_display")()
    if isinstance(field, models.DateTimeField):
        return date_format(timezone.localtime(value), "j M Y H:i")
    if isinstance(field, models.ForeignKey):
        return value.get_full_name() or value.username
    return str(value)


def _sections(cr, form):
    route = workflow.route_for(cr.change_type)
    reached = route[: route.index(cr.stage) + 1]
    sections = []
    for title, stage, names in SECTIONS:
        if stage not in reached:
            continue
        rows = []
        for name in names:
            wide = name in WIDE_FIELDS
            if form is not None and name in form.fields:
                rows.append({"field": form[name], "wide": wide})
                continue
            value = _display(cr, name)
            if value:  # empty read-only fields are hidden
                label = capfirst(ChangeRequest._meta.get_field(name).verbose_name)
                rows.append({"label": label, "value": value, "wide": wide})
        if rows:
            sections.append({"title": title, "rows": rows})
    return sections


def _tracker(cr):
    route = workflow.route_for(cr.change_type)
    current = route.index(cr.stage)
    return [
        {"number": i + 1, "label": short_stage(stage),
         "state": "done" if i < current else "current" if i == current else "todo"}
        for i, stage in enumerate(route)
    ]


def _detail_url(request, cr):
    url = reverse("detail", args=[cr.pk])
    return f"{url}?from=schedule" if request.GET.get("from") == "schedule" else url


def _render_detail(request, cr, form):
    user = request.user
    is_cm = user.has_role(Role.CM)
    on_own_board = cr.stage in workflow.BOARDS and user.has_role(workflow.BOARDS[cr.stage][0])
    target = workflow.next_stage(cr)
    return render(request, "changes/detail.html", {
        "cr": cr,
        "form": form,
        "sections": _sections(cr, form),
        "tracker": _tracker(cr),
        "history": cr.history.select_related("actor"),
        "attachments": cr.attachments.defer("data"),
        "upload_form": AttachmentForm() if cr.stage != Stage.CLOSE else None,
        "from_schedule": request.GET.get("from") == "schedule",
        "advance_label": f"Move to {Stage(target).label} →" if is_cm and target else "",
        "can_send_back": is_cm and cr.stage not in (Stage.REQUESTED, Stage.CLOSE),
        "can_reject": on_own_board,
        "can_needs_changes": on_own_board and cr.stage == Stage.TRB,
        "can_complete": cr.stage == Stage.IMPLEMENTATION and not cr.implementation_complete,
    })


def _run_action(action, cr, user, comment):
    """Carry out a detail-screen button. Returns the updated request and the message to show."""
    if action == "save":
        return cr, "Saved."
    if action == "advance":
        cr = workflow.advance(cr, user, comment)
        return cr, f"Moved to {cr.get_stage_display()}."
    if action == "back":
        cr = workflow.send_back(cr, user, comment)
        return cr, f"Sent back to {cr.get_stage_display()}."
    if action == "reject":
        return workflow.reject(cr, user, comment), "Change rejected and closed."
    if action == "needschanges":
        return workflow.needs_changes(cr, user, comment), "Sent back to the requester for changes."
    if action == "complete":
        return workflow.complete(cr, user, comment), "Marked complete."
    return workflow.add_comment(cr, user, comment), "Comment added."


ACTIONS = {"save", "advance", "back", "reject", "needschanges", "complete", "comment"}


@login_required
def detail(request, pk):
    cr = _get_visible(request, pk)
    if request.method != "POST":
        return _render_detail(request, cr, detail_form(cr, request.user))

    action = request.POST.get("action", "")
    if action not in ACTIONS:
        return HttpResponseBadRequest("Unknown action.")
    # The page lists the fields for one stage. If the request has moved since the
    # page was opened, those fields no longer apply, so nothing is saved.
    if request.POST.get("stage") != cr.stage:
        messages.warning(request, "This request changed while you had it open. Nothing was saved; check it and try again.")
        return redirect(_detail_url(request, cr))

    # Like the Power App, every button first saves whatever the user may edit.
    form = detail_form(cr, request.user, request.POST)
    if form is not None:
        if not form.is_valid():
            messages.error(request, "Nothing was saved. Fix the fields marked below and try again.")
            return _render_detail(request, cr, form)
        cr = workflow.apply_edits(cr, request.user, form.cleaned_data)

    try:
        cr, message = _run_action(action, cr, request.user, request.POST.get("comment", ""))
        messages.success(request, message)
    except WorkflowError as error:
        messages.error(request, str(error))

    if not workflow.can_view(cr, request.user):
        return redirect("board")
    return redirect(_detail_url(request, cr))


# ---------------------------------------------------------------- attachments

@login_required
@require_POST
def upload_attachment(request, pk):
    cr = _get_visible(request, pk)
    form = AttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            for upload in form.cleaned_data["files"]:
                workflow.attach(cr, request.user, upload)
            messages.success(request, "Files added.")
        except WorkflowError as error:
            messages.error(request, str(error))
    else:
        messages.error(request, " ".join(form.errors.get("files", ["Choose a file first."])))
    return redirect(_detail_url(request, cr))


@login_required
def download_attachment(request, pk):
    attachment = get_object_or_404(Attachment.objects.select_related("request"), pk=pk)
    if not workflow.can_view(attachment.request, request.user):
        raise Http404
    # Always sent as a download with a neutral type, so an uploaded file never runs in the browser.
    return FileResponse(
        io.BytesIO(bytes(attachment.data)),
        as_attachment=True,
        filename=attachment.filename,
        content_type="application/octet-stream",
    )


# ---------------------------------------------------------------- schedule

@login_required
def schedule(request):
    today = timezone.localdate()
    month = fsc.parse_month(request.GET.get("month"), today)
    default_day = today if (today.year, today.month) == (month.year, month.month) else month
    selected = fsc.parse_day(request.GET.get("day"), default_day)

    days = fsc.grid_days(month)
    entries = fsc.load_entries(request.user, days[0])
    cells = []
    for day in days:
        on_day = fsc.entries_on(entries, day)
        cells.append({
            "day": day,
            "in_month": day.month == month.month,
            "is_today": day == today,
            "is_selected": day == selected,
            "chips": on_day[:3],
            "more": max(len(on_day) - 3, 0),
        })
    previous_month = (month - datetime.timedelta(days=1)).replace(day=1)
    next_month = (month + datetime.timedelta(days=32)).replace(day=1)
    return render(request, "changes/schedule.html", {
        "month": month,
        "previous_month": previous_month,
        "next_month": next_month,
        "today": today,
        "cells": cells,
        "selected": selected,
        "selected_entries": fsc.entries_on(entries, selected),
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    })
