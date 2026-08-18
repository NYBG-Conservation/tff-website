from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.accounts.roles import (
    is_internal_staff,
    is_internal_superadmin,
    can_edit_project,
    can_view_project,
    scoped_datasets_filter,
    scoped_projects_filter,
)

from apps.organizations.models import Organization

from .figshare import figshare_doi_guide_url, validate_figshare_doi_url

from .models import (
    Dataset,
    DatasetFile,
    DatasetMetadataValue,
    DatasetPublication,
    MetadataFieldDefinition,
    Project,
    ProjectAlert,
    ProjectFile,
    ProjectManager,
    ProjectPublication,
    WebsiteDisplaySettings,
)


def _open_file_href(file_field, external_url: str = "") -> str:
    if file_field:
        try:
            return file_field.url
        except ValueError:
            pass
    return external_url or ""


def related_records_for_project(project: Project) -> dict:
    """Flatten catalog entries, files, and publications that belong to this project."""
    datasets = list(
        project.datasets.select_related("organization")
        .prefetch_related("files", "publications")
        .order_by("title")
    )
    catalog_files = []
    catalog_publications = []
    for dataset in datasets:
        dataset_url = reverse("admin:datasets_dataset_change", args=[dataset.pk])
        for file_obj in dataset.files.all():
            catalog_files.append(
                {
                    "name": file_obj.file_name or f"File {file_obj.pk}",
                    "kind": file_obj.get_file_kind_display(),
                    "dataset_title": dataset.title,
                    "dataset_url": dataset_url,
                    "public": file_obj.expose_on_public_api,
                    "href": _open_file_href(file_obj.file, file_obj.external_url),
                }
            )
        for publication in dataset.publications.all():
            catalog_publications.append(
                {
                    "title": publication.title,
                    "year": publication.publication_year,
                    "dataset_title": dataset.title,
                    "dataset_url": dataset_url,
                    "href": publication.url or _open_file_href(publication.attachment, ""),
                }
            )
    return {
        "datasets": [
            {
                "title": dataset.title,
                "data_type": dataset.get_data_type_display(),
                "status": dataset.get_status_display(),
                "file_count": len(dataset.files.all()),
                "url": reverse("admin:datasets_dataset_change", args=[dataset.pk]),
                "public": dataset.expose_on_public_api,
            }
            for dataset in datasets
        ],
        "catalog_files": catalog_files,
        "catalog_publications": catalog_publications,
        "alerts": [
            {
                "type": alert.get_alert_type_display(),
                "status": alert.get_status_display(),
                "milestones": ", ".join(str(day) for day in (alert.emailed_milestones or [])),
            }
            for alert in project.alerts.all()
        ],
    }


class DatasetFileInlineForm(forms.ModelForm):
    class Meta:
        model = DatasetFile
        exclude = ("uploaded_by",)

    def has_changed(self):
        if self.instance.pk:
            return super().has_changed()
        data = self.data or {}
        has_file = bool(data.get(self.add_prefix("file")))
        has_url = bool((data.get(self.add_prefix("external_url")) or "").strip())
        has_name = bool((data.get(self.add_prefix("file_name")) or "").strip())
        if not has_file and not has_url and not has_name:
            return False
        return super().has_changed()


class DatasetFileInline(admin.StackedInline):
    model = DatasetFile
    form = DatasetFileInlineForm
    extra = 0
    exclude = ("uploaded_by",)
    readonly_fields = ("uploaded_at", "version")
    classes = ("collapse",)
    verbose_name = "File"
    verbose_name_plural = "Files"
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


class ProjectFileInlineForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        exclude = ("uploaded_by",)

    def has_changed(self):
        if self.instance.pk:
            return super().has_changed()
        data = self.data or {}
        has_file = bool(data.get(self.add_prefix("file")) or data.get(self.add_prefix("file_0")))
        has_url = bool((data.get(self.add_prefix("external_url")) or "").strip())
        has_title = bool((data.get(self.add_prefix("title")) or "").strip())
        if not has_file and not has_url and not has_title:
            return False
        return super().has_changed()


