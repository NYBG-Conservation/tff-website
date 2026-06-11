from rest_framework import serializers

from .models import Dataset, Project


def _cadence_label(value: str) -> str:
    return dict(Dataset.Cadence.choices).get(value, value)


def _status_label(value: str) -> str:
    labels = dict(Dataset.Status.choices)
    labels[Dataset.Status.DRAFT] = "Planned"
    return labels.get(value, value)


class PublicDatasetSerializer(serializers.ModelSerializer):
    organization = serializers.CharField(source="organization.name", read_only=True)
    project_slug = serializers.SerializerMethodField()
    cadence = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    last_updated = serializers.DateTimeField(source="updated_at", format="%Y-%m-%d")

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
        )

    def get_project_slug(self, obj: Dataset) -> str:
        if obj.project_id:
            return obj.project.slug
        return obj.project_slug or ""

    def get_cadence(self, obj: Dataset) -> str:
        return _cadence_label(obj.cadence)

    def get_status(self, obj: Dataset) -> str:
        return _status_label(obj.status)


class PublicProjectSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="short_title", read_only=True)
    image = serializers.SerializerMethodField()
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
            "image",
            "description_paragraphs",
            "dataset_ids",
            "external_url",
            "lead_name",
            "lead_email",
            "organization_name",
            "collection_frequency",
            "update_frequency",
        )

    def get_image(self, obj: Project) -> str:
        if obj.hero_image:
            return obj.hero_image
        return "/images/home/forest-canopy.png"

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
