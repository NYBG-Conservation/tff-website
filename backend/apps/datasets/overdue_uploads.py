"""Evaluate projects that are overdue for associated data uploads (Figshare workflow)."""

from __future__ import annotations

from datetime import date, datetime

from django.conf import settings
from django.utils import timezone

from .figshare import figshare_doi_guide_url
from .models import DatasetFile, Project, ProjectAlert, ProjectFile


def alert_milestone_days() -> list[int]:
    milestones = getattr(settings, "PROJECT_ALERT_MILESTONE_DAYS", [30, 60, 90, 120])
    return sorted({int(day) for day in milestones if int(day) > 0})


def manual_outreach_day() -> int:
    configured = int(getattr(settings, "PROJECT_MANUAL_OUTREACH_DAY", 60))
    milestones = alert_milestone_days()
    return configured if configured in milestones else (milestones[1] if len(milestones) > 1 else 60)


def project_is_concluded_with_end_date(project: Project) -> bool:
    return not project.ongoing and project.end_date is not None


def days_since_project_end(project: Project, today: date | None = None) -> int | None:
    if not project_is_concluded_with_end_date(project):
        return None
    reference = today or timezone.localdate()
    return max(0, (reference - project.end_date).days)


def _figshare_reference_match(project: Project, url: str) -> bool:
    if not url:
        return False
    reference = (project.figshare_doi_url or "").strip().lower().rstrip("/")
    candidate = url.strip().lower().rstrip("/")
    if reference and (reference in candidate or candidate in reference):
        return True
    return "figshare.com" in candidate or "doi.org" in candidate


def _file_record_qualifies(project: Project, file_record) -> bool:
    if file_record.file:
        return True
    return _figshare_reference_match(project, file_record.external_url)


def project_has_qualifying_upload(project: Project) -> bool:
    """True when a dataset-kind project file or linked dataset file has upload/Figshare URL."""
    for file_record in project.project_files.filter(file_kind=ProjectFile.FileKind.DATASET):
        if _file_record_qualifies(project, file_record):
            return True

    dataset_ids = project.datasets.values_list("id", flat=True)
    if not dataset_ids:
        return False
    for file_record in DatasetFile.objects.filter(dataset_id__in=dataset_ids):
        if _file_record_qualifies(project, file_record):
            return True
    return False


def is_overdue_missing_data(project: Project, today: date | None = None) -> bool:
    days_since = days_since_project_end(project, today)
    if days_since is None:
        return False
    first_milestone = alert_milestone_days()[0] if alert_milestone_days() else 30
    return days_since >= first_milestone and not project_has_qualifying_upload(project)


def overdue_days(project: Project, today: date | None = None) -> int:
    """Days past the first upload reminder milestone (0 when not yet overdue)."""
    days_since = days_since_project_end(project, today)
    if days_since is None:
        return 0
    first_milestone = alert_milestone_days()[0] if alert_milestone_days() else 30
    if days_since < first_milestone:
        return 0
    return max(0, days_since - first_milestone)


def milestones_due_for_email(alert: ProjectAlert, days_since_end: int) -> list[int]:
    emailed = {int(day) for day in (alert.emailed_milestones or [])}
    return [day for day in alert_milestone_days() if days_since_end >= day and day not in emailed]


def next_milestone_to_email(alert: ProjectAlert, days_since_end: int) -> int | None:
    due = milestones_due_for_email(alert, days_since_end)
    return due[0] if due else None


def get_project_recipient_email(project: Project) -> str | None:
    lead_email = (project.lead_email or "").strip()
    if lead_email:
        return lead_email
    owner_email = getattr(project.owner, "email", "") or ""
    return owner_email.strip() or None


def django_admin_project_url(project: Project) -> str:
    base = getattr(settings, "DJANGO_API_PUBLIC_URL", "http://127.0.0.1:8000").rstrip("/")
    return f"{base}/admin/datasets/project/{project.pk}/change/"


