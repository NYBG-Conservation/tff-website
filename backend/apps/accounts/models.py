from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        INTERNAL_SUPERADMIN = "internal_superadmin", "Internal Superadmin"
        INTERNAL_ADMIN = "internal_admin", "Internal Admin"
        EXTERNAL_SUPERADMIN = "external_superadmin", "External Superadmin"
        EXTERNAL_ADMIN = "external_admin", "External Admin"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.EXTERNAL_ADMIN,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="member_profiles",
        help_text="Home organization for external roles. Empty for internal roles.",
    )

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"
