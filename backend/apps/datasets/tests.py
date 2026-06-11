from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
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
        self.organization = Organization.objects.create(name="NYBG")
        self.internal_user = User.objects.create_user(username="internal", password="pass12345")
        self.external_user = User.objects.create_user(username="external", password="pass12345")
        self.other_external = User.objects.create_user(username="other", password="pass12345")

        self.internal_user.profile.role = UserProfile.Role.INTERNAL_ADMIN
        self.internal_user.profile.save()
        self.external_user.profile.role = UserProfile.Role.EXTERNAL_PARTNER_ADMIN
        self.external_user.profile.save()
        self.other_external.profile.role = UserProfile.Role.EXTERNAL_PARTNER_ADMIN
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

    def test_internal_user_can_patch_any_dataset(self):
        self.client.force_authenticate(self.internal_user)
        response = self.client.patch(
            reverse("dataset-retrieve-update", kwargs={"pk": self.dataset_other.id}),
            {"title": "Updated By Internal"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dataset_other.refresh_from_db()
        self.assertEqual(self.dataset_other.title, "Updated By Internal")


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
            lead_email="john@nybg.org",
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
            lead_email="brad@nybg.org",
            organization=self.organization,
            owner=self.owner,
        )
        self.assertEqual(project.slug, "forest-soil-cores")

    def test_slugify_strips_punctuation(self):
        self.assertEqual(
            slugify_project_title("2026 Continuous Forest Index!"),
            "2026-continuous-forest-index",
        )

    def test_slug_collision_uses_numeric_suffix(self):
        Project.objects.create(
            short_title="Forest Soil Cores",
            lead_name="Brad",
            lead_email="brad@nybg.org",
            organization=self.organization,
            owner=self.owner,
        )
        second = Project.objects.create(
            short_title="Forest Soil Cores",
            lead_name="Eve",
            lead_email="eve@nybg.org",
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
            lead_email="eve@nybg.org",
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
            hero_image="/images/home/forest-trail.png",
            lead_name="Jane",
            lead_email="jane@nybg.org",
            shared_publicly=True,
            organization=self.organization,
            owner=self.owner,
        )
        self.private_project = Project.objects.create(
            slug="private-study",
            short_title="Private Study",
            lead_name="John",
            lead_email="john@nybg.org",
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

    def test_public_projects_requires_no_auth(self):
        response = self.client.get(reverse("public-project-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["slug"], "public-forest-study")
        self.assertEqual(response.data[0]["description_paragraphs"], ["First paragraph.", "Second paragraph."])
        self.assertEqual(response.data[0]["dataset_ids"], [str(self.public_dataset.id)])

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
