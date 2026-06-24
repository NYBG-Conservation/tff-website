from django.db import migrations, models
import django.db.models.deletion


def migrate_legacy_external_role(apps, schema_editor):
    UserProfile = apps.get_model("accounts", "UserProfile")
    UserProfile.objects.filter(role="external_partner_admin").update(role="external_admin")


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                help_text="Home organization for external roles. Empty for internal roles.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="member_profiles",
                to="organizations.organization",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                choices=[
                    ("internal_superadmin", "Internal Superadmin"),
                    ("internal_admin", "Internal Admin"),
                    ("external_superadmin", "External Superadmin"),
                    ("external_admin", "External Admin"),
                    ("external_partner_admin", "External Partner Admin (legacy)"),
                ],
                default="external_admin",
                max_length=32,
            ),
        ),
        migrations.RunPython(migrate_legacy_external_role, migrations.RunPython.noop),
    ]
