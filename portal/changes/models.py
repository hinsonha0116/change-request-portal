"""Data model. Mirrors the SharePoint lists built by Provision-ChangeRequestLists.ps1."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Stage(models.TextChoices):
    REQUESTED = "requested", "Requested"
    TRB = "trb", "Technical Review Board"
    CAB = "cab", "Change Advisory Board"
    AUTHORITY = "authority", "Change Authority"
    IMPLEMENTATION = "implementation", "Implementation"
    PIR = "pir", "PIR"
    CLOSE = "close", "Close"


class ChangeType(models.TextChoices):
    STANDARD = "standard", "Standard"
    NORMAL = "normal", "Normal"
    EMERGENCY = "emergency", "Emergency"


class Category(models.TextChoices):
    HARDWARE = "hardware", "Hardware"
    SOFTWARE = "software", "Software"
    NETWORK = "network", "Network"


class Priority(models.TextChoices):
    CRITICAL = "1", "1 - Critical"
    HIGH = "2", "2 - High"
    MODERATE = "3", "3 - Moderate"
    LOW = "4", "4 - Low"


class Severity(models.TextChoices):
    """Risk and Impact. Same scale as Priority, without Low."""

    CRITICAL = "1", "1 - Critical"
    HIGH = "2", "2 - High"
    MODERATE = "3", "3 - Moderate"


class Decision(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class TRBDecision(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    NEEDS_CHANGES = "needs_changes", "Needs changes"
    REJECTED = "rejected", "Rejected"


class ReviewOutcome(models.TextChoices):
    SUCCESSFUL = "successful", "Successful"
    SUCCESSFUL_WITH_ISSUES = "successful_with_issues", "Successful with issues"
    FAILED = "failed", "Failed"
    ROLLED_BACK = "rolled_back", "Rolled back"
    REJECTED = "rejected", "Rejected"


class ChangeRequest(models.Model):
    cr_number = models.CharField("CR number", max_length=20, unique=True, editable=False)
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.REQUESTED, db_index=True)

    # The request, as filled in on the New Request screen
    title = models.CharField(max_length=255)
    a6_program = models.CharField("A6 program", max_length=255, blank=True)
    dsn = models.CharField("DSN", max_length=50, blank=True)
    requested_by = models.CharField(max_length=255)
    requester_email = models.EmailField()
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submitted_requests"
    )
    category = models.CharField(max_length=20, choices=Category.choices)
    change_type = models.CharField(max_length=20, choices=ChangeType.choices)
    priority = models.CharField(max_length=1, choices=Priority.choices)
    risk = models.CharField(max_length=1, choices=Severity.choices)
    impact = models.CharField(max_length=1, choices=Severity.choices)
    description = models.TextField()
    impact_details = models.TextField(blank=True)
    justification = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    affected_systems = models.CharField(max_length=255)
    outage_expected = models.BooleanField(default=False)
    outage_duration = models.CharField(max_length=100, blank=True)
    planned_start = models.DateTimeField(null=True, blank=True, db_index=True)
    planned_end = models.DateTimeField(null=True, blank=True)

    # Technical Review Board (Normal changes only)
    trb_decision = models.CharField(
        "TRB decision", max_length=20, choices=TRBDecision.choices, default=TRBDecision.PENDING
    )
    trb_notes = models.TextField("TRB notes", blank=True)
    trb_rollback_reviewed = models.BooleanField("Rollback plan reviewed", default=False)
    trb_tested = models.BooleanField("Tested in lab / test", default=False)
    trb_security_reviewed = models.BooleanField("Security / STIG impact reviewed", default=False)

    # Change Advisory Board
    cab_decision = models.CharField(
        "CAB decision", max_length=20, choices=Decision.choices, default=Decision.PENDING
    )
    cab_notes = models.TextField("CAB notes", blank=True)

    # Change Authority
    authority_decision = models.CharField(max_length=20, choices=Decision.choices, default=Decision.PENDING)
    authority_notes = models.TextField(blank=True)

    # Implementation
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_requests",
    )
    implementation_notes = models.TextField(blank=True)
    implementation_complete = models.BooleanField(default=False)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)

    # PIR and Close
    review_outcome = models.CharField("PIR outcome", max_length=30, choices=ReviewOutcome.choices, blank=True)
    review_notes = models.TextField("PIR notes", blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.cr_number} - {self.title}"

    def clean(self):
        errors = {}
        if self.outage_expected and not self.outage_duration.strip():
            errors["outage_duration"] = "Say how long the outage is expected to last."
        if self.planned_start and self.planned_end and self.planned_end < self.planned_start:
            errors["planned_end"] = "Planned end can't be before planned start."
        if self.actual_start and self.actual_end and self.actual_end < self.actual_start:
            errors["actual_end"] = "Actual end can't be before actual start."
        if errors:
            raise ValidationError(errors)


class HistoryEntry(models.Model):
    """Audit trail: one row per submit, move, decision, completion or comment."""

    class Kind(models.TextChoices):
        CREATED = "created", "Created"
        MOVED = "moved", "Moved on"
        SENT_BACK = "sent_back", "Sent back"
        NEEDS_CHANGES = "needs_changes", "Needs changes"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Implementation complete"
        COMMENT = "comment", "Comment"

    request = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE, related_name="history")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    from_stage = models.CharField(max_length=20, choices=Stage.choices, blank=True)
    to_stage = models.CharField(max_length=20, choices=Stage.choices)
    comment = models.TextField(blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        verbose_name_plural = "history entries"

    def __str__(self):
        return f"{self.request.cr_number}: {self.get_kind_display()}"

    @property
    def summary(self):
        """One line for the history list, e.g. 'Requested → Technical Review Board'."""
        if self.kind == self.Kind.CREATED:
            return "Created"
        if self.kind == self.Kind.COMPLETED:
            return "✔ Implementation complete"
        if self.kind == self.Kind.COMMENT:
            return f"Comment ({self.get_to_stage_display()})"
        return f"{self.get_from_stage_display()} → {self.get_to_stage_display()}"


class Notification(models.Model):
    """Something a user should know about a request. Shown in the app; also emailed when email is set up."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    request = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE, related_name="notifications")
    subject = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["user", "read_at"])]

    def __str__(self):
        return self.subject


class Attachment(models.Model):
    """Rollback plan and other uploads. Stored in the database so one backup covers everything."""

    request = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE, related_name="attachments")
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100, blank=True)
    size = models.PositiveIntegerField()
    data = models.BinaryField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class CRCounter(models.Model):
    """Last CR number handed out in each year. Locked while a number is taken, so no two requests share one."""

    year = models.PositiveIntegerField(primary_key=True)
    last_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.year}: {self.last_number}"
