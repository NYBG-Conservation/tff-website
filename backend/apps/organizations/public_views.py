from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.organizations.models import Organization


class PublicOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name")


class PublicOrganizationListView(ListAPIView):
    """Anonymous org picker for the research application form."""

    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = Organization.objects.all().order_by("name")
    serializer_class = PublicOrganizationSerializer
