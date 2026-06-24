from rest_framework.permissions import BasePermission

from .roles import can_assign_roles


class IsInternalSuperadmin(BasePermission):
    def has_permission(self, request, view):
        return can_assign_roles(request.user)
