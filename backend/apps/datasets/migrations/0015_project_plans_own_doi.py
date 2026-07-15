from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0014_update_seed_lead_emails"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="plans_own_doi",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Opt out of the Figshare reservation requirement: I plan to publish this data "
                    "with my own DOI (e.g. journal, Dryad, Zenodo). You can still paste a doi.org "
                    "or Figshare URL in the deposit field when available."
                ),
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="figshare_doi_url",
            field=models.URLField(
                blank=True,
                help_text=(
                    "Figshare item URL or reserved DOI link for this project's data deposit. "
                    "Required when creating a new project unless “plans own DOI” is checked."
                ),
                max_length=500,
            ),
        ),
    ]
