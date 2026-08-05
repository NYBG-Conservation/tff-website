from rest_framework import serializers

from .models import ResearchApplication

_DATE_FIELDS = (
    "start_date",
    "end_date",
    "anticipated_start_date",
    "anticipated_end_date",
    "attestation_date",
)


class PublicResearchApplicationSerializer(serializers.ModelSerializer):
    """Public create payload. `website` is a honeypot (must stay empty)."""

    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = ResearchApplication
        fields = (
            "website",
            "applicant_name",
            "title_position",
            "institution",
            "email",
            "phone",
            "address",
            "co_pi",
            "project_title",
            "project_type",
            "description",
            "start_date",
            "end_date",
            "anticipated_start_date",
            "anticipated_end_date",
            "desired_species",
            "collection_type",
            "research_location",
            "plant_tracker_notes",
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
            "attestation_name",
            "attestation_date",
        )
        extra_kwargs = {
            "start_date": {"required": False, "allow_null": True},
            "end_date": {"required": False, "allow_null": True},
            "anticipated_start_date": {"required": False, "allow_null": True},
            "anticipated_end_date": {"required": False, "allow_null": True},
            "collection_type": {"required": False, "allow_blank": True},
        }

    def to_internal_value(self, data):
        if hasattr(data, "copy"):
            data = data.copy()
        else:
            data = dict(data)
        for field in _DATE_FIELDS:
            if data.get(field) == "":
                data[field] = None
        return super().to_internal_value(data)

    def validate_website(self, value: str) -> str:
        if value:
            raise serializers.ValidationError("Invalid submission.")
        return value

    def validate(self, attrs):
        attrs.pop("website", None)
        project_type = attrs.get("project_type")
        if project_type == ResearchApplication.ProjectType.PLANT_MATERIAL:
            if not (attrs.get("desired_species") or "").strip():
                raise serializers.ValidationError(
                    {"desired_species": "Required for plant material collection applications."}
                )
        if project_type == ResearchApplication.ProjectType.ONSITE_RESEARCH:
            if not (attrs.get("research_location") or "").strip():
                raise serializers.ValidationError(
                    {"research_location": "Required for on-site research applications."}
                )
        start = attrs.get("start_date") or attrs.get("anticipated_start_date")
        end = attrs.get("end_date") or attrs.get("anticipated_end_date")
        if start and end and end < start:
            raise serializers.ValidationError("End date cannot be earlier than start date.")
        if not (attrs.get("attestation_name") or "").strip():
            raise serializers.ValidationError({"attestation_name": "PI attestation name is required."})
        if not attrs.get("attestation_date"):
            raise serializers.ValidationError({"attestation_date": "Attestation date is required."})
        return attrs

    def create(self, validated_data):
        return ResearchApplication.objects.create(**validated_data)
