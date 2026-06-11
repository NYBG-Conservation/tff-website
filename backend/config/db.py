import os
import urllib.parse


def database_config() -> dict:
    """Build Django DATABASES['default'] from DATABASE_URL or POSTGRES_* env vars."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        parsed = urllib.parse.urlparse(database_url)
        if parsed.scheme not in ("postgres", "postgresql"):
            raise ValueError(f"Unsupported DATABASE_URL scheme: {parsed.scheme}")
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": urllib.parse.unquote(parsed.path.lstrip("/")),
            "USER": urllib.parse.unquote(parsed.username or ""),
            "PASSWORD": urllib.parse.unquote(parsed.password or ""),
            "HOST": parsed.hostname or "",
            "PORT": str(parsed.port or 5432),
            "OPTIONS": _postgres_ssl_options(),
        }

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "tff_db"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "OPTIONS": _postgres_ssl_options(),
    }


def _postgres_ssl_options() -> dict:
    sslmode = os.getenv("POSTGRES_SSLMODE", "").strip()
    if sslmode:
        return {"sslmode": sslmode}
    return {}
