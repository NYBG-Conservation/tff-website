import mimetypes
import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from apps.datasets.models import Dataset, DatasetFile, Project
from apps.organizations.models import Organization

# Repo root: .../backend/apps/datasets/management/commands/this_file.py -> parents[5]
_REPO_ROOT = Path(__file__).resolve().parents[5]
def resolve_sample_data_root() -> Path | None:
    candidates: list[Path] = []
    env_dir = os.environ.get("TFF_SAMPLE_DATA_DIR", "").strip()
    if env_dir:
        candidates.append(Path(env_dir))
    candidates.extend((_REPO_ROOT / "src/lib/data/tff-sample-data", Path("/app/sample-data")))
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


# Maps each folder under tff-sample-data to a project slug. When the project already
# exists (e.g. from seed_sample_projects), datasets and files are linked to it.
SAMPLE_FOLDER_CONFIG = [
    {
        "folder": "knotweed",
        "project_slug": "knotweed-management-study",
        "project_title": "Knotweed Management Study",
        "dataset_title": "Knotweed Treatment Plot Outcomes",
        "dataset_description": "Plot-level knotweed treatment outcomes and related documentation.",
        "cadence": Dataset.Cadence.ANNUAL,
        "data_type": Dataset.DataType.TABULAR,
        "require_existing_project": True,
    },
    {
        "folder": "CFI",
        "project_slug": "forest-inventory-transect-study",
        "project_title": "CFI",
        "project_full_title": "New York Botanical Garden Forest Inventory Transect Study",
        "dataset_title": "Continuous Forest Inventory — Field Data & Manual",
        "dataset_description": "Overstory and understory inventory spreadsheets and field manual.",
        "cadence": Dataset.Cadence.ANNUAL,
        "data_type": Dataset.DataType.TABULAR,
        "require_existing_project": True,
    },
    {
        "folder": "breeding bird census",
        "project_slug": "breeding-bird-census",
        "project_title": "Annual Breeding Bird Census",
        "dataset_title": "NYBG Breeding Bird Census Data",
        "dataset_description": "Breeding bird census data, handbook, and presentation materials.",
        "cadence": Dataset.Cadence.ANNUAL,
        "data_type": Dataset.DataType.BIODIVERSITY_OBSERVATION,
        "require_existing_project": False,
    },
    {
        "folder": "acorn planting",
        "project_slug": "acorn-planting",
        "project_title": "Acorn Planting — Ten Tallest Method",
        "dataset_title": "Ten Tallest Plot Data",
        "dataset_description": "Ten-tallest plot data and method instructions.",
        "cadence": Dataset.Cadence.ANNUAL,
        "data_type": Dataset.DataType.TABULAR,
        "require_existing_project": False,
    },
    {
        "folder": "million tree plot",
        "project_slug": "million-tree-plot",
        "project_title": "Million Tree Plot Monitoring",
        "dataset_title": "Million Tree Plot — Plot 101-1",
        "dataset_description": "MillionTreesNYC reforestation plot data and related publications.",
        "cadence": Dataset.Cadence.ONE_OFF,
        "data_type": Dataset.DataType.TABULAR,
        "require_existing_project": False,
    },
    {
        "folder": "soil monitoring",
        "project_slug": "soil-monitoring",
        "project_title": "Forest Soil Monitoring",
        "dataset_title": "Forest Soil Sampling & FEMC Analysis",
        "dataset_description": "Soil sampling plots, FEMC nutrient analysis, and proposal documents.",
        "cadence": Dataset.Cadence.ANNUAL,
        "data_type": Dataset.DataType.TABULAR,
        "require_existing_project": False,
    },
]

_TABULAR_EXTENSIONS = {".xlsx", ".xls", ".csv"}
_DOCUMENTATION_EXTENSIONS = {".pdf", ".pptx", ".ppt", ".doc", ".docx"}