class ProjectFileInline(admin.StackedInline):
    model = ProjectFile
    form = ProjectFileInlineForm
    extra = 0
    exclude = ("uploaded_by",)
    readonly_fields = ("uploaded_at",)
    verbose_name = "Project file"
    verbose_name_plural = "Project files"
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "file_kind",
                    "title",
                    "file",
                    "external_url",
                    "file_name",
                    "notes",
                    "expose_on_public_api",
                    "uploaded_at",
                )
            },
        ),
    )

    def has_add_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_delete_permission(request, obj)


class DatasetCatalogInlineForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ("title", "data_type", "cadence", "status", "expose_on_public_api")

    def has_changed(self):
        title = ""
        if self.data:
            title = (self.data.get(self.add_prefix("title")) or "").strip()
        if not self.instance.pk and not title:
            return False
        return super().has_changed()


class DatasetInline(admin.TabularInline):
    """Catalog entries that belong to this project (not nested files — those are listed on the page)."""

    model = Dataset
    form = DatasetCatalogInlineForm
    extra = 0
    show_change_link = True
    fields = ("title", "data_type", "cadence", "status", "expose_on_public_api")
    verbose_name = "Dataset catalog entry"
    verbose_name_plural = "Dataset catalog"

    def has_add_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_delete_permission(request, obj)


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

    def has_add_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_delete_permission(request, obj)


class ProjectManagerInline(admin.TabularInline):
    model = ProjectManager
    extra = 0
    verbose_name = "Team member"
    verbose_name_plural = "Team members"
    fields = ("user", "added_by", "created_at")
    readonly_fields = ("added_by", "created_at")
    autocomplete_fields = ("user",)

    def has_add_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and not can_edit_project(request.user, obj):
            return False
        return super().has_delete_permission(request, obj)


