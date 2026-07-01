from django.urls import reverse
from rest_framework import serializers

from .models import Dataset, Project, ProjectPublication


def _cadence_label(value: str) -> str:
    return dict(Dataset.Cadence.choices).get(value, value)


def _status_label(value: str) -> str:
    labels = dict(Dataset.Status.choices)
    labels[Dataset.Status.DRAFT] = "Planned"
    return labels.get(value, value)


def _data_type_label(value: str) -> str:
    return dict(Dataset.DataType.choices).get(value, value)


class PublicDatasetFileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    file_name = serializers.CharField()
    file_kind = serializers.CharField()
    download_available = serializers.BooleanField()
    download_url = serializers.CharField(allow_blank=True)


def _public_file_payload(request, dataset: Dataset, file_record) -> dict:
    download_url = ""
    download_available = False

    if file_record.external_url:
        download_url = file_record.external_url
        download_available = True
    elif file_record.file:
        path = reverse(
            "public-dataset-file-download",
            kwargs={"dataset_pk": dataset.pk, "file_pk": file_record.pk},
        )
        download_url = request.build_absolute_uri(path) if request else path
        download_available = True

    return {
        "id": file_record.id,
        "file_name": file_record.file_name,
        "file_kind": file_record.get_file_kind_display(),
        "download_available": download_available,
        "download_url": download_url,
    }


class PublicMetadataFieldSerializer(serializers.Serializer):
    label = serializers.CharField()
    field_type = serializers.CharField()
    unit = serializers.CharField()
    required = serializers.BooleanField()


class PublicDatasetSerializer(serializers.ModelSerializer):
    organization = serializers.CharField(source="organization.name", read_only=True)
    project_slug = serializers.SerializerMethodField()
    cadence = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    data_type = serializers.SerializerMethodField()
    last_updated = serializers.DateTimeField(source="updated_at", format="%Y-%m-%d")
    files = serializers.SerializerMethodField()
    metadata_fields = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = (
            "id",
            "title",
            "description",
            "organization",
            "project_slug",
            "cadence",
            "status",
            "last_updated",
            "data_type",
            "files",
            "metadata_fields",
        )

    def get_project_slug(self, obj: Dataset) -> str:
        if obj.project_id:
            return obj.project.slug
        return obj.project_slug or ""

    def get_cadence(self, obj: Dataset) -> str:
        return _cadence_label(obj.cadence)

    def get_status(self, obj: Dataset) -> str:
        return _status_label(obj.status)

    def get_data_type(self, obj: Dataset) -> str:
        return _data_type_label(obj.data_type)

    def get_files(self, obj: Dataset) -> list[dict]:
        request = self.context.get("request")
        return [
            _public_file_payload(request, obj, file_record)
            for file_record in obj.files.filter(expose_on_public_api=True).order_by("-uploaded_at")
        ]

    def get_metadata_fields(self, obj: Dataset) -> list[dict]:
        return [
            {
                "label": field.label,
                "field_type": field.get_field_type_display(),
                "unit": field.unit,
                "required": field.required,
            }
            for field in obj.metadata_fields.all().order_by("sort_order", "id")
        ]


class PublicProjectSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="short_title", read_only=True)
    description_paragraphs = serializers.SerializerMethodField()
    dataset_ids = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = Project
        fields = (
            "slug",
            "title",
            "full_title",
            "summary",
            "description_paragraphs",
            "dataset_ids",
            "external_url",
            "lead_name",
            "lead_email",
            "organization_name",
            "institutional_partners",
            "ongoing",
            "collection_frequency",
            "update_frequency",
        )

    def get_description_paragraphs(self, obj: Project) -> list[str]:
        if obj.description:
            paragraphs = [part.strip() for part in obj.description.split("\n\n") if part.strip()]
            if paragraphs:
                return paragraphs
        if obj.full_title:
            return [obj.full_title]
        return []

    def get_dataset_ids(self, obj: Project) -> list[str]:
        public_statuses = [Dataset.Status.ACTIVE, Dataset.Status.ARCHIVED]
        ids = obj.datasets.filter(expose_on_public_api=True, status__in=public_statuses).values_list("id", flat=True)
        return [str(dataset_id) for dataset_id in ids]


class PublicPublicationSerializer(serializers.ModelSerializer):
    project_slug = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPublication
        fields = (
            "id",
            "citation",
            "title",
            "publication_year",
            "doi",
            "url",
            "featured",
            "project_slug",
        )

    def get_project_slug(self, obj: ProjectPublication) -> str | None:
        if obj.project_id:
            return obj.project.slug
        return None
