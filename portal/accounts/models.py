from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """Replaces CMTeam, TRBMembers, CABMembers and ChangeAuthorities in App.Formulas."""

    CM = "cm", "Change Management team"
    TRB = "trb", "Technical Review Board"
    CAB = "cab", "Change Advisory Board"
    AUTHORITY = "authority", "Change Authority"
    SW_MANAGER = "sw_manager", "Software manager"
    HW_MANAGER = "hw_manager", "Hardware manager"


class User(AbstractUser):
    def has_role(self, role):
        return self.is_active and self.role_assignments.filter(role=role).exists()

    def has_any_role(self, *roles):
        return self.is_active and self.role_assignments.filter(role__in=roles).exists()


class RoleAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role_assignments")
    role = models.CharField(max_length=20, choices=Role.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "role"], name="unique_role_per_user"),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_role_display()}"
