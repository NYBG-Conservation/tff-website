import os

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")

admin.site.site_header = "Thain Family Forest"
admin.site.site_title = "TFF Admin"
admin.site.index_title = "Research & dataset administration"


def root_to_frontend(_request):
    return HttpResponseRedirect(FRONTEND_URL)


urlpatterns = [
    path("", root_to_frontend, name="root-to-frontend"),
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/organizations/", include("apps.organizations.urls")),
    path("api/", include("apps.applications.urls")),
    path("api/", include("apps.datasets.urls")),
]
