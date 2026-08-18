"""Staff-only markdown guides served inside Django admin."""

from __future__ import annotations

import html
import re
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

GUIDES = {
    "partner-intro": {
        "title": "Portal intro (short)",
        "path": "docs/EXTERNAL_ADMIN_INTRO.md",
    },
    "partner-guide": {
        "title": "External partner guide",
        "path": "docs/EXTERNAL_PARTNER_GUIDE.md",
    },
    "operations": {
        "title": "NYBG operations guide",
        "path": "docs/NYBG_OPERATIONS_GUIDE.md",
    },
    "overdue-alerts": {
        "title": "Data-upload reminder spec",
        "path": "backend/OVERDUE_DATA_ALERT_SPEC.md",
    },
    "seed-data": {
        "title": "Seed data runbook",
        "path": "docs/SEED_DATA.md",
    },
    "deployment": {
        "title": "Deployment",
        "path": "docs/DEPLOYMENT.md",
    },
    "api-contract": {
        "title": "API contract",
        "path": "backend/API_CONTRACT.md",
    },
}

_PUBLIC_PREFIXES = (
    "/research",
    "/data",
    "/projects",
    "/about",
    "/visit",
    "/contact",
    "/education",
)


def resolve_guide_path(relative: str) -> Path | None:
    """Find a guide file at the repo root (local) or /app (Docker)."""
    rel = Path(relative)
    roots = [Path(settings.BASE_DIR)]
    backend_dir = getattr(settings, "BACKEND_DIR", None)
    if backend_dir:
        roots.append(Path(backend_dir).parent)
        roots.append(Path(backend_dir))
    seen: set[Path] = set()
    candidates: list[Path] = []
    for root in roots:
        candidates.append(root / rel)
        if rel.parts and rel.parts[0] == "backend":
            candidates.append(root / Path(*rel.parts[1:]))
        candidates.append(root / rel.name)
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if path.is_file():
            return path
    return None


def _slug_for_markdown_path(href_path: str) -> str | None:
    name = Path(href_path.split("#", 1)[0]).name.lower()
    if not name.endswith(".md"):
        return None
    for slug, meta in GUIDES.items():
        if Path(meta["path"]).name.lower() == name:
            return slug
    return None


def rewrite_markdown_href(href: str) -> str:
    """Point in-guide links at the public site or another admin guide page."""
    raw = href.strip().strip("<>")
    if not raw or raw.startswith(("#", "mailto:", "http://", "https://")):
        return raw

    path, _, fragment = raw.partition("#")
    path = path.strip()
    suffix = f"#{fragment}" if fragment else ""

    if any(path == prefix or path.startswith(f"{prefix}/") or path.startswith(f"{prefix}?") for prefix in _PUBLIC_PREFIXES):
        base = str(getattr(settings, "FRONTEND_URL", "") or "").rstrip("/")
        return f"{base}{path}{suffix}" if base else f"{path}{suffix}"

    slug = _slug_for_markdown_path(path)
    if slug:
        return f"{reverse('admin-guide', kwargs={'slug': slug})}{suffix}"
    return raw


def _format_inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def _inline(text: str) -> str:
    pieces: list[str] = []
    last = 0
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        pieces.append(_format_inline(text[last : match.start()]))
        label, href = match.group(1), match.group(2)
        resolved = rewrite_markdown_href(href)
        pieces.append(
            f'<a href="{html.escape(resolved, quote=True)}" rel="noopener noreferrer">'
            f"{_format_inline(label)}</a>"
        )
        last = match.end()
    pieces.append(_format_inline(text[last:]))
    return "".join(pieces)


def render_markdown_lite(source: str) -> str:
    lines = source.replace("\r\n", "\n").split("\n")
    parts: list[str] = []
    in_code = False
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph:
            return
        text = " ".join(paragraph).strip()
        paragraph.clear()
        if text:
            parts.append(f"<p>{_inline(text)}</p>")

    for line in lines:
        if line.strip().startswith("```"):
            flush_paragraph()
            if in_code:
                parts.append("</pre>")
                in_code = False
            else:
                parts.append("<pre>")
                in_code = True
            continue
        if in_code:
            parts.append(html.escape(line) + "\n")
            continue
        if not line.strip():
            flush_paragraph()
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            parts.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            continue
        if re.match(r"^[-*]\s+", line):
            flush_paragraph()
            parts.append(f"<li>{_inline(re.sub(r'^[-*]\s+', '', line))}</li>")
            continue
        paragraph.append(line.strip())

    flush_paragraph()
    if in_code:
        parts.append("</pre>")

    html_out: list[str] = []
    in_list = False
    for part in parts:
        is_li = part.startswith("<li>")
        if is_li and not in_list:
            html_out.append("<ul>")
            in_list = True
        elif not is_li and in_list:
            html_out.append("</ul>")
            in_list = False
        html_out.append(part)
    if in_list:
        html_out.append("</ul>")
    return "".join(html_out)


@staff_member_required(login_url="/admin/login/")
def guide_view(request, slug: str):
    meta = GUIDES.get(slug)
    if not meta:
        raise Http404("Unknown guide.")
    path = resolve_guide_path(meta["path"])
    if path is None:
        raise Http404("Guide file is missing.")
    body = render_markdown_lite(path.read_text(encoding="utf-8"))
    return render(
        request,
        "admin/tff_guide.html",
        {
            "title": meta["title"],
            "guide_html": mark_safe(body),
        },
    )
