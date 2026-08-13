"""Figshare DOI workflow helpers for Thain Family Forest research projects."""

from __future__ import annotations

from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError

FIGSHARE_HOST_SUFFIXES = (
    "figshare.com",
    "doi.org",
    "dx.doi.org",
)


def figshare_doi_guide_url() -> str:
    return getattr(
        settings,
        "FIGSHARE_DOI_GUIDE_URL",
        "https://info.figshare.com/user-guide/how-to-reserve-a-doi/",
    )


def normalize_figshare_doi_url(value: str) -> str:
    return (value or "").strip()


def validate_figshare_doi_url(value: str, *, required: bool = False) -> str:
    normalized = normalize_figshare_doi_url(value)
    if not normalized:
        if required:
            raise ValidationError(
                "A Figshare item URL or reserved DOI link is required. "
                f"See {figshare_doi_guide_url()} for Figshare instructions."
            )
        return ""

    parsed = urlparse(normalized)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValidationError("Enter a valid http(s) URL for your Figshare item or reserved DOI.")

    host = (parsed.hostname or "").lower()
    if not any(host == suffix or host.endswith(f".{suffix}") for suffix in FIGSHARE_HOST_SUFFIXES):
        raise ValidationError(
            "Enter a Figshare item URL (figshare.com) or DOI resolver link (doi.org)."
        )
    return normalized
