from django.db import migrations, models


def convert_partner_names_to_ids(apps, schema_editor):
    Project = apps.get_model("datasets", "Project")
    Organization = apps.get_model("organizations", "Organization")

    for project in Project.objects.all().iterator():
        raw = project.institutional_partners or []
        if not isinstance(raw, list) or not raw:
            continue
        ids: list[int] = []
        changed = False
        for item in raw:
            if isinstance(item, int) or (isinstance(item, str) and str(item).isdigit()):
                org_id = int(item)
                if Organization.objects.filter(pk=org_id).exists():
                    ids.append(org_id)
                changed = True
                continue
            if isinstance(item, dict) and item.get("id") is not None:
                org_id = int(item["id"])
                if Organization.objects.filter(pk=org_id).exists():
                    ids.append(org_id)
                changed = True
                continue
            if isinstance(item, str) and item.strip():
                name = item.strip()
                org = Organization.objects.filter(name__iexact=name).first()
                if org is None:
                    org = Organization.objects.create(name=name)
                ids.append(org.id)
                changed = True
        seen: set[int] = set()
        unique_ids: list[int] = []
        for org_id in ids:
            if org_id not in seen:
                seen.add(org_id)
                unique_ids.append(org_id)
        if changed or unique_ids != raw:
            project.institutional_partners = unique_ids
            project.save(update_fields=["institutional_partners"])


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0016_dataset_project_required_team_member"),
        ("organizations", "0002_organization_contact_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="institutional_partners",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="List of Organization primary keys (integers) for partner institutions.",
            ),
        ),
        migrations.RunPython(convert_partner_names_to_ids, migrations.RunPython.noop),
    ]
