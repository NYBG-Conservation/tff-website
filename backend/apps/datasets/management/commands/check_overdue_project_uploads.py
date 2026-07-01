import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.datasets.models import Project, ProjectAlert
from apps.datasets.overdue_uploads import (
    build_overdue_upload_email,
    get_project_recipient_email,
    is_overdue_missing_data,
    overdue_days,
    project_has_qualifying_upload,
    should_send_reminder,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Flag concluded projects overdue for data upload and email project leads (Figshare workflow)."

    def handle(self, *args, **options):
        now = timezone.now()
        today = timezone.localdate()

        checked = 0
        newly_flagged = 0
        reminders_sent = 0
        resolved = 0
        skipped_no_recipient = 0

        candidates = Project.objects.filter(ongoing=False, end_date__isnull=False).select_related("owner")
        for project in candidates:
            checked += 1
            overdue = is_overdue_missing_data(project, today)
            active_alert = project.alerts.filter(
                alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
                status=ProjectAlert.Status.ACTIVE,
            ).first()

            if not overdue:
                if active_alert:
                    active_alert.status = ProjectAlert.Status.RESOLVED
                    active_alert.resolved_at = now
                    active_alert.last_evaluated_at = now
                    active_alert.resolution_note = "Qualifying dataset upload detected."
                    active_alert.save(
                        update_fields=[
                            "status",
                            "resolved_at",
                            "last_evaluated_at",
                            "resolution_note",
                            "updated_at",
                        ]
                    )
                    resolved += 1
                continue

            if not active_alert:
                active_alert = ProjectAlert.objects.create(
                    project=project,
                    alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
                    status=ProjectAlert.Status.ACTIVE,
                    first_triggered_at=now,
                    last_evaluated_at=now,
                )
                newly_flagged += 1
            else:
                active_alert.last_evaluated_at = now
                active_alert.save(update_fields=["last_evaluated_at", "updated_at"])

            if not should_send_reminder(active_alert, now):
                continue

            recipient = get_project_recipient_email(project)
            if not recipient:
                skipped_no_recipient += 1
                logger.warning("Skipping email for project %s — no lead or owner email.", project.pk)
                continue

            day_count = overdue_days(project, today)
            subject, body = build_overdue_upload_email(project, day_count)
            send_mail(
                subject,
                body,
                getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
                [recipient],
                fail_silently=False,
            )
            active_alert.last_emailed_at = now
            active_alert.save(update_fields=["last_emailed_at", "updated_at"])
            reminders_sent += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Overdue upload check complete: "
                f"checked={checked}, newly_flagged={newly_flagged}, "
                f"reminders_sent={reminders_sent}, resolved={resolved}, "
                f"skipped_no_recipient={skipped_no_recipient}"
            )
        )
