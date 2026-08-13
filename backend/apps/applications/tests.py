from datetime import date
from pathlib import Path

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.applications.invite import (
    InviteError,
    approve_and_invite,
    claim_invite,
    ensure_organization_from_institution,
    invite_legacy_applicant,
)
from apps.applications.models import LegacySurvey123Application, ResearchApplication
from apps.datasets.models import Project
from apps.organizations.models import Organization


def _valid_payload(**overrides):
    payload = {
        "website": "",
        "organization_name": "Example University",
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


def _make_application(**overrides) -> ResearchApplication:
    defaults = {
        "applicant_name": "Ada Researcher",
        "institution": "Example University",
        "email": "ada@example.edu",
        "project_title": "Canopy study",
        "project_type": ResearchApplication.ProjectType.ONSITE_RESEARCH,
        "description": "Study of canopy gaps.",
        "research_location": "Plot A",
        "attestation_name": "Ada Researcher",
        "attestation_date": date(2026, 8, 1),
    }
    defaults.update(overrides)
    return ResearchApplication.objects.create(**defaults)


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
        self.assertIsNotNone(app.organization_id)
        self.assertEqual(app.organization.name, "Example University")
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertTrue(any("New research application" in m.subject for m in mail.outbox))
        self.assertTrue(any(app.email in m.to for m in mail.outbox))

    def test_requires_organization(self):
        response = self.client.post(
            reverse("public-research-application-create"),
            _valid_payload(organization_name="", organization_id=None),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ResearchApplication.objects.count(), 0)

    def test_selects_existing_organization_by_id(self):
        org = Organization.objects.create(name="Existing College")
        response = self.client.post(
            reverse("public-research-application-create"),
            _valid_payload(organization_id=org.id, organization_name=""),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        app = ResearchApplication.objects.get()
        self.assertEqual(app.organization_id, org.id)
        self.assertEqual(Organization.objects.filter(name="Existing College").count(), 1)

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


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FRONTEND_URL="http://testserver",
)
class ApproveInviteClaimTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Example University")
        self.staff = User.objects.create_user(username="nybgstaff", password="StaffPass123!")
        self.application = _make_application()

    def test_approve_without_org_or_institution_errors(self):
        self.application.institution = ""
        self.application.organization = None
        self.application.save(update_fields=["institution", "organization"])
        with self.assertRaises(InviteError):
            approve_and_invite(self.application, self.staff, auto_org=True)
        self.application.refresh_from_db()
        self.assertIsNone(self.application.invite_token)
        self.assertEqual(len(mail.outbox), 0)

    def test_approve_auto_creates_org_from_institution(self):
        mail.outbox.clear()
        self.application.organization = None
        self.application.institution = "Example University"
        self.application.save(update_fields=["organization", "institution"])
        # Matching existing org case-insensitively
        approve_and_invite(self.application, self.staff, auto_org=True)
        self.application.refresh_from_db()
        self.assertEqual(self.application.organization_id, self.org.id)
        self.assertTrue(self.application.invite_token)
        self.assertEqual(len(mail.outbox), 1)

    def test_approve_creates_new_org_when_institution_unknown(self):
        self.application.organization = None
        self.application.institution = "Brand New College"
        self.application.save(update_fields=["organization", "institution"])
        approve_and_invite(self.application, self.staff, auto_org=True)
        self.application.refresh_from_db()
        self.assertIsNotNone(self.application.organization_id)
        self.assertEqual(self.application.organization.name, "Brand New College")

    def test_approve_and_invite_sends_email(self):
        mail.outbox.clear()
        self.application.organization = self.org
        self.application.save(update_fields=["organization"])
        approve_and_invite(self.application, self.staff)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, ResearchApplication.Status.APPROVED)
        self.assertTrue(self.application.invite_token)
        self.assertIsNotNone(self.application.invite_sent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("approved", mail.outbox[0].subject.lower())
        self.assertIn(self.application.invite_token, mail.outbox[0].body)

    def test_legacy_invite_uses_legacy_email_copy(self):
        mail.outbox.clear()
        self.application.legacy_global_id = "legacy-gid-001"
        self.application.organization = None
        self.application.institution = "Example University"
        self.application.save(update_fields=["legacy_global_id", "organization", "institution"])
        invite_legacy_applicant(self.application, self.staff)
        self.application.refresh_from_db()
        self.assertTrue(self.application.invite_token)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("new research portal", mail.outbox[0].subject.lower())
        self.assertIn("do not need to re-apply", mail.outbox[0].body.lower())

    def test_invite_legacy_requires_global_id(self):
        self.application.legacy_global_id = None
        self.application.save(update_fields=["legacy_global_id"])
        with self.assertRaises(InviteError):
            invite_legacy_applicant(self.application, self.staff)

    def test_ensure_organization_idempotent(self):
        self.application.organization = None
        self.application.institution = "example university"
        self.application.save(update_fields=["organization", "institution"])
        org1 = ensure_organization_from_institution(self.application)
        org2 = ensure_organization_from_institution(self.application)
        self.assertEqual(org1.id, self.org.id)
        self.assertEqual(org2.id, self.org.id)
        self.assertEqual(Organization.objects.filter(name__iexact="example university").count(), 1)

    def test_status_only_approve_does_not_invite(self):
        mail.outbox.clear()
        self.application.status = ResearchApplication.Status.APPROVED
        self.application.reviewed_by = self.staff
        self.application.save()
        self.assertIsNone(self.application.invite_token)
        self.assertEqual(len(mail.outbox), 0)

    def test_claim_creates_user_and_project(self):
        self.application.organization = self.org
        self.application.save(update_fields=["organization"])
        approve_and_invite(self.application, self.staff)
        token = self.application.invite_token

        response = self.client.post(
            reverse("public-research-application-invite-claim"),
            {
                "token": token,
                "username": "ada_researcher",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "ada_researcher")

        user = User.objects.get(username="ada_researcher")
        self.assertEqual(user.profile.organization_id, self.org.id)
        self.assertTrue(user.is_staff)

        self.application.refresh_from_db()
        self.assertIsNotNone(self.application.invite_accepted_at)
        self.assertIsNotNone(self.application.project_id)
        project = Project.objects.get(pk=self.application.project_id)
        self.assertEqual(project.owner_id, user.id)
        self.assertEqual(project.organization_id, self.org.id)
        self.assertTrue(project.plans_own_doi)
        self.assertEqual(project.lead_email, "ada@example.edu")

        response2 = self.client.post(
            reverse("public-research-application-invite-claim"),
            {
                "token": token,
                "username": "ada_other",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            },
            format="json",
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.filter(username="ada_other").count(), 0)

    def test_claim_invite_helper_idempotent_guard(self):
        self.application.organization = self.org
        self.application.save(update_fields=["organization"])
        approve_and_invite(self.application, self.staff)
        claim_invite(self.application.invite_token, "ada1", "SecurePass123!")
        with self.assertRaises(InviteError):
            claim_invite(self.application.invite_token, "ada2", "SecurePass123!")


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
        self.assertEqual(LegacySurvey123Application.objects.count(), 1)
