from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html, format_html_join

from .models import UserProfile
from .role_group_metadata import ROLE_GROUP_META, role_group_blurb


class RoleGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ("permissions",)
    list_display = ("name", "role_summary_column", "member_count")
    search_fields = ("name",)
    ordering = ("name",)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return ("role_guide",)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return ((None, {"fields": ("name",)}),)
        return (
            (None, {"fields": ("name", "role_guide")}),
            (
                "Django permissions",
                {
                    "fields": ("permissions",),
                    "description": (
                        "TFF access is controlled primarily by User profile → Role. "
                        "These Django permissions are optional; most staff rely on role scoping only."
                    ),
                },
            ),
        )

    @admin.display(description="Summary")
    def role_summary_column(self, obj: Group) -> str:
        return role_group_blurb(obj.name)

    @admin.display(description="Members")
    def member_count(self, obj: Group) -> int:
        return obj.user_set.count()

    @admin.display(description="Role guide")
    def role_guide(self, obj: Group) -> str:
        meta = ROLE_GROUP_META.get(obj.name)
        if not meta:
            return format_html(
                "<p><strong>Custom group.</strong> This is not a standard TFF role group. "
                "Platform access is normally set via <em>Accounts → User profiles → Role</em>.</p>"
            )

        deprecated = (
            format_html(
                '<p style="margin:0 0 0.75rem;padding:0.5rem 0.75rem;background:#fff3cd;border:1px solid #ffc107;">'
                "<strong>Deprecated.</strong> Do not assign new users to this group. "
                "Use <code>external_admin</code> on the user profile instead.</p>"
            )
            if meta["deprecated"]
            else ""
        )

        rows = [
            ("Audience", meta["audience"]),
            ("Summary", meta["summary"]),
            ("View", meta["view_scope"]),
            ("Edit", meta["edit_scope"]),
            ("Organization", meta["organization"]),
            (
                "Assign roles",
                "Yes — can promote users via API and user profiles"
                if meta["assign_roles"]
                else "No",
            ),
        ]

        return format_html(
            "{}{}<table style=\"width:100%;max-width:40rem;border-collapse:collapse;\">{}</table>"
            "<p style=\"margin:0.75rem 0 0;font-size:0.9em;color:#555;\">"
            "Set the active role on each user under <strong>Accounts → User profiles</strong>. "
            "Saving a profile syncs membership in this group automatically.</p>",
            deprecated,
            format_html("<p style=\"margin:0 0 0.5rem;\"><strong>{}</strong></p>", meta["title"]),
            format_html_join(
                "",
                "<tr><th style=\"text-align:left;vertical-align:top;padding:0.35rem 0.75rem 0.35rem 0;"
                "width:7rem;border-top:1px solid #ddd;\">{}</th>"
                "<td style=\"padding:0.35rem 0;border-top:1px solid #ddd;\">{}</td></tr>",
                ((label, value) for label, value in rows),
            ),
        )


try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass
admin.site.register(Group, RoleGroupAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "organization")
    list_select_related = ("user", "organization")
    search_fields = ("user__username", "user__email", "organization__name")
    list_filter = ("role", "organization")
    autocomplete_fields = ("organization",)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        formfield = super().formfield_for_choice_field(db_field, request, **kwargs)
        if db_field.name == "role" and formfield is not None:
            formfield.help_text = (
                "Platform role controls project/dataset visibility. "
                "See Authentication → Groups for a full permissions summary of each role."
            )
        return formfield
