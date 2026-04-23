from django.urls import path

from .views import (
    DatasetFileUploadView,
    DatasetListCreateView,
    DatasetRetrieveUpdateView,
    MetadataFieldTypeListView,
    RoleSeedView,
)

urlpatterns = [
    path("datasets/", DatasetListCreateView.as_view(), name="dataset-list-create"),
    path("datasets/<int:pk>/", DatasetRetrieveUpdateView.as_view(), name="dataset-retrieve-update"),
    path("datasets/<int:pk>/files/", DatasetFileUploadView.as_view(), name="dataset-file-upload"),
    path("metadata/field-types/", MetadataFieldTypeListView.as_view(), name="metadata-field-types"),
    path("admin/seed-roles/", RoleSeedView.as_view(), name="seed-roles"),
]
