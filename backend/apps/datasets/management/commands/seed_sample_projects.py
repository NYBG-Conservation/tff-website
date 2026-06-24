from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.datasets.models import Project
from apps.datasets.seed_utils import consolidate_projects_for_slug
from apps.organizations.models import Organization

# Research projects aligned with legacy /research copy and researchProjects.ts.
# Intro paragraph for the research page lives in the frontend — not stored as a Project row.
SAMPLE_PROJECTS = [
    {
        "short_title": "CFI",
        "full_title": "New York Botanical Garden Forest Inventory Transect Study",
        "slug": "forest-inventory-transect-study",
        "lead_name": "NYBG Forest staff",
        "lead_email": "john@nybg.org",
        "organization_name": "New York Botanical Garden",
        "shared_publicly": False,
        "summary": "Long-running transect sampling of trees, shrubs, and herbaceous cover across the forest.",
        "description": (
            "Since 2001, Garden staff have been sampling fourteen, 10-meter wide transects across the Forest "
            "from the western boundary to the Bronx River. The data collected includes all trees and shrubs that "
            "are 1 cm or greater in diameter at breast height (DBH at 4.5 feet) and herbaceous plants and tree "
            "seedling percent cover.\n\n"
            "The data collected from this study are used to monitor how the Forest is changing, to track invasive "
            "plant management, and to help prioritize ongoing restoration work such as native plant restoration. "
            "The results of the 2011 survey has shown that the Amur honeysuckle and Amur corktree management has "
            "been successful in removing the largest specimens but, there are still small Amur corktree present in "
            "the Forest. The biggest focus of management recently was derived from these data, the Japanese angelica "
            "tree is currently on the rise and the Forest staff is focusing management efforts on this species."
        ),
        "hero_image": "/images/home/forest-trail.png",
        "ongoing": True,
        "collection_frequency": "periodic",
        "update_frequency": "periodic",
    },
    {
        "short_title": "Filling in the Gaps: Plant Establishment After Hurricane Sandy",
        "slug": "filling-in-the-gaps",
        "lead_name": "NYBG Forest staff",
        "lead_email": "john@nybg.org",
        "organization_name": "New York Botanical Garden",
        "shared_publicly": False,
        "summary": "Post-disturbance canopy gap study following Hurricane Sandy.",
        "description": (
            "On October 29, 2012, Hurricane Sandy caused tremendous damage to the structure of the Forest by "
            "uprooting or destroying 167 trees that were 6 inches in diameter at breast height or greater, and "
            "creating canopy gaps. While hurricanes and nor'easters have always been part of our region's natural "
            "disturbance regime and have played a major role in shaping the Forest as we know it today, Hurricane "
            "Sandy was the most damaging storm in the recorded history of the Garden landscape.\n\n"
            "The purpose of this study is to assess the newly formed canopy gaps created by Hurricane Sandy, the "
            "reestablishment of plant species after the disturbance, and to guide forest management in these newly "
            "disturbed areas. In this project, we assess the abundance and distribution of first year tree and "
            "herbaceous seedling species in 10 newly formed canopy gaps. 1 m2 plots were placed within the canopy "
            "gaps and intact forest along a 10 m transect north and south of the center of the canopy gap."
        ),
        "hero_image": "/images/home/forest-group.png",
        "ongoing": True,
        "collection_frequency": "periodic",
        "update_frequency": "periodic",
    },
    {
        "short_title": "Long-term Redback Salamander Monitoring",
        "slug": "redback-salamander-monitoring",
        "lead_name": "NYBG Forest staff",
        "lead_email": "eve@nybg.org",
        "organization_name": "New York Botanical Garden",
        "shared_publicly": False,
        "summary": "Indicator species monitoring for forest health in urban northeastern deciduous forest.",
        "description": (
            "The eastern redback salamander (Plethodon cinereus) can act as an indicator of forest health in "
            "northeastern deciduous forests. In 2010, a long-term monitoring study was established in the Thain "
            "Family Forest to document the abundance and distribution of eastern redback salamanders throughout the "
            "Forest. See a blog post featuring a short video documentary focusing on the salamander study on the "
            "NYBG blog, Plant Talk."
        ),
        "hero_image": "/images/home/forest-canopy.png",
        "ongoing": True,
        "start_date": "2010-01-01",
        "collection_frequency": "annual",
        "update_frequency": "annual",
    },
    {
        "short_title": "Citizen Science Phenology Monitoring",
        "slug": "citizen-science-phenology-monitoring",
        "lead_name": "NYBG Forest staff",
        "lead_email": "john@nybg.org",
        "organization_name": "New York Botanical Garden",
        "shared_publicly": False,
        "summary": "Volunteer-supported phenology observations to track climate-related seasonal changes.",
        "description": (
            "To study the impacts of climate change on the Thain Family Forest, the Garden engages volunteers in "
            "collecting important scientific data on specific species of trees. With training by experts, these "
            "citizen scientists learn about eight native tree species and how to collect and input data on the "
            "seasonal biological processes of those species in the Forest such as when leaves, flowers, and fruits "
            "appear (a science known as phenology).\n\n"
            "Working with partners at the National Phenology Network, New York Phenology Project, and the Northeast "
            "Regional Phenology Network, the Garden has tailored its program to match the needs of scientists who "
            "use the collected data to study various aspects of climate change. Equally important, the program allows "
            "participants to learn about and actively engage in plant biology, forest ecology, and similar sciences "
            "as well as gain an intimate knowledge of the beautiful Thain Family Forest.\n\n"
            "If you would like to participate as a citizen scientist, please contact Volunteer Services."
        ),
        "hero_image": "/images/home/forest-trail.png",
        "ongoing": True,
        "institutional_partners": [
            "National Phenology Network",
            "New York Phenology Project",
            "Northeast Regional Phenology Network",
        ],
        "collection_frequency": "seasonal",
        "update_frequency": "seasonal",
    },
    {
        "short_title": "Knotweed Management Study",
        "slug": "knotweed-management-study",
        "lead_name": "NYBG Staff",
        "lead_email": "john@nybg.org",
        "organization_name": "Bronx River Alliance",
        "shared_publicly": False,
        "summary": "Collaborative invasive species management trial for Japanese knotweed control.",
        "description": (
            "This study is in partnership with the Bronx River Alliance, the Natural Resources Group of the "
            "Department of Parks and Recreation, and Columbia University to help determine best management practices "
            "for controlling knotweed both Japanese knotweed and the hybrid knotweed (Reynoutria x bohemica). "
            "The project management techniques include cutting the knotweed back three times a year or cutting the "
            "knotweed once and removing the Japanese knotweed rhizomes two times a year.\n\n"
            "The data we are collecting will document the impacts of this management on plant species diversity, "
            "plant species percent cover, restoration tree establishment, and Japanese knotweed height and stem count. "
            "This project was supported by a grant from WCS-NOAA Regional Partnership Grants (2009 to 2011). "
            "Project is ongoing 2009 to present."
        ),
        "hero_image": "/images/home/forest-group.png",
        "ongoing": True,
        "institutional_partners": [
            "Bronx River Alliance",
            "NYC Parks Natural Resources Group",
            "Columbia University",
        ],
        "start_date": "2009-01-01",
        "collection_frequency": "annual",
        "update_frequency": "annual",
    },
    {
        "short_title": "Macroinvertebrate Monitoring",
        "slug": "macroinvertebrate-monitoring",
        "lead_name": "NYBG Forest staff",
        "lead_email": "john@nybg.org",
        "organization_name": "Bronx River Alliance",
        "shared_publicly": False,
        "summary": "Community science stream biodiversity and water quality monitoring.",
        "description": (
            "Freshwater streams are one the most biologically diverse ecosystems on earth. They share interdependence "
            "with forests, outflow into larger bodies of water, and are greatly impacted by overuse, pollution, and "
            "urbanization. This project involves student including visiting school groups and Citizen Science monitoring "
            "of benthic macroinvertebrates (small animals living among sediments and stones on the bottom of rivers, "
            "lakes, and streams. Insects comprise of the largest diversity of these organisms) whose diversity are "
            "indicators of water quality of the Forest stream along the Sweet Gum Trail and the Bronx River.\n\n"
            "Using the Stroud Leaf Pack Network protocols, kick netting, and the Bronx River Alliance's water quality "
            "monitoring protocols, students, and Citizen Scientists collect data on the biodiversity and water quality "
            "of the stream. These data document the health and interdependence of the Forest stream and Bronx River "
            "ecosystem. This project is in partnership with Garden volunteers and the Bronx River Alliance, and was "
            "supported by the WCS-NOAA Regional Partnership Grants (2011-2013). Project is ongoing 2010 to present.\n\n"
            "If you would like to participate as a citizen scientist, please contact Volunteer Services.\n\n"
            "If you would like to participate in a teacher professional development workshop or have your school "
            "participate in this project, please contact Children's Education."
        ),
        "hero_image": "/images/home/forest-canopy.png",
        "ongoing": True,
        "institutional_partners": ["Bronx River Alliance"],
        "start_date": "2010-01-01",
        "collection_frequency": "seasonal",
        "update_frequency": "seasonal",
    },
]


