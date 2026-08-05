from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.applications.models import ResearchApplication


# Survey123 export has duplicate header labels; map by column index.
COL = {
    "global_id": 1,
    "applicant_name": 4,
    "title_position": 5,
    "institution": 6,
    "email": 7,
    "phone": 8,
    "address": 9,
    "co_pi": 10,
    "project_title": 11,
    "project_type": 12,
    "description_plant": 14,
    "desired_species": 15,
    "collection_type": 16,
    "start_a": 17,
    "end_a": 18,
    "start_b": 19,
    "end_b": 20,
    "resources_plant": 21,
    "publications_plant": 22,
    "comments_plant": 23,
    "description_onsite": 24,
    "anticipated_start": 25,
    "anticipated_end": 26,
    "abiotic": 27,
    "biotic": 28,
    "funding": 29,
    "wildlife": 30,
    "publications_onsite": 31,
    "location": 33,
    "infrastructure": 34,
    "site_visits": 35,
    "visitor_impacts": 36,
    "sensitivity": 37,
    "resources_onsite": 38,
    "comments_onsite": 39,
    "attestation_name": 41,
    "attestation_date": 42,
    "creation_date": 44,
}


def _cell(row: list[str], key: str) -> str:
    idx = COL[key]
    if idx >= len(row):
        return ""
    return (row[idx] or "").strip()


def _parse_date(value: str):
    if not value:
        return None
    for fmt in (
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    parsed = parse_datetime(value)
    if parsed:
        return parsed.date()
    return None


def _parse_datetime(value: str):
    if not value:
        return None
    for fmt in (
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ):
        try:
            dt = datetime.strptime(value, fmt)
            if timezone.is_naive(dt):
                return timezone.make_aware(dt, timezone.get_current_timezone())
            return dt
        except ValueError:
            continue
    parsed = parse_datetime(value)
    if parsed and timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _first(*values: str) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""


def row_to_defaults(row: list[str]) -> dict:
    project_type = _cell(row, "project_type")
    if project_type not in {
        ResearchApplication.ProjectType.PLANT_MATERIAL,
        ResearchApplication.ProjectType.ONSITE_RESEARCH,
    }:
        # Keep unknown legacy values if they appear; otherwise blank fails model validation.
        if not project_type:
            project_type = ResearchApplication.ProjectType.ONSITE_RESEARCH

    collection_type = _cell(row, "collection_type")
    valid_collections = {c.value for c in ResearchApplication.CollectionType}
    if collection_type and collection_type not in valid_collections:
        collection_type = ResearchApplication.CollectionType.OTHER

    description = _first(_cell(row, "description_plant"), _cell(row, "description_onsite")) or "(imported)"
    email = _cell(row, "email") or "unknown@example.com"
    # Survey123 sometimes dumps dual emails like "a@x.com or b@y.com"
    if " or " in email:
        email = email.split(" or ", 1)[0].strip()
    if "," in email:
        email = email.split(",", 1)[0].strip()

    attestation_name = _cell(row, "attestation_name") or _cell(row, "applicant_name") or "Unknown"
    attestation_date = _parse_date(_cell(row, "attestation_date")) or _parse_date(
        _cell(row, "creation_date")
    )
    if attestation_date is None:
        attestation_date = timezone.localdate()

    submitted_at = _parse_datetime(_cell(row, "creation_date")) or timezone.now()

    return {
        "applicant_name": _cell(row, "applicant_name") or "Unknown",
        "title_position": _cell(row, "title_position"),
        "institution": _cell(row, "institution") or "Unknown",
        "email": email,
        "phone": _cell(row, "phone"),
        "address": _cell(row, "address"),
        "co_pi": _cell(row, "co_pi"),
        "project_title": _cell(row, "project_title") or "(untitled)",
        "project_type": project_type,
        "description": description,
        "start_date": _parse_date(_cell(row, "start_a")) or _parse_date(_cell(row, "start_b")),
        "end_date": _parse_date(_cell(row, "end_a")) or _parse_date(_cell(row, "end_b")),
        "anticipated_start_date": _parse_date(_cell(row, "anticipated_start")),
        "anticipated_end_date": _parse_date(_cell(row, "anticipated_end")),
        "desired_species": _cell(row, "desired_species"),
        "collection_type": collection_type,
        "research_location": _cell(row, "location"),
        "plant_tracker_notes": "",
        "abiotic_variables": _cell(row, "abiotic"),
        "biotic_variables": _cell(row, "biotic"),
        "funding_sources": _cell(row, "funding"),
        "wildlife_permits": _cell(row, "wildlife"),
        "nybg_infrastructure": _cell(row, "infrastructure"),
        "site_visits": _cell(row, "site_visits"),
        "visitor_impacts": _cell(row, "visitor_impacts"),
        "research_sensitivity": _cell(row, "sensitivity"),
        "resources": _first(_cell(row, "resources_plant"), _cell(row, "resources_onsite")),
        "publications": _first(
            _cell(row, "publications_plant"), _cell(row, "publications_onsite")
        ),
        "additional_comments": _first(
            _cell(row, "comments_plant"), _cell(row, "comments_onsite")
        ),
        "attestation_name": attestation_name,
        "attestation_date": attestation_date,
        "submitted_at": submitted_at,
        "status": ResearchApplication.Status.SUBMITTED,
    }


class Command(BaseCommand):
    help = (
        "Import legacy Survey123 research applications from CSV. "
        "Idempotent on GlobalID → legacy_global_id."
    )

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to Survey123 export CSV")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and report counts without writing",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing rows matched by GlobalID (default: skip existing)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["csv_path"]).expanduser()
        if not path.is_file():
            raise CommandError(f"CSV not found: {path}")

        dry_run = options["dry_run"]
        update = options["update"]
        created = updated = skipped = errors = 0

        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            if not header or "GlobalID" not in header[1]:
                # Position-based; still warn if GlobalID column missing textually.
                if not header or len(header) < 42:
                    raise CommandError("CSV does not look like a Survey123 research export.")

            for line_no, row in enumerate(reader, start=2):
                global_id = _cell(row, "global_id")
                if not global_id:
                    skipped += 1
                    continue
                try:
                    defaults = row_to_defaults(row)
                except Exception as exc:  # noqa: BLE001 — report and continue
                    errors += 1
                    self.stderr.write(f"Line {line_no}: {exc}")
                    continue

                existing = ResearchApplication.objects.filter(legacy_global_id=global_id).first()
                if existing:
                    if update and not dry_run:
                        for key, value in defaults.items():
                            setattr(existing, key, value)
                        existing.save()
                        updated += 1
                    else:
                        skipped += 1
                    continue

                if dry_run:
                    created += 1
                    continue

                ResearchApplication.objects.create(legacy_global_id=global_id, **defaults)
                created += 1

        if dry_run:
            transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: created={created} updated={updated} "
                f"skipped={skipped} errors={errors} dry_run={dry_run}"
            )
        )
