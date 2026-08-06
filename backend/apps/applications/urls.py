from django.urls import path

from apps.organizations.public_views import PublicOrganizationListView

from .views import (
    PublicResearchApplicationCreateView,
    PublicResearchApplicationInviteClaimView,
)

urlpatterns = [
    path(
        "public/research-applications/",
        PublicResearchApplicationCreateView.as_view(),
        name="public-research-application-create",
    ),
    path(
        "public/research-application-invites/claim/",
        PublicResearchApplicationInviteClaimView.as_view(),
        name="public-research-application-invite-claim",
    ),
    path(
        "public/organizations/",
        PublicOrganizationListView.as_view(),
        name="public-organization-list",
    ),
]
