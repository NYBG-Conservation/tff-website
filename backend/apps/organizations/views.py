from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Organization.objects.all().order_by("name")
    serializer_class = OrganizationSerializer
