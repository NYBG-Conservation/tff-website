import re

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


def find_projects_for_canonical_slug(canonical_slug: str) -> list[Project]:
    return [
        project
        for project in Project.objects.all()
        if canonical_slug_for(project.slug) == canonical_slug
    ]


def pick_keeper_project(projects: list[Project], canonical_slug: str) -> Project:
    for project in projects:
        if project.slug == canonical_slug:
            return project
    return max(projects, key=lambda project: (project.datasets.count(), -project.id))


def merge_datasets(source: Project, target: Project) -> int:
    moved = 0
    for dataset in list(source.datasets.all()):
        conflict = Dataset.objects.filter(project=target, title=dataset.title).exclude(pk=dataset.pk).first()
        if conflict:
            for file_record in list(dataset.files.all()):
                file_record.dataset = conflict
                file_record.save(update_fields=["dataset"])
                moved += 1
            dataset.delete()
        else:
            dataset.project = target
            dataset.project_slug = target.slug
            dataset.save(update_fields=["project", "project_slug"])
            moved += 1
    return moved


def consolidate_projects_for_slug(canonical_slug: str) -> tuple[Project | None, int, int]:
    """
    Merge all alias/duplicate rows onto one keeper and rename to canonical_slug.

    Returns (keeper, datasets_merged, duplicates_deleted).
    """
    projects = find_projects_for_canonical_slug(canonical_slug)
    if not projects:
        return None, 0, 0

    keeper = pick_keeper_project(projects, canonical_slug)
    datasets_merged = 0
    duplicates_deleted = 0

    for duplicate in projects:
        if duplicate.pk == keeper.pk:
            continue
        datasets_merged += merge_datasets(duplicate, keeper)
        duplicate.delete()
        duplicates_deleted += 1

    collision = Project.objects.filter(slug=canonical_slug).exclude(pk=keeper.pk).first()
    if collision:
        datasets_merged += merge_datasets(keeper, collision)
        keeper.delete()
        keeper = collision
        duplicates_deleted += 1

    if keeper.slug != canonical_slug:
        keeper.slug = canonical_slug
        keeper.save(update_fields=["slug"])
        for dataset in keeper.datasets.all():
            if dataset.project_slug != canonical_slug:
                dataset.project_slug = canonical_slug
                dataset.save(update_fields=["project_slug"])

    return keeper, datasets_merged, duplicates_deleted


def find_project_by_canonical_slug(canonical_slug: str) -> Project | None:
    keeper, _, _ = consolidate_projects_for_slug(canonical_slug)
    return keeper
