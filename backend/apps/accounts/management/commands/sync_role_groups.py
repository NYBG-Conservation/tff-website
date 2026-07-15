from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.constants import ALL_ROLE_GROUPS, ROLE_TO_GROUP
from apps.accounts.models import UserProfile
from apps.accounts.role_group_permissions import ensure_role_group_permissions


class Command(BaseCommand):
    help = (
        "Ensure role groups exist, attach Django admin permissions, "
        "and assign users based on profile.role."
    )

    def handle(self, *args, **options):
        perm_counts = ensure_role_group_permissions()
        groups = {name: Group.objects.get(name=name) for name in ALL_ROLE_GROUPS}

        for profile in UserProfile.objects.select_related("user"):
            group_name = ROLE_TO_GROUP.get(profile.role, ROLE_TO_GROUP["external_admin"])
            profile.user.groups.remove(*groups.values())
            profile.user.groups.add(groups[group_name])

        for name, count in perm_counts.items():
            self.stdout.write(f"  {name}: {count} permissions")

        self.stdout.write(self.style.SUCCESS("Role groups synced (membership + admin permissions)."))
