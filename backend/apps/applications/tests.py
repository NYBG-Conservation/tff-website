from datetime import date
from pathlib import Path

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.applications.models import ResearchApplication


def _valid_payload(**overrides):
    payload = {
        "website": "",
        "applicant_name": "Ada Researcher",
        "title_position": "Postdoc",
        "institution": "Example University",
        "email": "ada@example.edu",
        "phone": "555-0100",
        "address": "1 Main St",
        "co_pi": "",
        "project_title": "Canopy study",
        "project_type": ResearchApplication.ProjectType.ONSITE_RESEARCH,
        "description": "Study of canopy gaps.",
        "anticipated_start_date": "2026-09-01",
        "anticipated_end_date": "2026-09-15",
        "research_location": "Thain Family Forest plot A",
        "funding_sources": "Internal",
        "attestation_name": "Ada Researcher",
        "attestation_date": "2026-08-01",
    }
    payload.update(overrides)
    return payload


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PublicResearchApplicationApiTests(APITestCase):
    def test_creates_application_and_notifies(self):
        mail.outbox.clear()
        response = self.client.post(
            reverse("public-research-application-create"),
            _valid_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResearchApplication.objects.count(), 1)
        app = ResearchApplication.objects.get()
        self.assertEqual(app.status, ResearchApplication.Status.SUBMITTED)
        self.assertEqual(app.project_title, "Canopy study")
        # Staff notify + applicant confirmation
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertTrue(any("New research application" in m.subject for m in mail.outbox))
        self.assertTrue(any(app.email in m.to for m in mail.outbox))

    def test_honeypot_rejects_bots(self):
        response = self.client.post(
            reverse("public-research-application-create"),
            _valid_payload(website="http://spam.example"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ResearchApplication.objects.count(), 0)

    def test_plant_material_requires_species(self):
        response = self.client.post(
            reverse("public-research-application-create"),
            _valid_payload(
                project_type=ResearchApplication.ProjectType.PLANT_MATERIAL,
                desired_species="",
                research_location="",
                collection_type=ResearchApplication.CollectionType.ON_SITE,
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("desired_species", response.data)


class ImportSurvey123ApplicationsTests(TestCase):
    def test_import_idempotent_on_global_id(self):
        csv_path = Path(__file__).parent / "fixtures" / "survey123_sample.csv"
        call_command("import_survey123_applications", str(csv_path))
        self.assertEqual(ResearchApplication.objects.count(), 1)
        app = ResearchApplication.objects.get()
        self.assertEqual(app.legacy_global_id, "56888751-7493-443b-8494-d62dfe2ebf7c")
        self.assertEqual(app.applicant_name, "Zhang Zhongshuai")
        self.assertEqual(app.project_type, ResearchApplication.ProjectType.PLANT_MATERIAL)
        self.assertEqual(app.attestation_date, date(2023, 8, 15))

        call_command("import_survey123_applications", str(csv_path))
        self.assertEqual(ResearchApplication.objects.count(), 1)

        call_command("import_survey123_applications", str(csv_path), update=True)
        self.assertEqual(ResearchApplication.objects.count(), 1)
