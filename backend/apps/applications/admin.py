from django.contrib import admin, messages
from django.utils import timezone

from .invite import InviteError, approve_and_invite, resend_invite
from .models import ResearchApplication


@admin.register(ResearchApplication)
class ResearchApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "project_title",
        "applicant_name",
        "institution",
        "email",
        "organization",
        "project_type",
        "status",
        "invite_status",
        "submitted_at",
    )
    list_filter = ("status", "project_type", "collection_type", "organization", "submitted_at")
    search_fields = (
        "project_title",
        "applicant_name",
        "email",
        "institution",
        "legacy_global_id",
    )
    autocomplete_fields = ("organization", "project", "reviewed_by")
    readonly_fields = (
        "submitted_at",
        "created_at",
        "updated_at",
        "legacy_global_id",
        "invite_token",
        "invite_sent_at",
        "invite_accepted_at",
        "invite_status",
    )
    date_hierarchy = "submitted_at"
    actions = (
        "mark_under_review",
        "mark_approved",
        "approve_and_send_portal_invite",
        "resend_portal_invite",
        "mark_declined",
    )
    fieldsets = (
        (
            "Review",
            {
                "fields": (
                    "status",
                    "organization",
                    "reviewed_by",
                    "review_notes",
                    "project",
                    "invite_status",
                    "invite_token",
                    "invite_sent_at",
                    "invite_accepted_at",
                    "submitted_at",
                    "created_at",
                    "updated_at",
                    "legacy_global_id",
                )
            },
        ),
        (
            "Applicant",
            {
                "fields": (
                    "applicant_name",
                    "title_position",
                    "institution",
                    "email",
                    "phone",
                    "address",
                    "co_pi",
                )
            },
        ),
        (
            "Project",
            {
                "fields": (
                    "project_title",
                    "project_type",
                    "description",
                    "start_date",
                    "end_date",
                    "anticipated_start_date",
                    "anticipated_end_date",
                )
            },
        ),
        (
            "Collection / location",
            {
                "fields": (
                    "desired_species",
                    "collection_type",
                    "research_location",
                    "plant_tracker_notes",
                )
            },
        ),
        (
            "Operations & risk",
            {
                "fields": (
                    "abiotic_variables",
                    "biotic_variables",
                    "funding_sources",
                    "wildlife_permits",
                    "nybg_infrastructure",
                    "site_visits",
                    "visitor_impacts",
                    "research_sensitivity",
                    "resources",
                    "publications",
                    "additional_comments",
                )
            },
        ),
        ("Attestation", {"fields": ("attestation_name", "attestation_date")}),
    )

    @admin.display(description="Invite")
    def invite_status(self, obj: ResearchApplication) -> str:
        if obj.invite_accepted_at:
            return "Accepted"
        if obj.invite_token and obj.invite_is_expired():
            return "Expired"
        if obj.invite_is_pending():
            return "Pending"
        return "—"

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change and obj.pk:
            previous_status = (
                ResearchApplication.objects.filter(pk=obj.pk)
                .values_list("status", flat=True)
                .first()
            )
        super().save_model(request, obj, form, change)

        # Saving with status → Approved and no invite yet runs the invite path
        # when Organization is set (same as Approve & send portal invite).
        if (
            obj.status == ResearchApplication.Status.APPROVED
            and previous_status != ResearchApplication.Status.APPROVED
            and not obj.invite_token
            and not obj.invite_accepted_at
            and obj.organization_id
        ):
            try:
                approve_and_invite(obj, request.user)
                self.message_user(
                    request,
                    "Portal invite emailed to the applicant.",
                    messages.SUCCESS,
                )
            except InviteError as exc:
                self.message_user(request, str(exc), messages.ERROR)

    @admin.action(description="Mark selected as under review")
    def mark_under_review(self, request, queryset):
        queryset.update(
            status=ResearchApplication.Status.UNDER_REVIEW,
            reviewed_by=request.user,
            updated_at=timezone.now(),
        )

    @admin.action(description="Mark selected as approved (status only, no invite)")
    def mark_approved(self, request, queryset):
        queryset.update(
            status=ResearchApplication.Status.APPROVED,
            reviewed_by=request.user,
            updated_at=timezone.now(),
        )
        self.message_user(
            request,
            "Marked approved without sending a portal invite.",
            messages.INFO,
        )

    @admin.action(description="Approve & send portal invite")
    def approve_and_send_portal_invite(self, request, queryset):
        ok = 0
        for application in queryset:
            try:
                approve_and_invite(application, request.user)
                ok += 1
            except InviteError as exc:
                self.message_user(
                    request,
                    f"{application}: {exc}",
                    messages.ERROR,
                )
        if ok:
            self.message_user(
                request,
                f"Sent portal invite for {ok} application(s).",
                messages.SUCCESS,
            )

    @admin.action(description="Resend portal invite")
    def resend_portal_invite(self, request, queryset):
        ok = 0
        for application in queryset:
            try:
                resend_invite(application)
                ok += 1
            except InviteError as exc:
                self.message_user(
                    request,
                    f"{application}: {exc}",
                    messages.ERROR,
                )
        if ok:
            self.message_user(
                request,
                f"Resent portal invite for {ok} application(s).",
                messages.SUCCESS,
            )

    @admin.action(description="Mark selected as declined")
    def mark_declined(self, request, queryset):
        queryset.update(
            status=ResearchApplication.Status.DECLINED,
            reviewed_by=request.user,
            updated_at=timezone.now(),
        )
