#!/usr/bin/env python3
"""Build a compact one-page-style Chinese PM resume PDF from structured JSON.

Use this when batch tests need PDF deliverables but Word/LibreOffice conversion
would trigger macOS permission prompts. Generate the DOCX and PDF from the same
structured JSON so Word does not need to open files from Desktop/Documents.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
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

IMPORTANT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?\s*(?:\+|%|％|w|W|万|千|百|小时|分钟|天|周|月|年|人|次|个|条|篇)|"
    r"\d+(?:\.\d+)?/\d+(?:\.\d+)?|"
    r"(?:TOP|Top|top)\s*\d+|"
    r"(?:GMV|ROI|CTR|CVR|DAU|MAU|SQL|A/B|PRD|SOP|RAG|LLM|AI))(?:[。；;，,])?"
)


def register_fonts() -> None:
    global FONT
    font_candidates = [
        (
            Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts/Deng.ttf"),
            Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts/Dengb.ttf"),
        ),
        (
            Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts/SimHei.ttf"),
            Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts/SimHei.ttf"),
        ),
    ]
    for regular, bold in font_candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont(FONT, str(regular)))
            pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))
            pdfmetrics.registerFontFamily(FONT, normal=FONT, bold=FONT_BOLD, italic=FONT, boldItalic=FONT_BOLD)
            return
    FONT = "STSong-Light"
    pdfmetrics.registerFont(UnicodeCIDFont(FONT))


def sizes(compactness: str) -> dict[str, float]:
    return {
        "ultra": {"name": 15, "body": 8.1, "small": 7.8, "heading": 9.6, "lead": 9.4, "gap": 1.2, "margin": 0.40},
        "tight": {"name": 16, "body": 8.5, "small": 8.1, "heading": 10.0, "lead": 10.0, "gap": 2.0, "margin": 0.45},
        "normal": {"name": 17, "body": 8.9, "small": 8.4, "heading": 10.5, "lead": 10.8, "gap": 3.0, "margin": 0.52},
        "roomy": {"name": 18.5, "body": 10.2, "small": 9.4, "heading": 11.5, "lead": 13.2, "gap": 6.0, "margin": 0.68},
        "expanded": {"name": 20, "body": 11.2, "small": 10.2, "heading": 12.4, "lead": 15.0, "gap": 9.0, "margin": 0.86},
        "fill1": {"name": 20.2, "body": 11.35, "small": 10.35, "heading": 12.6, "lead": 15.35, "gap": 10.4, "margin": 0.88},
        "fill2": {"name": 20.4, "body": 11.5, "small": 10.5, "heading": 12.8, "lead": 15.7, "gap": 11.8, "margin": 0.90},
        "fill3": {"name": 20.6, "body": 11.65, "small": 10.65, "heading": 13.0, "lead": 16.05, "gap": 13.2, "margin": 0.92},
        "fill4": {"name": 20.8, "body": 11.8, "small": 10.8, "heading": 13.1, "lead": 16.4, "gap": 14.6, "margin": 0.94},
        "filled": {"name": 21, "body": 12.0, "small": 10.9, "heading": 13.2, "lead": 16.8, "gap": 16.0, "margin": 0.96},
        "maxfill": {"name": 22, "body": 12.8, "small": 11.5, "heading": 14.0, "lead": 18.2, "gap": 22.0, "margin": 1.05},
        "maxfill1": {"name": 22.5, "body": 13.0, "small": 11.7, "heading": 14.3, "lead": 18.8, "gap": 24.0, "margin": 1.07},
        "maxfill2": {"name": 23.0, "body": 13.25, "small": 12.0, "heading": 14.6, "lead": 19.55, "gap": 26.6, "margin": 1.09},
        "maxfill3": {"name": 23.5, "body": 13.4, "small": 12.1, "heading": 14.8, "lead": 19.9, "gap": 28.0, "margin": 1.10},
        "sparsefill": {"name": 24, "body": 13.6, "small": 12.2, "heading": 15.0, "lead": 20.5, "gap": 30.0, "margin": 1.12},
    }[compactness]


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


def add_section(story: list[Any], title: str, heading_style: ParagraphStyle, gap: float) -> None:
    story.append(Spacer(1, gap))
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


def count_sections(data: dict[str, Any]) -> int:
    count = 0
    if data.get("education"):
        count += 1
    count += sum(1 for sec in data.get("sections") or [] if sec.get("entries"))
    if split_skill_lines(data.get("skills") or []):
        count += 1
    return max(1, count)


def make_story(data: dict[str, Any], compactness: str, section_stretch: float = 0.0) -> list[Any]:
    s = sizes(compactness)
    body = style("body", s["body"], leading=s["lead"])
    small = style("small", s["small"], leading=s["lead"] - 0.4)
    heading = style("heading", s["heading"], leading=s["heading"] + 1.0, color=ACCENT)
    centered = style("center", s["body"], leading=s["lead"], align=TA_CENTER)
    name_style = style("name", s["name"], leading=s["name"] + 2, color=ACCENT, align=TA_CENTER)
    bullet_style = style("bullet", s["body"], leading=s["lead"], leftIndent=12, firstLineIndent=0, bulletIndent=0)

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
        add_section(story, "教育背景", heading, s["gap"] + section_stretch)
        for edu in education:
            line = "｜".join([str(x) for x in [edu.get("school"), edu.get("major"), edu.get("degree"), edu.get("time")] if x])
            add_paragraph(story, line, body, bold=True)
            details = "；".join([str(x) for x in edu.get("details") or [] if x])
            add_paragraph(story, details, small)

    for sec in data.get("sections") or []:
        entries = sec.get("entries") or []
        if not entries:
            continue
        add_section(story, str(sec.get("title") or "经历"), heading, s["gap"] + section_stretch)
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
        add_section(story, "技能与其他", heading, s["gap"] + section_stretch)
        for line in skill_lines:
            add_paragraph(story, line, body)

    return story


def build(data: dict[str, Any], output: Path, compactness: str, section_stretch: float = 0.0) -> None:
    s = sizes(compactness)
    margin_pt = s["margin"] * 72
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=margin_pt,
        rightMargin=margin_pt,
        topMargin=margin_pt,
        bottomMargin=min(margin_pt, 32),
        title="",
        author="",
        subject="",
    )
    doc.build(make_story(data, compactness, section_stretch))


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
    parser.add_argument(
        "--compactness",
        choices=["auto", "sparsefill", "maxfill3", "maxfill2", "maxfill1", "maxfill", "filled", "fill4", "fill3", "fill2", "fill1", "expanded", "roomy", "normal", "tight", "ultra"],
        default="auto",
    )
    parser.add_argument("--max-bottom-blank-pt", type=float, default=48.0, help="Target bottom whitespace for auto mode.")
    args = parser.parse_args()

    register_fonts()
    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    variants = ["sparsefill", "maxfill3", "maxfill2", "maxfill1", "maxfill", "filled", "fill4", "fill3", "fill2", "fill1", "expanded", "roomy", "normal", "tight", "ultra"] if args.compactness == "auto" else [args.compactness]
    best: tuple[float, str, Path, int | None, float | None] | None = None
    first_one_page: tuple[str, Path, int | None, float | None] | None = None
    with tempfile.TemporaryDirectory(prefix="pm-resume-pdf-") as td:
        tmp = Path(td)
        for compactness in variants:
            candidate = tmp / f"resume-{compactness}.pdf"
            build(data, candidate, compactness)
            pages = page_count(candidate)
            gap = bottom_gap_points(candidate)
            if pages is not None and pages > 1:
                continue
            if first_one_page is None:
                first_one_page = (compactness, candidate, pages, gap)
            score = gap if gap is not None else 9999.0
            if best is None or score < best[0]:
                best = (score, compactness, candidate, pages, gap)
            if gap is not None and gap <= args.max_bottom_blank_pt:
                best = (score, compactness, candidate, pages, gap)
                break

        chosen = best or (None if first_one_page is None else (9999.0, *first_one_page))
        if chosen is None:
            fallback = tmp / f"resume-{variants[-1]}.pdf"
            build(data, fallback, variants[-1])
            chosen = (9999.0, variants[-1], fallback, page_count(fallback), bottom_gap_points(fallback))
        _, compactness, candidate, pages, gap = chosen
        if gap is not None and gap > args.max_bottom_blank_pt and (pages is None or pages <= 1):
            section_count = count_sections(data)
            needed = min(28.0, max(0.0, (gap - args.max_bottom_blank_pt) / section_count))
            for factor in (1.0, 0.75, 0.5, 0.25):
                stretched = tmp / f"resume-{compactness}-stretch-{factor}.pdf"
                build(data, stretched, compactness, needed * factor)
                stretched_pages = page_count(stretched)
                stretched_gap = bottom_gap_points(stretched)
                if stretched_pages is not None and stretched_pages > 1:
                    continue
                if stretched_gap is not None and stretched_gap < gap:
                    candidate, pages, gap = stretched, stretched_pages, stretched_gap
                    break
        args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
        args.output_pdf.write_bytes(candidate.read_bytes())
        gap_text = "unknown" if gap is None else f"{gap:.1f}pt"
        print(f"Wrote {args.output_pdf} compactness={compactness} pages={pages or 'unknown'} bottom_blank={gap_text}")
        if pages is not None and pages > 1:
            raise SystemExit("PDF exceeds one page; compress source content before delivery.")


if __name__ == "__main__":
    main()
