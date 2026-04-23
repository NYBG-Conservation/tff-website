from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        INTERNAL_ADMIN = "internal_admin", "Internal Admin"
        EXTERNAL_PARTNER_ADMIN = "external_partner_admin", "External Partner Admin"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.EXTERNAL_PARTNER_ADMIN)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"
