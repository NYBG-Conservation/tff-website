# Generated manually for public research/data pages.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0006_remove_projectalert_unique_active_project_alert"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="summary",
            field=models.TextField(
                blank=True,
                help_text="Short teaser shown on the public research project card.",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Longer project description for the public modal. Separate paragraphs with a blank line.",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="hero_image",
            field=models.CharField(
                blank=True,
                help_text="Public site image path or URL (e.g. /images/home/forest-canopy.png).",
                max_length=500,
            ),
        ),
    ]
