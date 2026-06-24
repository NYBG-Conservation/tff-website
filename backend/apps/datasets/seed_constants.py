"""Canonical slugs shared by seed and cleanup management commands."""

# Research projects (seed_sample_projects)
RESEARCH_PROJECT_SLUGS = frozenset(
    {
        "forest-inventory-transect-study",
        "filling-in-the-gaps",
        "redback-salamander-monitoring",
        "citizen-science-phenology-monitoring",
        "knotweed-management-study",
        "macroinvertebrate-monitoring",
    }
)

# Sample-data-only projects (seed_sample_datasets)
SAMPLE_DATA_PROJECT_SLUGS = frozenset(
    {
        "breeding-bird-census",
        "acorn-planting",
        "million-tree-plot",
        "soil-monitoring",
    }
)

CANONICAL_PROJECT_SLUGS = RESEARCH_PROJECT_SLUGS | SAMPLE_DATA_PROJECT_SLUGS

# Wrong slugs produced before Project.save() respected explicit slug values.
PROJECT_SLUG_ALIASES: dict[str, str] = {
    "acorn-planting-ten-tallest-method": "acorn-planting",
    "annual-breeding-bird-census": "breeding-bird-census",
    "forest-soil-monitoring": "soil-monitoring",
    "million-tree-plot-monitoring": "million-tree-plot",
    "filling-in-the-gaps-plant-establishment-after-hurricane-sandy": "filling-in-the-gaps",
    "long-term-redback-salamander-monitoring": "redback-salamander-monitoring",
    "cfi": "forest-inventory-transect-study",
}
