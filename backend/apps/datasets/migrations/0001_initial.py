import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("organizations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Dataset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "cadence",
                    models.CharField(
                        choices=[("annual", "Annual"), ("one_off", "One Off"), ("continuous", "Continuous")],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("active", "Active"), ("archived", "Archived")],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("additional_research_partners", models.JSONField(blank=True, default=list)),
                ("paper_links", models.JSONField(blank=True, default=list)),
                ("data_collection_start", models.DateField(blank=True, null=True)),
                ("data_collection_end", models.DateField(blank=True, null=True)),
                ("projected_project_end_date", models.DateField(blank=True, null=True)),
                ("metadata_schema_version", models.PositiveIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="datasets",
                        to="organizations.organization",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="owned_datasets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MetadataFieldDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.SlugField(max_length=80)),
                ("label", models.CharField(max_length=120)),
                (
                    "field_type",
                    models.CharField(
                        choices=[
                            ("text", "Text"),
                            ("long_text", "Long Text"),
                            ("number", "Number"),
                            ("integer", "Integer"),
                            ("boolean", "Boolean"),
                            ("date", "Date"),
                            ("datetime", "Datetime"),
                            ("enum", "Enum"),
                            ("url", "URL"),
                        ],
                        max_length=20,
                    ),
                ),
                ("unit", models.CharField(blank=True, max_length=50)),
                ("required", models.BooleanField(default=False)),
                ("allowed_values", models.JSONField(blank=True, default=list)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                (
                    "dataset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="metadata_fields",
                        to="datasets.dataset",
                    ),
                ),
            ],
            options={"ordering": ("sort_order", "id"), "unique_together": {("dataset", "key")}},
        ),
        migrations.CreateModel(
            name="DatasetFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="datasets/%Y/%m/")),
                ("file_name", models.CharField(max_length=255)),
                ("content_type", models.CharField(blank=True, max_length=120)),
                ("version", models.PositiveIntegerField(default=1)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "dataset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="files", to="datasets.dataset"
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="uploaded_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ("-uploaded_at",)},
        ),
        migrations.CreateModel(
            name="DatasetMetadataValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.JSONField()),
                (
                    "dataset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="metadata_values",
                        to="datasets.dataset",
                    ),
                ),
                (
                    "field_definition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="values",
                        to="datasets.metadatafielddefinition",
                    ),
                ),
            ],
            options={"unique_together": {("dataset", "field_definition")}},
        ),
    ]
