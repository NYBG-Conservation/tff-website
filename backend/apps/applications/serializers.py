from rest_framework import serializers

from apps.organizations.models import Organization

from .invite import InviteError, claim_invite
from .models import ResearchApplication
from .notifications import django_admin_login_url

_DATE_FIELDS = (
    "start_date",
    "end_date",
    "anticipated_start_date",
    "anticipated_end_date",
    "attestation_date",
)


def resolve_organization(*, organization_id, organization_name: str) -> Organization:
    """Select existing org by id, or get_or_create by name (case-insensitive)."""
    if organization_id is not None:
        try:
            return Organization.objects.get(pk=organization_id)
        except Organization.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"organization_id": "Organization not found."}
            ) from exc

    name = (organization_name or "").strip()
    if not name:
        raise serializers.ValidationError(
            {
                "organization_name": (
                    "Select an organization or enter a new organization name."
                )
            }
        )

    existing = Organization.objects.filter(name__iexact=name).first()
    if existing:
        return existing
    return Organization.objects.create(name=name)


class PublicResearchApplicationSerializer(serializers.ModelSerializer):
    """Public create payload. `website` is a honeypot (must stay empty)."""

    website = serializers.CharField(required=False, allow_blank=True, write_only=True)
    organization_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    organization_name = serializers.CharField(
        required=False, allow_blank=True, write_only=True, max_length=255
    )

    class Meta:
        model = ResearchApplication
        fields = (
            "website",
            "organization_id",
            "organization_name",
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
            "institution": {"required": False, "allow_blank": True},
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
        if data.get("organization_id") == "" or data.get("organization_id") == "new":
            data["organization_id"] = None
        return super().to_internal_value(data)

    def validate_website(self, value: str) -> str:
        if value:
            raise serializers.ValidationError("Invalid submission.")
        return value

    def validate(self, attrs):
        attrs.pop("website", None)
        organization_id = attrs.pop("organization_id", None)
        organization_name = attrs.pop("organization_name", "")
        attrs["organization"] = resolve_organization(
            organization_id=organization_id,
            organization_name=organization_name,
        )
        if not (attrs.get("institution") or "").strip():
            attrs["institution"] = attrs["organization"].name

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


class ClaimResearchApplicationInviteSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        try:
            result = claim_invite(
                token=validated_data["token"],
                username=validated_data["username"],
                password=validated_data["password"],
            )
        except InviteError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc
        result["admin_login_url"] = django_admin_login_url()
        result["detail"] = (
            "Account created. Your project has been set up. "
            "Sign in to Django admin with your username."
        )
        return result
