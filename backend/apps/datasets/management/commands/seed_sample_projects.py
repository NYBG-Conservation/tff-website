from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.datasets.models import Dataset, Project
from apps.organizations.models import Organization

SAMPLE_PROJECTS = [
    {
        "short_title": "Knotweed Management Study",
        "slug": "knotweed-management-study",
        "lead_name": "NYBG Staff",
        "lead_email": "john@nybg.org",
        "organization_name": "Bronx River Alliance",
        "shared_publicly": True,
        "summary": "Collaborative invasive species management trial for Japanese knotweed control.",
        "description": (
            "This study is a partnership with the Bronx River Alliance, NYC Parks, and Columbia University "
            "to determine best management practices for controlling Japanese knotweed.\n\n"
            "Management techniques include cutting knotweed back three times per year, or cutting once and "
            "removing rhizomes twice per year."
        ),
        "hero_image": "/images/home/forest-group.png",
        "collection_frequency": "annual",
        "update_frequency": "annual",
        "last_updated_note": "Data from 2024 and (expected) 2025",
    },
    {
        "short_title": "Annual Christmas bird count",
        "lead_name": "John",
        "lead_email": "john@nybg.org",
        "organization_name": "NYC Bird Alliance",
        "shared_publicly": True,
        "collection_frequency": "annual",
        "update_frequency": "annual",
        "last_updated_note": "Data from 2024 and (expected) 2025",
    },
    {
        "short_title": "Forest soil cores",
        "lead_name": "Brad",
        "lead_email": "brad@nybg.org",
        "organization_name": "NYBG",
        "shared_publicly": True,
        "external_url": "https://www.uvm.edu/femc/project-enhanced-ecosystem-monitoring-new-york-citys-only-old-growth-forest-overview",
        "institutional_partners": ["Forest Ecosystem Monitoring Cooperative"],
        "collection_frequency": "onetime",
        "update_frequency": "onetime",
    },
    {
        "short_title": "Forest Lidar dataset",
        "lead_name": "Brad",
        "lead_email": "brad@nybg.org",
        "organization_name": "New York Botanical Garden",
        "shared_publicly": True,
        "collection_frequency": "onetime",
        "update_frequency": "onetime",
    },
    {
        "short_title": "Biodiversity monitoring data",
        "lead_name": "Eve",
        "lead_email": "eve@nybg.org",
        "ongoing": True,
        "organization_name": "New York Botanical Garden",
        "collection_frequency": "tbd",
        "update_frequency": "monthly",
    },
    {
        "short_title": "Continuous Forest Inventory Data",
        "lead_name": "John",
        "lead_email": "john@nybg.org",
        "ongoing": True,
        "organization_name": "New York Botanical Garden",
        "collection_frequency": "Every 5 years",
        "update_frequency": "Every 5 years",
    },
    {
        "short_title": "Stream gage (continuous)",
        "lead_name": "John",
        "lead_email": "john@nybg.org",
        "ongoing": True,
        "organization_name": "USGS",
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
        knotweed_project = None
        for source_payload in SAMPLE_PROJECTS:
            payload = dict(source_payload)
            slug = payload.pop("slug", None)
            org_name = payload.pop("organization_name", "New York Botanical Garden")
            organization, _ = Organization.objects.get_or_create(name=org_name)
            lookup = {"slug": slug} if slug else {"short_title": payload["short_title"]}
            project, was_created = Project.objects.get_or_create(
                **lookup,
                defaults={
                    **payload,
                    "organization": organization,
                    "owner": owner,
                },
            )
            if slug and not project.slug:
                project.slug = slug
                project.save(update_fields=["slug"])
            if payload["short_title"] == "Knotweed Management Study":
                knotweed_project = project
            if was_created:
                created += 1

        if knotweed_project:
            Dataset.objects.get_or_create(
                title="Knotweed Treatment Plot Outcomes",
                project=knotweed_project,
                defaults={
                    "description": "Plot-level knotweed treatment outcomes.",
                    "cadence": Dataset.Cadence.ANNUAL,
                    "status": Dataset.Status.ACTIVE,
                    "data_type": Dataset.DataType.TABULAR,
                    "project_slug": knotweed_project.slug,
                    "expose_on_public_api": True,
                    "owner": owner,
                    "organization": nybg,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new projects for owner '{owner_username}'"))
