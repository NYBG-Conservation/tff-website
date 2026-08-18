import os
import urllib.parse

from config.email import env_bool, env_int


def database_config(*, getenv=os.getenv) -> dict:
    """Build Django DATABASES['default'] from DATABASE_URL or POSTGRES_* env vars."""
    conn_max_age = env_int("CONN_MAX_AGE", 60, getenv=getenv)
    health_default = "true" if conn_max_age > 0 else "false"
    persistence = {
        "CONN_MAX_AGE": conn_max_age,
        "CONN_HEALTH_CHECKS": env_bool("CONN_HEALTH_CHECKS", health_default, getenv=getenv),
    }

    database_url = (getenv("DATABASE_URL") or "").strip()
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
            "OPTIONS": _postgres_ssl_options(getenv=getenv),
            **persistence,
        }

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": getenv("POSTGRES_DB", "tff_db"),
        "USER": getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": getenv("POSTGRES_HOST", "localhost"),
        "PORT": getenv("POSTGRES_PORT", "5432"),
        "OPTIONS": _postgres_ssl_options(getenv=getenv),
        **persistence,
    }


def _postgres_ssl_options(*, getenv=os.getenv) -> dict:
    sslmode = (getenv("POSTGRES_SSLMODE") or "").strip()
    if sslmode:
        return {"sslmode": sslmode}
    return {}
