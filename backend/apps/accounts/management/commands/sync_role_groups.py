from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.constants import ALL_ROLE_GROUPS, ROLE_TO_GROUP
from apps.accounts.models import UserProfile


class Command(BaseCommand):
    help = "Ensure role groups exist and users are assigned based on profile.role."

    def handle(self, *args, **options):
        groups = {name: Group.objects.get_or_create(name=name)[0] for name in ALL_ROLE_GROUPS}

        for profile in UserProfile.objects.select_related("user"):
            group_name = ROLE_TO_GROUP.get(profile.role, ROLE_TO_GROUP["external_admin"])
            profile.user.groups.remove(*groups.values())
            profile.user.groups.add(groups[group_name])

        self.stdout.write(self.style.SUCCESS("Role groups synced."))
