from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Dataset, Project, ProjectPublication
from .public_serializers import PublicDatasetSerializer, PublicProjectSerializer, PublicPublicationSerializer
from .public_utils import is_mobile_user_agent

PUBLIC_DATASET_STATUSES = [Dataset.Status.ACTIVE, Dataset.Status.ARCHIVED]


def public_datasets_queryset():
    return (
        Dataset.objects.filter(
            expose_on_public_api=True,
            status__in=PUBLIC_DATASET_STATUSES,
        )
        .filter(Q(project__isnull=True) | Q(project__shared_publicly=True))
        .select_related("organization", "project")
        .prefetch_related("metadata_fields", "files")
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


class PublicDatasetFileDownloadView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, dataset_pk: int, file_pk: int):
        if is_mobile_user_agent(request.META.get("HTTP_USER_AGENT", "")):
            return Response(
                {
                    "detail": "Downloads are not available on mobile devices. Please use a desktop browser.",
                },
                status=403,
            )

        dataset = get_object_or_404(public_datasets_queryset(), pk=dataset_pk)
        file_record = get_object_or_404(
            dataset.files.filter(expose_on_public_api=True),
            pk=file_pk,
        )

        if file_record.external_url:
            return HttpResponseRedirect(file_record.external_url)

        if not file_record.file:
            raise Http404("No downloadable file is available.")

        response = FileResponse(
            file_record.file.open("rb"),
            as_attachment=True,
            filename=file_record.file_name,
        )
        if file_record.content_type:
            response["Content-Type"] = file_record.content_type
        return response


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
