from django.urls import path

from .public_views import (
    PublicDatasetFileDownloadView,
    PublicDatasetListView,
    PublicProjectListView,
    PublicPublicationListView,
)
from .views import (
    DatasetFileUploadView,
    DatasetListCreateView,
    DatasetRetrieveUpdateView,
    MetadataFieldTypeListView,
    ProjectListCreateView,
    ProjectManagerAddView,
    ProjectManagerRemoveView,
    ProjectPublicationDetailView,
    ProjectPublicationListCreateView,
    ProjectRetrieveUpdateView,
)

urlpatterns = [
    path("public/projects/", PublicProjectListView.as_view(), name="public-project-list"),
    path("public/datasets/", PublicDatasetListView.as_view(), name="public-dataset-list"),
    path(
        "public/datasets/<int:dataset_pk>/files/<int:file_pk>/download/",
        PublicDatasetFileDownloadView.as_view(),
        name="public-dataset-file-download",
    ),
    path("public/publications/", PublicPublicationListView.as_view(), name="public-publication-list"),
    path("projects/", ProjectListCreateView.as_view(), name="project-list-create"),
    path("projects/<int:pk>/", ProjectRetrieveUpdateView.as_view(), name="project-retrieve-update"),
    path(
        "projects/<int:pk>/publications/",
        ProjectPublicationListCreateView.as_view(),
        name="project-publication-list-create",
    ),
    path(
        "projects/<int:project_pk>/publications/<int:pk>/",
        ProjectPublicationDetailView.as_view(),
        name="project-publication-detail",
    ),
    path("projects/<int:pk>/managers/", ProjectManagerAddView.as_view(), name="project-manager-add"),
    path(
        "projects/<int:pk>/managers/<int:user_id>/",
        ProjectManagerRemoveView.as_view(),
        name="project-manager-remove",
    ),
    path("datasets/", DatasetListCreateView.as_view(), name="dataset-list-create"),
    path("datasets/<int:pk>/", DatasetRetrieveUpdateView.as_view(), name="dataset-retrieve-update"),
    path("datasets/<int:pk>/files/", DatasetFileUploadView.as_view(), name="dataset-file-upload"),
    path("metadata/field-types/", MetadataFieldTypeListView.as_view(), name="metadata-field-types"),
]
