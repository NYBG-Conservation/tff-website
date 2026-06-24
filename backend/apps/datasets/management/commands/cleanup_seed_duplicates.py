import re

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.datasets.models import Dataset, Project
from apps.datasets.seed_constants import CANONICAL_PROJECT_SLUGS, PROJECT_SLUG_ALIASES

_SUFFIX_RE = re.compile(r"^(.+)-(\d+)$")


def canonical_slug_for(slug: str) -> str | None:
    if slug in CANONICAL_PROJECT_SLUGS:
        return slug
    if slug in PROJECT_SLUG_ALIASES:
        return PROJECT_SLUG_ALIASES[slug]
    match = _SUFFIX_RE.match(slug)
    if match:
        base = match.group(1)
        if base in PROJECT_SLUG_ALIASES:
            return PROJECT_SLUG_ALIASES[base]
        if base in CANONICAL_PROJECT_SLUGS:
            return base
    return None


def _merge_datasets(source: Project, target: Project, dry_run: bool) -> int:
    moved = 0
    for dataset in list(source.datasets.all()):
        conflict = Dataset.objects.filter(project=target, title=dataset.title).exclude(pk=dataset.pk).first()
        if conflict:
            for file_record in list(dataset.files.all()):
                if not dry_run:
                    file_record.dataset = conflict
                    file_record.save(update_fields=["dataset"])
                moved += 1
            if not dry_run:
                dataset.delete()
        else:
            if not dry_run:
                dataset.project = target
                dataset.project_slug = target.slug
                dataset.save(update_fields=["project", "project_slug"])
            moved += 1
    return moved


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
        renamed = 0
        merged_datasets = 0
        deleted_projects = 0

        groups: dict[str, list[Project]] = {}
        for project in Project.objects.order_by("id"):
            canonical = canonical_slug_for(project.slug)
            if canonical:
                groups.setdefault(canonical, []).append(project)

        for canonical, projects in groups.items():
            keeper = next((project for project in projects if project.slug == canonical), projects[0])
            for duplicate in projects:
                if duplicate.pk == keeper.pk:
                    continue
                merged_datasets += _merge_datasets(duplicate, keeper, dry_run)
                if not dry_run:
                    duplicate.delete()
                deleted_projects += 1

            if keeper.slug != canonical:
                collision = Project.objects.filter(slug=canonical).exclude(pk=keeper.pk).first()
                if collision:
                    merged_datasets += _merge_datasets(keeper, collision, dry_run)
                    if not dry_run:
                        keeper.delete()
                    deleted_projects += 1
                else:
                    if not dry_run:
                        keeper.slug = canonical
                        keeper.save(update_fields=["slug"])
                        for dataset in keeper.datasets.all():
                            if dataset.project_slug != canonical:
                                dataset.project_slug = canonical
                                dataset.save(update_fields=["project_slug"])
                    renamed += 1

        orphan_deleted = 0
        for project in Project.objects.order_by("id"):
            if canonical_slug_for(project.slug):
                continue
            if project.datasets.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Leaving non-canonical project '{project.slug}' (id={project.pk}) — has datasets and no alias."
                    )
                )
                continue
            if not dry_run:
                project.delete()
            orphan_deleted += 1

        prefix = "DRY RUN: " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}Renamed {renamed} projects, merged {merged_datasets} datasets, "
                f"deleted {deleted_projects + orphan_deleted} duplicate/orphan projects."
            )
        )
