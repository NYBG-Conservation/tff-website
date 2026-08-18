from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.accounts.admin_dashboard import patch_admin_index
from apps.accounts.models import UserProfile
from apps.datasets.models import Dataset, DatasetFile, DatasetPublication, Project, ProjectManager
from apps.organizations.models import Organization


class ProjectAdminRelatedRecordsTests(TestCase):
    def setUp(self):
        patch_admin_index()
        self.organization = Organization.objects.create(name="NYBG")
        self.user = User.objects.create_user(
            username="projadmin",
            password="pass12345",
            is_staff=True,
            is_superuser=True,
        )
        self.user.profile.role = UserProfile.Role.INTERNAL_SUPERADMIN
        self.user.profile.save()
        self.project = Project.objects.create(
            short_title="Canopy Gaps",
            lead_name="Ada",
            lead_email="ada@nybg.org",
            organization=self.organization,
            owner=self.user,
        )
        self.dataset = Dataset.objects.create(
            title="Gap photos",
            cadence=Dataset.Cadence.ONE_OFF,
            status=Dataset.Status.ACTIVE,
            data_type=Dataset.DataType.IMAGE,
            project=self.project,
            owner=self.user,
            organization=self.organization,
        )
        DatasetFile.objects.create(
            dataset=self.dataset,
            external_url="https://figshare.com/articles/gap-photo/1",
            file_name="gap-photo.tif",
            file_kind=DatasetFile.FileKind.DATASET,
            uploaded_by=self.user,
        )
        DatasetPublication.objects.create(
            dataset=self.dataset,
            title="Canopy paper",
            publication_year=2024,
            url="https://doi.org/10.1234/example",
        )

    def test_projects_is_first_model_in_project_admin_section(self):
        request = RequestFactory().get("/admin/")
        request.user = self.user
        app_list = site.get_app_list(request)
        datasets_app = next(app for app in app_list if app["app_label"] == "datasets")
        self.assertEqual(datasets_app["models"][0]["object_name"], "Project")
        self.assertEqual(datasets_app["models"][1]["object_name"], "Dataset")

    def test_project_change_page_lists_catalog_files_and_publications(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("admin:datasets_project_change", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Catalog files and publications")
        self.assertContains(response, "Gap photos")
        self.assertContains(response, "gap-photo.tif")
        self.assertContains(response, "Canopy paper")
        self.assertContains(
            response, reverse("admin:datasets_dataset_change", args=[self.dataset.pk])
        )

    def test_owner_who_is_also_manager_sees_project_once(self):
        from django.contrib.admin.sites import site as admin_site

        from apps.datasets.admin import ProjectAdmin

        member = User.objects.create_user(
            username="ownermanager",
            password="pass12345",
            is_staff=True,
            is_superuser=True,
        )
        member.profile.role = UserProfile.Role.EXTERNAL_ADMIN
        member.profile.save()
        project = Project.objects.create(
            short_title="Owned And Managed",
            lead_name="Ada",
            lead_email="ada@example.edu",
            organization=self.organization,
            owner=member,
        )
        ProjectManager.objects.create(project=project, user=member, added_by=member)

        request = RequestFactory().get("/admin/datasets/project/")
        request.user = member
        queryset = ProjectAdmin(Project, admin_site).get_queryset(request)
        self.assertEqual(queryset.filter(pk=project.pk).count(), 1)

    def test_saving_project_does_not_insert_blank_catalog_row(self):
        self.client.force_login(self.user)
        url = reverse("admin:datasets_project_change", args=[self.project.pk])
        payload = {
            "short_title": self.project.short_title,
            "full_title": self.project.full_title,
            "summary": self.project.summary,
            "description": self.project.description,
            "shared_publicly": "on" if self.project.shared_publicly else "",
            "lead_name": self.project.lead_name,
            "lead_email": self.project.lead_email,
            "organization": str(self.project.organization_id),
            "owner": str(self.project.owner_id),
            "ongoing": "on" if self.project.ongoing else "",
            "plans_own_doi": "on" if self.project.plans_own_doi else "",
            "figshare_doi_url": self.project.figshare_doi_url,
            "external_url": self.project.external_url,
            "datasets-TOTAL_FORMS": "2",
            "datasets-INITIAL_FORMS": "1",
            "datasets-MIN_NUM_FORMS": "0",
            "datasets-MAX_NUM_FORMS": "1000",
            "datasets-0-id": str(self.dataset.pk),
            "datasets-0-title": self.dataset.title,
            "datasets-0-data_type": self.dataset.data_type,
            "datasets-0-cadence": self.dataset.cadence,
            "datasets-0-status": self.dataset.status,
            "datasets-1-title": "",
            "datasets-1-data_type": Dataset.DataType.TABULAR,
            "datasets-1-cadence": "",
            "datasets-1-status": Dataset.Status.DRAFT,
            "project_files-TOTAL_FORMS": "0",
            "project_files-INITIAL_FORMS": "0",
            "project_files-MIN_NUM_FORMS": "0",
            "project_files-MAX_NUM_FORMS": "1000",
            "publications-TOTAL_FORMS": "0",
            "publications-INITIAL_FORMS": "0",
            "publications-MIN_NUM_FORMS": "0",
            "publications-MAX_NUM_FORMS": "1000",
            "project_managers-TOTAL_FORMS": "0",
            "project_managers-INITIAL_FORMS": "0",
            "project_managers-MIN_NUM_FORMS": "0",
            "project_managers-MAX_NUM_FORMS": "1000",
        }
        payload = {key: value for key, value in payload.items() if value != ""}
        response = self.client.post(url, payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Dataset.objects.filter(project=self.project).count(), 1)
