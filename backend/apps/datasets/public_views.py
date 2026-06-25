from django.db.models import Q
from rest_framework import generics, permissions

from .models import Dataset, Project, ProjectPublication
from .public_serializers import PublicDatasetSerializer, PublicProjectSerializer, PublicPublicationSerializer

PUBLIC_DATASET_STATUSES = [Dataset.Status.ACTIVE, Dataset.Status.ARCHIVED]


def public_datasets_queryset():
    return (
        Dataset.objects.filter(
            expose_on_public_api=True,
            status__in=PUBLIC_DATASET_STATUSES,
        )
        .filter(Q(project__isnull=True) | Q(project__shared_publicly=True))
        .select_related("organization", "project")
        .order_by("title")
    )


class PublicProjectListView(generics.ListAPIView):
    serializer_class = PublicProjectSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (
            Project.objects.filter(shared_publicly=True)
            .select_related("organization")
            .prefetch_related("datasets")
            .order_by("short_title")
        )


class PublicDatasetListView(generics.ListAPIView):
    serializer_class = PublicDatasetSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = public_datasets_queryset()
        project_slug = self.request.query_params.get("project")
        if project_slug:
            qs = qs.filter(Q(project__slug=project_slug) | Q(project_slug=project_slug))
        return qs


class PublicPublicationListView(generics.ListAPIView):
    serializer_class = PublicPublicationSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = (
            ProjectPublication.objects.filter(expose_on_public_api=True)
            .select_related("project")
            .filter(Q(project__isnull=True) | Q(project__shared_publicly=True))
        )
        featured = self.request.query_params.get("featured")
        if featured in {"true", "1"}:
            qs = qs.filter(featured=True)
        project_slug = self.request.query_params.get("project")
        if project_slug:
            qs = qs.filter(project__slug=project_slug)
        return qs.order_by("-publication_year", "-sort_order", "-created_at")
