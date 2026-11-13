from django.contrib import admin

from .models import ChangeRequest, HistoryEntry


class HistoryInline(admin.TabularInline):
    model = HistoryEntry
    extra = 0
    can_delete = False
    readonly_fields = ["kind", "from_stage", "to_stage", "comment", "actor", "created_at"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    """Read-only look at the data. Changes go through the workflow so the rules and history apply."""

    list_display = ["cr_number", "title", "stage", "change_type", "category", "planned_start"]
    list_filter = ["stage", "change_type", "category"]
    search_fields = ["cr_number", "title"]
    inlines = [HistoryInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
