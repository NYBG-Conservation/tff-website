from django.contrib import admin
from django.utils import timezone

from .models import ResearchApplication


@admin.register(ResearchApplication)
class ResearchApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "project_title",
        "applicant_name",
        "institution",
        "email",
        "project_type",
        "status",
        "submitted_at",
    )
    list_filter = ("status", "project_type", "collection_type", "submitted_at")
    search_fields = (
        "project_title",
        "applicant_name",
        "email",
        "institution",
        "legacy_global_id",
    )
    autocomplete_fields = ("project", "reviewed_by")
    readonly_fields = ("submitted_at", "created_at", "updated_at", "legacy_global_id")
    date_hierarchy = "submitted_at"
    actions = ("mark_under_review", "mark_approved", "mark_declined")
    fieldsets = (
        (
            "Review",
            {
                "fields": (
                    "status",
                    "reviewed_by",
                    "review_notes",
                    "project",
                    "submitted_at",
                    "created_at",
                    "updated_at",
                    "legacy_global_id",
                )
            },
        ),
        (
            "Applicant",
            {
                "fields": (
                    "applicant_name",
                    "title_position",
                    "institution",
                    "email",
                    "phone",
                    "address",
                    "co_pi",
                )
            },
        ),
        (
            "Project",
            {
                "fields": (
                    "project_title",
                    "project_type",
                    "description",
                    "start_date",
                    "end_date",
                    "anticipated_start_date",
                    "anticipated_end_date",
                )
            },
        ),
        (
            "Collection / location",
            {
                "fields": (
                    "desired_species",
                    "collection_type",
                    "research_location",
                    "plant_tracker_notes",
                )
            },
        ),
        (
            "Operations & risk",
            {
                "fields": (
                    "abiotic_variables",
                    "biotic_variables",
                    "funding_sources",
                    "wildlife_permits",
                    "nybg_infrastructure",
                    "site_visits",
                    "visitor_impacts",
                    "research_sensitivity",
                    "resources",
                    "publications",
                    "additional_comments",
                )
            },
        ),
        ("Attestation", {"fields": ("attestation_name", "attestation_date")}),
    )

    @admin.action(description="Mark selected as under review")
    def mark_under_review(self, request, queryset):
        queryset.update(
            status=ResearchApplication.Status.UNDER_REVIEW,
            reviewed_by=request.user,
            updated_at=timezone.now(),
        )

    @admin.action(description="Mark selected as approved")
    def mark_approved(self, request, queryset):
        queryset.update(
            status=ResearchApplication.Status.APPROVED,
            reviewed_by=request.user,
            updated_at=timezone.now(),
        )

    @admin.action(description="Mark selected as declined")
    def mark_declined(self, request, queryset):
        queryset.update(
            status=ResearchApplication.Status.DECLINED,
            reviewed_by=request.user,
            updated_at=timezone.now(),
        )
