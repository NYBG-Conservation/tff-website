from rest_framework.permissions import BasePermission

from apps.accounts.models import UserProfile


def is_internal_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    profile = getattr(user, "profile", None)
    return bool(profile and profile.role == UserProfile.Role.INTERNAL_ADMIN)


class IsInternalAdminOrDatasetOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if is_internal_admin(request.user):
            return True
        return obj.owner_id == request.user.id
