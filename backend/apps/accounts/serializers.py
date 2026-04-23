from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class CurrentUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "role")

    def get_role(self, obj: User) -> str | None:
        profile = getattr(obj, "profile", None)
        return profile.role if profile else None


class RoleSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("role",)
