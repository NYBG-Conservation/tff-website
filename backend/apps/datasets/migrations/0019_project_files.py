import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


OLD_TO_NEW_FILE_KIND = {
    "primary_data": "dataset",
    "documentation": "extramural_documents",
    "code": "other",
    "derived_output": "other",
    "image_media": "public_infographic",
    "other": "other",
}


def remap_dataset_file_kinds(apps, schema_editor):
    DatasetFile = apps.get_model("datasets", "DatasetFile")
    for old, new in OLD_TO_NEW_FILE_KIND.items():
        DatasetFile.objects.filter(file_kind=old).update(file_kind=new)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("datasets", "0018_website_display_settings"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(blank=True, null=True, upload_to="project_files/%Y/%m/")),
                (
                    "external_url",
                    models.URLField(
                        blank=True,
                        help_text="Use for large assets hosted outside this system (e.g. Figshare) or files over ~100 MB.",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        help_text="Optional display title. Defaults to the file name.",
                        max_length=255,
                    ),
                ),
                ("file_name", models.CharField(blank=True, max_length=255)),
                (
                    "file_kind",
                    models.CharField(
                        choices=[
                            ("peer_reviewed", "Peer-reviewed publication"),
                            ("dataset", "Dataset"),
                            ("presentation", "Presentation"),
                            ("extramural_documents", "Extramural documents / methods / summary"),
                            ("public_infographic", "Public infographic"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=40,
                    ),
                ),
                ("content_type", models.CharField(blank=True, max_length=120)),
                ("notes", models.TextField(blank=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "expose_on_public_api",
                    models.BooleanField(
                        default=False,
                        help_text="When enabled, this file can appear on the public research project page.",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="project_files",
                        to="datasets.project",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        help_text="Set automatically to the user who uploads the file.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="uploaded_project_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Project file",
                "verbose_name_plural": "Project files",
                "ordering": ("file_kind", "-uploaded_at"),
            },
        ),
        migrations.AlterModelOptions(
            name="dataset",
            options={"verbose_name": "Dataset catalog entry", "verbose_name_plural": "Dataset catalog"},
        ),
        migrations.AlterField(
            model_name="datasetfile",
            name="file_kind",
            field=models.CharField(
                choices=[
                    ("peer_reviewed", "Peer-reviewed publication"),
                    ("dataset", "Dataset"),
                    ("presentation", "Presentation"),
                    ("extramural_documents", "Extramural documents / methods / summary"),
                    ("public_infographic", "Public infographic"),
                    ("other", "Other"),
                ],
                default="dataset",
                max_length=40,
            ),
        ),
        migrations.RunPython(remap_dataset_file_kinds, migrations.RunPython.noop),
    ]
