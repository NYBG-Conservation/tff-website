from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0011_remove_project_hero_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="figshare_doi_url",
            field=models.URLField(
                blank=True,
                help_text=(
                    "Figshare item URL or reserved DOI link for this project's data deposit. "
                    "Required when creating a new project."
                ),
                max_length=500,
            ),
        ),
    ]
