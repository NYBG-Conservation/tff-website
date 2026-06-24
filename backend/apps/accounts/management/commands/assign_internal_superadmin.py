from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Bootstrap the first internal superadmin (run once after deploy)."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Username to promote to internal_superadmin.")

    def handle(self, *args, **options):
        username = options["username"]
        user = User.objects.filter(username=username).first()
        if not user:
            raise CommandError(f"User '{username}' does not exist.")

        profile = user.profile
        profile.role = UserProfile.Role.INTERNAL_SUPERADMIN
        profile.organization = None
        profile.save(update_fields=["role", "organization"])
        self.stdout.write(self.style.SUCCESS(f"Promoted '{username}' to internal_superadmin."))
