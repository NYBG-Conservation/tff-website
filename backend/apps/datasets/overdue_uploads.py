"""Evaluate projects that are overdue for associated data uploads."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from django.conf import settings
from django.utils import timezone

from .figshare import figshare_doi_guide_url
from .models import DatasetFile, Project, ProjectAlert


def project_has_qualifying_upload(project: Project) -> bool:
    """True when the project has at least one dataset file (upload or external link)."""
    dataset_ids = project.datasets.values_list("id", flat=True)
    if not dataset_ids:
        return False
    return DatasetFile.objects.filter(dataset_id__in=dataset_ids).exists()


def project_overdue_start_date(project: Project, today: date | None = None) -> date | None:
    if project.ongoing or not project.end_date:
        return None
    overdue_days = getattr(settings, "PROJECT_OVERDUE_DAYS", 30)
    threshold = project.end_date + timedelta(days=overdue_days)
    reference = today or timezone.localdate()
    if reference < threshold:
        return None
    return threshold


def overdue_days(project: Project, today: date | None = None) -> int:
    threshold = project_overdue_start_date(project, today)
    if not threshold:
        return 0
    reference = today or timezone.localdate()
    return max(0, (reference - threshold).days)


def is_overdue_missing_data(project: Project, today: date | None = None) -> bool:
    if project_overdue_start_date(project, today) is None:
        return False
    return not project_has_qualifying_upload(project)


def get_project_recipient_email(project: Project) -> str | None:
    lead_email = (project.lead_email or "").strip()
    if lead_email:
        return lead_email
    owner_email = getattr(project.owner, "email", "") or ""
    owner_email = owner_email.strip()
    return owner_email or None


def django_admin_project_url(project: Project) -> str:
    base = getattr(settings, "DJANGO_API_PUBLIC_URL", "http://127.0.0.1:8000").rstrip("/")
    return f"{base}/admin/datasets/project/{project.pk}/change/"


def build_overdue_upload_email(project: Project, overdue_day_count: int) -> tuple[str, str]:
    figshare_url = project.figshare_doi_url or "(not recorded — add in Django admin)"
    guide_url = figshare_doi_guide_url()
    admin_url = django_admin_project_url(project)
    end_date = project.end_date.isoformat() if project.end_date else "unknown"

    subject = f"[Action needed] Upload project data to Figshare: {project.short_title}"
    body = f"""Hello,

Your Thain Family Forest research project "{project.short_title}" ended on {end_date} and associated data has not yet been recorded on this site.

Please upload your datasets to your Figshare deposit and link them from the project record:

  Figshare deposit: {figshare_url}
  Manage project: {admin_url}

Steps:
1. Sign in to Figshare and open your project's reserved item.
2. Upload files and publish or update the deposit when ready.
3. In Django admin, add a dataset for this project and attach files (under 100 MB) or paste the Figshare URL as an external link for larger archives.

If you have not reserved a Figshare DOI yet, follow NYBG's guide:
  {guide_url}

This reminder will repeat every {getattr(settings, "PROJECT_ALERT_REMINDER_DAYS", 7)} days until data is linked or the alert is resolved.

Thank you,
Thain Family Forest data team
"""
    return subject, body


def get_active_missing_data_alert(project: Project) -> ProjectAlert | None:
    return (
        project.alerts.filter(
            alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
            status=ProjectAlert.Status.ACTIVE,
        )
        .order_by("-first_triggered_at")
        .first()
    )


def should_send_reminder(alert: ProjectAlert, now: datetime) -> bool:
    if alert.last_emailed_at is None:
        return True
    reminder_days = getattr(settings, "PROJECT_ALERT_REMINDER_DAYS", 7)
    return alert.last_emailed_at <= now - timedelta(days=reminder_days)
