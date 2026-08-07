from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile
from apps.accounts.roles import (
    NYBG_ORGANIZATION_NAME,
    is_internal_staff,
    is_internal_superadmin,
    scoped_datasets_filter,
    scoped_projects_filter,
    user_home_organization,
)

from .models import Dataset, DatasetFile, MetadataFieldDefinition, Project, ProjectManager, ProjectPublication
from .permissions import CanEditDataset, CanEditProject, CanEditProjectPublication, CanViewOrEditProject
from .serializers import (
    DatasetFileSerializer,
    DatasetSerializer,
    FieldTypeSerializer,
    ProjectManagerAddSerializer,
    ProjectPublicationSerializer,
    ProjectSerializer,
)


def scoped_projects_for_user(user):
    return Project.objects.select_related("owner", "organization").prefetch_related(
        "project_managers__user"
    ).filter(scoped_projects_filter(user))


def scoped_datasets_for_user(user):
    return Dataset.objects.select_related("owner", "organization", "project").prefetch_related(
        "metadata_fields", "metadata_values", "files", "publications", "project__managers"
    ).filter(scoped_datasets_filter(user))


def _organization_from_validated(serializer) -> object | None:
    return serializer.validated_data.get("organization")


def _assert_can_create_in_organization(user, organization) -> None:
    role = user.profile.role
    if role == UserProfile.Role.INTERNAL_SUPERADMIN:
        return
    if role == UserProfile.Role.INTERNAL_ADMIN:
        if organization.name != NYBG_ORGANIZATION_NAME:
            raise PermissionDenied("Internal admins can only create NYBG organization records.")
        return
    if role == UserProfile.Role.EXTERNAL_SUPERADMIN:
        home = user_home_organization(user)
        if not home or organization.id != home.id:
            raise PermissionDenied("External superadmins can only create records in their organization.")


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
        user = self.request.user
        organization = _organization_from_validated(serializer)
        if organization:
            _assert_can_create_in_organization(user, organization)
        if is_internal_superadmin(user) or is_internal_staff(user):
            serializer.save()
            return
        if user.profile.role == UserProfile.Role.EXTERNAL_SUPERADMIN:
            serializer.save()
            return
        serializer.save(owner=user)


class ProjectRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewOrEditProject]

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
            return Response({"detail": "User is already a team member."}, status=status.HTTP_200_OK)
        return Response({"id": link.id, "username": link.user.username}, status=status.HTTP_201_CREATED)


class ProjectManagerRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanEditProject]

    def delete(self, request, pk, user_id):
        project = generics.get_object_or_404(Project.objects.select_related("organization"), pk=pk)
        self.check_object_permissions(request, project)
        link = ProjectManager.objects.filter(project=project, user_id=user_id).first()
        if not link:
            return Response({"detail": "Team member relationship not found."}, status=status.HTTP_404_NOT_FOUND)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectPublicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectPublicationSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditProject]

    def get_project(self):
        project = generics.get_object_or_404(
            Project.objects.select_related("organization"),
            pk=self.kwargs["pk"],
        )
        self.check_object_permissions(self.request, project)
        return project

    def get_queryset(self):
        project = self.get_project()
        return ProjectPublication.objects.filter(project=project).select_related("project")

    def perform_create(self, serializer):
        project = self.get_project()
        serializer.save(project=project)


class ProjectPublicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectPublicationSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditProjectPublication]

    def get_queryset(self):
        qs = ProjectPublication.objects.select_related("project", "project__organization")
        if is_internal_superadmin(self.request.user):
            return qs
        return qs.filter(project__in=Project.objects.filter(scoped_projects_filter(self.request.user)))


class DatasetListCreateView(generics.ListCreateAPIView):
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return scoped_datasets_for_user(self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        organization = _organization_from_validated(serializer)
        if organization:
            _assert_can_create_in_organization(user, organization)
        # Owner is always set from request.user inside DatasetSerializer.create.
        serializer.save()


class DatasetRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditDataset]

    def get_queryset(self):
        return scoped_datasets_for_user(self.request.user)


class DatasetFileUploadView(generics.CreateAPIView):
    serializer_class = DatasetFileSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditDataset]
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
