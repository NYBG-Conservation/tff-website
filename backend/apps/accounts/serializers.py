from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import Organization

from .models import UserProfile
from .roles import ASSIGNABLE_ROLES, validate_role_organization

User = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    organization_id = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    can_assign_roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "organization_id",
            "organization_name",
            "can_assign_roles",
        )

    def get_role(self, obj: User) -> str | None:
        profile = getattr(obj, "profile", None)
        return profile.role if profile else None

    def get_organization_id(self, obj: User) -> int | None:
        profile = getattr(obj, "profile", None)
        return profile.organization_id if profile and profile.organization_id else None

    def get_organization_name(self, obj: User) -> str | None:
        profile = getattr(obj, "profile", None)
        if profile and profile.organization_id:
            return profile.organization.name
        return None

    def get_can_assign_roles(self, obj: User) -> bool:
        from .roles import can_assign_roles

        return can_assign_roles(obj)


class AssignRoleSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.ChoiceField(choices=sorted(ASSIGNABLE_ROLES))
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        validate_role_organization(attrs["role"], attrs.get("organization"))
        return attrs

    def validate_username(self, value: str) -> str:
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User not found.")
        return value
