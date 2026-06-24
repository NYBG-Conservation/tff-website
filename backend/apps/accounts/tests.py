from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import UserProfile
from apps.organizations.models import Organization


class AssignRoleApiTests(APITestCase):
    def setUp(self):
        self.nybg = Organization.objects.create(name="New York Botanical Garden")
        self.partner = Organization.objects.create(name="Bronx River Alliance")

        self.superadmin = User.objects.create_user(username="superadmin", password="pass12345")
        self.superadmin.profile.role = UserProfile.Role.INTERNAL_SUPERADMIN
        self.superadmin.profile.save()

        self.internal_admin = User.objects.create_user(username="internal", password="pass12345")
        self.internal_admin.profile.role = UserProfile.Role.INTERNAL_ADMIN
        self.internal_admin.profile.save()

        self.target = User.objects.create_user(username="target", password="pass12345")

    def test_superadmin_can_assign_internal_superadmin(self):
        self.client.force_authenticate(self.superadmin)
        response = self.client.post(
            reverse("assign-role"),
            {"username": "target", "role": "internal_superadmin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target.profile.refresh_from_db()
        self.assertEqual(self.target.profile.role, UserProfile.Role.INTERNAL_SUPERADMIN)
        self.assertIsNone(self.target.profile.organization_id)

    def test_superadmin_can_assign_external_superadmin_with_org(self):
        self.client.force_authenticate(self.superadmin)
        response = self.client.post(
            reverse("assign-role"),
            {
                "username": "target",
                "role": "external_superadmin",
                "organization": self.partner.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target.profile.refresh_from_db()
        self.assertEqual(self.target.profile.role, UserProfile.Role.EXTERNAL_SUPERADMIN)
        self.assertEqual(self.target.profile.organization_id, self.partner.id)

    def test_internal_admin_cannot_assign_roles(self):
        self.client.force_authenticate(self.internal_admin)
        response = self.client.post(
            reverse("assign-role"),
            {"username": "target", "role": "internal_admin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_external_role_without_organization(self):
        self.client.force_authenticate(self.superadmin)
        response = self.client.post(
            reverse("assign-role"),
            {"username": "target", "role": "external_admin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_includes_can_assign_roles(self):
        self.client.force_authenticate(self.superadmin)
        response = self.client.get(reverse("current-user"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["can_assign_roles"])

        self.client.force_authenticate(self.internal_admin)
        response = self.client.get(reverse("current-user"))
        self.assertFalse(response.data["can_assign_roles"])
