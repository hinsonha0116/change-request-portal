from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import RoleAssignment, User


class RoleInline(admin.TabularInline):
    model = RoleAssignment
    extra = 1


@admin.register(User)
class PortalUserAdmin(UserAdmin):
    inlines = [RoleInline]
