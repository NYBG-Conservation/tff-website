import os

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import include, path, re_path
from django.views.static import serve

from apps.accounts.guides import guide_view

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")

admin.site.site_header = "Thain Family Forest"
admin.site.site_title = "TFF Admin"
admin.site.index_title = "Research & dataset administration"
admin.site.site_url = FRONTEND_URL


def root_to_frontend(_request):
    return HttpResponseRedirect(FRONTEND_URL)


@login_required(login_url="/admin/login/")
def media_serve(request, path):
    """Phase-1 local uploads: admin “view file” links hit /media/…

    Require login so dataset uploads are not world-readable by URL alone.
    Public /data downloads use /api/public/datasets/.../download/ instead.
    """
    return serve(request, path, document_root=settings.MEDIA_ROOT)


urlpatterns = [
    path("", root_to_frontend, name="root-to-frontend"),
    path("admin/guides/<slug:slug>/", guide_view, name="admin-guide"),
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/organizations/", include("apps.organizations.urls")),
    path("api/", include("apps.applications.urls")),
    path("api/", include("apps.datasets.urls")),
    re_path(r"^media/(?P<path>.*)$", media_serve, name="media"),
]
