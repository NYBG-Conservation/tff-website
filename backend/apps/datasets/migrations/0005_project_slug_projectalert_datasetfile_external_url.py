# Generated manually for database buildout (2026-05-20)

import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def populate_project_slugs(apps, schema_editor):
    Project = apps.get_model("datasets", "Project")
    for project in Project.objects.all():
        if project.slug:
            continue
        base = slugify(project.short_title)[:110] or "project"
        candidate = base
        suffix = 2
        while Project.objects.filter(slug=candidate).exclude(pk=project.pk).exists():
            candidate = f"{base}-{suffix}"
            suffix += 1
        project.slug = candidate
        project.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0004_dataset_expose_on_public_api_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="slug",
            field=models.SlugField(
                blank=True,
                db_index=False,
                help_text="Stable identifier for public research pages and dataset linking (e.g. knotweed-management-study).",
                max_length=120,
            ),
        ),
        migrations.RunPython(populate_project_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="project",
            name="slug",
            field=models.SlugField(
                db_index=False,
                help_text="Stable identifier for public research pages and dataset linking (e.g. knotweed-management-study).",
                max_length=120,
                unique=True,
            ),
        ),
        migrations.CreateModel(
            name="ProjectAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "alert_type",
                    models.CharField(
                        choices=[("missing_data_overdue", "Missing Data Overdue")],
                        max_length=40,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("resolved", "Resolved"), ("snoozed", "Snoozed")],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("first_triggered_at", models.DateTimeField()),
                ("last_evaluated_at", models.DateTimeField()),
                ("last_emailed_at", models.DateTimeField(blank=True, null=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("resolution_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="alerts",
                        to="datasets.project",
                    ),
                ),
            ],
            options={
                "ordering": ("-last_evaluated_at", "-id"),
            },
        ),
        migrations.AlterField(
            model_name="datasetfile",
            name="file",
            field=models.FileField(blank=True, null=True, upload_to="datasets/%Y/%m/"),
        ),
        migrations.AddField(
            model_name="datasetfile",
            name="external_url",
            field=models.URLField(
                blank=True,
                help_text="Use for large assets hosted outside this system (>1 GB governance policy).",
            ),
        ),
    ]
