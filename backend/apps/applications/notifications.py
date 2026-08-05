from __future__ import annotations

import os

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def research_application_notify_emails() -> list[str]:
    raw = getattr(settings, "RESEARCH_APPLICATION_NOTIFY", None) or os.getenv(
        "RESEARCH_APPLICATION_NOTIFY", "forest@nybg.org"
    )
    return [part.strip() for part in raw.split(",") if part.strip()]


def application_admin_url(application_id: int) -> str:
    base = getattr(settings, "DJANGO_API_PUBLIC_URL", "http://127.0.0.1:8000").rstrip("/")
    path = reverse("admin:applications_researchapplication_change", args=[application_id])
    return f"{base}{path}"


def notify_staff_of_application(application) -> None:
    recipients = research_application_notify_emails()
    if not recipients:
        return

    admin_url = application_admin_url(application.pk)
    subject = f"[TFF] New research application: {application.project_title}"
    body = (
        f"A new Thain Family Forest research application was submitted.\n\n"
        f"Title: {application.project_title}\n"
        f"Type: {application.get_project_type_display()}\n"
        f"Applicant: {application.applicant_name}\n"
        f"Institution: {application.institution}\n"
        f"Email: {application.email}\n"
        f"Phone: {application.phone or '(none)'}\n"
        f"Anticipated start: {application.anticipated_start_date or application.start_date or '(none)'}\n"
        f"Anticipated end: {application.anticipated_end_date or application.end_date or '(none)'}\n\n"
        f"Review in admin:\n{admin_url}\n"
    )
    send_mail(
        subject,
        body,
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
        recipients,
        fail_silently=False,
    )


def notify_applicant_confirmation(application) -> None:
    if not application.email:
        return
    subject = "Thain Family Forest — research application received"
    body = (
        f"Dear {application.applicant_name},\n\n"
        f"We received your research application: “{application.project_title}”.\n"
        f"NYBG Forest staff will review it and follow up by email.\n\n"
        f"Questions: forest@nybg.org\n\n"
        f"— Thain Family Forest / NYBG\n"
    )
    send_mail(
        subject,
        body,
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
        [application.email],
        fail_silently=True,
    )
