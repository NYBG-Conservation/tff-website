from django.contrib import admin

from apps.accounts.models import UserProfile

from .models import Dataset, DatasetFile, DatasetMetadataValue, DatasetPublication, MetadataFieldDefinition


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


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("title", "project_id", "data_type", "organization", "owner", "cadence", "status", "updated_at")
    list_filter = ("data_type", "cadence", "status", "organization")
    search_fields = ("title", "project_id", "description", "owner__username")
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


@admin.register(DatasetFile)
class DatasetFileAdmin(admin.ModelAdmin):
    list_display = ("dataset", "file_name", "file_kind", "version", "uploaded_by", "uploaded_at")
    search_fields = ("dataset__title", "file_name", "uploaded_by__username")


@admin.register(MetadataFieldDefinition)
class MetadataFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ("dataset", "key", "field_type", "required", "unit")
    search_fields = ("dataset__title", "key", "label")


@admin.register(DatasetMetadataValue)
class DatasetMetadataValueAdmin(admin.ModelAdmin):
    list_display = ("dataset", "field_definition", "value")
    search_fields = ("dataset__title", "field_definition__key")


@admin.register(DatasetPublication)
class DatasetPublicationAdmin(admin.ModelAdmin):
    list_display = ("title", "dataset", "publication_year", "doi", "updated_at")
    search_fields = ("title", "citation", "doi", "dataset__title")
