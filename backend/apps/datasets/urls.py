from django.urls import path

from .views import (
    DatasetFileUploadView,
    DatasetListCreateView,
    DatasetRetrieveUpdateView,
    MetadataFieldTypeListView,
    ProjectListCreateView,
    ProjectManagerAddView,
    ProjectManagerRemoveView,
    ProjectRetrieveUpdateView,
    RoleSeedView,
)

urlpatterns = [
    path("projects/", ProjectListCreateView.as_view(), name="project-list-create"),
    path("projects/<int:pk>/", ProjectRetrieveUpdateView.as_view(), name="project-retrieve-update"),
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
    path("admin/seed-roles/", RoleSeedView.as_view(), name="seed-roles"),
]
