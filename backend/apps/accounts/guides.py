"""Staff-only markdown guides served inside Django admin."""

from __future__ import annotations

import html
import re
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import render
from django.utils.safestring import mark_safe

from .admin_dashboard import GUIDES


def _render_markdown_lite(source: str) -> str:
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

    def _inline(text: str) -> str:
        escaped = html.escape(text)
        escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
        escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
        escaped = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            r'<a href="\2" rel="noopener noreferrer">\1</a>',
            escaped,
        )
        return escaped

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
    path = Path(settings.BASE_DIR) / meta["path"]
    if not path.is_file():
        raise Http404("Guide file is missing.")
    body = _render_markdown_lite(path.read_text(encoding="utf-8"))
    return render(
        request,
        "admin/tff_guide.html",
        {
            "title": meta["title"],
            "guide_html": mark_safe(body),
        },
    )
