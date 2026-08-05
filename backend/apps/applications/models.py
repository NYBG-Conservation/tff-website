from django.conf import settings
from django.db import models
from django.utils import timezone


class ResearchApplication(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under review"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"
        WITHDRAWN = "withdrawn", "Withdrawn"

    class ProjectType(models.TextChoices):
        PLANT_MATERIAL = "Plant_material_collections", "Plant material collections"
        ONSITE_RESEARCH = "onsite_research", "On-site research"

    class CollectionType(models.TextChoices):
        ON_SITE = "on-site_collection", "On-site collection"
        OFF_SITE = "off-site_collection", "Off-site collection"
        OTHER = "other", "Other / not applicable"

    legacy_global_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        unique=True,
        help_text="Survey123 GlobalID when imported from legacy export.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
        db_index=True,
    )

    # PI / applicant
    applicant_name = models.CharField(max_length=255)
    title_position = models.CharField(max_length=255, blank=True)
    institution = models.CharField(max_length=500)
    email = models.EmailField()
    phone = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)
    co_pi = models.TextField(blank=True, help_text="Co-PI names and affiliations.")

    # Project
    project_title = models.CharField(max_length=500)
    project_type = models.CharField(max_length=64, choices=ProjectType.choices)
    description = models.TextField(help_text="Project description / abstract.")

    # Scheduling
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    anticipated_start_date = models.DateField(null=True, blank=True)
    anticipated_end_date = models.DateField(null=True, blank=True)

    # Plant material / collection
    desired_species = models.TextField(blank=True)
    collection_type = models.CharField(
        max_length=64,
        choices=CollectionType.choices,
        blank=True,
    )

    # Location / on-site
    research_location = models.TextField(blank=True)
    plant_tracker_notes = models.TextField(blank=True)

    # Ops / risk
    abiotic_variables = models.TextField(blank=True)
    biotic_variables = models.TextField(blank=True)
    funding_sources = models.TextField(blank=True)
    wildlife_permits = models.TextField(blank=True)
    nybg_infrastructure = models.TextField(blank=True)
    site_visits = models.TextField(blank=True)
    visitor_impacts = models.TextField(blank=True)
    research_sensitivity = models.TextField(blank=True)
    resources = models.TextField(blank=True)
    publications = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)

    # Attestation
    attestation_name = models.CharField(
        max_length=255,
        help_text="PI name confirming they completed this application.",
    )
    attestation_date = models.DateField()

    # Review / links
    project = models.ForeignKey(
        "datasets.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="research_applications",
        help_text="Optional portal project linked after approval.",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_research_applications",
    )
    review_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-submitted_at", "-id")
        verbose_name = "Research application"
        verbose_name_plural = "Research applications"

    def __str__(self) -> str:
        return f"{self.project_title} ({self.applicant_name})"
