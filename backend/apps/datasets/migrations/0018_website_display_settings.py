import django.db.models.deletion
from django.db import migrations, models


HIGHLIGHT_SLUGS = (
    "forest-inventory-transect-study",
    "knotweed-management-study",
    "soil-monitoring",
)


def seed_display_settings(apps, schema_editor):
    Project = apps.get_model("datasets", "Project")
    WebsiteDisplaySettings = apps.get_model("datasets", "WebsiteDisplaySettings")

    settings, _ = WebsiteDisplaySettings.objects.get_or_create(pk=1)
    public = list(Project.objects.filter(shared_publicly=True).order_by("short_title"))
    for index, project in enumerate(public, start=1):
        if project.public_sort_order == 0:
            project.public_sort_order = index * 10
            project.save(update_fields=["public_sort_order"])

    highlights = []
    for slug in HIGHLIGHT_SLUGS:
        project = Project.objects.filter(slug=slug, shared_publicly=True).first()
        if project:
            highlights.append(project)
    if not highlights:
        highlights = public[:3]
    while len(highlights) < 3:
        highlights.append(None)
    settings.highlight_1_id = highlights[0].pk if highlights[0] else None
    settings.highlight_2_id = highlights[1].pk if highlights[1] else None
    settings.highlight_3_id = highlights[2].pk if highlights[2] else None
    settings.save()


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0017_institutional_partners_org_ids"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="public_sort_order",
            field=models.IntegerField(
                default=0,
                help_text="Lower numbers appear first on the public /research directory. Set in Website display settings.",
            ),
        ),
        migrations.CreateModel(
            name="WebsiteDisplaySettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "highlight_1",
                    models.ForeignKey(
                        blank=True,
                        help_text="First card under Research highlights on the public homepage.",
                        limit_choices_to={"shared_publicly": True},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="datasets.project",
                    ),
                ),
                (
                    "highlight_2",
                    models.ForeignKey(
                        blank=True,
                        help_text="Second homepage highlight card.",
                        limit_choices_to={"shared_publicly": True},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="datasets.project",
                    ),
                ),
                (
                    "highlight_3",
                    models.ForeignKey(
                        blank=True,
                        help_text="Third homepage highlight card.",
                        limit_choices_to={"shared_publicly": True},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="datasets.project",
                    ),
                ),
            ],
            options={
                "verbose_name": "Website display settings",
                "verbose_name_plural": "Website display settings",
            },
        ),
        migrations.RunPython(seed_display_settings, migrations.RunPython.noop),
    ]
