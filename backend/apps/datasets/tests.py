from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import UserProfile
from apps.datasets.models import Dataset, DatasetFile, Project, ProjectAlert, ProjectManager
from apps.datasets.slug_utils import generate_unique_project_slug, slugify_project_title
from apps.organizations.models import Organization


class DatasetApiPermissionTests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="New York Botanical Garden")
        self.internal_user = User.objects.create_user(username="internal", password="pass12345")
        self.external_user = User.objects.create_user(username="external", password="pass12345")
        self.other_external = User.objects.create_user(username="other", password="pass12345")

        self.internal_user.profile.role = UserProfile.Role.INTERNAL_ADMIN
        self.internal_user.profile.save()
        self.external_user.profile.role = UserProfile.Role.EXTERNAL_ADMIN
        self.external_user.profile.save()
        self.other_external.profile.role = UserProfile.Role.EXTERNAL_ADMIN
        self.other_external.profile.save()

        self.dataset_external = Dataset.objects.create(
            title="External Dataset",
            cadence=Dataset.Cadence.ANNUAL,
            owner=self.external_user,
            organization=self.organization,
        )
        self.dataset_other = Dataset.objects.create(
            title="Other Dataset",
            cadence=Dataset.Cadence.CONTINUOUS,
            owner=self.other_external,
            organization=self.organization,
        )

    def test_external_user_only_sees_owned_datasets(self):
        self.client.force_authenticate(self.external_user)
        response = self.client.get(reverse("dataset-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.dataset_external.id)

    def test_external_user_cannot_patch_another_users_dataset(self):
        self.client.force_authenticate(self.external_user)
        response = self.client.patch(
            reverse("dataset-retrieve-update", kwargs={"pk": self.dataset_other.id}),
            {"title": "Illegal Update"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_internal_admin_can_patch_nybg_org_dataset(self):
        self.client.force_authenticate(self.internal_user)
        response = self.client.patch(
            reverse("dataset-retrieve-update", kwargs={"pk": self.dataset_other.id}),
            {"title": "Updated By Internal"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DatasetMetadataValidationTests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Partner Org")
        self.user = User.objects.create_user(username="partner", password="pass12345")
        self.client.force_authenticate(self.user)

    def test_rejects_invalid_metadata_value_type(self):
        payload = {
            "title": "Canopy Data",
            "description": "Tree canopy percentages",
            "cadence": Dataset.Cadence.ANNUAL,
            "status": Dataset.Status.DRAFT,
            "organization": self.organization.id,
            "metadata_fields": [
                {
                    "key": "canopy_percent",
                    "label": "Canopy %",
                    "field_type": "number",
                    "unit": "%",
                    "required": True,
                    "allowed_values": [],
                    "sort_order": 0,
                }
            ],
            "metadata_values": [{"field_key": "canopy_percent", "value": "not-a-number"}],
        }
        response = self.client.post(reverse("dataset-list-create"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("metadata_values", response.data)


class ProjectApiPermissionTests(APITestCase):
    def setUp(self):
        self.nybg_org = Organization.objects.create(name="New York Botanical Garden")
        self.other_org = Organization.objects.create(name="Other Org")
        self.internal_user = User.objects.create_user(username="internal_project", password="pass12345")
        self.owner_user = User.objects.create_user(username="owner_user", password="pass12345")
        self.manager_user = User.objects.create_user(username="manager_user", password="pass12345")
        self.unrelated_user = User.objects.create_user(username="unrelated_user", password="pass12345")

        self.internal_user.profile.role = UserProfile.Role.INTERNAL_ADMIN
        self.internal_user.profile.save()

        self.project_nybg = Project.objects.create(
            short_title="NYBG Project",
            lead_name="John",
            lead_email="jzeiger@nybg.org",
            organization=self.nybg_org,
            owner=self.owner_user,
        )
        self.project_other_org = Project.objects.create(
            short_title="Other Project",
            lead_name="Brad",
            lead_email="brad@example.org",
            organization=self.other_org,
            owner=self.owner_user,
        )
        ProjectManager.objects.create(project=self.project_nybg, user=self.manager_user, added_by=self.owner_user)

    def test_internal_admin_only_sees_nybg_projects(self):
        self.client.force_authenticate(self.internal_user)
        response = self.client.get(reverse("project-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(self.project_nybg.id, ids)
        self.assertNotIn(self.project_other_org.id, ids)

    def test_owner_and_manager_visibility(self):
        self.client.force_authenticate(self.owner_user)
        owner_response = self.client.get(reverse("project-list-create"))
        self.assertEqual(owner_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(owner_response.data), 2)

        self.client.force_authenticate(self.manager_user)
        manager_response = self.client.get(reverse("project-list-create"))
        self.assertEqual(manager_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(manager_response.data), 1)
        self.assertEqual(manager_response.data[0]["id"], self.project_nybg.id)

    def test_unrelated_user_cannot_edit_project(self):
        self.client.force_authenticate(self.unrelated_user)
        response = self.client.patch(
            reverse("project-retrieve-update", kwargs={"pk": self.project_nybg.id}),
            {"short_title": "Nope"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_add_and_remove_project_manager(self):
        self.client.force_authenticate(self.owner_user)
        add_response = self.client.post(
            reverse("project-manager-add", kwargs={"pk": self.project_other_org.id}),
            {"username": self.unrelated_user.username},
            format="json",
        )
        self.assertEqual(add_response.status_code, status.HTTP_201_CREATED)

        remove_response = self.client.delete(
            reverse(
                "project-manager-remove",
                kwargs={"pk": self.project_other_org.id, "user_id": self.unrelated_user.id},
            )
        )
        self.assertEqual(remove_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_project_create_defaults_owner(self):
        self.client.force_authenticate(self.owner_user)
        payload = {
            "short_title": "Created Project",
            "lead_name": "Eve",
            "lead_email": "eve@example.org",
            "organization": self.other_org.id,
            "shared_publicly": True,
            "collection_frequency": "annual",
            "update_frequency": "annual",
            "figshare_doi_url": "https://figshare.com/articles/example/12345678",
        }
        response = self.client.post(reverse("project-list-create"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=response.data["id"])
        self.assertEqual(project.owner_id, self.owner_user.id)
        self.assertEqual(project.slug, "created-project")


class ProjectModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="NYBG")
        self.owner = User.objects.create_user(username="owner", password="pass12345")

    def test_project_auto_generates_slug_from_title(self):
        project = Project.objects.create(
            short_title="Forest Soil Cores",
            lead_name="Brad",
            lead_email="boberle@nybg.org",
            organization=self.organization,
            owner=self.owner,
        )
        self.assertEqual(project.slug, "forest-soil-cores")

    def test_explicit_slug_is_preserved_on_create(self):
        project = Project.objects.create(
            short_title="CFI",
            slug="forest-inventory-transect-study",
            lead_name="John",
            lead_email="jzeiger@nybg.org",
            organization=self.organization,
            owner=self.owner,
        )
        self.assertEqual(project.slug, "forest-inventory-transect-study")

    def test_slugify_strips_punctuation(self):
        self.assertEqual(
            slugify_project_title("2026 Continuous Forest Index!"),
            "2026-continuous-forest-index",
        )

    def test_slug_collision_uses_numeric_suffix(self):
        Project.objects.create(
            short_title="Forest Soil Cores",
            lead_name="Brad",
            lead_email="boberle@nybg.org",
            organization=self.organization,
            owner=self.owner,
        )
        second = Project.objects.create(
            short_title="Forest Soil Cores",
            lead_name="Eve",
            lead_email="ebeaury@nybg.org",
            organization=self.organization,
            owner=self.owner,
        )
        self.assertEqual(second.slug, "forest-soil-cores-1")

    def test_generate_unique_slug_truncates_long_titles(self):
        long_title = "A" * 200 + " Study"
        slug = generate_unique_project_slug(long_title)
        self.assertLessEqual(len(slug), 100)
        self.assertTrue(slug.startswith("a-study") or slug.startswith("a"))

    def test_only_one_active_alert_per_project_and_type(self):
        project = Project.objects.create(
            short_title="Overdue Study",
            lead_name="Eve",
            lead_email="ebeaury@nybg.org",
            organization=self.organization,
            owner=self.owner,
        )
        now = timezone.now()
        ProjectAlert.objects.create(
            project=project,
            alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
            status=ProjectAlert.Status.ACTIVE,
            first_triggered_at=now,
            last_evaluated_at=now,
        )
        duplicate = ProjectAlert(
            project=project,
            alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
            status=ProjectAlert.Status.ACTIVE,
            first_triggered_at=now,
            last_evaluated_at=now,
        )
        with self.assertRaises(ValidationError):
            duplicate.save()

        ProjectAlert.objects.create(
            project=project,
            alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
            status=ProjectAlert.Status.RESOLVED,
            first_triggered_at=now,
            last_evaluated_at=now,
            resolved_at=now,
        )


class DatasetFileModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="NYBG")
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.dataset = Dataset.objects.create(
            title="Lidar",
            cadence=Dataset.Cadence.ONE_OFF,
            owner=self.owner,
            organization=self.organization,
        )

    def test_requires_file_or_external_url(self):
        record = DatasetFile(
            dataset=self.dataset,
            file_name="missing",
            uploaded_by=self.owner,
        )
        with self.assertRaises(ValidationError):
            record.full_clean()


class PublicApiTests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="NYBG")
        self.owner = User.objects.create_user(username="public_owner", password="pass12345")
        self.public_project = Project.objects.create(
            slug="public-forest-study",
            short_title="Public Forest Study",
            summary="A public-facing study.",
            description="First paragraph.\n\nSecond paragraph.",
            lead_name="Jane",
            lead_email="jane@nybg.org",
            shared_publicly=True,
            ongoing=True,
            institutional_partners=["Example Partner Lab"],
            organization=self.organization,
            owner=self.owner,
        )
        self.private_project = Project.objects.create(
            slug="private-study",
            short_title="Private Study",
            lead_name="John",
            lead_email="jzeiger@nybg.org",
            shared_publicly=False,
            organization=self.organization,
            owner=self.owner,
        )
        self.public_dataset = Dataset.objects.create(
            title="Public Dataset",
            cadence=Dataset.Cadence.ANNUAL,
            status=Dataset.Status.ACTIVE,
            owner=self.owner,
            organization=self.organization,
            project=self.public_project,
            project_slug=self.public_project.slug,
            expose_on_public_api=True,
        )
        Dataset.objects.create(
            title="Draft Public Flag",
            cadence=Dataset.Cadence.ANNUAL,
            status=Dataset.Status.DRAFT,
            owner=self.owner,
            organization=self.organization,
            project=self.public_project,
            expose_on_public_api=True,
        )
        Dataset.objects.create(
            title="Private Project Dataset",
            cadence=Dataset.Cadence.ANNUAL,
            status=Dataset.Status.ACTIVE,
            owner=self.owner,
            organization=self.organization,
            project=self.private_project,
            expose_on_public_api=True,
        )
        self.public_file = DatasetFile.objects.create(
            dataset=self.public_dataset,
            file_name="survey.csv",
            file_kind=DatasetFile.FileKind.PRIMARY_DATA,
            content_type="text/csv",
            uploaded_by=self.owner,
            expose_on_public_api=True,
            file=SimpleUploadedFile("survey.csv", b"plot,canopy\n1,42", content_type="text/csv"),
        )
        self.external_public_file = DatasetFile.objects.create(
            dataset=self.public_dataset,
            file_name="remote-archive.zip",
            file_kind=DatasetFile.FileKind.PRIMARY_DATA,
            uploaded_by=self.owner,
            expose_on_public_api=True,
            external_url="https://example.org/remote-archive.zip",
        )

    def test_public_projects_requires_no_auth(self):
        response = self.client.get(reverse("public-project-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["slug"], "public-forest-study")
        self.assertEqual(response.data[0]["description_paragraphs"], ["First paragraph.", "Second paragraph."])
        self.assertEqual(response.data[0]["dataset_ids"], [str(self.public_dataset.id)])
        self.assertTrue(response.data[0]["ongoing"])
        self.assertEqual(response.data[0]["institutional_partners"], ["Example Partner Lab"])

    def test_public_datasets_filters_visibility(self):
        response = self.client.get(reverse("public-dataset-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item["title"] for item in response.data]
        self.assertEqual(titles, ["Public Dataset"])

    def test_public_datasets_filter_by_project_slug(self):
        response = self.client.get(reverse("public-dataset-list"), {"project": "public-forest-study"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["project_slug"], "public-forest-study")

    def test_public_datasets_include_download_metadata(self):
        response = self.client.get(reverse("public-dataset-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        files = response.data[0]["files"]
        self.assertEqual(len(files), 2)

        uploaded = next(item for item in files if item["file_name"] == "survey.csv")
        self.assertTrue(uploaded["download_available"])
        self.assertIn("/api/public/datasets/", uploaded["download_url"])
        self.assertIn("/download/", uploaded["download_url"])

        external = next(item for item in files if item["file_name"] == "remote-archive.zip")
        self.assertTrue(external["download_available"])
        self.assertEqual(external["download_url"], "https://example.org/remote-archive.zip")

    def test_public_dataset_file_download_serves_uploaded_file(self):
        response = self.client.get(
            reverse(
                "public-dataset-file-download",
                kwargs={"dataset_pk": self.public_dataset.id, "file_pk": self.public_file.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertEqual(b"".join(response.streaming_content), b"plot,canopy\n1,42")

    def test_public_dataset_file_download_redirects_external_url(self):
        response = self.client.get(
            reverse(
                "public-dataset-file-download",
                kwargs={"dataset_pk": self.public_dataset.id, "file_pk": self.external_public_file.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], "https://example.org/remote-archive.zip")

    def test_public_dataset_file_download_rejects_private_dataset(self):
        private_dataset = Dataset.objects.create(
            title="Hidden Dataset",
            cadence=Dataset.Cadence.ANNUAL,
            status=Dataset.Status.ACTIVE,
            owner=self.owner,
            organization=self.organization,
            project=self.private_project,
            expose_on_public_api=True,
        )
        private_file = DatasetFile.objects.create(
            dataset=private_dataset,
            file_name="hidden.csv",
            uploaded_by=self.owner,
            expose_on_public_api=True,
            file=SimpleUploadedFile("hidden.csv", b"secret", content_type="text/csv"),
        )
        response = self.client.get(
            reverse(
                "public-dataset-file-download",
                kwargs={"dataset_pk": private_dataset.id, "file_pk": private_file.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_dataset_file_download_rejects_mobile_user_agent(self):
        response = self.client.get(
            reverse(
                "public-dataset-file-download",
                kwargs={"dataset_pk": self.public_dataset.id, "file_pk": self.public_file.id},
            ),
            HTTP_USER_AGENT="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FigshareDoiUrlTests(TestCase):
    def test_rejects_missing_url_on_create(self):
        from apps.datasets.figshare import validate_figshare_doi_url

        with self.assertRaises(ValidationError):
            validate_figshare_doi_url("", required=True)

    def test_accepts_figshare_and_doi_hosts(self):
        from apps.datasets.figshare import validate_figshare_doi_url

        self.assertEqual(
            validate_figshare_doi_url("https://figshare.com/articles/example/12345678"),
            "https://figshare.com/articles/example/12345678",
        )
        self.assertEqual(
            validate_figshare_doi_url("https://doi.org/10.6084/m9.figshare.12345678"),
            "https://doi.org/10.6084/m9.figshare.12345678",
        )

    def test_rejects_unrelated_host(self):
        from apps.datasets.figshare import validate_figshare_doi_url

        with self.assertRaises(ValidationError):
            validate_figshare_doi_url("https://example.org/not-figshare")


class OverdueUploadTests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="NYBG")
        self.owner = User.objects.create_user(username="overdue_owner", password="pass12345", email="owner@nybg.org")
        self.client.force_authenticate(self.owner)

    def test_project_create_requires_figshare_url(self):
        payload = {
            "short_title": "No Figshare",
            "lead_name": "Pat",
            "lead_email": "pat@nybg.org",
            "organization": self.organization.id,
        }
        response = self.client.post(reverse("project-list-create"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("figshare_doi_url", response.data)

    def test_project_create_allows_own_doi_opt_out(self):
        payload = {
            "short_title": "Own DOI Path",
            "lead_name": "Pat",
            "lead_email": "pat@nybg.org",
            "organization": self.organization.id,
            "plans_own_doi": True,
        }
        response = self.client.post(reverse("project-list-create"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["plans_own_doi"])
        self.assertEqual(response.data["figshare_doi_url"], "")

    def test_project_create_still_requires_figshare_when_not_opting_out(self):
        payload = {
            "short_title": "Needs Figshare",
            "lead_name": "Pat",
            "lead_email": "pat@nybg.org",
            "organization": self.organization.id,
            "plans_own_doi": False,
        }
        response = self.client.post(reverse("project-list-create"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("figshare_doi_url", response.data)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_overdue_command_flags_project_and_sends_email(self):
        from datetime import timedelta

        from django.core import mail

        project = Project.objects.create(
            short_title="Ended Study",
            lead_name="Pat",
            lead_email="pat@nybg.org",
            organization=self.organization,
            owner=self.owner,
            ongoing=False,
            end_date=timezone.localdate() - timedelta(days=45),
            figshare_doi_url="https://figshare.com/articles/ended-study/999",
        )

        from django.core.management import call_command

        mail.outbox.clear()
        call_command("check_overdue_project_uploads")

        project.refresh_from_db()
        alert = project.alerts.filter(
            alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
            status=ProjectAlert.Status.ACTIVE,
        ).first()
        self.assertIsNotNone(alert)
        self.assertEqual(alert.emailed_milestones, [30])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Figshare", mail.outbox[0].body)
        self.assertIn(project.figshare_doi_url, mail.outbox[0].body)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_manual_outreach_flag_at_90_days(self):
        from datetime import timedelta

        from django.core.management import call_command

        project = Project.objects.create(
            short_title="Stale Study",
            lead_name="Pat",
            lead_email="pat@nybg.org",
            organization=self.organization,
            owner=self.owner,
            ongoing=False,
            end_date=timezone.localdate() - timedelta(days=95),
            figshare_doi_url="https://figshare.com/articles/stale/777",
        )

        call_command("check_overdue_project_uploads")

        project.refresh_from_db()
        self.assertTrue(project.manual_outreach_required)
        self.assertIsNotNone(project.manual_outreach_at)
        self.assertTrue(
            project.alerts.filter(
                alert_type=ProjectAlert.AlertType.MANUAL_OUTREACH_REQUIRED,
                status=ProjectAlert.Status.ACTIVE,
            ).exists()
        )
        missing_alert = project.alerts.get(
            alert_type=ProjectAlert.AlertType.MISSING_DATA_OVERDUE,
            status=ProjectAlert.Status.ACTIVE,
        )
        self.assertEqual(missing_alert.emailed_milestones, [30])

    def test_overdue_resolves_when_dataset_file_added(self):
        from datetime import timedelta

        from django.core.management import call_command

        project = Project.objects.create(
            short_title="Resolved Study",
            lead_name="Pat",
            lead_email="pat@nybg.org",
            organization=self.organization,
            owner=self.owner,
            ongoing=False,
            end_date=timezone.localdate() - timedelta(days=45),
            figshare_doi_url="https://figshare.com/articles/resolved/888",
        )
        dataset = Dataset.objects.create(
            title="Field notes",
            cadence=Dataset.Cadence.ONE_OFF,
            owner=self.owner,
            organization=self.organization,
            project=project,
            project_slug=project.slug,
        )
        DatasetFile.objects.create(
            dataset=dataset,
            file_name="notes.csv",
            uploaded_by=self.owner,
            external_url="https://figshare.com/articles/resolved/888",
        )

        call_command("check_overdue_project_uploads")
        self.assertFalse(project.alerts.filter(status=ProjectAlert.Status.ACTIVE).exists())
        project.refresh_from_db()
        self.assertFalse(project.manual_outreach_required)
