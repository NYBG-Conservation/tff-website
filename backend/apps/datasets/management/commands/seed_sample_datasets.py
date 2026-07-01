import mimetypes
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from apps.datasets.models import Dataset, DatasetFile, Project
from apps.datasets.sample_data_config import SAMPLE_FOLDER_CONFIG
from apps.datasets.sample_data_paths import resolve_sample_data_root
from apps.datasets.seed_utils import find_project_by_canonical_slug
from apps.organizations.models import Organization

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
    help = "Link tff-sample-data files to projects by slug (idempotent; does not create projects by default)."

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True, help="Username assigned as dataset owner and file uploader.")
        parser.add_argument(
            "--create-missing-projects",
            action="store_true",
            help="Create minimal project rows when the canonical slug is missing (off by default).",
        )
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
        create_missing_projects = options["create_missing_projects"]
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

            project = find_project_by_canonical_slug(config["project_slug"])
            if not project:
                if not create_missing_projects:
                    skipped_folders.append(
                        f"{folder_name} (no project '{config['project_slug']}' — run seed_sample_projects or cleanup_seed_duplicates)"
                    )
                    continue
                project, was_created = Project.objects.get_or_create(
                    slug=config["project_slug"],
                    defaults={
                        "short_title": config["project_title"],
                        "full_title": config.get("project_full_title", ""),
                        "lead_name": "NYBG Forest staff",
                        "lead_email": "jzeiger@nybg.org",
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
            elif dataset.project_slug != project.slug:
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
