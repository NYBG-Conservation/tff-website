"""tff-sample-data folder → project/dataset mapping (shared by seed, audit, publish commands)."""

from apps.datasets.models import Dataset

SAMPLE_FOLDER_CONFIG: list[dict] = [
    {
        "folder": "knotweed",
        "project_slug": "knotweed-management-study",
        "project_title": "Knotweed Management Study",
        "dataset_title": "Knotweed Treatment Plot Outcomes",
        "dataset_description": "Plot-level knotweed treatment outcomes and related documentation.",
        "cadence": Dataset.Cadence.ANNUAL,
        "data_type": Dataset.DataType.TABULAR,
        "on_research_page": True,
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
        "on_research_page": True,
    },
    {
        "folder": "breeding bird census",
        "project_slug": "breeding-bird-census",
        "project_title": "Annual Breeding Bird Census",
        "dataset_title": "NYBG Breeding Bird Census Data",
        "dataset_description": "Breeding bird census data, handbook, and presentation materials.",
        "cadence": Dataset.Cadence.ANNUAL,
        "data_type": Dataset.DataType.BIODIVERSITY_OBSERVATION,
        "on_research_page": True,
    },
    {
        "folder": "acorn planting",
        "project_slug": "acorn-planting",
        "project_title": "Acorn Planting",
        "dataset_title": "Ten Tallest Plot Data",
        "dataset_description": "Ten-tallest plot data and method instructions.",
        "cadence": Dataset.Cadence.ANNUAL,
        "data_type": Dataset.DataType.TABULAR,
        "on_research_page": True,
    },
    {
        "folder": "million tree plot",
        "project_slug": "million-tree-plot",
        "project_title": "Million Tree Plot Monitoring",
        "dataset_title": "Million Tree Plot — Plot 101-1",
        "dataset_description": "MillionTreesNYC reforestation plot data and related publications.",
        "cadence": Dataset.Cadence.ONE_OFF,
        "data_type": Dataset.DataType.TABULAR,
        "on_research_page": True,
    },
    {
        "folder": "soil monitoring",
        "project_slug": "soil-monitoring",
        "project_title": "Forest Soil Monitoring",
        "dataset_title": "Forest Soil Sampling & FEMC Analysis",
        "dataset_description": "Soil sampling plots, FEMC nutrient analysis, and proposal documents.",
        "cadence": Dataset.Cadence.ANNUAL,
        "data_type": Dataset.DataType.TABULAR,
        "on_research_page": True,
    },
]

EXPECTED_SAMPLE_FILE_COUNT = 18
EXPECTED_SAMPLE_DATASET_COUNT = len(SAMPLE_FOLDER_CONFIG)