class Command(BaseCommand):
    help = "Seed Thain Family Forest research project metadata (legacy /research copy)."

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True, help="Username to assign as seeded project owner.")
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update summary, description, and other metadata on existing projects (matched by slug).",
        )

    def handle(self, *args, **options):
        owner_username = options["owner"]
        update = options["update"]
        User = get_user_model()
        owner = User.objects.filter(username=owner_username).first()
        if not owner:
            raise CommandError(f"Owner user '{owner_username}' does not exist.")

        created = 0
        updated = 0
        consolidated = 0

        for source_payload in SAMPLE_PROJECTS:
            payload = dict(source_payload)
            slug = payload.pop("slug", None)
            org_name = payload.pop("organization_name", "New York Botanical Garden")
            organization, _ = Organization.objects.get_or_create(name=org_name)
            if not slug:
                raise CommandError(f"Project '{payload['short_title']}' is missing a slug.")

            defaults = {**payload, "organization": organization, "owner": owner, "slug": slug}
            keeper, _, deleted = consolidate_projects_for_slug(slug)
            if deleted:
                consolidated += deleted

            if keeper:
                if update:
                    for field, value in defaults.items():
                        setattr(keeper, field, value)
                    keeper.save()
                    updated += 1
                continue

            Project.objects.create(**defaults)
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created} new projects, updated {updated} existing, "
                f"removed {consolidated} duplicates for owner '{owner_username}'"
            )
        )
