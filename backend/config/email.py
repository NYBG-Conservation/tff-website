"""Outbound SMTP settings from environment.

Used by Django settings. Defaults send as forest@nybg.org. Local/dev prints to
the console unless EMAIL_HOST (or EMAIL_BACKEND) is set.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from django.core.checks import Warning, register

Getenv = Callable[..., str | None]

NYBG_FROM_EMAIL = "forest@nybg.org"
SMTP_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
CONSOLE_BACKEND = "django.core.mail.backends.console.EmailBackend"

_TRUE = {"1", "true", "yes", "on"}


def env_bool(name: str, default: str = "false", *, getenv: Getenv = os.getenv) -> bool:
    raw = getenv(name, default)
    return str(raw or default).strip().lower() in _TRUE


def env_int(name: str, default: int, *, getenv: Getenv = os.getenv) -> int:
    raw = getenv(name, "")
    if raw is None or not str(raw).strip():
        return default
    return int(str(raw).strip())


def build_email_config(*, getenv: Getenv = os.getenv, debug: bool = False) -> dict[str, Any]:
    from_email = (getenv("DEFAULT_FROM_EMAIL") or NYBG_FROM_EMAIL).strip() or NYBG_FROM_EMAIL
    server_email = (getenv("SERVER_EMAIL") or from_email).strip() or from_email
    host = (getenv("EMAIL_HOST") or "").strip()
    use_ssl = env_bool("EMAIL_USE_SSL", "false", getenv=getenv)
    use_tls = env_bool("EMAIL_USE_TLS", "true", getenv=getenv)
    if use_ssl:
        use_tls = False

    explicit_backend = (getenv("EMAIL_BACKEND") or "").strip()
    if explicit_backend:
        backend = explicit_backend
    elif debug and not host:
        backend = CONSOLE_BACKEND
    else:
        backend = SMTP_BACKEND

    timeout_raw = getenv("EMAIL_TIMEOUT")
    if timeout_raw is None or not str(timeout_raw).strip():
        timeout: int | None = 10
    else:
        timeout = int(str(timeout_raw).strip())

    return {
        "EMAIL_BACKEND": backend,
        "DEFAULT_FROM_EMAIL": from_email,
        "SERVER_EMAIL": server_email,
        "EMAIL_HOST": host,
        "EMAIL_PORT": env_int("EMAIL_PORT", 587, getenv=getenv),
        "EMAIL_HOST_USER": (getenv("EMAIL_HOST_USER") or "").strip(),
        "EMAIL_HOST_PASSWORD": getenv("EMAIL_HOST_PASSWORD") or "",
        "EMAIL_USE_TLS": use_tls,
        "EMAIL_USE_SSL": use_ssl,
        "EMAIL_TIMEOUT": timeout,
    }


@register()
def check_outbound_email(app_configs, **kwargs) -> list[Warning]:
    """Warn in production if SMTP is not pointed at a real relay."""
    from django.conf import settings

    warnings: list[Warning] = []
    if getattr(settings, "DEBUG", False):
        return warnings

    backend = getattr(settings, "EMAIL_BACKEND", "")
    host = (getattr(settings, "EMAIL_HOST", "") or "").strip()
    if backend == SMTP_BACKEND and (not host or host in {"localhost", "127.0.0.1"}):
        warnings.append(
            Warning(
                "EMAIL_HOST is unset or localhost; Django will not be able to send "
                "invites, application notices, or overdue-upload reminders.",
                hint=(
                    "Set EMAIL_HOST / EMAIL_PORT / EMAIL_USE_TLS in backend/.env to "
                    "the NYBG SMTP relay (see backend/.env.production.example)."
                ),
                id="config.W001",
            )
        )

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "")
    if "nybg.org" not in from_email.lower():
        warnings.append(
            Warning(
                "DEFAULT_FROM_EMAIL is not an nybg.org address; messages may be "
                "rejected or marked as spam (SPF/DKIM).",
                hint=f"Use {NYBG_FROM_EMAIL} or Thain Family Forest <{NYBG_FROM_EMAIL}>.",
                id="config.W002",
            )
        )
    return warnings
