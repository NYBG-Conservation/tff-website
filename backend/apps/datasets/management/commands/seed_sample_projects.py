from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.datasets.models import Project
from apps.organizations.models import Organization

SAMPLE_PROJECTS = [
    {
        "short_title": "Annual Christmas bird count",
        "nybg_pi_name": "John",
        "contact_email": "john@nybg.org",
        "shared_publicly": True,
        "lead_institution_name": "NYC Bird Alliance",
        "collection_frequency": "annual",
        "update_frequency": "annual",
        "last_updated_note": "Data from 2024 and (expected) 2025",
    },
    {
        "short_title": "Forest soil cores",
        "nybg_pi_name": "Brad",
        "contact_email": "brad@nybg.org",
        "shared_publicly": True,
        "lead_institution_name": "NYBG",
        "external_url": "https://www.uvm.edu/femc/project-enhanced-ecosystem-monitoring-new-york-citys-only-old-growth-forest-overview",
        "institutional_partners": ["Forest Ecosystem Monitoring Cooperative"],
        "collection_frequency": "onetime",
        "update_frequency": "onetime",
    },
    {
        "short_title": "Forest Lidar dataset",
        "nybg_pi_name": "Brad",
        "contact_email": "brad@nybg.org",
        "shared_publicly": True,
        "collection_frequency": "onetime",
        "update_frequency": "onetime",
    },
    {
        "short_title": "Biodiversity monitoring data",
        "nybg_pi_name": "Eve",
        "contact_email": "eve@nybg.org",
        "ongoing": True,
        "lead_institution_name": "NYBG",
        "collection_frequency": "tbd",
        "update_frequency": "monthly",
    },
    {
        "short_title": "Continuous Forest Inventory Data",
        "nybg_pi_name": "John",
        "contact_email": "john@nybg.org",
        "ongoing": True,
        "lead_institution_name": "NYBG",
        "collection_frequency": "Every 5 years",
        "update_frequency": "Every 5 years",
    },
    {
        "short_title": "Stream gage (continuous)",
        "nybg_pi_name": "John",
        "contact_email": "john@nybg.org",
        "ongoing": True,
        "lead_institution_name": "USGS",
        "external_url": "https://waterdata.usgs.gov/monitoring-location/01302020/",
        "update_frequency": "as needed",
    },
]


class Command(BaseCommand):
    help = "Seed sample Thain Family Forest project records from planning CSV."

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True, help="Username to assign as seeded project owner.")

    def handle(self, *args, **options):
        owner_username = options["owner"]
        User = get_user_model()
        owner = User.objects.filter(username=owner_username).first()
        if not owner:
            raise CommandError(f"Owner user '{owner_username}' does not exist.")

        nybg, _ = Organization.objects.get_or_create(name="New York Botanical Garden")
        created = 0
        for source_payload in SAMPLE_PROJECTS:
            payload = dict(source_payload)
            institution_name = payload.pop("lead_institution_name", "")
            lead_institution = None
            if institution_name:
                lead_institution, _ = Organization.objects.get_or_create(name=institution_name)
            _, was_created = Project.objects.get_or_create(
                short_title=payload["short_title"],
                defaults={
                    **payload,
                    "organization": nybg,
                    "owner": owner,
                    "lead_institution": lead_institution,
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new projects for owner '{owner_username}'"))
