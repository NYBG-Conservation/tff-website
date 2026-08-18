from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.admin_dashboard import _guide_links_for_role
from apps.accounts.guides import (
    GUIDES,
    render_markdown_lite,
    resolve_guide_path,
    rewrite_markdown_href,
)
from apps.accounts.models import UserProfile


class GuidePathTests(TestCase):
    def test_homepage_guides_resolve_on_disk(self):
        for slug in ("partner-intro", "partner-guide", "operations", "overdue-alerts"):
            path = resolve_guide_path(GUIDES[slug]["path"])
            self.assertIsNotNone(path, slug)
            self.assertTrue(path.is_file(), slug)

    def test_related_doc_guides_resolve_on_disk(self):
        for slug in ("seed-data", "deployment", "api-contract"):
            path = resolve_guide_path(GUIDES[slug]["path"])
            self.assertIsNotNone(path, slug)


class GuideLinkRewriteTests(TestCase):
    @override_settings(FRONTEND_URL="https://forest.nybg.org")
    def test_public_site_paths_use_frontend_url(self):
        self.assertEqual(
            rewrite_markdown_href("/research/apply"),
            "https://forest.nybg.org/research/apply",
        )
        self.assertEqual(
            rewrite_markdown_href("/research#conducting-research-heading"),
            "https://forest.nybg.org/research#conducting-research-heading",
        )

    def test_markdown_files_map_to_admin_guides(self):
        self.assertEqual(
            rewrite_markdown_href("EXTERNAL_PARTNER_GUIDE.md"),
            reverse("admin-guide", kwargs={"slug": "partner-guide"}),
        )
        self.assertEqual(
            rewrite_markdown_href("../backend/OVERDUE_DATA_ALERT_SPEC.md"),
            reverse("admin-guide", kwargs={"slug": "overdue-alerts"}),
        )
        self.assertTrue(
            rewrite_markdown_href("SEED_DATA.md#why-duplicates-happened-ec2-june-2026").endswith(
                "#why-duplicates-happened-ec2-june-2026"
            )
        )

    def test_external_and_mailto_unchanged(self):
        self.assertEqual(
            rewrite_markdown_href("https://info.figshare.com/user-guide/how-to-reserve-a-doi/"),
            "https://info.figshare.com/user-guide/how-to-reserve-a-doi/",
        )
        self.assertEqual(rewrite_markdown_href("mailto:forest@nybg.org"), "mailto:forest@nybg.org")

    @override_settings(FRONTEND_URL="https://forest.nybg.org")
    def test_rendered_html_rewrites_links(self):
        html = render_markdown_lite(
            "See the [apply form](/research/apply) and the [partner guide](EXTERNAL_PARTNER_GUIDE.md)."
        )
        self.assertIn('href="https://forest.nybg.org/research/apply"', html)
        self.assertIn(reverse("admin-guide", kwargs={"slug": "partner-guide"}), html)


class GuideViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="guideuser", password="pass12345")
        self.staff.is_staff = True
        self.staff.save()
        self.staff.profile.role = UserProfile.Role.INTERNAL_SUPERADMIN
        self.staff.profile.save()

    def test_operations_guide_renders(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("admin-guide", kwargs={"slug": "operations"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NYBG Operations Guide")

    def test_partner_intro_renders(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("admin-guide", kwargs={"slug": "partner-intro"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portal intro")

    def test_superadmin_homepage_guide_links_are_live(self):
        self.client.force_login(self.staff)
        links = _guide_links_for_role(UserProfile.Role.INTERNAL_SUPERADMIN)
        self.assertGreaterEqual(len(links), 1)
        for link in links:
            response = self.client.get(link["url"])
            self.assertEqual(response.status_code, 200, link)
