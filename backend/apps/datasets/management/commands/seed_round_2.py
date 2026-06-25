from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.datasets.models import Dataset, DatasetFile, Project


class Command(BaseCommand):
    help = (
        "Round 2 bootstrap: consolidate duplicate projects, refresh research metadata, "
        "create any missing sample-data projects, and import all tff-sample-data files."
    )

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True, help="Username for dataset ownership and file uploads.")
        parser.add_argument(
            "--skip-cleanup",
            action="store_true",
            help="Skip cleanup_seed_duplicates (not recommended on EC2).",
        )
        parser.add_argument(
            "--skip-research-metadata",
            action="store_true",
            help="Skip seed_sample_projects --update.",
        )
        parser.add_argument(
            "--update-files",
            action="store_true",
            help="Replace file blobs that already exist (passes --update to seed_sample_datasets).",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Flag sample projects/datasets for the public /research and /data pages.",
        )

    def handle(self, *args, **options):
        owner_username = options["owner"]
        User = get_user_model()
        if not User.objects.filter(username=owner_username).exists():
            raise CommandError(f"Owner user '{owner_username}' does not exist.")

        if not options["skip_cleanup"]:
            self.stdout.write(self.style.MIGRATE_HEADING("Step 1/3: Consolidate duplicate projects"))
            call_command("cleanup_seed_duplicates")

        if not options["skip_research_metadata"]:
            self.stdout.write(self.style.MIGRATE_HEADING("Step 2/3: Research project metadata"))
            call_command("seed_sample_projects", owner=owner_username, update=True)

        self.stdout.write(self.style.MIGRATE_HEADING("Step 3/3: Import tff-sample-data"))
        dataset_kwargs = {"owner": owner_username, "create_missing_projects": True}
        if options["update_files"]:
            dataset_kwargs["update"] = True
        call_command("seed_sample_datasets", **dataset_kwargs)

        project_count = Project.objects.count()
        dataset_count = Dataset.objects.count()
        file_count = DatasetFile.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed round 2 complete for '{owner_username}': "
                f"{project_count} projects, {dataset_count} datasets, {file_count} files in database."
            )
        )
        if dataset_count < 6:
            self.stdout.write(
                self.style.WARNING(
                    "Expected 6 sample datasets. If folders were skipped, rebuild Docker on EC2 "
                    "(sample files are copied to /app/sample-data at image build) and re-run."
                )
            )

        if options["publish"]:
            self.stdout.write(self.style.MIGRATE_HEADING("Publishing sample data to public API"))
            call_command("publish_sample_data")
