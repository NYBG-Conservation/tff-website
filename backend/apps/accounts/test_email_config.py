from django.core.checks import Warning
from django.test import SimpleTestCase, override_settings

from config.email import (
    CONSOLE_BACKEND,
    NYBG_FROM_EMAIL,
    SMTP_BACKEND,
    build_email_config,
    check_outbound_email,
)


def _getenv(values):
    def getter(key, default=None):
        if key in values:
            return values[key]
        return default

    return getter


class EmailConfigTests(SimpleTestCase):
    def test_defaults_send_from_forest_nybg(self):
        config = build_email_config(getenv=_getenv({}), debug=False)
        self.assertEqual(config["DEFAULT_FROM_EMAIL"], NYBG_FROM_EMAIL)
        self.assertEqual(config["SERVER_EMAIL"], NYBG_FROM_EMAIL)
        self.assertEqual(config["EMAIL_BACKEND"], SMTP_BACKEND)
        self.assertEqual(config["EMAIL_PORT"], 587)
        self.assertTrue(config["EMAIL_USE_TLS"])
        self.assertFalse(config["EMAIL_USE_SSL"])
        self.assertEqual(config["EMAIL_HOST"], "")

    def test_dev_without_host_uses_console(self):
        config = build_email_config(getenv=_getenv({}), debug=True)
        self.assertEqual(config["EMAIL_BACKEND"], CONSOLE_BACKEND)

    def test_dev_with_host_uses_smtp(self):
        config = build_email_config(
            getenv=_getenv({"EMAIL_HOST": "smtp.nybg.org"}),
            debug=True,
        )
        self.assertEqual(config["EMAIL_BACKEND"], SMTP_BACKEND)
        self.assertEqual(config["EMAIL_HOST"], "smtp.nybg.org")

    def test_ssl_disables_tls(self):
        config = build_email_config(
            getenv=_getenv(
                {
                    "EMAIL_HOST": "smtp.office365.com",
                    "EMAIL_USE_SSL": "true",
                    "EMAIL_USE_TLS": "true",
                    "EMAIL_PORT": "465",
                }
            ),
            debug=False,
        )
        self.assertTrue(config["EMAIL_USE_SSL"])
        self.assertFalse(config["EMAIL_USE_TLS"])
        self.assertEqual(config["EMAIL_PORT"], 465)

    def test_display_name_from_is_kept(self):
        config = build_email_config(
            getenv=_getenv({"DEFAULT_FROM_EMAIL": "Thain Family Forest <forest@nybg.org>"}),
            debug=False,
        )
        self.assertEqual(config["DEFAULT_FROM_EMAIL"], "Thain Family Forest <forest@nybg.org>")

    @override_settings(
        DEBUG=False,
        EMAIL_BACKEND=SMTP_BACKEND,
        EMAIL_HOST="",
        DEFAULT_FROM_EMAIL=NYBG_FROM_EMAIL,
    )
    def test_prod_warns_when_smtp_host_missing(self):
        warnings = check_outbound_email(None)
        self.assertTrue(any(w.id == "config.W001" for w in warnings))

    @override_settings(
        DEBUG=False,
        EMAIL_BACKEND=SMTP_BACKEND,
        EMAIL_HOST="smtp.nybg.org",
        DEFAULT_FROM_EMAIL="me@gmail.com",
    )
    def test_prod_warns_when_from_is_not_nybg(self):
        warnings = check_outbound_email(None)
        self.assertTrue(any(isinstance(w, Warning) and w.id == "config.W002" for w in warnings))
