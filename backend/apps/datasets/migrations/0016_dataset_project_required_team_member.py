from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_dataset_projects(apps, schema_editor):
    Dataset = apps.get_model("datasets", "Dataset")
    Project = apps.get_model("datasets", "Project")
    Organization = apps.get_model("organizations", "Organization")
    User = apps.get_model(settings.AUTH_USER_MODEL)

    for dataset in Dataset.objects.filter(project__isnull=True):
        project = None
        if dataset.project_slug:
            project = Project.objects.filter(slug=dataset.project_slug).first()
        if project is None and dataset.organization_id:
            project = (
                Project.objects.filter(organization_id=dataset.organization_id)
                .order_by("id")
                .first()
            )
        if project is None:
            org = None
            if dataset.organization_id:
                org = Organization.objects.filter(pk=dataset.organization_id).first()
            if org is None:
                org, _ = Organization.objects.get_or_create(name="Unassigned Datasets")
            owner = None
            if dataset.owner_id:
                owner = User.objects.filter(pk=dataset.owner_id).first()
            if owner is None:
                owner = User.objects.order_by("id").first()
            if owner is None:
                continue
            project = Project.objects.create(
                short_title=f"Recovered: {dataset.title}"[:255],
                lead_name=owner.username,
                lead_email=owner.email or f"{owner.username}@example.com",
                organization=org,
                owner=owner,
                plans_own_doi=True,
            )
        dataset.project = project
        dataset.save(update_fields=["project"])


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0015_project_plans_own_doi"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="projectmanager",
            options={
                "ordering": ("-created_at",),
                "verbose_name": "Team member",
                "verbose_name_plural": "Team members",
            },
        ),
        migrations.RunPython(backfill_dataset_projects, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="dataset",
            name="owner",
            field=models.ForeignKey(
                help_text="Set automatically to the user who creates the dataset.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="owned_datasets",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="dataset",
            name="project",
            field=models.ForeignKey(
                help_text="Required. Every dataset belongs to a research project.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="datasets",
                to="datasets.project",
            ),
        ),
        migrations.AlterField(
            model_name="datasetfile",
            name="uploaded_by",
            field=models.ForeignKey(
                help_text="Set automatically to the user who uploads the file.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="uploaded_files",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
