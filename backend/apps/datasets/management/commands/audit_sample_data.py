from django.core.management.base import BaseCommand

from apps.datasets.models import Dataset, DatasetFile, Project
from apps.datasets.sample_data_config import SAMPLE_FOLDER_CONFIG
from apps.datasets.sample_data_paths import resolve_sample_data_root
from apps.datasets.seed_constants import RESEARCH_PROJECT_SLUGS


class Command(BaseCommand):
    help = "Compare tff-sample-data on disk to datasets/files in the database."

    def handle(self, *args, **options):
        sample_root = resolve_sample_data_root()
        if not sample_root:
            self.stdout.write(self.style.ERROR("Sample data directory not found."))
            return

        missing_files = []
        missing_datasets = []
        db_extra_files = []

        for config in SAMPLE_FOLDER_CONFIG:
            folder_path = sample_root / config["folder"]
            project = Project.objects.filter(slug=config["project_slug"]).first()
            dataset = (
                Dataset.objects.filter(project=project, title=config["dataset_title"]).first()
                if project
                else None
            )

            self.stdout.write(self.style.MIGRATE_HEADING(f"{config['folder']} → {config['project_slug']}"))
            if not project:
                self.stdout.write(self.style.WARNING("  Project missing in database"))
            if not dataset:
                self.stdout.write(self.style.WARNING("  Dataset missing in database"))
                missing_datasets.append(config["dataset_title"])
                continue

            if not folder_path.is_dir():
                self.stdout.write(self.style.ERROR(f"  Folder missing on disk: {folder_path}"))
                continue

            disk_files = sorted(
                path.name for path in folder_path.iterdir() if path.is_file() and not path.name.startswith(".")
            )
            db_files = set(dataset.files.values_list("file_name", flat=True))
            for file_name in disk_files:
                if file_name not in db_files:
                    missing_files.append(f"{config['folder']}/{file_name}")
                    self.stdout.write(self.style.WARNING(f"  NOT IN DB: {file_name}"))
                else:
                    self.stdout.write(f"  ok: {file_name}")

            for file_name in sorted(db_files - set(disk_files)):
                db_extra_files.append(f"{config['folder']}/{file_name}")

        self.stdout.write("")
        self.stdout.write(
            f"Totals: {DatasetFile.objects.count()} files in DB "
            f"(expect 18 from tff-sample-data), {Dataset.objects.count()} datasets (expect 6)."
        )

        sample_slugs = {config["project_slug"] for config in SAMPLE_FOLDER_CONFIG}
        research_without_files = sorted(RESEARCH_PROJECT_SLUGS - sample_slugs)
        if research_without_files:
            self.stdout.write("")
            self.stdout.write(
                "Research projects with NO files in tff-sample-data (metadata only until files are added):"
            )
            for slug in research_without_files:
                self.stdout.write(f"  - {slug}")

        data_only = [config["project_slug"] for config in SAMPLE_FOLDER_CONFIG if not config.get("on_research_page")]
        if data_only:
            self.stdout.write("")
            self.stdout.write("Sample-data projects on /data only (not on /research unless you add them):")
            for slug in data_only:
                self.stdout.write(f"  - {slug}")

        public_datasets = Dataset.objects.filter(expose_on_public_api=True).count()
        if public_datasets == 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "No datasets have expose_on_public_api=True — run publish_sample_data for the public portal."
                )
            )

        if missing_files or missing_datasets:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("Run: python backend/manage.py seed_round_2 --owner <user>"))
