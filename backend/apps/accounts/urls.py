from django.urls import path

from .views import CsrfTokenView, CurrentUserView

urlpatterns = [
    path("csrf/", CsrfTokenView.as_view(), name="csrf-token"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
]
