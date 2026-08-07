from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.roles import (
    NYBG_ORGANIZATION_NAME,
    can_edit_dataset,
    can_edit_project,
    can_view_project,
)

# Re-export for backwards compatibility in imports.
__all__ = [
    "NYBG_ORGANIZATION_NAME",
    "CanEditDataset",
    "CanEditProject",
    "CanViewOrEditProject",
    "CanEditProjectPublication",
    "can_edit_dataset",
    "can_edit_project",
    "can_view_project",
]


class CanEditProject(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return can_edit_project(request.user, obj)


class CanViewOrEditProject(BasePermission):
    """GET/HEAD/OPTIONS: can_view_project; write methods: can_edit_project."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return can_view_project(request.user, obj)
        return can_edit_project(request.user, obj)


class CanEditDataset(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return can_edit_dataset(request.user, obj)


class CanEditProjectPublication(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if obj.project_id:
            return can_edit_project(request.user, obj.project)
        from apps.accounts.roles import is_internal_superadmin

        return is_internal_superadmin(request.user)


# Legacy name used by dataset file upload views.
IsInternalAdminOrDatasetOwner = CanEditDataset
