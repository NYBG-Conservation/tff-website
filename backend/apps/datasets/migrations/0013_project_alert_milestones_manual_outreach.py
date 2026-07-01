from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0012_project_figshare_doi_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="manual_outreach_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When the project was flagged for NYBG staff follow-up after 90 days without linked data.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="manual_outreach_required",
            field=models.BooleanField(
                default=False,
                help_text="Set automatically when a concluded project reaches 90 days post-end without linked dataset files.",
            ),
        ),
        migrations.AddField(
            model_name="projectalert",
            name="emailed_milestones",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Post-end reminder days already emailed for this alert (e.g. [30, 60, 90]).",
            ),
        ),
        migrations.AlterField(
            model_name="projectalert",
            name="alert_type",
            field=models.CharField(
                choices=[
                    ("missing_data_overdue", "Missing Data Overdue"),
                    ("manual_outreach_required", "Manual Outreach Required"),
                ],
                max_length=40,
            ),
        ),
    ]
