# Drop partial unique index when present (from an earlier 0005 revision).

from django.db import migrations


def drop_active_alert_constraint(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor == "sqlite":
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='unique_active_project_alert'"
            )
            if cursor.fetchone():
                schema_editor.execute("DROP INDEX unique_active_project_alert")
    elif connection.vendor == "postgresql":
        schema_editor.execute(
            "ALTER TABLE datasets_projectalert DROP CONSTRAINT IF EXISTS unique_active_project_alert"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0005_project_slug_projectalert_datasetfile_external_url"),
    ]

    operations = [
        migrations.RunPython(drop_active_alert_constraint, migrations.RunPython.noop),
    ]
