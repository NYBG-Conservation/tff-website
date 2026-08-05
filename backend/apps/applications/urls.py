from django.urls import path

from .views import PublicResearchApplicationCreateView

urlpatterns = [
    path(
        "public/research-applications/",
        PublicResearchApplicationCreateView.as_view(),
        name="public-research-application-create",
    ),
]
