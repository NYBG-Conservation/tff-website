from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.organizations.models import Organization

from .slug_utils import generate_unique_project_slug


class Project(models.Model):
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="Auto-generated from short title (punctuation removed, spaces as hyphens). Collision suffix -1, -2, …",
    )
    short_title = models.CharField(max_length=255)
    full_title = models.CharField(max_length=500, blank=True)
    summary = models.TextField(
        blank=True,
        help_text="Short teaser shown on the public research project card.",
    )
    description = models.TextField(
        blank=True,
        help_text="Longer project description for the public modal. Separate paragraphs with a blank line.",
    )
    lead_name = models.CharField(max_length=255, help_text="Primary project lead (display name).")
    lead_email = models.EmailField(help_text="Project lead contact email.")
    shared_publicly = models.BooleanField(
        default=False,
        help_text="When enabled, this project can appear on the public Thain Family Forest website.",
    )
    public_sort_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first on the public /research directory. Set in Website display settings.",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    ongoing = models.BooleanField(default=False)
    external_url = models.URLField(blank=True)
    figshare_doi_url = models.URLField(
        max_length=500,
        blank=True,
        help_text=(
            "Figshare item URL or reserved DOI link for this project's data deposit. "
            "Required when creating a new project unless “plans own DOI” is checked."
        ),
    )
    plans_own_doi = models.BooleanField(
        default=False,
        help_text=(
            "Opt out of the Figshare reservation requirement: I plan to publish this data "
            "with my own DOI (e.g. journal, Dryad, Zenodo). You can still paste a doi.org "
            "or Figshare URL in the deposit field when available."
        ),
    )
    institutional_partners = models.JSONField(
        default=list,
        blank=True,
        help_text="List of Organization primary keys (integers) for partner institutions.",
    )
    collection_frequency = models.CharField(max_length=120, blank=True)
    update_frequency = models.CharField(max_length=120, blank=True)
    last_updated_note = models.TextField(blank=True)
    manual_outreach_required = models.BooleanField(
        default=False,
        help_text=(
            "Set automatically when a concluded project reaches the manual-outreach "
            "milestone (default 60 days) without linked dataset files. Cleared when "
            "data is linked or the related alert is snoozed. NYBG superadmin only."
        ),
    )
    manual_outreach_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the system flagged this project for NYBG staff follow-up.",
    )
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="projects")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_projects")
    managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjectManager",
        through_fields=("project", "user"),
        related_name="managed_projects",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("short_title",)

    def save(self, *args, **kwargs):
        if self.short_title and not self.slug:
            self.slug = generate_unique_project_slug(
                self.short_title,
                exclude_pk=self.pk,
            )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.short_title


