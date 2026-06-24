from django.contrib import admin

from apps.accounts.models import UserProfile
from apps.accounts.roles import is_internal_staff, is_internal_superadmin, scoped_datasets_filter, scoped_projects_filter

from .models import (
    Dataset,
    DatasetFile,
    DatasetMetadataValue,
    DatasetPublication,
    MetadataFieldDefinition,
    Project,
    ProjectAlert,
    ProjectManager,
)


class DatasetFileInline(admin.TabularInline):
    model = DatasetFile
    extra = 0
    readonly_fields = ("uploaded_at", "version")


class MetadataFieldDefinitionInline(admin.TabularInline):
    model = MetadataFieldDefinition
    extra = 0


class DatasetMetadataValueInline(admin.TabularInline):
    model = DatasetMetadataValue
    extra = 0


class DatasetPublicationInline(admin.TabularInline):
    model = DatasetPublication
    extra = 0


class ProjectManagerInline(admin.TabularInline):
    model = ProjectManager
    extra = 0


class ProjectAlertInline(admin.TabularInline):
    model = ProjectAlert
    extra = 0
    readonly_fields = ("first_triggered_at", "last_evaluated_at", "last_emailed_at", "resolved_at", "created_at", "updated_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "short_title",
        "slug",
        "shared_publicly",
        "organization",
        "lead_name",
        "lead_email",
        "owner",
        "ongoing",
        "updated_at",
    )
    fieldsets = (
        (None, {"fields": ("short_title", "slug", "full_title", "summary", "description", "hero_image", "shared_publicly")}),
        (
            "Project lead",
            {"fields": ("lead_name", "lead_email", "organization")},
        ),
        ("Permissions", {"fields": ("owner",)}),
        ("Schedule", {"fields": ("start_date", "end_date", "ongoing", "collection_frequency", "update_frequency", "last_updated_note")}),
        ("Links", {"fields": ("external_url", "institutional_partners")}),
    )
    list_filter = ("organization", "shared_publicly", "ongoing")
    search_fields = ("short_title", "slug", "full_title", "lead_name", "lead_email", "organization__name", "owner__username")
    readonly_fields = ("slug",)
    inlines = [ProjectManagerInline, ProjectAlertInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_internal_superadmin(request.user):
            return qs
        return qs.filter(scoped_projects_filter(request.user))


@admin.register(ProjectAlert)
class ProjectAlertAdmin(admin.ModelAdmin):
    list_display = ("project", "alert_type", "status", "first_triggered_at", "last_emailed_at", "resolved_at")
    list_filter = ("alert_type", "status")
    search_fields = ("project__short_title", "project__slug", "resolution_note")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "project_slug",
        "data_type",
        "expose_on_public_api",
        "organization",
        "owner",
        "cadence",
        "status",
        "updated_at",
    )
    list_filter = ("data_type", "cadence", "status", "organization")
    search_fields = ("title", "project_slug", "description", "owner__username")
    inlines = [MetadataFieldDefinitionInline, DatasetMetadataValueInline, DatasetFileInline, DatasetPublicationInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_internal_superadmin(request.user):
            return qs
        return qs.filter(scoped_datasets_filter(request.user))

    def get_readonly_fields(self, request, obj=None):
        if is_internal_superadmin(request.user) or is_internal_staff(request.user):
            return ()
        return ("owner",)

    def save_model(self, request, obj, form, change):
        if not (is_internal_superadmin(request.user) or is_internal_staff(request.user)):
            obj.owner = request.user
        super().save_model(request, obj, form, change)
