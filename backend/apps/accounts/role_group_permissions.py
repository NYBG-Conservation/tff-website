"""Django auth permissions attached to role Groups for admin UI access.

Staff status alone is not enough for Django admin: without model permissions,
users see “You don’t have permission to view or edit anything.”

Platform scoping (who can see which rows) still comes from UserProfile.role via
`apps.accounts.roles`. These permissions only unlock the admin app modules.
"""

from __future__ import annotations

from django.contrib.auth.models import Group, Permission

from .constants import (
    EXTERNAL_ADMIN_GROUP,
    EXTERNAL_SUPERADMIN_GROUP,
    INTERNAL_ADMIN_GROUP,
    INTERNAL_SUPERADMIN_GROUP,
)

# (app_label, model) pairs — CRUD unlocks admin list/add/change for partners and NYBG editors.
_CONTENT_MODELS: tuple[tuple[str, str], ...] = (
    ("datasets", "project"),
    ("datasets", "dataset"),
    ("datasets", "datasetfile"),
    ("datasets", "projectpublication"),
    ("datasets", "projectmanager"),
    ("datasets", "metadatafielddefinition"),
    ("datasets", "datasetmetadatavalue"),
    ("datasets", "datasetpublication"),
)

# Partners need to select Organization on project/dataset forms.
_VIEW_ONLY_MODELS: tuple[tuple[str, str], ...] = (
    ("organizations", "organization"),
)

# NYBG internal editors also manage overdue alerts in admin.
_INTERNAL_EXTRA_MODELS: tuple[tuple[str, str], ...] = (
    ("datasets", "projectalert"),
)

_CRUD = ("add", "change", "delete", "view")


def _permission_codenames(model: str, actions: tuple[str, ...]) -> list[str]:
    return [f"{action}_{model}" for action in actions]


def permissions_for_role_group(group_name: str) -> list[Permission]:
    specs: list[tuple[str, str, tuple[str, ...]]] = [
        (app, model, _CRUD) for app, model in _CONTENT_MODELS
    ]
    specs.extend((app, model, ("view",)) for app, model in _VIEW_ONLY_MODELS)

    if group_name in {INTERNAL_SUPERADMIN_GROUP, INTERNAL_ADMIN_GROUP}:
        specs.extend((app, model, _CRUD) for app, model in _INTERNAL_EXTRA_MODELS)

    if group_name == INTERNAL_SUPERADMIN_GROUP:
        # Superadmins who are not Django is_superuser still need profile tools.
        specs.extend(
            [
                ("accounts", "userprofile", _CRUD),
                ("auth", "user", ("view", "change")),
                ("auth", "group", ("view",)),
                ("organizations", "organization", _CRUD),
            ]
        )

    wanted: set[tuple[str, str]] = set()
    for app_label, model, actions in specs:
        for codename in _permission_codenames(model, actions):
            wanted.add((app_label, codename))

    if not wanted:
        return []

    perms: list[Permission] = []
    for app_label, codename in sorted(wanted):
        perm = Permission.objects.filter(
            content_type__app_label=app_label,
            codename=codename,
        ).first()
        if perm:
            perms.append(perm)
    return perms


def ensure_role_group_permissions() -> dict[str, int]:
    """Create role groups (if needed) and set their Django permissions."""
    counts: dict[str, int] = {}
    group_names = (
        INTERNAL_SUPERADMIN_GROUP,
        INTERNAL_ADMIN_GROUP,
        EXTERNAL_SUPERADMIN_GROUP,
        EXTERNAL_ADMIN_GROUP,
    )
    for name in group_names:
        group, _ = Group.objects.get_or_create(name=name)
        perms = permissions_for_role_group(name)
        group.permissions.set(perms)
        counts[name] = len(perms)
    return counts
