from django.core.management.base import BaseCommand
from django.db import transaction

from apps.datasets.models import Project
from apps.datasets.seed_constants import CANONICAL_PROJECT_SLUGS
from apps.datasets.seed_utils import canonical_slug_for, consolidate_projects_for_slug


class Command(BaseCommand):
    help = "Remove duplicate seed projects and move datasets/files onto canonical project slugs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print actions without changing the database.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no database changes will be made."))
            grouped: dict[str, list[str]] = {}
            for project in Project.objects.order_by("id"):
                canonical = canonical_slug_for(project.slug)
                if canonical:
                    grouped.setdefault(canonical, []).append(project.slug)
            for canonical, slugs in sorted(grouped.items()):
                if len(slugs) > 1 or slugs[0] != canonical:
                    self.stdout.write(f"  {canonical}: would consolidate {slugs}")
            orphan = [
                project.slug
                for project in Project.objects.all()
                if not canonical_slug_for(project.slug) and not project.datasets.exists()
            ]
            if orphan:
                self.stdout.write(f"  would delete orphan slugs: {orphan}")
            return

        renamed = 0
        merged_datasets = 0
        deleted_projects = 0

        for canonical in sorted(CANONICAL_PROJECT_SLUGS):
            keeper, moved, deleted = consolidate_projects_for_slug(canonical)
            if keeper and keeper.slug == canonical:
                renamed += 1
            merged_datasets += moved
            deleted_projects += deleted

        orphan_deleted = 0
        for project in list(Project.objects.order_by("id")):
            if canonical_slug_for(project.slug):
                continue
            if project.datasets.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Leaving non-canonical project '{project.slug}' (id={project.pk}) — has datasets and no alias."
                    )
                )
                continue
            project.delete()
            orphan_deleted += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Consolidated {renamed} canonical projects, merged {merged_datasets} datasets, "
                f"deleted {deleted_projects + orphan_deleted} duplicate/orphan projects."
            )
        )