def build_milestone_upload_email(project: Project, milestone_day: int) -> tuple[str, str]:
    figshare_url = project.figshare_doi_url or "(not recorded — add in Django admin)"
    guide_url = figshare_doi_guide_url()
    admin_url = django_admin_project_url(project)
    end_date = project.end_date.isoformat() if project.end_date else "unknown"
    days_since = days_since_project_end(project) or milestone_day
    milestones = alert_milestone_days()
    last_milestone = milestones[-1] if milestones else 120
    outreach_day = manual_outreach_day()

    if milestone_day >= last_milestone:
        subject = f"[Final notice] Upload project data to Figshare: {project.short_title}"
        deadline_note = (
            "This is the final automated reminder. NYBG staff may continue follow-up "
            "if linked dataset files are still missing."
        )
    elif milestone_day >= outreach_day:
        subject = f"[Reminder] Upload project data to Figshare: {project.short_title}"
        deadline_note = (
            "Please upload and link your data soon. NYBG staff have been notified to "
            "follow up if deposits remain missing."
        )
    else:
        subject = f"[Action needed] Upload project data to Figshare: {project.short_title}"
        deadline_note = "Please upload your datasets and link them from the project record."

    body = f"""Hello,

Your Thain Family Forest research project "{project.short_title}" ended on {end_date}. It has now been {days_since} days since the project concluded and we do not yet see linked dataset files for your Figshare deposit.

{deadline_note}

Figshare deposit: {figshare_url}
Manage project: {admin_url}

Steps:
1. Sign in to Figshare and open your project's reserved item.
2. Upload files and publish or update the deposit when ready.
3. In Django admin, add or update a dataset for this project and attach files (under 100 MB) or paste your Figshare URL as an external link.

Figshare DOI guide: {guide_url}

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


def get_snoozed_missing_data_alert(project: Project) -> ProjectAlert | None:
    return (
        project.alerts.filter(
            alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
            status=ProjectAlert.Status.SNOOZED,
        )
        .order_by("-first_triggered_at")
        .first()
    )


def get_active_manual_outreach_alert(project: Project) -> ProjectAlert | None:
    return (
        project.alerts.filter(
            alert_type=ProjectAlert.AlertType.MANUAL_OUTREACH_REQUIRED,
            status=ProjectAlert.Status.ACTIVE,
        )
        .order_by("-first_triggered_at")
        .first()
    )


def project_alerts_are_snoozed(project: Project) -> bool:
    """True when staff snoozed the missing-data pipeline for this project."""
    return get_snoozed_missing_data_alert(project) is not None


def clear_manual_outreach_state(project: Project) -> bool:
    changed = False
    if project.manual_outreach_required or project.manual_outreach_at:
        project.manual_outreach_required = False
        project.manual_outreach_at = None
        project.save(update_fields=["manual_outreach_required", "manual_outreach_at", "updated_at"])
        changed = True
    outreach_alert = get_active_manual_outreach_alert(project)
    if outreach_alert:
        outreach_alert.status = ProjectAlert.Status.RESOLVED
        outreach_alert.resolved_at = timezone.now()
        outreach_alert.last_evaluated_at = timezone.now()
        outreach_alert.resolution_note = "Qualifying dataset files linked to Figshare deposit."
        outreach_alert.save(
            update_fields=[
                "status",
                "resolved_at",
                "last_evaluated_at",
                "resolution_note",
                "updated_at",
            ]
        )
        changed = True
    return changed


def resolve_missing_data_alert(alert: ProjectAlert, *, note: str) -> None:
    now = timezone.now()
    alert.status = ProjectAlert.Status.RESOLVED
    alert.resolved_at = now
    alert.last_evaluated_at = now
    alert.resolution_note = note
    alert.save(
        update_fields=[
            "status",
            "resolved_at",
            "last_evaluated_at",
            "resolution_note",
            "updated_at",
        ]
    )


def ensure_manual_outreach_flag(project: Project, now: datetime) -> ProjectAlert | None:
    """Keep Project.manual_outreach_* in sync with an active outreach alert at the milestone."""
    outreach_day = manual_outreach_day()
    days_since = days_since_project_end(project, now.date())
    if (
        days_since is None
        or days_since < outreach_day
        or project_has_qualifying_upload(project)
        or project_alerts_are_snoozed(project)
    ):
        return None

    if not project.manual_outreach_required:
        project.manual_outreach_required = True
        project.manual_outreach_at = now
        project.save(update_fields=["manual_outreach_required", "manual_outreach_at", "updated_at"])

    alert = get_active_manual_outreach_alert(project)
    if alert:
        alert.last_evaluated_at = now
        alert.save(update_fields=["last_evaluated_at", "updated_at"])
        return alert

    return ProjectAlert.objects.create(
        project=project,
        alert_type=ProjectAlert.AlertType.MANUAL_OUTREACH_REQUIRED,
        status=ProjectAlert.Status.ACTIVE,
        first_triggered_at=now,
        last_evaluated_at=now,
        resolution_note=f"No linked dataset files {outreach_day} days after project end date.",
    )


def snooze_project_alerts(project: Project, *, note: str = "") -> int:
    """Pause reminder emails and clear the needs-follow-up flag until unsnoozed or data arrives."""
    now = timezone.now()
    note = (note or "Snoozed by NYBG staff.").strip()
    count = 0
    for alert in project.alerts.filter(status=ProjectAlert.Status.ACTIVE):
        alert.status = ProjectAlert.Status.SNOOZED
        alert.last_evaluated_at = now
        alert.resolution_note = note
        alert.save(update_fields=["status", "last_evaluated_at", "resolution_note", "updated_at"])
        count += 1
    if project.manual_outreach_required or project.manual_outreach_at:
        project.manual_outreach_required = False
        project.manual_outreach_at = None
        project.save(update_fields=["manual_outreach_required", "manual_outreach_at", "updated_at"])
    return count


def unsnooze_project_alerts(project: Project) -> int:
    """Re-open snoozed alerts so the daily command resumes emails and outreach flagging."""
    now = timezone.now()
    count = 0
    for alert in project.alerts.filter(status=ProjectAlert.Status.SNOOZED):
        alert.status = ProjectAlert.Status.ACTIVE
        alert.last_evaluated_at = now
        alert.resolved_at = None
        if alert.resolution_note.startswith("Snoozed"):
            alert.resolution_note = ""
        alert.save(
            update_fields=["status", "last_evaluated_at", "resolved_at", "resolution_note", "updated_at"]
        )
        count += 1
    return count