class ProjectAlert(models.Model):
    class AlertType(models.TextChoices):
        MISSING_DATA_OVERDUE = "missing_data_overdue", "Missing Data Overdue"
        MANUAL_OUTREACH_REQUIRED = "manual_outreach_required", "Manual Outreach Required"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RESOLVED = "resolved", "Resolved"
        SNOOZED = "snoozed", "Snoozed"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=40, choices=AlertType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    emailed_milestones = models.JSONField(
        default=list,
        blank=True,
        help_text="Post-end reminder days already emailed for this alert (e.g. [30, 60, 90, 120]).",
    )
    first_triggered_at = models.DateTimeField()
    last_evaluated_at = models.DateTimeField()
    last_emailed_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-last_evaluated_at", "-id")

    def clean(self) -> None:
        if self.status == self.Status.ACTIVE:
            duplicate = ProjectAlert.objects.filter(
                project=self.project,
                alert_type=self.alert_type,
                status=self.Status.ACTIVE,
            ).exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError("An active alert of this type already exists for this project.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.project.short_title} :: {self.alert_type} ({self.status})"


class ProjectManager(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_managers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_manager_links")
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="project_manager_additions",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "user")
        ordering = ("-created_at",)
        verbose_name = "Team member"
        verbose_name_plural = "Team members"

    def __str__(self) -> str:
        return f"{self.project.short_title} :: {self.user.username}"


class ProjectPublication(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="publications",
        null=True,
        blank=True,
        help_text="Optional. Leave blank for site-wide research publications.",
    )
    citation = models.TextField(
        help_text="Formatted citation. Basic HTML such as <em> for journal titles is allowed.",
    )
    title = models.CharField(max_length=500, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    doi = models.CharField(max_length=120, blank=True)
    url = models.URLField(blank=True)
    featured = models.BooleanField(
        default=False,
        help_text="When enabled, appears in the Selected Publications list on /research.",
    )
    expose_on_public_api = models.BooleanField(
        default=False,
        help_text="Controls whether this publication is exposed via the public-facing website API.",
    )
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-publication_year", "-sort_order", "-created_at")

    def __str__(self) -> str:
        if self.title:
            return self.title
        return self.citation[:80]


class ProjectFile(models.Model):
    """Files attached directly to a research project (admin: Project files)."""

    class FileKind(models.TextChoices):
        PEER_REVIEWED = "peer_reviewed", "Peer-reviewed publication"
        DATASET = "dataset", "Dataset"
        PRESENTATION = "presentation", "Presentation"
        EXTRAMURAL_DOCUMENTS = "extramural_documents", "Extramural documents / methods / summary"
        PUBLIC_INFOGRAPHIC = "public_infographic", "Public infographic"
        OTHER = "other", "Other"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_files")
    file = models.FileField(upload_to="project_files/%Y/%m/", blank=True, null=True)
    external_url = models.URLField(
        blank=True,
        help_text="Use for large assets hosted outside this system (e.g. Figshare) or files over ~100 MB.",
    )
    title = models.CharField(max_length=255, blank=True, help_text="Optional display title. Defaults to the file name.")
    file_name = models.CharField(max_length=255, blank=True)
    file_kind = models.CharField(
        max_length=40,
        choices=FileKind.choices,
        default=FileKind.OTHER,
    )
    content_type = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_project_files",
        help_text="Set automatically to the user who uploads the file.",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expose_on_public_api = models.BooleanField(
        default=False,
        help_text="When enabled, this file can appear on the public research project page.",
    )

    class Meta:
        ordering = ("file_kind", "-uploaded_at")
        verbose_name = "Project file"
        verbose_name_plural = "Project files"

    def clean(self) -> None:
        if not self.file and not self.external_url:
            raise ValidationError("Provide either an uploaded file or an external URL.")
        if self.file and self.external_url:
            raise ValidationError("Provide only one of file upload or external URL.")

    def save(self, *args, **kwargs):
        if not self.file_name:
            if self.file:
                self.file_name = self.file.name.rsplit("/", 1)[-1]
            elif self.external_url:
                self.file_name = self.external_url.rstrip("/").rsplit("/", 1)[-1] or "external-link"
        if not self.title:
            self.title = self.file_name
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title or self.file_name or f"Project file {self.pk}"


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
    project_slug = models.SlugField(
        max_length=120,
        blank=True,
        db_index=False,
        help_text="Optional frontend/backoffice project identifier for linking research cards and datasets.",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="datasets",
        help_text="Required. Every dataset belongs to a research project.",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_datasets",
        help_text="Set automatically to the user who creates the dataset.",
    )
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="datasets")
    additional_research_partners = models.JSONField(default=list, blank=True)
    paper_links = models.JSONField(default=list, blank=True)
    data_collection_start = models.DateField(null=True, blank=True)
    data_collection_end = models.DateField(null=True, blank=True)
    projected_project_end_date = models.DateField(null=True, blank=True)
    expose_on_public_api = models.BooleanField(
        default=False,
        help_text="Controls whether this dataset is exposed via the public-facing website API.",
    )
    metadata_schema_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dataset catalog entry"
        verbose_name_plural = "Dataset catalog"

    def save(self, *args, **kwargs):
        if self.additional_research_partners is None:
            self.additional_research_partners = []
        if self.paper_links is None:
            self.paper_links = []
        super().save(*args, **kwargs)

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
        PEER_REVIEWED = "peer_reviewed", "Peer-reviewed publication"
        DATASET = "dataset", "Dataset"
        PRESENTATION = "presentation", "Presentation"
        EXTRAMURAL_DOCUMENTS = "extramural_documents", "Extramural documents / methods / summary"
        PUBLIC_INFOGRAPHIC = "public_infographic", "Public infographic"
        OTHER = "other", "Other"

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="datasets/%Y/%m/", blank=True, null=True)
    external_url = models.URLField(
        blank=True,
        help_text="Use for large assets hosted outside this system (>1 GB governance policy).",
    )
    file_name = models.CharField(max_length=255)
    file_kind = models.CharField(max_length=40, choices=FileKind.choices, default=FileKind.DATASET)
    content_type = models.CharField(max_length=120, blank=True)
    version = models.PositiveIntegerField(default=1)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_files",
        help_text="Set automatically to the user who uploads the file.",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    expose_on_public_api = models.BooleanField(
        default=False,
        help_text="Controls whether this dataset file is exposed via the public-facing website API.",
    )

    class Meta:
        ordering = ("-uploaded_at",)

    def clean(self) -> None:
        if not self.file and not self.external_url:
            raise ValidationError("Provide either an uploaded file or an external_url.")
        if self.file and self.external_url:
            raise ValidationError("Provide only one of file upload or external_url.")

    def save(self, *args, **kwargs):
        if not self.file_name:
            if self.file:
                self.file_name = self.file.name
            elif self.external_url:
                self.file_name = self.external_url.rstrip("/").rsplit("/", 1)[-1] or "external-link"
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
    expose_on_public_api = models.BooleanField(
        default=False,
        help_text="Controls whether this publication is exposed via the public-facing website API.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-publication_year", "-created_at")

    def __str__(self) -> str:
        return self.title


class WebsiteDisplaySettings(models.Model):
    """Singleton: homepage research highlights. Research-page order lives on Project.public_sort_order."""

    highlight_1 = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        limit_choices_to={"shared_publicly": True},
        help_text="First card under Research highlights on the public homepage.",
    )
    highlight_2 = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        limit_choices_to={"shared_publicly": True},
        help_text="Second homepage highlight card.",
    )
    highlight_3 = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        limit_choices_to={"shared_publicly": True},
        help_text="Third homepage highlight card.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website display settings"
        verbose_name_plural = "Website display settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return

    @classmethod
    def load(cls) -> "WebsiteDisplaySettings":
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    def highlight_projects(self) -> list[Project]:
        projects: list[Project] = []
        seen: set[int] = set()
        for project in (self.highlight_1, self.highlight_2, self.highlight_3):
            if project is None or not project.shared_publicly or project.pk in seen:
                continue
            seen.add(project.pk)
            projects.append(project)
        return projects

    def __str__(self) -> str:
        return "Website display settings"

