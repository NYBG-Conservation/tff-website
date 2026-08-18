import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.datasets.models import Project, ProjectAlert
from apps.datasets.overdue_uploads import (
    alert_milestone_days,
    build_milestone_upload_email,
    clear_manual_outreach_state,
    days_since_project_end,
    ensure_manual_outreach_flag,
    get_project_recipient_email,
    manual_outreach_day,
    next_milestone_to_email,
    project_alerts_are_snoozed,
    project_has_qualifying_upload,
    project_is_concluded_with_end_date,
    resolve_missing_data_alert,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Email project leads at 30/60/90/120 days post-end without linked Figshare data; "
        "flag manual outreach at 60 days. Skips snoozed projects."
    )

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()

        checked = 0
        newly_flagged = 0
        milestone_emails_sent = 0
        manual_outreach_flagged = 0
        resolved = 0
        skipped_snoozed = 0
        skipped_no_recipient = 0

        candidates = Project.objects.filter(ongoing=False, end_date__isnull=False).select_related("owner")
        for project in candidates:
            checked += 1
            if not project_is_concluded_with_end_date(project):
                continue

            days_since = days_since_project_end(project, today)
            if days_since is None:
                continue

            if project_has_qualifying_upload(project):
                active_alert = ProjectAlert.objects.filter(
                    project=project,
                    alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
                    status__in=[ProjectAlert.Status.ACTIVE, ProjectAlert.Status.SNOOZED],
                ).first()
                if active_alert:
                    resolve_missing_data_alert(
                        active_alert, note="Qualifying dataset files linked to Figshare deposit."
                    )
                    resolved += 1
                # Resolve any remaining active/snoozed outreach rows
                for outreach in project.alerts.filter(
                    alert_type=ProjectAlert.AlertType.MANUAL_OUTREACH_REQUIRED,
                    status__in=[ProjectAlert.Status.ACTIVE, ProjectAlert.Status.SNOOZED],
                ):
                    resolve_missing_data_alert(
                        outreach, note="Qualifying dataset files linked to Figshare deposit."
                    )
                    resolved += 1
                if clear_manual_outreach_state(project):
                    resolved += 1
                continue

            if project_alerts_are_snoozed(project):
                skipped_snoozed += 1
                continue

            active_alert = ProjectAlert.objects.filter(
                project=project,
                alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
                status=ProjectAlert.Status.ACTIVE,
            ).first()

            first_milestone = alert_milestone_days()[0] if alert_milestone_days() else 30
            if days_since < first_milestone:
                continue

            if not active_alert:
                active_alert = ProjectAlert.objects.create(
                    project=project,
                    alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
                    status=ProjectAlert.Status.ACTIVE,
                    first_triggered_at=now,
                    last_evaluated_at=now,
                    emailed_milestones=[],
                )
                newly_flagged += 1
            else:
                active_alert.last_evaluated_at = now
                active_alert.save(update_fields=["last_evaluated_at", "updated_at"])

            milestone = next_milestone_to_email(active_alert, days_since)
            if milestone is not None:
                recipient = get_project_recipient_email(project)
                if not recipient:
                    skipped_no_recipient += 1
                    logger.warning("Skipping milestone email for project %s — no lead or owner email.", project.pk)
                else:
                    subject, body = build_milestone_upload_email(project, milestone)
                    send_mail(
                        subject,
                        body,
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient],
                        fail_silently=False,
                    )
                    emailed = sorted(set((active_alert.emailed_milestones or []) + [milestone]))
                    active_alert.emailed_milestones = emailed
                    active_alert.last_emailed_at = now
                    active_alert.save(update_fields=["emailed_milestones", "last_emailed_at", "updated_at"])
                    milestone_emails_sent += 1

            if days_since >= manual_outreach_day():
                had_flag = project.manual_outreach_required
                ensure_manual_outreach_flag(project, now)
                project.refresh_from_db()
                if project.manual_outreach_required and not had_flag:
                    manual_outreach_flagged += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Upload reminder check complete: "
                f"checked={checked}, newly_flagged={newly_flagged}, "
                f"milestone_emails_sent={milestone_emails_sent}, "
                f"manual_outreach_flagged={manual_outreach_flagged}, resolved={resolved}, "
                f"skipped_snoozed={skipped_snoozed}, skipped_no_recipient={skipped_no_recipient}, "
                f"milestones={alert_milestone_days()}, manual_outreach_day={manual_outreach_day()}"
            )
        )
