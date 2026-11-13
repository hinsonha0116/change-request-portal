from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect, render

from .models import Role, RoleAssignment, User


def can_manage_people(user):
    return user.is_active and (user.is_superuser or user.has_role(Role.CM))


@login_required
def people(request):
    """Who holds which role. Replaces the email lists in App.Formulas and the planned App Roles list."""
    if not can_manage_people(request.user):
        raise PermissionDenied("Only the Change Management team can manage roles.")
    users = User.objects.filter(is_active=True).order_by("last_name", "first_name", "username")

    if request.method == "POST":
        kept_own_cm = True
        with transaction.atomic():
            for user in users:
                wanted = {role for role in Role.values if f"role-{user.pk}-{role}" in request.POST}
                # Don't let someone remove their own CM role and lock themselves out of this screen.
                if user == request.user and user.has_role(Role.CM) and Role.CM not in wanted:
                    wanted.add(Role.CM)
                    kept_own_cm = False
                RoleAssignment.objects.filter(user=user).exclude(role__in=wanted).delete()
                for role in wanted:
                    RoleAssignment.objects.get_or_create(user=user, role=role)
        messages.success(request, "Roles saved.")
        if not kept_own_cm:
            messages.warning(request, "You can't remove your own Change Management role. Ask another CM team member to do it.")
        return redirect("people")

    held = {}
    for user_id, role in RoleAssignment.objects.values_list("user_id", "role"):
        held.setdefault(user_id, set()).add(role)
    rows = [
        {"user": user, "cells": [{"role": role, "label": label, "held": role in held.get(user.pk, ())}
                                 for role, label in Role.choices]}
        for user in users
    ]
    return render(request, "accounts/people.html", {"rows": rows, "roles": Role.choices})
