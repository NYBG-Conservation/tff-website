from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile

from .models import Dataset, DatasetFile, MetadataFieldDefinition
from .permissions import IsInternalAdminOrDatasetOwner, is_internal_admin
from .serializers import (
    DatasetFileSerializer,
    DatasetSerializer,
    FieldTypeSerializer,
)


def scoped_datasets_for_user(user):
    qs = Dataset.objects.select_related("owner", "organization").prefetch_related(
        "metadata_fields", "metadata_values", "files"
    )
    if is_internal_admin(user):
        return qs
    return qs.filter(Q(owner=user))


class DatasetListCreateView(generics.ListCreateAPIView):
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return scoped_datasets_for_user(self.request.user)

    def perform_create(self, serializer):
        if is_internal_admin(self.request.user):
            serializer.save()
            return
        serializer.save(owner=self.request.user)


class DatasetRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated, IsInternalAdminOrDatasetOwner]

    def get_queryset(self):
        return scoped_datasets_for_user(self.request.user)


class DatasetFileUploadView(generics.CreateAPIView):
    serializer_class = DatasetFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsInternalAdminOrDatasetOwner]
    parser_classes = [MultiPartParser, FormParser]

    def get_dataset(self):
        dataset = generics.get_object_or_404(Dataset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, dataset)
        return dataset

    def create(self, request, *args, **kwargs):
        dataset = self.get_dataset()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        latest = DatasetFile.objects.filter(dataset=dataset).order_by("-version").first()
        next_version = 1 if latest is None else latest.version + 1
        serializer.save(dataset=dataset, uploaded_by=request.user, version=next_version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MetadataFieldTypeListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        payload = [
            {"value": value, "label": label}
            for value, label in MetadataFieldDefinition.FieldType.choices
        ]
        serializer = FieldTypeSerializer(payload, many=True)
        return Response(serializer.data)


class RoleSeedView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        usernames = request.data.get("internal_admin_usernames", [])
        updated = []
        for username in usernames:
            profile = UserProfile.objects.select_related("user").filter(user__username=username).first()
            if not profile:
                continue
            profile.role = UserProfile.Role.INTERNAL_ADMIN
            profile.save(update_fields=["role"])
            updated.append(username)
        return Response({"updated_internal_admins": updated})
