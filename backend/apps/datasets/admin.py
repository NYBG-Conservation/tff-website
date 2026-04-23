from django.contrib import admin
from django.db import models

from apps.accounts.models import UserProfile

from .models import (
    Dataset,
    DatasetFile,
    DatasetMetadataValue,
    DatasetPublication,
    MetadataFieldDefinition,
    Project,
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


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("short_title", "organization", "lead_institution", "owner", "shared_publicly", "ongoing", "updated_at")
    list_filter = ("organization", "shared_publicly", "ongoing")
    search_fields = ("short_title", "full_title", "nybg_pi_name", "external_pi_name", "owner__username")
    inlines = [ProjectManagerInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        profile = getattr(request.user, "profile", None)
        if profile and profile.role == UserProfile.Role.INTERNAL_ADMIN:
            return qs.filter(organization__name="New York Botanical Garden")
        return qs.filter(models.Q(owner=request.user) | models.Q(managers=request.user)).distinct()


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
        profile = getattr(request.user, "profile", None)
        if profile and profile.role == UserProfile.Role.INTERNAL_ADMIN:
            return qs
        return qs.filter(owner=request.user)

    def get_readonly_fields(self, request, obj=None):
        profile = getattr(request.user, "profile", None)
        if profile and profile.role == UserProfile.Role.INTERNAL_ADMIN:
            return ()
        return ("owner",)

    def save_model(self, request, obj, form, change):
        profile = getattr(request.user, "profile", None)
        if not (profile and profile.role == UserProfile.Role.INTERNAL_ADMIN):
            obj.owner = request.user
        super().save_model(request, obj, form, change)

