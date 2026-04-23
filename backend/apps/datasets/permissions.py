from rest_framework.permissions import BasePermission

from apps.accounts.models import UserProfile

NYBG_ORGANIZATION_NAME = "New York Botanical Garden"


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
        if obj.owner_id == request.user.id:
            return True
        if getattr(obj, "project_id", None):
            return obj.project.managers.filter(id=request.user.id).exists()
        return False


class CanEditProject(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if is_internal_admin(request.user):
            return obj.organization.name == NYBG_ORGANIZATION_NAME
        if obj.owner_id == request.user.id:
            return True
        return obj.managers.filter(id=request.user.id).exists()
