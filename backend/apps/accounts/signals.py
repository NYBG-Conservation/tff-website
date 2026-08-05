from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .constants import ALL_ROLE_GROUPS, EXTERNAL_ADMIN_GROUP, ROLE_TO_GROUP
from .models import UserProfile
from .role_group_permissions import ensure_role_group_permissions


def _ensure_staff_for_platform_role(user: User) -> None:
    """Platform roles use Django admin; staff status is required to open /admin/."""
    if user.is_staff:
        return
    user.is_staff = True
    user.save(update_fields=["is_staff"])


def _heal_empty_role_group_permissions() -> None:
    """Only seed group permissions when a canonical group has none.

    Do not rewrite permissions on every profile save — that undoes manual Group
    permission edits made in Django admin. Use `sync_role_groups` for a full reset.
    """
    group, _ = Group.objects.get_or_create(name=EXTERNAL_ADMIN_GROUP)
    if group.permissions.count() == 0:
        ensure_role_group_permissions()


def _sync_role_group(profile: UserProfile) -> None:
    _heal_empty_role_group_permissions()
    group_name = ROLE_TO_GROUP.get(profile.role, ROLE_TO_GROUP["external_admin"])
    groups = {name: Group.objects.get_or_create(name=name)[0] for name in ALL_ROLE_GROUPS}
    profile.user.groups.remove(*groups.values())
    profile.user.groups.add(groups[group_name])
    _ensure_staff_for_platform_role(profile.user)


@receiver(post_save, sender=User)
def ensure_profile(sender, instance: User, created: bool, **kwargs) -> None:
    if created:
        profile = UserProfile.objects.create(user=instance)
        _sync_role_group(profile)
        return
    profile, _ = UserProfile.objects.get_or_create(user=instance)
    _sync_role_group(profile)


@receiver(post_save, sender=UserProfile)
def sync_profile_role_group(sender, instance: UserProfile, **kwargs) -> None:
    _sync_role_group(instance)