def infer_file_kind(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension in _TABULAR_EXTENSIONS:
        return DatasetFile.FileKind.PRIMARY_DATA
    if extension in _DOCUMENTATION_EXTENSIONS:
        return DatasetFile.FileKind.DOCUMENTATION
    return DatasetFile.FileKind.OTHER


class Command(BaseCommand):
    help = "Import files from src/lib/data/tff-sample-data into datasets, linking to existing projects by slug."

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True, help="Username assigned as dataset owner and file uploader.")
        parser.add_argument(
            "--update",
            action="store_true",
            help="Replace file blobs when a matching dataset file name already exists.",
        )
        parser.add_argument(
            "--folder",
            action="append",
            dest="folders",
            help="Import only this sample folder (repeatable). Default: all configured folders.",
        )

    def handle(self, *args, **options):
        owner_username = options["owner"]
        update = options["update"]
        folder_filter = set(options["folders"] or [])

        User = get_user_model()
        owner = User.objects.filter(username=owner_username).first()
        if not owner:
            raise CommandError(f"Owner user '{owner_username}' does not exist.")

        sample_root = resolve_sample_data_root()
        if not sample_root:
            raise CommandError(
                "Sample data directory not found. Expected src/lib/data/tff-sample-data in the repo "
                "or /app/sample-data in Docker."
            )

        nybg, _ = Organization.objects.get_or_create(name="New York Botanical Garden")
        projects_linked = 0
        projects_created = 0
        datasets_created = 0
        files_added = 0
        files_updated = 0
        skipped_folders = []

        for config in SAMPLE_FOLDER_CONFIG:
            folder_name = config["folder"]
            if folder_filter and folder_name not in folder_filter:
                continue

            folder_path = sample_root / folder_name
            if not folder_path.is_dir():
                skipped_folders.append(f"{folder_name} (missing directory)")
                continue

            project = Project.objects.filter(slug=config["project_slug"]).first()
            if not project:
                if config["require_existing_project"]:
                    skipped_folders.append(
                        f"{folder_name} (project '{config['project_slug']}' not found — run seed_sample_projects first)"
                    )
                    continue
                project, was_created = Project.objects.get_or_create(
                    slug=config["project_slug"],
                    defaults={
                        "short_title": config["project_title"],
                        "full_title": config.get("project_full_title", ""),
                        "lead_name": "NYBG Forest staff",
                        "lead_email": "john@nybg.org",
                        "organization": nybg,
                        "owner": owner,
                        "shared_publicly": False,
                        "ongoing": True,
                    },
                )
                if was_created:
                    projects_created += 1
            else:
                projects_linked += 1

            dataset, dataset_was_created = Dataset.objects.get_or_create(
                title=config["dataset_title"],
                project=project,
                defaults={
                    "description": config["dataset_description"],
                    "cadence": config["cadence"],
                    "status": Dataset.Status.ACTIVE,
                    "data_type": config["data_type"],
                    "project_slug": project.slug,
                    "expose_on_public_api": False,
                    "owner": owner,
                    "organization": nybg,
                },
            )
            if dataset_was_created:
                datasets_created += 1
            elif not dataset.project_slug:
                dataset.project_slug = project.slug
                dataset.save(update_fields=["project_slug"])

            for file_path in sorted(folder_path.iterdir()):
                if not file_path.is_file() or file_path.name.startswith("."):
                    continue

                file_name = file_path.name
                content_type = mimetypes.guess_type(file_name)[0] or ""
                file_kind = infer_file_kind(file_name)
                existing = DatasetFile.objects.filter(dataset=dataset, file_name=file_name).first()

                if existing and not update:
                    continue

                if existing and update:
                    if existing.file:
                        existing.file.delete(save=False)
                    with file_path.open("rb") as handle:
                        existing.file.save(file_name, File(handle), save=False)
                    existing.file_kind = file_kind
                    existing.content_type = content_type
                    existing.uploaded_by = owner
                    existing.save()
                    files_updated += 1
                    continue

                dataset_file = DatasetFile(
                    dataset=dataset,
                    file_name=file_name,
                    file_kind=file_kind,
                    content_type=content_type,
                    uploaded_by=owner,
                    expose_on_public_api=False,
                )
                with file_path.open("rb") as handle:
                    dataset_file.file.save(file_name, File(handle), save=True)
                files_added += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sample data import complete for '{owner_username}': "
                f"{projects_created} projects created, {projects_linked} existing projects linked, "
                f"{datasets_created} datasets created, {files_added} files added, {files_updated} files updated."
            )
        )
        if skipped_folders:
            self.stdout.write(self.style.WARNING("Skipped: " + "; ".join(skipped_folders)))
