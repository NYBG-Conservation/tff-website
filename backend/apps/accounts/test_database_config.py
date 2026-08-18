from django.test import SimpleTestCase

from config.db import database_config


def _getenv(values):
    def getter(key, default=None):
        if key in values:
            return values[key]
        return default

    return getter


class DatabaseConfigTests(SimpleTestCase):
    def test_reuses_connections_by_default(self):
        cfg = database_config(
            getenv=_getenv({"DATABASE_URL": "postgresql://u:p@db.example:5432/tff_db"})
        )
        self.assertEqual(cfg["CONN_MAX_AGE"], 60)
        self.assertTrue(cfg["CONN_HEALTH_CHECKS"])
        self.assertEqual(cfg["HOST"], "db.example")
        self.assertEqual(cfg["NAME"], "tff_db")

    def test_can_disable_persistent_connections(self):
        cfg = database_config(
            getenv=_getenv(
                {
                    "POSTGRES_HOST": "localhost",
                    "CONN_MAX_AGE": "0",
                }
            )
        )
        self.assertEqual(cfg["CONN_MAX_AGE"], 0)
        self.assertFalse(cfg["CONN_HEALTH_CHECKS"])

    def test_sslmode_and_health_check_override(self):
        cfg = database_config(
            getenv=_getenv(
                {
                    "DATABASE_URL": "postgresql://u:p@rds.amazonaws.com:5432/tff_db",
                    "POSTGRES_SSLMODE": "require",
                    "CONN_MAX_AGE": "120",
                    "CONN_HEALTH_CHECKS": "false",
                }
            )
        )
        self.assertEqual(cfg["CONN_MAX_AGE"], 120)
        self.assertFalse(cfg["CONN_HEALTH_CHECKS"])
        self.assertEqual(cfg["OPTIONS"], {"sslmode": "require"})
