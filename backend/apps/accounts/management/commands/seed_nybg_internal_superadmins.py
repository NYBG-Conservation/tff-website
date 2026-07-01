from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.constants import INTERNAL_SUPERADMIN_GROUP
from apps.accounts.models import UserProfile
from apps.accounts.nybg_staff import NYBG_INTERNAL_SUPERADMINS

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Create or update NYBG internal_superadmin accounts for core platform owners. "
        "New users get an unusable password — run changepassword before first login."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Refresh name and email fields for accounts that already exist.",
        )

    def handle(self, *args, **options):
        update = options["update"]
        created_count = 0
        promoted_count = 0
        updated_count = 0

        Group.objects.get_or_create(name=INTERNAL_SUPERADMIN_GROUP)

        for entry in NYBG_INTERNAL_SUPERADMINS:
            username = entry["email"].split("@", 1)[0]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": entry["email"],
                    "first_name": entry["first_name"],
                    "last_name": entry["last_name"],
                    "is_staff": True,
                    "is_superuser": True,
                },
            )

            if created:
                user.set_unusable_password()
                user.save()
                created_count += 1
                self.stdout.write(f"Created user '{username}' ({entry['email']}).")
            else:
                user_fields: list[str] = []
                if not user.is_staff:
                    user.is_staff = True
                    user_fields.append("is_staff")
                if not user.is_superuser:
                    user.is_superuser = True
                    user_fields.append("is_superuser")
                if update:
                    user.email = entry["email"]
                    user.first_name = entry["first_name"]
                    user.last_name = entry["last_name"]
                    user_fields.extend(["email", "first_name", "last_name"])
                if user_fields:
                    user.save(update_fields=user_fields)
                    updated_count += 1
                    self.stdout.write(f"Updated user '{username}'.")

            profile = user.profile
            profile_changed = False
            if profile.role != UserProfile.Role.INTERNAL_SUPERADMIN:
                profile.role = UserProfile.Role.INTERNAL_SUPERADMIN
                profile_changed = True
                promoted_count += 1
            if profile.organization_id is not None:
                profile.organization = None
                profile_changed = True
            if profile_changed:
                profile.save(update_fields=["role", "organization"])
                self.stdout.write(f"Set '{username}' to internal_superadmin.")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. created={created_count}, promoted={promoted_count}, "
                f"profile_fields_updated={updated_count}."
            )
        )
        if created_count:
            self.stdout.write(
                "Set passwords with: python backend/manage.py changepassword <username>"
            )
