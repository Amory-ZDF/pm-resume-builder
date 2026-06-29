#!/usr/bin/env python3
"""Build a fixed-style Chinese PM resume PDF from structured JSON.

This PDF is a convenience deliverable generated from the same content as the
DOCX. Do not use PDF auto-scaling to decide Word fit; verify the DOCX itself.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: reportlab. Use the Codex bundled Python runtime or install reportlab.") from exc

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

try:
    import pdfplumber
except Exception:  # pragma: no cover
    pdfplumber = None

FONT = "PMResumeCN"
FONT_BOLD = "PMResumeCN-Bold"
ACCENT = colors.HexColor("#1F4E79")
TEXT = colors.HexColor("#1E1E1E")

# Fixed style aligned with build_pm_resume_docx.py.
MARGIN_PT = 0.45 * 72
NAME_PT = 16.0
INFO_PT = 8.7
SECTION_PT = 10.2
BODY_PT = 8.6
SMALL_PT = 8.3
LEADING_PT = 10.0
SECTION_GAP_PT = 2.0
BULLET_AFTER_PT = 0.3

IMPORTANT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?\s*(?:\+|%|％|w|W|万|千|百|小时|分钟|天|周|月|年|人|次|个|条|篇)|"
    r"\d+(?:\.\d+)?/\d+(?:\.\d+)?|"
    r"(?:TOP|Top|top)\s*\d+|"
    r"(?:GMV|ROI|CTR|CVR|DAU|MAU|SQL|A/B|PRD|SOP|RAG|LLM|AI))(?:[。；;，,])?"
)


def register_fonts() -> None:
    global FONT
    candidates = [
        (Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts/Deng.ttf"), Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts/Dengb.ttf")),
        (Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts/SimHei.ttf"), Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts/SimHei.ttf")),
    ]
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont(FONT, str(regular)))
            pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))
            pdfmetrics.registerFontFamily(FONT, normal=FONT, bold=FONT_BOLD, italic=FONT, boldItalic=FONT_BOLD)
            return
    FONT = "STSong-Light"
    pdfmetrics.registerFont(UnicodeCIDFont(FONT))


def style(name: str, size: float, *, leading: float, color=TEXT, align: int | None = None, **extra: Any) -> ParagraphStyle:
    kwargs: dict[str, Any] = {
        "name": name,
        "fontName": FONT,
        "fontSize": size,
        "leading": leading,
        "textColor": color,
        "spaceBefore": 0,
        "spaceAfter": 0,
    }
    if align is not None:
        kwargs["alignment"] = align
    kwargs.update(extra)
    return ParagraphStyle(**kwargs)


def rich(text: Any, *, emphasize_metrics: bool = True) -> str:
    raw = re.sub(r"\s+", " ", str(text or "")).strip()
    pos = 0
    parts: list[str] = []
    for match in IMPORTANT_PATTERN.finditer(raw) if emphasize_metrics else []:
        if match.start() > pos:
            parts.append(html.escape(raw[pos : match.start()]))
        parts.append(f"<b>{html.escape(match.group(0))}</b>")
        pos = match.end()
    if pos < len(raw):
        parts.append(html.escape(raw[pos:]))
    return "".join(parts)


def clean_bullet_text(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().rstrip("。.")


def add_paragraph(story: list[Any], text: Any, para_style: ParagraphStyle, *, bold: bool = False) -> None:
    if not text:
        return
    body = rich(text)
    if bold:
        body = f"<b>{body}</b>"
    story.append(Paragraph(body, para_style))


def add_section(story: list[Any], title: str, heading_style: ParagraphStyle) -> None:
    story.append(Spacer(1, SECTION_GAP_PT))
    story.append(Paragraph(f'<font color="#1F4E79"><b>{html.escape(title)}</b></font>', heading_style))
    story.append(HRFlowable(width="100%", thickness=0.7, color=ACCENT, spaceBefore=0.4, spaceAfter=1.2))


def split_skill_lines(skills: list[Any]) -> list[str]:
    lines: list[str] = []
    for item in skills:
        if not item:
            continue
        if isinstance(item, dict):
            label = str(item.get("label") or item.get("category") or "").strip()
            values = item.get("items") or item.get("values") or item.get("text") or ""
            if isinstance(values, list):
                values = "、".join([str(v) for v in values if v])
            line = f"{label}：{values}" if label else str(values)
        else:
            line = str(item).strip()
        parts = [p.strip() for p in re.split(r"[;；]", line) if p.strip()]
        lines.extend(parts if len(parts) > 1 else ([line] if line else []))
    return lines


def make_story(data: dict[str, Any]) -> list[Any]:
    body = style("body", BODY_PT, leading=LEADING_PT)
    small = style("small", SMALL_PT, leading=LEADING_PT - 0.4)
    heading = style("heading", SECTION_PT, leading=SECTION_PT + 1.0, color=ACCENT)
    centered = style("center", INFO_PT, leading=LEADING_PT, align=TA_CENTER)
    name_style = style("name", NAME_PT, leading=NAME_PT + 2, color=ACCENT, align=TA_CENTER)
    bullet_style = style("bullet", BODY_PT, leading=LEADING_PT, leftIndent=12, firstLineIndent=0, bulletIndent=0, spaceAfter=BULLET_AFTER_PT)

    story: list[Any] = []
    basics = data.get("basics") or {}
    add_paragraph(story, basics.get("name") or "姓名", name_style, bold=True)
    parts = [basics.get("title") or basics.get("intention") or "求职意向：产品经理"]
    for key in ["phone", "email", "city"]:
        if basics.get(key):
            parts.append(str(basics[key]))
    parts.extend([str(x) for x in basics.get("links") or [] if x])
    add_paragraph(story, "｜".join(parts), centered)

    education = data.get("education") or []
    if education:
        add_section(story, "教育背景", heading)
        for edu in education:
            line = "｜".join([str(x) for x in [edu.get("school"), edu.get("major"), edu.get("degree"), edu.get("time")] if x])
            add_paragraph(story, line, body, bold=True)
            details = "；".join([str(x) for x in edu.get("details") or [] if x])
            add_paragraph(story, details, small)

    for sec in data.get("sections") or []:
        entries = sec.get("entries") or []
        if not entries:
            continue
        add_section(story, str(sec.get("title") or "经历"), heading)
        for entry in entries:
            add_paragraph(story, entry.get("heading"), body, bold=True)
            add_paragraph(story, entry.get("summary"), small)
            for project in entry.get("projects") or []:
                add_paragraph(story, project.get("name"), body, bold=True)
                add_paragraph(story, project.get("summary"), small)
                for bullet in project.get("bullets") or []:
                    story.append(Paragraph(rich(clean_bullet_text(bullet)), bullet_style, bulletText="•"))
            for bullet in entry.get("bullets") or []:
                story.append(Paragraph(rich(clean_bullet_text(bullet)), bullet_style, bulletText="•"))

    skill_lines = split_skill_lines(data.get("skills") or [])
    if skill_lines:
        add_section(story, "技能与其他", heading)
        for line in skill_lines:
            add_paragraph(story, line, body)
    return story


def build(data: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=MARGIN_PT,
        rightMargin=MARGIN_PT,
        topMargin=MARGIN_PT,
        bottomMargin=MARGIN_PT,
        title="",
        author="",
        subject="",
    )
    doc.build(make_story(data))


def page_count(pdf: Path) -> int | None:
    if PdfReader is None:
        return None
    return len(PdfReader(str(pdf)).pages)


def bottom_gap_points(pdf: Path) -> float | None:
    if pdfplumber is None:
        return None
    with pdfplumber.open(str(pdf)) as p:
        if not p.pages:
            return None
        page = p.pages[-1]
        chars = page.chars
        if not chars:
            return float(page.height)
        lowest = max(float(ch.get("bottom", 0)) for ch in chars)
        return max(0.0, float(page.height) - lowest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--compactness", default="standard", help="Deprecated; layout is fixed. Adjust content instead.")
    args = parser.parse_args()

    register_fonts()
    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    build(data, args.output_pdf)
    pages = page_count(args.output_pdf)
    gap = bottom_gap_points(args.output_pdf)
    gap_text = "unknown" if gap is None else f"{gap:.1f}pt"
    print(f"Wrote {args.output_pdf} layout=standard pages={pages or 'unknown'} bottom_blank={gap_text}")


if __name__ == "__main__":
    main()
