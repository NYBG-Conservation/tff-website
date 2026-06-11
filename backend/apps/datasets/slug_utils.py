"""Project slug generation for public URLs and dataset linking."""

from django.utils.text import slugify

# SlugField max_length on Project.slug
PROJECT_SLUG_MAX_LENGTH = 120
# Reserve characters for collision suffixes such as -1, -12, -123
PROJECT_SLUG_BASE_MAX_LENGTH = 100


def slugify_project_title(title: str) -> str:
    """Lowercase slug from title: punctuation removed, spaces as hyphens."""
    return slugify(title.strip()) or "project"


def generate_unique_project_slug(
    title: str,
    *,
    exclude_pk: int | None = None,
    max_base_length: int = PROJECT_SLUG_BASE_MAX_LENGTH,
) -> str:
    """
  Build a unique slug from short_title.

  Uses the first max_base_length characters of the slugified title, then appends
  -1, -2, -3, ... when the base is already taken.
    """
    from .models import Project

    base = slugify_project_title(title)[:max_base_length].strip("-") or "project"

    qs = Project.objects.all()
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)

    if not qs.filter(slug=base).exists():
        return base[:PROJECT_SLUG_MAX_LENGTH]

    suffix = 1
    while suffix < 10_000:
        suffix_part = f"-{suffix}"
        trimmed = base[: max_base_length - len(suffix_part)].rstrip("-") or "project"
        candidate = f"{trimmed}{suffix_part}"
        if len(candidate) > PROJECT_SLUG_MAX_LENGTH:
            candidate = candidate[:PROJECT_SLUG_MAX_LENGTH].rstrip("-")
        if not qs.filter(slug=candidate).exists():
            return candidate
        suffix += 1

    raise ValueError("Unable to generate a unique project slug.")
