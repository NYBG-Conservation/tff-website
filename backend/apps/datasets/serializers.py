from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .figshare import validate_figshare_doi_url
from .models import (
    Dataset,
    DatasetFile,
    DatasetMetadataValue,
    DatasetPublication,
    MetadataFieldDefinition,
    Project,
    ProjectManager,
    ProjectPublication,
)
from .overdue_uploads import (
    days_since_project_end,
    get_active_manual_outreach_alert,
    get_active_missing_data_alert,
    is_overdue_missing_data,
    overdue_days,
)


FIELD_TYPE_CHOICES = [choice for choice, _ in MetadataFieldDefinition.FieldType.choices]


def _is_value_valid_for_field(field: MetadataFieldDefinition, value) -> bool:
    field_type = field.field_type
    if value is None:
        return not field.required
    if field_type in (MetadataFieldDefinition.FieldType.TEXT, MetadataFieldDefinition.FieldType.LONG_TEXT):
        return isinstance(value, str)
    if field_type == MetadataFieldDefinition.FieldType.NUMBER:
        return isinstance(value, (int, float))
    if field_type == MetadataFieldDefinition.FieldType.INTEGER:
        return isinstance(value, int)
    if field_type == MetadataFieldDefinition.FieldType.BOOLEAN:
        return isinstance(value, bool)
    if field_type in (MetadataFieldDefinition.FieldType.DATE, MetadataFieldDefinition.FieldType.DATETIME):
        return isinstance(value, str)
    if field_type == MetadataFieldDefinition.FieldType.URL:
        return isinstance(value, str) and value.startswith(("http://", "https://"))
    if field_type == MetadataFieldDefinition.FieldType.ENUM:
        return isinstance(value, str) and (not field.allowed_values or value in field.allowed_values)
    return True


class MetadataFieldDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadataFieldDefinition
        fields = ("id", "key", "label", "field_type", "unit", "required", "allowed_values", "sort_order")


class DatasetMetadataValueSerializer(serializers.ModelSerializer):
    field_key = serializers.CharField(source="field_definition.key", read_only=True)

    class Meta:
        model = DatasetMetadataValue
        fields = ("id", "field_definition", "field_key", "value")


class DatasetMetadataValueInputSerializer(serializers.Serializer):
    field_key = serializers.SlugField()
    value = serializers.JSONField()


class DatasetFileSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source="uploaded_by.username", read_only=True)

    def validate(self, attrs):
        file_obj = attrs.get("file")
        external_url = attrs.get("external_url", "")
        if self.instance:
            file_obj = file_obj if file_obj is not None else self.instance.file
            external_url = external_url or self.instance.external_url
        if not file_obj and not external_url:
            raise serializers.ValidationError("Provide either file or external_url.")
        if file_obj and external_url:
            raise serializers.ValidationError("Provide only one of file or external_url.")
        return attrs

    class Meta:
        model = DatasetFile
        fields = (
            "id",
            "file",
            "external_url",
            "file_name",
            "content_type",
            "file_kind",
            "version",
            "uploaded_by",
            "uploaded_by_username",
            "uploaded_at",
            "notes",
            "expose_on_public_api",
        )
        read_only_fields = ("uploaded_by", "version", "uploaded_at")


class DatasetPublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetPublication
        fields = (
            "id",
            "title",
            "citation",
            "doi",
            "url",
            "publication_year",
            "notes",
            "attachment",
            "expose_on_public_api",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class ProjectPublicationSerializer(serializers.ModelSerializer):
    project_slug = serializers.SlugField(source="project.slug", read_only=True, allow_null=True)

    class Meta:
        model = ProjectPublication
        fields = (
            "id",
            "project",
            "project_slug",
            "citation",
            "title",
            "publication_year",
            "doi",
            "url",
            "featured",
            "expose_on_public_api",
            "sort_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "project_slug")

    def validate_citation(self, value: str) -> str:
        citation = (value or "").strip()
        if not citation:
            raise serializers.ValidationError("Citation is required.")
        return citation


class DatasetSerializer(serializers.ModelSerializer):
    metadata_fields = MetadataFieldDefinitionSerializer(many=True, required=False)
    metadata_values = DatasetMetadataValueInputSerializer(many=True, required=False, write_only=True)
    resolved_metadata_values = DatasetMetadataValueSerializer(source="metadata_values", many=True, read_only=True)
    files = DatasetFileSerializer(many=True, read_only=True)
    publications = DatasetPublicationSerializer(many=True, required=False)
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    project_id = serializers.SlugField(source="project_slug", required=False, allow_blank=True)

    class Meta:
        model = Dataset
        fields = (
            "id",
            "title",
            "description",
            "cadence",
            "status",
            "data_type",
            "project_id",
            "project",
            "owner",
            "owner_username",
            "organization",
            "additional_research_partners",
            "paper_links",
            "data_collection_start",
            "data_collection_end",
            "projected_project_end_date",
            "expose_on_public_api",
            "metadata_schema_version",
            "metadata_fields",
            "metadata_values",
            "resolved_metadata_values",
            "files",
            "publications",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {"owner": {"required": False}}

    def validate(self, attrs):
        start = attrs.get("data_collection_start", getattr(self.instance, "data_collection_start", None))
        end = attrs.get("data_collection_end", getattr(self.instance, "data_collection_end", None))
        if start and end and end < start:
            raise serializers.ValidationError("data_collection_end cannot be earlier than data_collection_start")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        metadata_fields = validated_data.pop("metadata_fields", [])
        metadata_values = validated_data.pop("metadata_values", [])
        publications = validated_data.pop("publications", [])

        request = self.context.get("request")
        if request and not validated_data.get("owner"):
            validated_data["owner"] = request.user

        dataset = Dataset.objects.create(**validated_data)
        field_map: dict[str, MetadataFieldDefinition] = {}
        for field_payload in metadata_fields:
            field = MetadataFieldDefinition.objects.create(dataset=dataset, **field_payload)
            field_map[field.key] = field

        for value_payload in metadata_values:
            field_definition = field_map.get(value_payload["field_key"])
            if not field_definition:
                continue
            if not _is_value_valid_for_field(field_definition, value_payload["value"]):
                raise serializers.ValidationError(
                    {"metadata_values": f"Value for {field_definition.key} does not match field type."}
                )
            DatasetMetadataValue.objects.create(
                dataset=dataset, field_definition=field_definition, value=value_payload["value"]
            )

        for publication_payload in publications:
            DatasetPublication.objects.create(dataset=dataset, **publication_payload)
        return dataset

    @transaction.atomic
    def update(self, instance, validated_data):
        metadata_fields = validated_data.pop("metadata_fields", None)
        metadata_values = validated_data.pop("metadata_values", None)
        publications = validated_data.pop("publications", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if metadata_fields is not None:
            existing = {field.id: field for field in instance.metadata_fields.all()}
            retained_ids = set()
            for field_payload in metadata_fields:
                field_id = field_payload.get("id")
                if field_id and field_id in existing:
                    field = existing[field_id]
                    for key, value in field_payload.items():
                        if key != "id":
                            setattr(field, key, value)
                    field.save()
                    retained_ids.add(field_id)
                else:
                    field = MetadataFieldDefinition.objects.create(dataset=instance, **field_payload)
                    retained_ids.add(field.id)
            instance.metadata_fields.exclude(id__in=retained_ids).delete()

        if metadata_values is not None:
            instance.metadata_values.all().delete()
            fields_by_key = {field.key: field for field in instance.metadata_fields.all()}
            for value_payload in metadata_values:
                field_obj = fields_by_key.get(value_payload["field_key"])
                if not field_obj:
                    continue
                if not _is_value_valid_for_field(field_obj, value_payload["value"]):
                    raise serializers.ValidationError(
                        {"metadata_values": f"Value for {field_obj.key} does not match field type."}
                    )
                DatasetMetadataValue.objects.create(
                    dataset=instance, field_definition=field_obj, value=value_payload["value"]
                )

        if publications is not None:
            instance.publications.all().delete()
            for publication_payload in publications:
                DatasetPublication.objects.create(dataset=instance, **publication_payload)
        return instance


class FieldTypeSerializer(serializers.Serializer):
    value = serializers.ChoiceField(choices=FIELD_TYPE_CHOICES)
    label = serializers.CharField()


class ProjectManagerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    added_by_username = serializers.CharField(source="added_by.username", read_only=True)

    class Meta:
        model = ProjectManager
        fields = ("id", "user", "username", "added_by", "added_by_username", "created_at")
        read_only_fields = ("added_by", "created_at")


class ProjectSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    managers = ProjectManagerSerializer(source="project_managers", many=True, read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    is_overdue_missing_data = serializers.SerializerMethodField()
    overdue_days = serializers.SerializerMethodField()
    days_since_project_end = serializers.SerializerMethodField()
    manual_outreach_required = serializers.BooleanField(read_only=True)
    manual_outreach_at = serializers.DateTimeField(read_only=True)
    active_alert_id = serializers.SerializerMethodField()
    last_alert_emailed_at = serializers.SerializerMethodField()
    emailed_milestones = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "slug",
            "short_title",
            "full_title",
            "summary",
            "description",
            "lead_name",
            "lead_email",
            "shared_publicly",
            "start_date",
            "end_date",
            "ongoing",
            "external_url",
            "plans_own_doi",
            "figshare_doi_url",
            "institutional_partners",
            "collection_frequency",
            "update_frequency",
            "last_updated_note",
            "organization",
            "organization_name",
            "owner",
            "owner_username",
            "managers",
            "is_overdue_missing_data",
            "overdue_days",
            "days_since_project_end",
            "manual_outreach_required",
            "manual_outreach_at",
            "active_alert_id",
            "last_alert_emailed_at",
            "emailed_milestones",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "slug",
            "created_at",
            "updated_at",
            "owner_username",
            "organization_name",
            "owner",
            "is_overdue_missing_data",
            "overdue_days",
            "days_since_project_end",
            "manual_outreach_required",
            "manual_outreach_at",
            "active_alert_id",
            "last_alert_emailed_at",
            "emailed_milestones",
        )
        extra_kwargs = {"owner": {"required": False}}

    def get_days_since_project_end(self, obj: Project) -> int | None:
        return days_since_project_end(obj)

    def get_is_overdue_missing_data(self, obj: Project) -> bool:
        return is_overdue_missing_data(obj)

    def get_overdue_days(self, obj: Project) -> int:
        return overdue_days(obj)

    def get_active_alert_id(self, obj: Project) -> int | None:
        alert = get_active_missing_data_alert(obj)
        return alert.id if alert else None

    def get_last_alert_emailed_at(self, obj: Project):
        alert = get_active_missing_data_alert(obj)
        return alert.last_emailed_at if alert else None

    def get_emailed_milestones(self, obj: Project) -> list[int]:
        alert = get_active_missing_data_alert(obj)
        if not alert:
            alert = get_active_manual_outreach_alert(obj)
        if not alert:
            return []
        return [int(day) for day in (alert.emailed_milestones or [])]

    def validate_figshare_doi_url(self, value: str) -> str:
        # Required-ness is decided in validate() once plans_own_doi is known.
        try:
            return validate_figshare_doi_url(value, required=False)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        ongoing = attrs.get("ongoing", getattr(self.instance, "ongoing", False))
        if start and end and end < start:
            raise serializers.ValidationError("end_date cannot be earlier than start_date")
        if ongoing and end:
            raise serializers.ValidationError("end_date should be empty when ongoing is true")
        lead_name = (attrs.get("lead_name") or getattr(self.instance, "lead_name", "") or "").strip()
        if not lead_name:
            raise serializers.ValidationError({"lead_name": "Project lead name is required."})
        lead_email = (attrs.get("lead_email") or getattr(self.instance, "lead_email", "") or "").strip()
        if not lead_email:
            raise serializers.ValidationError({"lead_email": "Project lead email is required."})
        if not attrs.get("organization") and not getattr(self.instance, "organization_id", None):
            raise serializers.ValidationError({"organization": "Organization is required."})
        if self.instance is None:
            plans_own_doi = bool(attrs.get("plans_own_doi", False))
            figshare_value = attrs.get("figshare_doi_url", "")
            try:
                attrs["figshare_doi_url"] = validate_figshare_doi_url(
                    figshare_value, required=not plans_own_doi
                )
            except DjangoValidationError as exc:
                raise serializers.ValidationError({"figshare_doi_url": exc.messages}) from exc
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and not validated_data.get("owner"):
            validated_data["owner"] = request.user
        return Project.objects.create(**validated_data)


class ProjectManagerAddSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        user = User.objects.filter(username=value).first()
        if not user:
            raise serializers.ValidationError("User not found.")
        return value
