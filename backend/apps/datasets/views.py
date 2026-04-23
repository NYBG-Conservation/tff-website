from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile

from .models import Dataset, DatasetFile, MetadataFieldDefinition, Project, ProjectManager
from .permissions import CanEditProject, IsInternalAdminOrDatasetOwner, NYBG_ORGANIZATION_NAME, is_internal_admin
from .serializers import (
    DatasetFileSerializer,
    DatasetSerializer,
    FieldTypeSerializer,
    ProjectManagerAddSerializer,
    ProjectSerializer,
)


def scoped_projects_for_user(user):
    qs = Project.objects.select_related("owner", "organization").prefetch_related("project_managers__user")
    if is_internal_admin(user):
        return qs.filter(organization__name=NYBG_ORGANIZATION_NAME)
    return qs.filter(Q(owner=user) | Q(managers=user)).distinct()


def scoped_datasets_for_user(user):
    qs = Dataset.objects.select_related("owner", "organization").prefetch_related(
        "metadata_fields", "metadata_values", "files", "publications", "project"
    )
    if is_internal_admin(user):
        return qs.filter(Q(project__organization__name=NYBG_ORGANIZATION_NAME) | Q(project__isnull=True))
    return qs.filter(Q(owner=user) | Q(project__managers=user)).distinct()


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = scoped_projects_for_user(self.request.user)
        mine = self.request.query_params.get("mine")
        organization = self.request.query_params.get("organization")
        shared_publicly = self.request.query_params.get("shared_publicly")

        if mine == "true":
            qs = qs.filter(owner=self.request.user)
        if organization:
            qs = qs.filter(organization_id=organization)
        if shared_publicly in {"true", "false"}:
            qs = qs.filter(shared_publicly=(shared_publicly == "true"))
        return qs

    def perform_create(self, serializer):
        if is_internal_admin(self.request.user):
            serializer.save()
            return
        serializer.save(owner=self.request.user)


class ProjectRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditProject]

    def get_queryset(self):
        return scoped_projects_for_user(self.request.user)


class ProjectManagerAddView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanEditProject]

    def post(self, request, pk):
        project = generics.get_object_or_404(Project.objects.select_related("organization"), pk=pk)
        self.check_object_permissions(request, project)

        serializer = ProjectManagerAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
        link, created = ProjectManager.objects.get_or_create(
            project=project, user=user, defaults={"added_by": request.user}
        )
        if not created:
            return Response({"detail": "User is already a project manager."}, status=status.HTTP_200_OK)
        return Response({"id": link.id, "username": link.user.username}, status=status.HTTP_201_CREATED)


class ProjectManagerRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanEditProject]

    def delete(self, request, pk, user_id):
        project = generics.get_object_or_404(Project.objects.select_related("organization"), pk=pk)
        self.check_object_permissions(request, project)
        link = ProjectManager.objects.filter(project=project, user_id=user_id).first()
        if not link:
            return Response({"detail": "Project manager relationship not found."}, status=status.HTTP_404_NOT_FOUND)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