class ProjectAdminForm(forms.ModelForm):
    institutional_partner_orgs = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all().order_by("name"),
        required=False,
        label="Institutional partners",
        help_text="Filter the left list, then choose partners. Add a missing institution below.",
        widget=admin.widgets.FilteredSelectMultiple("institutional partners", is_stacked=False),
    )
    new_partner_name = forms.CharField(
        required=False,
        label="Add a new partner institution",
        max_length=255,
        help_text="If the partner is not in the list, type the name and save. It will be created and selected.",
    )

    class Meta:
        model = Project
        exclude = ("institutional_partners", "manual_outreach_required", "manual_outreach_at", "public_sort_order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ids = []
        if self.instance and self.instance.pk:
            for item in self.instance.institutional_partners or []:
                try:
                    ids.append(int(item))
                except (TypeError, ValueError):
                    continue
        self.fields["institutional_partner_orgs"].initial = Organization.objects.filter(pk__in=ids)

    def clean_new_partner_name(self):
        return (self.cleaned_data.get("new_partner_name") or "").strip()

    def _resolve_partner_orgs(self) -> list[Organization]:
        selected = list(self.cleaned_data.get("institutional_partner_orgs") or [])
        name = self.cleaned_data.get("new_partner_name") or ""
        if name:
            org = Organization.objects.filter(name__iexact=name).first()
            if org is None:
                org = Organization.objects.create(name=name)
            if org not in selected:
                selected.append(org)
        return selected

    def clean(self):
        cleaned = super().clean()
        value = cleaned.get("figshare_doi_url", "")
        try:
            cleaned["figshare_doi_url"] = validate_figshare_doi_url(value, required=False)
        except DjangoValidationError as exc:
            self.add_error("figshare_doi_url", exc)
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.institutional_partners = [org.id for org in self._resolve_partner_orgs()]
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Media:
        css = {"all": ("admin/css/widgets.css",)}
        js = ("admin/js/core.js", "admin/js/SelectBox.js", "admin/js/SelectFilter2.js")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = (
        "short_title",
        "slug",
        "shared_publicly",
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
            "Data deposit (Figshare)",
            {
                "fields": ("plans_own_doi", "figshare_doi_url"),
                "description": (
                    "Optional. You may reserve a DOI in Figshare "
                    f"({figshare_doi_guide_url()}) and paste the item or doi.org URL here, "
                    "or leave blank and add it later. Check “plans own DOI” if you expect "
                    "to publish under a journal / Dryad / Zenodo DOI instead."
                ),
            },
        ),
        (
            "Links",
            {"fields": ("external_url", "institutional_partner_orgs", "new_partner_name")},
        ),
    )
    list_filter = ("organization", "shared_publicly", "ongoing")
    search_fields = ("short_title", "slug", "full_title", "lead_name", "lead_email", "organization__name", "owner__username")
    readonly_fields = ("slug", "manual_outreach_required", "manual_outreach_at")
    # Catalog files live on Dataset rows (Django cannot nest those inlines here).
    # They are listed on the project change form; Project alerts stay on their own page.
    inlines = [DatasetInline, ProjectFileInline, ProjectPublicationInline, ProjectManagerInline]
    change_form_template = "admin/datasets/project/change_form.html"

    def save_model(self, request, obj, form, change):
        if not change or not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        display = list(self.list_display)
        if is_internal_superadmin(request.user):
            display.insert(3, "manual_outreach_required")
        return display

    def get_list_filter(self, request):
        filters = list(self.list_filter)
        if is_internal_superadmin(request.user):
            filters.append("manual_outreach_required")
        return filters

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(self.fieldsets)
        if is_internal_superadmin(request.user):
            fieldsets.insert(
                4,
                (
                    "Data upload follow-up",
                    {
                        "fields": ("manual_outreach_required", "manual_outreach_at"),
                        "description": (
                            "Set automatically from the alert timeline (default: day 60). "
                            "Cleared when data is linked or alerts are snoozed. "
                            "Use Project alerts → Snooze to pause follow-up."
                        ),
                    },
                ),
            )
        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("organization", "owner").prefetch_related(
            "datasets__files",
            "datasets__publications",
            "project_files",
            "alerts",
        )
        if is_internal_superadmin(request.user):
            return qs
        return qs.filter(scoped_projects_filter(request.user)).distinct()

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            project = self.get_queryset(request).filter(pk=object_id).first()
            if project is not None:
                extra_context["tff_related"] = related_records_for_project(project)
                extra_context["tff_show_alerts"] = is_internal_superadmin(request.user)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def has_view_permission(self, request, obj=None):
        if not super().has_view_permission(request, obj):
            return False
        if obj is None:
            return True
        return can_view_project(request.user, obj)

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj is None:
            return True
        return can_edit_project(request.user, obj)

    def has_delete_permission(self, request, obj=None):
        if not super().has_delete_permission(request, obj):
            return False
        if obj is None:
            return True
        return can_edit_project(request.user, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and not can_edit_project(request.user, obj):
            names: list[str] = []
            for _label, opts in self.get_fieldsets(request, obj):
                names.extend(opts.get("fields", ()))
            return list(dict.fromkeys([*readonly, *names]))
        return readonly

    def save_formset(self, request, form, formset, change):
        if formset.model is ProjectManager:
            instances = formset.save(commit=False)
            for obj in instances:
                if not obj.added_by_id:
                    obj.added_by = request.user
                obj.save()
            formset.save_m2m()
            for obj in formset.deleted_objects:
                obj.delete()
            return
        if formset.model is ProjectFile:
            instances = formset.save(commit=False)
            for obj in instances:
                if not obj.uploaded_by_id:
                    obj.uploaded_by = request.user
                obj.save()
            formset.save_m2m()
            for obj in formset.deleted_objects:
                obj.delete()
            return
        if formset.model is Dataset:
            instances = formset.save(commit=False)
            for obj in instances:
                obj.project = form.instance
                if not obj.owner_id:
                    obj.owner = request.user
                if not obj.organization_id and form.instance.organization_id:
                    obj.organization = form.instance.organization
                if form.instance.slug:
                    obj.project_slug = form.instance.slug
                obj.save()
            formset.save_m2m()
            for obj in formset.deleted_objects:
                obj.delete()
            return
        super().save_formset(request, form, formset, change)


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
    actions = ("snooze_selected", "unsnooze_selected")
    readonly_fields = (
        "project",
        "alert_type",
        "status",
        "emailed_milestones",
        "first_triggered_at",
        "last_evaluated_at",
        "last_emailed_at",
        "resolved_at",
        "resolution_note",
        "created_at",
        "updated_at",
    )

    def has_module_permission(self, request):
        return is_internal_superadmin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_internal_superadmin(request.user)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Needed so list actions (snooze) work; fields are all read-only.
        return is_internal_superadmin(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Snooze selected alerts (pause emails & clear follow-up flag)")
    def snooze_selected(self, request, queryset):
        from apps.datasets.overdue_uploads import snooze_project_alerts

        if not is_internal_superadmin(request.user):
            self.message_user(request, "Only NYBG superadmins can snooze alerts.", level="error")
            return
        project_ids = set(queryset.values_list("project_id", flat=True))
        total = 0
        for project in Project.objects.filter(pk__in=project_ids):
            total += snooze_project_alerts(project, note=f"Snoozed by {request.user.username}.")
        self.message_user(request, f"Snoozed alerts on {len(project_ids)} project(s) ({total} alert row(s)).")

    @admin.action(description="Unsnooze selected alerts (resume automated reminders)")
    def unsnooze_selected(self, request, queryset):
        from apps.datasets.overdue_uploads import unsnooze_project_alerts

        if not is_internal_superadmin(request.user):
            self.message_user(request, "Only NYBG superadmins can unsnooze alerts.", level="error")
            return
        project_ids = set(queryset.values_list("project_id", flat=True))
        total = 0
        for project in Project.objects.filter(pk__in=project_ids):
            total += unsnooze_project_alerts(project)
        self.message_user(request, f"Unsnoozed alerts on {len(project_ids)} project(s) ({total} alert row(s)).")


class WebsiteDisplaySettingsForm(forms.ModelForm):
    class Meta:
        model = WebsiteDisplaySettings
        fields = ("highlight_1", "highlight_2", "highlight_3")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        public_projects = Project.objects.filter(shared_publicly=True).order_by("short_title")
        for name in ("highlight_1", "highlight_2", "highlight_3"):
            self.fields[name].queryset = public_projects
            self.fields[name].required = False

    def clean(self):
        cleaned = super().clean()
        slots = [cleaned.get("highlight_1"), cleaned.get("highlight_2"), cleaned.get("highlight_3")]
        ids = [project.pk for project in slots if project]
        if len(ids) != len(set(ids)):
            raise DjangoValidationError("Each homepage highlight must be a different project.")
        for project in slots:
            if project and not project.shared_publicly:
                raise DjangoValidationError(
                    f"“{project.short_title}” is not shared publicly, so it cannot be a homepage highlight."
                )
        return cleaned


@admin.register(WebsiteDisplaySettings)
class WebsiteDisplaySettingsAdmin(admin.ModelAdmin):
    form = WebsiteDisplaySettingsForm
    autocomplete_fields = ("highlight_1", "highlight_2", "highlight_3")
    fieldsets = (
        (
            "Homepage research highlights",
            {
                "description": (
                    "Choose up to three projects that are marked Shared publicly. "
                    "These appear under Research highlights on the public homepage."
                ),
                "fields": ("highlight_1", "highlight_2", "highlight_3"),
            },
        ),
    )

    def has_module_permission(self, request):
        return is_internal_superadmin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_internal_superadmin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_internal_superadmin(request.user)

    def has_add_permission(self, request):
        return is_internal_superadmin(request.user) and not WebsiteDisplaySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = WebsiteDisplaySettings.load()
        return HttpResponseRedirect(
            reverse("admin:datasets_websitedisplaysettings_change", args=[obj.pk])
        )

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["public_projects"] = Project.objects.filter(shared_publicly=True).order_by(
            "public_sort_order", "short_title"
        )
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        for project in Project.objects.filter(shared_publicly=True):
            raw = request.POST.get(f"public_sort_order_{project.pk}")
            if raw is None:
                continue
            try:
                project.public_sort_order = int(raw)
            except (TypeError, ValueError):
                continue
            project.save(update_fields=["public_sort_order", "updated_at"])


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
        return qs.filter(scoped_datasets_filter(request.user)).distinct()

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
