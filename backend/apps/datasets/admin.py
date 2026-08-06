from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.accounts.models import UserProfile
from apps.accounts.roles import is_internal_staff, is_internal_superadmin, scoped_datasets_filter, scoped_projects_filter

from .figshare import figshare_doi_guide_url, validate_figshare_doi_url

from .models import (
    Dataset,
    DatasetFile,
    DatasetMetadataValue,
    DatasetPublication,
    MetadataFieldDefinition,
    Project,
    ProjectAlert,
    ProjectManager,
    ProjectPublication,
)


class DatasetFileInline(admin.StackedInline):
    model = DatasetFile
    extra = 0
    exclude = ("uploaded_by",)
    readonly_fields = ("uploaded_at", "version")
    classes = ("collapse",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "file",
                    "external_url",
                    "file_name",
                    "file_kind",
                    "content_type",
                    "notes",
                    "expose_on_public_api",
                    "uploaded_at",
                    "version",
                )
            },
        ),
    )


class MetadataFieldDefinitionInline(admin.StackedInline):
    model = MetadataFieldDefinition
    extra = 0
    classes = ("collapse",)


class DatasetMetadataValueInline(admin.StackedInline):
    model = DatasetMetadataValue
    extra = 0
    classes = ("collapse",)


class DatasetPublicationInline(admin.StackedInline):
    model = DatasetPublication
    extra = 0
    classes = ("collapse",)


class ProjectPublicationInline(admin.TabularInline):
    model = ProjectPublication
    extra = 0
    fields = ("citation", "publication_year", "featured", "expose_on_public_api", "sort_order")


class ProjectManagerInline(admin.TabularInline):
    model = ProjectManager
    extra = 0
    verbose_name = "Team member"
    verbose_name_plural = "Team members"


class ProjectAlertInline(admin.TabularInline):
    model = ProjectAlert
    extra = 0
    readonly_fields = (
        "first_triggered_at",
        "last_evaluated_at",
        "last_emailed_at",
        "emailed_milestones",
        "resolved_at",
        "created_at",
        "updated_at",
    )


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        plans_own_doi = cleaned.get("plans_own_doi", getattr(self.instance, "plans_own_doi", False))
        is_new = not self.instance.pk
        value = cleaned.get("figshare_doi_url", "")
        required = is_new and not plans_own_doi
        try:
            cleaned["figshare_doi_url"] = validate_figshare_doi_url(value, required=required)
        except DjangoValidationError as exc:
            self.add_error("figshare_doi_url", exc)
        return cleaned


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = (
        "short_title",
        "slug",
        "shared_publicly",
        "manual_outreach_required",
        "organization",
        "lead_name",
        "lead_email",
        "owner",
        "ongoing",
        "end_date",
        "updated_at",
    )
    fieldsets = (
        (None, {"fields": ("short_title", "slug", "full_title", "summary", "description", "shared_publicly")}),
        (
            "Project lead",
            {"fields": ("lead_name", "lead_email", "organization")},
        ),
        ("Permissions", {"fields": ("owner",)}),
        ("Schedule", {"fields": ("start_date", "end_date", "ongoing", "collection_frequency", "update_frequency", "last_updated_note")}),
        (
            "Data upload follow-up",
            {"fields": ("manual_outreach_required", "manual_outreach_at")},
        ),
        (
            "Data deposit (Figshare)",
            {
                "fields": ("plans_own_doi", "figshare_doi_url"),
                "description": (
                    "By default, reserve a DOI in Figshare before data collection "
                    f"({figshare_doi_guide_url()}). Check “plans own DOI” only if you will "
                    "publish the data under your own DOI instead."
                ),
            },
        ),
        ("Links", {"fields": ("external_url", "institutional_partners")}),
    )
    list_filter = ("organization", "shared_publicly", "ongoing", "manual_outreach_required")
    search_fields = ("short_title", "slug", "full_title", "lead_name", "lead_email", "organization__name", "owner__username")
    readonly_fields = ("slug",)
    inlines = [ProjectPublicationInline, ProjectManagerInline, ProjectAlertInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_internal_superadmin(request.user):
            return qs
        return qs.filter(scoped_projects_filter(request.user))


@admin.register(ProjectPublication)
class ProjectPublicationAdmin(admin.ModelAdmin):
    list_display = (
        "short_label",
        "project",
        "publication_year",
        "featured",
        "expose_on_public_api",
        "updated_at",
    )
    list_filter = ("featured", "expose_on_public_api", "publication_year")
    search_fields = ("citation", "title", "doi", "project__short_title", "project__slug")
    autocomplete_fields = ("project",)

    @admin.display(description="Citation")
    def short_label(self, obj: ProjectPublication) -> str:
        return obj.citation[:100]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_internal_superadmin(request.user):
            return qs
        return qs.filter(project__in=Project.objects.filter(scoped_projects_filter(request.user)))


@admin.register(ProjectAlert)
class ProjectAlertAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "alert_type",
        "status",
        "emailed_milestones",
        "first_triggered_at",
        "last_emailed_at",
        "resolved_at",
    )
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
        # Owner is always the creating user for non-staff; staff see it but new rows still auto-set.
        if is_internal_superadmin(request.user) or is_internal_staff(request.user):
            if obj is None:
                return ("owner",)
            return ()
        return ("owner",)

    def save_model(self, request, obj, form, change):
        if not change or not obj.owner_id:
            obj.owner = request.user
        elif not (is_internal_superadmin(request.user) or is_internal_staff(request.user)):
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if formset.model is DatasetFile:
            instances = formset.save(commit=False)
            for obj in instances:
                if not obj.uploaded_by_id:
                    obj.uploaded_by = request.user
                obj.save()
            formset.save_m2m()
            for obj in formset.deleted_objects:
                obj.delete()
            return
        super().save_formset(request, form, formset, change)
