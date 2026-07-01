from django.db import migrations

LEAD_EMAIL_REPLACEMENTS = {
    "john@nybg.org": "jzeiger@nybg.org",
    "eve@nybg.org": "ebeaury@nybg.org",
    "brad@nybg.org": "boberle@nybg.org",
}


def forwards(apps, schema_editor):
    Project = apps.get_model("datasets", "Project")
    for old_email, new_email in LEAD_EMAIL_REPLACEMENTS.items():
        Project.objects.filter(lead_email=old_email).update(lead_email=new_email)


def backwards(apps, schema_editor):
    Project = apps.get_model("datasets", "Project")
    for old_email, new_email in LEAD_EMAIL_REPLACEMENTS.items():
        Project.objects.filter(lead_email=new_email).update(lead_email=old_email)


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0013_project_alert_milestones_manual_outreach"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
