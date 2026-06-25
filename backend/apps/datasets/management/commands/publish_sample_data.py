from django.core.management.base import BaseCommand

from apps.datasets.models import Dataset, DatasetFile, Project
from apps.datasets.sample_data_config import SAMPLE_FOLDER_CONFIG
from apps.datasets.seed_constants import RESEARCH_PROJECT_SLUGS


class Command(BaseCommand):
    help = (
        "Mark research projects and sample datasets visible on the public /research and /data pages "
        "(shared_publicly + expose_on_public_api)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--research-only",
            action="store_true",
            help="Only set shared_publicly on research projects; skip dataset/file flags for /data.",
        )

    def handle(self, *args, **options):
        research_only = options["research_only"]
        projects_updated = 0
        datasets_updated = 0
        files_updated = 0

        for slug in sorted(RESEARCH_PROJECT_SLUGS):
            project = Project.objects.filter(slug=slug).first()
            if not project:
                self.stdout.write(self.style.WARNING(f"Skip missing research project: {slug}"))
                continue

            if not project.shared_publicly:
                project.shared_publicly = True
                project.save(update_fields=["shared_publicly"])
                projects_updated += 1

        if research_only:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Published research projects: {projects_updated} projects flagged for /research."
                )
            )
            return

        for config in SAMPLE_FOLDER_CONFIG:
            project = Project.objects.filter(slug=config["project_slug"]).first()
            if not project:
                self.stdout.write(self.style.WARNING(f"Skip missing project: {config['project_slug']}"))
                continue

            dataset = Dataset.objects.filter(project=project, title=config["dataset_title"]).first()
            if not dataset:
                self.stdout.write(self.style.WARNING(f"Skip missing dataset: {config['dataset_title']}"))
                continue

            if not dataset.expose_on_public_api:
                dataset.expose_on_public_api = True
                dataset.save(update_fields=["expose_on_public_api"])
                datasets_updated += 1

            for file_record in dataset.files.all():
                if not file_record.expose_on_public_api:
                    file_record.expose_on_public_api = True
                    file_record.save(update_fields=["expose_on_public_api"])
                    files_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Published sample data: {projects_updated} projects, {datasets_updated} datasets, "
                f"{files_updated} files flagged for the public API."
            )
        )
