from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField(blank=True)
    website_url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name
