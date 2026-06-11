# Consolidate PI / contact / lead institution into lead_name, lead_email, organization.

from django.db import migrations, models


def forwards(apps, schema_editor):
    Project = apps.get_model("datasets", "Project")
    for project in Project.objects.all():
        nybg = getattr(project, "nybg_pi_name", "") or ""
        external = getattr(project, "external_pi_name", "") or ""
        if nybg and external and nybg != external:
            project.lead_name = f"{nybg} / {external}"
        else:
            project.lead_name = nybg or external or "Project lead"
        project.lead_email = getattr(project, "contact_email", "") or "unknown@example.org"
        project.save(update_fields=["lead_name", "lead_email"])


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0007_project_summary_description_hero_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="lead_name",
            field=models.CharField(blank=True, help_text="Primary project lead (display name).", max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="lead_email",
            field=models.EmailField(blank=True, help_text="Project lead contact email.", null=True),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="project",
            name="lead_name",
            field=models.CharField(help_text="Primary project lead (display name).", max_length=255),
        ),
        migrations.AlterField(
            model_name="project",
            name="lead_email",
            field=models.EmailField(help_text="Project lead contact email."),
        ),
        migrations.RemoveField(model_name="project", name="nybg_pi_name"),
        migrations.RemoveField(model_name="project", name="external_pi_name"),
        migrations.RemoveField(model_name="project", name="contact_email"),
        migrations.RemoveField(model_name="project", name="lead_institution"),
    ]
