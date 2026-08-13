from django.contrib import admin, messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .invite import (
    InviteError,
    approve_and_invite,
    ensure_organization_from_institution,
    invite_legacy_applicant,
    resend_invite,
)
from .models import LegacySurvey123Application, ResearchApplication


class LegacySurvey123Filter(admin.SimpleListFilter):
    title = "Legacy (Survey123)"
    parameter_name = "is_legacy"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Survey123 import"),
            ("no", "In-site application"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(Q(legacy_global_id__isnull=True) | Q(legacy_global_id=""))
        if self.value() == "no":
            return queryset.filter(Q(legacy_global_id__isnull=True) | Q(legacy_global_id=""))
        return queryset


class InviteStateFilter(admin.SimpleListFilter):
    title = "Invite state"
    parameter_name = "invite_state"

    def lookups(self, request, model_admin):
        return (
            ("not_invited", "Not invited"),
            ("pending", "Invite pending"),
            ("accepted", "Invite accepted"),
            ("expired", "Invite expired"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "not_invited":
            return queryset.filter(invite_token__isnull=True, invite_accepted_at__isnull=True)
        if value == "pending":
            return queryset.filter(invite_token__isnull=False, invite_accepted_at__isnull=True)
        if value == "accepted":
            return queryset.filter(invite_accepted_at__isnull=False)
        if value == "expired":
            # Approximate: pending invites older than validity window
            cutoff = timezone.now() - timedelta(days=ResearchApplication.INVITE_VALID_DAYS)
            return queryset.filter(
                invite_token__isnull=False,
                invite_accepted_at__isnull=True,
                invite_sent_at__lt=cutoff,
            )
        return queryset


class HasOrganizationFilter(admin.SimpleListFilter):
    title = "Organization set"
    parameter_name = "has_org"

    def lookups(self, request, model_admin):
        return (("yes", "Yes"), ("no", "No"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(organization__isnull=False)
        if self.value() == "no":
            return queryset.filter(organization__isnull=True)
        return queryset


class ResearchApplicationAdminBase(admin.ModelAdmin):
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


@admin.register(ResearchApplication)
class ResearchApplicationAdmin(ResearchApplicationAdminBase):
    list_filter = (
        LegacySurvey123Filter,
        "status",
        "project_type",
        "collection_type",
        "organization",
        "submitted_at",
    )
    actions = (
        "mark_under_review",
        "mark_approved",
        "approve_and_send_portal_invite",
        "resend_portal_invite",
        "mark_declined",
    )

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
        # (auto-creates Organization from Institution when needed).
        if (
            obj.status == ResearchApplication.Status.APPROVED
            and previous_status != ResearchApplication.Status.APPROVED
            and not obj.invite_token
            and not obj.invite_accepted_at
        ):
            try:
                approve_and_invite(obj, request.user, auto_org=True)
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
                approve_and_invite(application, request.user, auto_org=True)
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

    @admin.action(description="Mark selected as declined")
    def mark_declined(self, request, queryset):
        queryset.update(
            status=ResearchApplication.Status.DECLINED,
            reviewed_by=request.user,
            updated_at=timezone.now(),
        )


@admin.register(LegacySurvey123Application)
class LegacySurvey123ApplicationAdmin(ResearchApplicationAdminBase):
    change_list_template = "admin/applications/legacysurvey123application/change_list.html"
    list_display = (
        "project_title",
        "applicant_name",
        "email",
        "institution",
        "organization",
        "status",
        "invite_status",
        "project",
        "submitted_at",
        "legacy_global_id",
    )
    list_filter = (
        InviteStateFilter,
        HasOrganizationFilter,
        "status",
        "project_type",
        "submitted_at",
    )
    actions = (
        "invite_to_portal",
        "resend_portal_invite",
        "create_org_from_institution",
        "mark_declined",
    )
    # Staff browse/edit review fields; application payload stays readable.
    readonly_fields = ResearchApplicationAdminBase.readonly_fields + (
        "applicant_name",
        "title_position",
        "institution",
        "email",
        "phone",
        "address",
        "co_pi",
        "project_title",
        "project_type",
        "description",
        "start_date",
        "end_date",
        "anticipated_start_date",
        "anticipated_end_date",
        "desired_species",
        "collection_type",
        "research_location",
        "plant_tracker_notes",
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
        "attestation_name",
        "attestation_date",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(Q(legacy_global_id__isnull=True) | Q(legacy_global_id=""))

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        not_invited = qs.filter(invite_token__isnull=True, invite_accepted_at__isnull=True).count()
        pending = qs.filter(invite_token__isnull=False, invite_accepted_at__isnull=True).count()
        accepted = qs.filter(invite_accepted_at__isnull=False).count()
        extra_context.update(
            {
                "legacy_total": qs.count(),
                "legacy_not_invited": not_invited,
                "legacy_pending": pending,
                "legacy_accepted": accepted,
            }
        )
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="Invite to portal (auto-org from Institution)")
    def invite_to_portal(self, request, queryset):
        ok = 0
        for application in queryset:
            try:
                invite_legacy_applicant(application, request.user)
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
                f"Sent portal invite for {ok} legacy application(s).",
                messages.SUCCESS,
            )

    @admin.action(description="Create org from Institution only (no email)")
    def create_org_from_institution(self, request, queryset):
        ok = 0
        for application in queryset:
            try:
                ensure_organization_from_institution(application)
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
                f"Set Organization on {ok} application(s) from Institution.",
                messages.SUCCESS,
            )

    @admin.action(description="Mark selected as declined")
    def mark_declined(self, request, queryset):
        queryset.update(
            status=ResearchApplication.Status.DECLINED,
            reviewed_by=request.user,
            updated_at=timezone.now(),
        )
