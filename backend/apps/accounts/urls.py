from django.urls import path

from .views import AssignRoleView, CsrfTokenView, CurrentUserView

urlpatterns = [
    path("csrf/", CsrfTokenView.as_view(), name="csrf-token"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("assign-role/", AssignRoleView.as_view(), name="assign-role"),
]
