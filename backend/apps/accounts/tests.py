from django.contrib.auth.models import User
from django.core.management import call_command
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


class SeedNybgInternalSuperadminsTests(APITestCase):
    def test_creates_nybg_internal_superadmins(self):
        call_command("seed_nybg_internal_superadmins")

        for username in ("ebeaury", "boberle", "jzeiger", "tforrest"):
            user = User.objects.get(username=username)
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)
            self.assertEqual(user.profile.role, UserProfile.Role.INTERNAL_SUPERADMIN)
            self.assertIsNone(user.profile.organization_id)
            self.assertTrue(user.groups.filter(name="internal_superadmin").exists())

    def test_idempotent_for_existing_user(self):
        existing = User.objects.create_user(username="jzeiger", password="pass12345", email="old@nybg.org")
        existing.profile.role = UserProfile.Role.EXTERNAL_ADMIN
        existing.profile.save()

        call_command("seed_nybg_internal_superadmins", "--update")

        existing.refresh_from_db()
        self.assertEqual(existing.email, "jzeiger@nybg.org")
        self.assertEqual(existing.first_name, "John")
        self.assertEqual(existing.profile.role, UserProfile.Role.INTERNAL_SUPERADMIN)


class SyncRoleGroupPermissionsTests(APITestCase):
    def test_external_admin_group_gets_project_permissions(self):
        from django.contrib.auth.models import Group

        org = Organization.objects.create(name="Partner Org")
        user = User.objects.create_user(username="partner1", password="pass12345")
        user.is_staff = True
        user.save()
        user.profile.role = UserProfile.Role.EXTERNAL_ADMIN
        user.profile.organization = org
        user.profile.save()

        call_command("sync_role_groups")

        group = Group.objects.get(name="external_admin")
        self.assertTrue(user.groups.filter(name="external_admin").exists())
        self.assertTrue(group.permissions.filter(codename="view_project").exists())
        self.assertTrue(group.permissions.filter(codename="add_project").exists())
        self.assertTrue(group.permissions.filter(codename="change_dataset").exists())
        self.assertTrue(user.has_perm("datasets.view_project"))
        self.assertTrue(user.has_perm("datasets.add_dataset"))
        self.assertFalse(Group.objects.filter(name="external_partner_admin").exists())

    def test_sync_deletes_legacy_external_partner_admin_group(self):
        from django.contrib.auth.models import Group

        Group.objects.get_or_create(name="external_partner_admin")
        self.assertTrue(Group.objects.filter(name="external_partner_admin").exists())
        call_command("sync_role_groups")
        self.assertFalse(Group.objects.filter(name="external_partner_admin").exists())

    def test_saving_external_admin_profile_sets_staff_and_permissions(self):
        """Creating a user (default external_admin profile) auto-sets staff + group perms."""
        from django.contrib.auth.models import Group

        org = Organization.objects.create(name="Partner Lab")
        user = User.objects.create_user(username="newpartner", password="pass12345")
        user.refresh_from_db()

        # Default profile role is external_admin — staff and group perms attach on create.
        self.assertTrue(user.is_staff)
        self.assertEqual(user.profile.role, UserProfile.Role.EXTERNAL_ADMIN)
        self.assertTrue(user.groups.filter(name="external_admin").exists())
        group = Group.objects.get(name="external_admin")
        self.assertTrue(group.permissions.filter(codename="add_project").exists())
        self.assertTrue(user.has_perm("datasets.view_project"))
        self.assertTrue(user.has_perm("datasets.add_project"))
        self.assertTrue(user.has_perm("datasets.change_dataset"))

        # Org can be set afterward without losing staff/permissions.
        profile = user.profile
        profile.organization = org
        profile.save()
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertEqual(user.profile.organization_id, org.id)
        self.assertTrue(user.has_perm("datasets.add_project"))
