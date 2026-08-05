from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.constants import ALL_ROLE_GROUPS, LEGACY_ROLE_GROUPS_TO_DELETE, ROLE_TO_GROUP
from apps.accounts.models import UserProfile
from apps.accounts.role_group_permissions import ensure_role_group_permissions


class Command(BaseCommand):
    help = (
        "Ensure role groups exist, attach Django admin permissions (full reset), "
        "assign users based on profile.role, and remove legacy groups. "
        "Note: this overwrites Group permission checkboxes in admin; "
        "routine user/profile saves no longer do that."
    )

    def handle(self, *args, **options):
        deleted = 0
        for name in LEGACY_ROLE_GROUPS_TO_DELETE:
            qs = Group.objects.filter(name=name)
            count = qs.count()
            if count:
                qs.delete()
                deleted += count
                self.stdout.write(f"Deleted legacy group '{name}'.")

        perm_counts = ensure_role_group_permissions()
        groups = {name: Group.objects.get(name=name) for name in ALL_ROLE_GROUPS}

        for profile in UserProfile.objects.select_related("user"):
            group_name = ROLE_TO_GROUP.get(profile.role, ROLE_TO_GROUP["external_admin"])
            profile.user.groups.remove(*groups.values())
            profile.user.groups.add(groups[group_name])

        for name, count in perm_counts.items():
            self.stdout.write(f"  {name}: {count} permissions")

        if deleted:
            self.stdout.write(f"Removed {deleted} legacy group(s).")
        self.stdout.write(self.style.SUCCESS("Role groups synced (membership + admin permissions)."))
