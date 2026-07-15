from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .constants import ALL_ROLE_GROUPS, EXTERNAL_ADMIN_GROUP, ROLE_TO_GROUP
from .models import UserProfile
from .role_group_permissions import ensure_role_group_permissions


def _sync_role_group(profile: UserProfile) -> None:
    group_name = ROLE_TO_GROUP.get(profile.role, ROLE_TO_GROUP["external_admin"])
    groups = {name: Group.objects.get_or_create(name=name)[0] for name in ALL_ROLE_GROUPS}
    # Heal empty groups once (staff login with no model perms shows a blank admin home).
    if groups[EXTERNAL_ADMIN_GROUP].permissions.count() == 0:
        ensure_role_group_permissions()
        groups = {name: Group.objects.get(name=name) for name in ALL_ROLE_GROUPS}
    profile.user.groups.remove(*groups.values())
    profile.user.groups.add(groups[group_name])


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
