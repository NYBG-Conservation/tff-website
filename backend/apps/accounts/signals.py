from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .constants import EXTERNAL_PARTNER_ADMIN_GROUP, INTERNAL_ADMIN_GROUP
from .models import UserProfile


def _sync_role_group(profile: UserProfile) -> None:
    internal_group, _ = Group.objects.get_or_create(name=INTERNAL_ADMIN_GROUP)
    external_group, _ = Group.objects.get_or_create(name=EXTERNAL_PARTNER_ADMIN_GROUP)
    profile.user.groups.remove(internal_group, external_group)
    if profile.role == UserProfile.Role.INTERNAL_ADMIN:
        profile.user.groups.add(internal_group)
    else:
        profile.user.groups.add(external_group)


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
