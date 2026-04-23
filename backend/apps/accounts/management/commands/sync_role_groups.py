from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.constants import EXTERNAL_PARTNER_ADMIN_GROUP, INTERNAL_ADMIN_GROUP
from apps.accounts.models import UserProfile


class Command(BaseCommand):
    help = "Ensure role groups exist and users are assigned based on profile.role."

    def handle(self, *args, **options):
        internal_group, _ = Group.objects.get_or_create(name=INTERNAL_ADMIN_GROUP)
        external_group, _ = Group.objects.get_or_create(name=EXTERNAL_PARTNER_ADMIN_GROUP)

        for profile in UserProfile.objects.select_related("user"):
            profile.user.groups.remove(internal_group, external_group)
            if profile.role == UserProfile.Role.INTERNAL_ADMIN:
                profile.user.groups.add(internal_group)
            else:
                profile.user.groups.add(external_group)

        self.stdout.write(self.style.SUCCESS("Role groups synced."))
