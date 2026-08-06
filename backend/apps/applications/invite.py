from __future__ import annotations

import secrets
from typing import Any

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.datasets.models import Project

from .models import ResearchApplication
from .notifications import notify_applicant_portal_invite


class InviteError(Exception):
    """Raised when approve/claim invite cannot proceed."""


def _mint_invite_token() -> str:
    return secrets.token_urlsafe(32)


def approve_and_invite(application: ResearchApplication, staff_user: User) -> ResearchApplication:
    """Mark approved, mint invite token, and email the applicant."""
    if application.invite_accepted_at or application.project_id:
        raise InviteError("This application already has an accepted portal invite / project.")
    if not application.organization_id:
        raise InviteError(
            "Set Organization on the application before Approve & send portal invite."
        )

    application.status = ResearchApplication.Status.APPROVED
    application.reviewed_by = staff_user
    if not application.invite_token:
        application.invite_token = _mint_invite_token()
    application.invite_sent_at = timezone.now()
    application.save(
        update_fields=[
            "status",
            "reviewed_by",
            "invite_token",
            "invite_sent_at",
            "updated_at",
        ]
    )
    notify_applicant_portal_invite(application)
    return application


def resend_invite(application: ResearchApplication) -> ResearchApplication:
    """Re-send a pending invite email (optionally refreshing the token)."""
    if application.invite_accepted_at or application.project_id:
        raise InviteError("Invite already accepted; cannot resend.")
    if not application.organization_id:
        raise InviteError("Set Organization before resending the invite.")
    if application.status != ResearchApplication.Status.APPROVED:
        raise InviteError("Application must be approved before resending an invite.")

    if not application.invite_token:
        application.invite_token = _mint_invite_token()
    application.invite_sent_at = timezone.now()
    application.save(update_fields=["invite_token", "invite_sent_at", "updated_at"])
    notify_applicant_portal_invite(application)
    return application


def _short_title_from_application(application: ResearchApplication) -> str:
    title = (application.project_title or "Untitled project").strip()
    if len(title) <= 255:
        return title
    return title[:252].rstrip() + "..."


def _project_dates(application: ResearchApplication) -> tuple[Any, Any, bool]:
    start = application.start_date or application.anticipated_start_date
    end = application.end_date or application.anticipated_end_date
    ongoing = end is None
    return start, end, ongoing


@transaction.atomic
def claim_invite(token: str, username: str, password: str) -> dict[str, Any]:
    """Create user + Project from a valid invite token. Idempotent against double-claim."""
    token = (token or "").strip()
    username = (username or "").strip()
    if not token:
        raise InviteError("Invite token is required.")
    if not username:
        raise InviteError("Username is required.")

    try:
        application = ResearchApplication.objects.select_for_update().get(invite_token=token)
    except ResearchApplication.DoesNotExist as exc:
        raise InviteError("Invalid or expired invite link.") from exc

    if application.invite_accepted_at or application.project_id:
        raise InviteError("This invite has already been used.")
    if application.invite_is_expired():
        raise InviteError("This invite has expired. Contact forest@nybg.org for a new link.")
    if not application.organization_id:
        raise InviteError("This invite is missing an organization. Contact forest@nybg.org.")
    if application.status != ResearchApplication.Status.APPROVED:
        raise InviteError("This application is not approved.")

    if User.objects.filter(username__iexact=username).exists():
        raise InviteError("That username is already taken. Choose another.")

    try:
        validate_password(password)
    except ValidationError as exc:
        raise InviteError(" ".join(exc.messages)) from exc

    user = User.objects.create_user(
        username=username,
        email=application.email,
        password=password,
        first_name=(application.applicant_name or "").split(" ", 1)[0][:150],
    )
    # Profile created by signal as external_admin; attach organization.
    profile = user.profile
    profile.role = UserProfile.Role.EXTERNAL_ADMIN
    profile.organization = application.organization
    profile.save(update_fields=["role", "organization"])

    start, end, ongoing = _project_dates(application)
    project = Project.objects.create(
        short_title=_short_title_from_application(application),
        full_title=application.project_title[:500],
        description=application.description,
        lead_name=application.applicant_name,
        lead_email=application.email,
        start_date=start,
        end_date=end,
        ongoing=ongoing,
        organization=application.organization,
        owner=user,
        plans_own_doi=True,
        figshare_doi_url="",
        shared_publicly=False,
    )

    application.project = project
    application.invite_accepted_at = timezone.now()
    application.save(update_fields=["project", "invite_accepted_at", "updated_at"])

    return {
        "username": user.username,
        "project_id": project.pk,
        "project_slug": project.slug,
        "application_id": application.pk,
    }
