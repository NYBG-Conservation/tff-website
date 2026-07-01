"""Human-readable descriptions for Django auth Groups that mirror UserProfile roles."""

from __future__ import annotations

from typing import TypedDict


class RoleGroupMeta(TypedDict):
    title: str
    audience: str
    summary: str
    view_scope: str
    edit_scope: str
    organization: str
    assign_roles: bool
    deprecated: bool


ROLE_GROUP_META: dict[str, RoleGroupMeta] = {
    "internal_superadmin": {
        "title": "Internal Superadmin",
        "audience": "NYBG platform owners and technical leads",
        "summary": "Full access to all organizations, projects, datasets, and user role assignment.",
        "view_scope": "All projects and datasets in the system.",
        "edit_scope": "All projects and datasets; can assign platform roles via API or User profiles.",
        "organization": "None — NYBG-wide (internal role).",
        "assign_roles": True,
        "deprecated": False,
    },
    "internal_admin": {
        "title": "Internal Admin",
        "audience": "NYBG staff managing Forest research and data",
        "summary": "Manage NYBG organization records on the public research and data catalog.",
        "view_scope": "Projects and datasets where organization is New York Botanical Garden.",
        "edit_scope": "Same NYBG-scoped records (projects, datasets, files, publications).",
        "organization": "None — scoped to NYBG organization records only.",
        "assign_roles": False,
        "deprecated": False,
    },
    "external_superadmin": {
        "title": "External Superadmin",
        "audience": "Lead contact at a partner institution",
        "summary": "Oversee all portal records for one partner organization.",
        "view_scope": "All projects and datasets belonging to the user’s home organization.",
        "edit_scope": "All records in that organization.",
        "organization": "Required — must match the partner institution.",
        "assign_roles": False,
        "deprecated": False,
    },
    "external_admin": {
        "title": "External Admin",
        "audience": "Individual external researchers and project leads",
        "summary": "Manage projects and datasets you own or are delegated to manage.",
        "view_scope": "Projects you own, projects where you are a manager, and linked datasets.",
        "edit_scope": "Same owned and delegated records.",
        "organization": "Required — your home institution.",
        "assign_roles": False,
        "deprecated": False,
    },
    "external_partner_admin": {
        "title": "External Partner Admin (legacy)",
        "audience": "Deprecated — do not assign to new users",
        "summary": "Legacy group name from an older role model. Treat as external_admin.",
        "view_scope": "Same as external_admin if any users remain on this group.",
        "edit_scope": "Same as external_admin.",
        "organization": "Required if used.",
        "assign_roles": False,
        "deprecated": True,
    },
}

LIST_BLURB_MAX = 72


def role_group_blurb(group_name: str) -> str:
    meta = ROLE_GROUP_META.get(group_name)
    if not meta:
        return "Custom group (no TFF role guide)"
    text = meta["summary"]
    if meta["deprecated"]:
        text = f"Legacy — {text}"
    if len(text) <= LIST_BLURB_MAX:
        return text
    return f"{text[: LIST_BLURB_MAX - 1].rstrip()}…"
