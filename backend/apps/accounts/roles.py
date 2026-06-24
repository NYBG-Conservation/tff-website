"""Role helpers for project/dataset visibility and edit permissions."""

from django.db.models import Q

from apps.organizations.models import Organization

from .models import UserProfile

NYBG_ORGANIZATION_NAME = "New York Botanical Garden"

INTERNAL_ROLES = frozenset(
    {
        UserProfile.Role.INTERNAL_SUPERADMIN,
        UserProfile.Role.INTERNAL_ADMIN,
    }
)
EXTERNAL_ROLES = frozenset(
    {
        UserProfile.Role.EXTERNAL_SUPERADMIN,
        UserProfile.Role.EXTERNAL_ADMIN,
    }
)
ASSIGNABLE_ROLES = frozenset(role.value for role in UserProfile.Role)


def get_profile(user) -> UserProfile | None:
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "profile", None)


def get_role(user) -> str | None:
    profile = get_profile(user)
    return profile.role if profile else None


def is_internal_superadmin(user) -> bool:
    return get_role(user) == UserProfile.Role.INTERNAL_SUPERADMIN


def is_internal_staff(user) -> bool:
    """NYBG internal roles (superadmin or admin)."""
    return get_role(user) in INTERNAL_ROLES


def is_external_superadmin(user) -> bool:
    return get_role(user) == UserProfile.Role.EXTERNAL_SUPERADMIN


def user_home_organization(user) -> Organization | None:
    profile = get_profile(user)
    if not profile:
        return None
    return profile.organization


def scoped_projects_filter(user) -> Q:
    role = get_role(user)
    if role == UserProfile.Role.INTERNAL_SUPERADMIN:
        return Q()
    if role == UserProfile.Role.INTERNAL_ADMIN:
        return Q(organization__name=NYBG_ORGANIZATION_NAME)
    if role == UserProfile.Role.EXTERNAL_SUPERADMIN:
        org = user_home_organization(user)
        if not org:
            return Q(pk__in=[])
        return Q(organization=org)
    return Q(owner=user) | Q(managers=user)


def scoped_datasets_filter(user) -> Q:
    role = get_role(user)
    if role == UserProfile.Role.INTERNAL_SUPERADMIN:
        return Q()
    if role == UserProfile.Role.INTERNAL_ADMIN:
        return Q(organization__name=NYBG_ORGANIZATION_NAME)
    if role == UserProfile.Role.EXTERNAL_SUPERADMIN:
        org = user_home_organization(user)
        if not org:
            return Q(pk__in=[])
        return Q(organization=org)
    return Q(owner=user) | Q(project__managers=user)


def can_edit_project(user, project) -> bool:
    role = get_role(user)
    if role == UserProfile.Role.INTERNAL_SUPERADMIN:
        return True
    if role == UserProfile.Role.INTERNAL_ADMIN:
        return project.organization.name == NYBG_ORGANIZATION_NAME
    if role == UserProfile.Role.EXTERNAL_SUPERADMIN:
        org = user_home_organization(user)
        return bool(org and project.organization_id == org.id)
    if project.owner_id == user.id:
        return True
    return project.managers.filter(id=user.id).exists()


def can_edit_dataset(user, dataset) -> bool:
    role = get_role(user)
    if role == UserProfile.Role.INTERNAL_SUPERADMIN:
        return True
    if role == UserProfile.Role.INTERNAL_ADMIN:
        return dataset.organization.name == NYBG_ORGANIZATION_NAME
    if role == UserProfile.Role.EXTERNAL_SUPERADMIN:
        org = user_home_organization(user)
        return bool(org and dataset.organization_id == org.id)
    if dataset.owner_id == user.id:
        return True
    if dataset.project_id:
        return dataset.project.managers.filter(id=user.id).exists()
    return False


def can_assign_roles(user) -> bool:
    return is_internal_superadmin(user)


def count_internal_superadmins() -> int:
    return UserProfile.objects.filter(role=UserProfile.Role.INTERNAL_SUPERADMIN).count()


def validate_role_organization(role: str, organization: Organization | None) -> None:
    from rest_framework.exceptions import ValidationError

    if role in INTERNAL_ROLES and organization is not None:
        raise ValidationError({"organization": "Internal roles must not have a home organization."})
    if role in EXTERNAL_ROLES and organization is None:
        raise ValidationError({"organization": "External roles require a home organization."})
