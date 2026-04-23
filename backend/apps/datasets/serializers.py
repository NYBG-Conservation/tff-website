from django.db import transaction
from rest_framework import serializers

from .models import Dataset, DatasetFile, DatasetMetadataValue, DatasetPublication, MetadataFieldDefinition


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

    class Meta:
        model = DatasetFile
        fields = (
            "id",
            "file",
            "file_name",
            "content_type",
            "file_kind",
            "version",
            "uploaded_by",
            "uploaded_by_username",
            "uploaded_at",
            "notes",
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
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class DatasetSerializer(serializers.ModelSerializer):
    metadata_fields = MetadataFieldDefinitionSerializer(many=True, required=False)
    metadata_values = DatasetMetadataValueInputSerializer(many=True, required=False, write_only=True)
    resolved_metadata_values = DatasetMetadataValueSerializer(source="metadata_values", many=True, read_only=True)
    files = DatasetFileSerializer(many=True, read_only=True)
    publications = DatasetPublicationSerializer(many=True, required=False)
    owner_username = serializers.CharField(source="owner.username", read_only=True)

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
            "owner",
            "owner_username",
            "organization",
            "additional_research_partners",
            "paper_links",
            "data_collection_start",
            "data_collection_end",
            "projected_project_end_date",
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
