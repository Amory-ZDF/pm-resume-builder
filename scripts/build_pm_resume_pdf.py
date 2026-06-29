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
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: reportlab. Use the Codex bundled Python runtime or install reportlab.") from exc

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None


FONT = "STSong-Light"
ACCENT = colors.HexColor("#1F4E79")
TEXT = colors.HexColor("#1E1E1E")

IMPORTANT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?\s*(?:\+|%|％|w|W|万|千|百|小时|分钟|天|周|月|年|人|次|个|条|篇)|"
    r"\d+(?:\.\d+)?/\d+(?:\.\d+)?|"
    r"(?:TOP|Top|top)\s*\d+|"
    r"(?:GMV|ROI|CTR|CVR|DAU|MAU|SQL|A/B|PRD|SOP|RAG|LLM|AI))"
)


def register_fonts() -> None:
    pdfmetrics.registerFont(UnicodeCIDFont(FONT))


def sizes(compactness: str) -> dict[str, float]:
    return {
        "normal": {"name": 17, "body": 8.9, "small": 8.4, "heading": 10.5, "lead": 10.8, "gap": 3.0, "margin": 0.52},
        "tight": {"name": 16, "body": 8.5, "small": 8.1, "heading": 10.0, "lead": 10.0, "gap": 2.0, "margin": 0.45},
        "ultra": {"name": 15, "body": 8.1, "small": 7.8, "heading": 9.6, "lead": 9.4, "gap": 1.2, "margin": 0.40},
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
    raw = str(text or "")
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


def make_story(data: dict[str, Any], compactness: str) -> list[Any]:
    s = sizes(compactness)
    body = style("body", s["body"], leading=s["lead"])
    small = style("small", s["small"], leading=s["lead"] - 0.4)
    heading = style("heading", s["heading"], leading=s["heading"] + 1.0, color=ACCENT)
    centered = style("center", s["body"], leading=s["lead"], align=TA_CENTER)
    name_style = style("name", s["name"], leading=s["name"] + 2, color=ACCENT, align=TA_CENTER)
    bullet_style = style("bullet", s["body"], leading=s["lead"], leftIndent=10, firstLineIndent=-7)

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
        add_section(story, "教育背景", heading, s["gap"])
        for edu in education:
            line = "｜".join([str(x) for x in [edu.get("school"), edu.get("major"), edu.get("degree"), edu.get("time")] if x])
            add_paragraph(story, line, body, bold=True)
            details = "；".join([str(x) for x in edu.get("details") or [] if x])
            add_paragraph(story, details, small)

    for sec in data.get("sections") or []:
        entries = sec.get("entries") or []
        if not entries:
            continue
        add_section(story, str(sec.get("title") or "经历"), heading, s["gap"])
        for entry in entries:
            add_paragraph(story, entry.get("heading"), body, bold=True)
            add_paragraph(story, entry.get("summary"), small)
            for project in entry.get("projects") or []:
                add_paragraph(story, project.get("name"), body, bold=True)
                add_paragraph(story, project.get("summary"), small)
                for bullet in project.get("bullets") or []:
                    story.append(Paragraph("• " + rich(bullet), bullet_style))
            for bullet in entry.get("bullets") or []:
                story.append(Paragraph("• " + rich(bullet), bullet_style))

    skill_lines = split_skill_lines(data.get("skills") or [])
    if skill_lines:
        add_section(story, "技能与其他", heading, s["gap"])
        for line in skill_lines:
            add_paragraph(story, line, body)

    return story


def build(data: dict[str, Any], output: Path, compactness: str) -> None:
    s = sizes(compactness)
    margin_pt = s["margin"] * 72
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=margin_pt,
        rightMargin=margin_pt,
        topMargin=margin_pt,
        bottomMargin=margin_pt,
        title="",
        author="",
        subject="",
    )
    doc.build(make_story(data, compactness))


def page_count(pdf: Path) -> int | None:
    if PdfReader is None:
        return None
    return len(PdfReader(str(pdf)).pages)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--compactness", choices=["auto", "normal", "tight", "ultra"], default="auto")
    args = parser.parse_args()

    register_fonts()
    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    variants = ["normal", "tight", "ultra"] if args.compactness == "auto" else [args.compactness]
    last_count: int | None = None
    with tempfile.TemporaryDirectory(prefix="pm-resume-pdf-") as td:
        tmp = Path(td)
        for compactness in variants:
            candidate = tmp / f"resume-{compactness}.pdf"
            build(data, candidate, compactness)
            last_count = page_count(candidate)
            if last_count is None or last_count <= 1 or compactness == variants[-1]:
                args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
                args.output_pdf.write_bytes(candidate.read_bytes())
                print(f"Wrote {args.output_pdf} compactness={compactness} pages={last_count or 'unknown'}")
                if last_count is not None and last_count > 1:
                    raise SystemExit("PDF exceeds one page; compress source content before delivery.")
                return


if __name__ == "__main__":
    main()
