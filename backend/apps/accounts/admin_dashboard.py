"""Django admin index welcome panel: guides and project shortcuts."""

from __future__ import annotations

from django.conf import settings
from django.db.models import Q
from django.urls import reverse

from .roles import get_role, is_internal_staff, is_internal_superadmin
from .models import UserProfile


GUIDES = {
    "partner-intro": {
        "title": "Portal intro (short)",
        "path": "docs/EXTERNAL_ADMIN_INTRO.md",
    },
    "partner-guide": {
        "title": "External partner guide",
        "path": "docs/EXTERNAL_PARTNER_GUIDE.md",
    },
    "operations": {
        "title": "NYBG operations guide",
        "path": "docs/NYBG_OPERATIONS_GUIDE.md",
    },
    "overdue-alerts": {
        "title": "Data-upload reminder spec",
        "path": "backend/OVERDUE_DATA_ALERT_SPEC.md",
    },
}


def _display_name(user) -> str:
    full = (user.get_full_name() or "").strip()
    if full:
        return full
    first = (user.first_name or "").strip()
    return first or user.username


def _guide_links_for_role(role: str | None) -> list[dict]:
    def link(slug: str) -> dict:
        meta = GUIDES[slug]
        return {
            "title": meta["title"],
            "url": reverse("admin-guide", kwargs={"slug": slug}),
        }

    if role == UserProfile.Role.INTERNAL_SUPERADMIN:
        return [link("operations"), link("overdue-alerts")]
    if role == UserProfile.Role.INTERNAL_ADMIN:
        return [link("operations")]
    if role == UserProfile.Role.EXTERNAL_SUPERADMIN:
        return [link("partner-guide"), link("partner-intro")]
    return [link("partner-intro"), link("partner-guide")]


def _welcome_message(user) -> str:
    name = _display_name(user)
    role = get_role(user)
    org = getattr(getattr(user, "profile", None), "organization", None)
    org_name = org.name if org else ""

    if role == UserProfile.Role.INTERNAL_SUPERADMIN:
        return (
            f"Welcome, {name}. You have full access to the research portal, including "
            "website display settings and data-upload follow-up."
        )
    if role == UserProfile.Role.INTERNAL_ADMIN:
        return (
            f"Welcome, {name}. You can manage NYBG Forest projects, datasets, and "
            "research applications."
        )
    if role == UserProfile.Role.EXTERNAL_SUPERADMIN:
        where = f" for {org_name}" if org_name else " for your organization"
        return (
            f"Welcome, {name}. You can view and edit all catalogued Forest projects{where}."
        )
    return (
        f"Welcome, {name}. This portal is where you catalog approved Forest research "
        "and link datasets. You can edit projects you own or are a team member on."
    )


def shortcut_projects_for_user(user, limit: int = 3):
    """Projects the user owns or manages, most recently edited first."""
    from apps.datasets.models import Project

    return list(
        Project.objects.filter(Q(owner=user) | Q(managers=user))
        .distinct()
        .order_by("-updated_at")[:limit]
    )


def build_index_context(request) -> dict:
    user = request.user
    role = get_role(user)
    projects = shortcut_projects_for_user(user)
    shortcuts = []
    for index, project in enumerate(projects, start=1):
        shortcuts.append(
            {
                "hotkey": str(index),
                "title": project.short_title,
                "url": reverse("admin:datasets_project_change", args=[project.pk]),
            }
        )

    extra_links = [
        {"title": "Public research page", "url": f"{settings.FRONTEND_URL.rstrip('/')}/research"},
        {"title": "Public data catalog", "url": f"{settings.FRONTEND_URL.rstrip('/')}/data"},
    ]
    if is_internal_superadmin(user):
        extra_links.insert(
            0,
            {
                "title": "Website display settings",
                "url": reverse("admin:datasets_websitedisplaysettings_changelist"),
            },
        )

    return {
        "tff_welcome_message": _welcome_message(user),
        "tff_guide_links": _guide_links_for_role(role),
        "tff_extra_links": extra_links,
        "tff_project_shortcuts": shortcuts,
        "tff_is_internal": is_internal_staff(user),
        "tff_add_project_url": reverse("admin:datasets_project_add"),
    }


def patch_admin_index() -> None:
    from django.contrib.admin.sites import AdminSite

    if getattr(AdminSite.index, "_tff_patched", False):
        return

    original = AdminSite.index

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(build_index_context(request))
        return original(self, request, extra_context)

    index._tff_patched = True
    AdminSite.index = index
