from django.db import migrations


def delete_legacy_external_partner_admin_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="external_partner_admin").delete()


def noop_reverse(apps, schema_editor):
    # Intentionally do not recreate the removed legacy group.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_sync_model_state"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(delete_legacy_external_partner_admin_group, noop_reverse),
    ]
