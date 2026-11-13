from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model

from . import workflow
from .models import ChangeRequest, Decision

# Field order on the New Request and detail screens (DetailScreen-Fixes.md, Part 2b).
REQUEST_FIELD_ORDER = [
    "a6_program", "requested_by", "dsn", "requester_email", "title", "category",
    "change_type", "priority", "risk", "impact", "planned_start", "planned_end",
    "outage_expected", "outage_duration", "location", "affected_systems",
    "description", "impact_details", "justification",
]
STAGE_FIELD_ORDER = [
    "trb_decision", "trb_rollback_reviewed", "trb_tested", "trb_security_reviewed", "trb_notes",
    "cab_decision", "cab_notes",
    "authority_decision", "authority_notes",
    "assignee", "actual_start", "actual_end", "implementation_notes",
    "review_outcome", "review_notes",
]

_DATETIME_FIELDS = ("planned_start", "planned_end", "actual_start", "actual_end")
_TEXT_FIELDS = (
    "description", "impact_details", "justification", "trb_notes", "cab_notes",
    "authority_notes", "implementation_notes", "review_notes",
)
_PLACEHOLDERS = {
    "location": "Base and building, e.g. Ramstein AB, Bldg 400",
    "affected_systems": "e.g. VDI servers, Exchange",
    "outage_duration": "e.g. 30 minutes",
    "impact_details": "Who and what is affected, and how",
    "justification": "Why this change is needed",
}


def _widgets(names):
    widgets = {}
    for name in names:
        if name in _DATETIME_FIELDS:
            widgets[name] = forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")
        elif name in _TEXT_FIELDS:
            widgets[name] = forms.Textarea(attrs={"rows": 4})
    return widgets


def _add_placeholders(form):
    for name, text in _PLACEHOLDERS.items():
        if name in form.fields:
            form.fields[name].widget.attrs["placeholder"] = text


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """A file input that accepts several files and checks each one's size."""

    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            data = []
        elif not isinstance(data, (list, tuple)):
            data = [data]
        if self.required and not data:
            raise forms.ValidationError(self.error_messages["required"], code="required")
        files = [super(MultipleFileField, self).clean(item, initial) for item in data]
        limit = settings.PORTAL_MAX_UPLOAD_MB * 1024 * 1024
        for upload in files:
            if upload.size > limit:
                raise forms.ValidationError(
                    f"{upload.name} is larger than {settings.PORTAL_MAX_UPLOAD_MB} MB."
                )
        return files


class NewRequestForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        help_text="Attach the completed Rollback Plan, plus anything else reviewers need.",
    )

    class Meta:
        model = ChangeRequest
        fields = REQUEST_FIELD_ORDER
        widgets = _widgets(REQUEST_FIELD_ORDER)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _add_placeholders(self)


class AttachmentForm(forms.Form):
    files = MultipleFileField(label="Add files")


def detail_form(cr, user, data=None):
    """A form holding just the fields this user may edit right now, or None if there are none."""
    allowed = workflow.editable_fields(cr, user)
    names = [n for n in REQUEST_FIELD_ORDER + STAGE_FIELD_ORDER if n in allowed]
    if not names:
        return None
    form_class = forms.modelform_factory(ChangeRequest, fields=names, widgets=_widgets(names))
    form = form_class(data, instance=cr)
    _add_placeholders(form)

    # Rejected and Needs changes are buttons, not drop-down choices.
    if cr.stage in workflow.BOARDS:
        decision_field = workflow.BOARDS[cr.stage][1]
        form.fields[decision_field].choices = [
            (Decision.PENDING, Decision.PENDING.label),
            (Decision.APPROVED, Decision.APPROVED.label),
        ]
    if "assignee" in form.fields:
        field = form.fields["assignee"]
        field.queryset = get_user_model().objects.filter(is_active=True).order_by("username")
        field.label_from_instance = lambda u: u.get_full_name() or u.username
    return form
