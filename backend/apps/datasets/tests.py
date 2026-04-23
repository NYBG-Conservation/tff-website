from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import UserProfile
from apps.datasets.models import Dataset
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
