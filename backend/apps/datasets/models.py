from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.organizations.models import Organization


class Dataset(models.Model):
    class DataType(models.TextChoices):
        TABULAR = "tabular", "Tabular"
        GEOSPATIAL = "geospatial", "Geospatial"
        IMAGE = "image", "Image"
        SENSOR_TIME_SERIES = "sensor_time_series", "Sensor Time Series"
        BIODIVERSITY_OBSERVATION = "biodiversity_observation", "Biodiversity Observation"
        DOCUMENT_ARCHIVE = "document_archive", "Document Archive"

    class Cadence(models.TextChoices):
        ANNUAL = "annual", "Annual"
        ONE_OFF = "one_off", "One Off"
        CONTINUOUS = "continuous", "Continuous"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cadence = models.CharField(max_length=20, choices=Cadence.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    data_type = models.CharField(max_length=40, choices=DataType.choices, default=DataType.TABULAR)
    project_id = models.SlugField(
        max_length=120,
        blank=True,
        help_text="Optional frontend/backoffice project identifier for linking research cards and datasets.",
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_datasets")
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="datasets")
    additional_research_partners = models.JSONField(default=list, blank=True)
    paper_links = models.JSONField(default=list, blank=True)
    data_collection_start = models.DateField(null=True, blank=True)
    data_collection_end = models.DateField(null=True, blank=True)
    projected_project_end_date = models.DateField(null=True, blank=True)
    metadata_schema_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class MetadataFieldDefinition(models.Model):
    class FieldType(models.TextChoices):
        TEXT = "text", "Text"
        LONG_TEXT = "long_text", "Long Text"
        NUMBER = "number", "Number"
        INTEGER = "integer", "Integer"
        BOOLEAN = "boolean", "Boolean"
        DATE = "date", "Date"
        DATETIME = "datetime", "Datetime"
        ENUM = "enum", "Enum"
        URL = "url", "URL"

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="metadata_fields")
    key = models.SlugField(max_length=80)
    label = models.CharField(max_length=120)
    field_type = models.CharField(max_length=20, choices=FieldType.choices)
    unit = models.CharField(max_length=50, blank=True)
    required = models.BooleanField(default=False)
    allowed_values = models.JSONField(default=list, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("dataset", "key")
        ordering = ("sort_order", "id")

    def clean(self) -> None:
        if self.field_type != self.FieldType.ENUM and self.allowed_values:
            raise ValidationError({"allowed_values": "Allowed values can only be set for enum fields."})

    def __str__(self) -> str:
        return f"{self.dataset.title}: {self.label}"


class DatasetMetadataValue(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="metadata_values")
    field_definition = models.ForeignKey(
        MetadataFieldDefinition, on_delete=models.CASCADE, related_name="values"
    )
    value = models.JSONField()

    class Meta:
        unique_together = ("dataset", "field_definition")

    def clean(self) -> None:
        if self.field_definition.dataset_id != self.dataset_id:
            raise ValidationError("Metadata field definition must belong to the same dataset.")

    def __str__(self) -> str:
        return f"{self.dataset.title} - {self.field_definition.key}"


class DatasetFile(models.Model):
    class FileKind(models.TextChoices):
        PRIMARY_DATA = "primary_data", "Primary Data"
        DOCUMENTATION = "documentation", "Documentation"
        CODE = "code", "Code"
        DERIVED_OUTPUT = "derived_output", "Derived Output"
        IMAGE_MEDIA = "image_media", "Image / Media"
        OTHER = "other", "Other"

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="datasets/%Y/%m/")
    file_name = models.CharField(max_length=255)
    file_kind = models.CharField(max_length=30, choices=FileKind.choices, default=FileKind.PRIMARY_DATA)
    content_type = models.CharField(max_length=120, blank=True)
    version = models.PositiveIntegerField(default=1)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_files")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-uploaded_at",)

    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = self.file.name
        if not self.pk and not self.version:
            latest = DatasetFile.objects.filter(dataset=self.dataset).order_by("-version").first()
            self.version = 1 if not latest else latest.version + 1
        super().save(*args, **kwargs)


class DatasetPublication(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="publications")
    title = models.CharField(max_length=255)
    citation = models.TextField(blank=True)
    doi = models.CharField(max_length=120, blank=True)
    url = models.URLField(blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to="publications/%Y/%m/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-publication_year", "-created_at")

    def __str__(self) -> str:
        return self.title

