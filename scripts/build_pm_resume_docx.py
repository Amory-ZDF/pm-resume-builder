#!/usr/bin/env python3
"""Build a fixed-style Chinese PM resume DOCX from structured JSON.

The script intentionally keeps typography and spacing stable. Page fit must be
solved by editing resume content, then verified with check_docx_layout.py.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

FONT_CN = "Microsoft YaHei"
FONT_FALLBACK = "PingFang SC"
ACCENT = RGBColor(31, 78, 121)
TEXT = RGBColor(30, 30, 30)

# Fixed Internet-company style. Do not change these values to force fit.
PAGE_MARGIN_IN = 0.45
NAME_PT = 16.0
INFO_PT = 8.7
SECTION_PT = 10.2
ENTRY_PT = 8.8
BODY_PT = 8.6
SMALL_PT = 8.3
LINE_SPACING = 1.0
BULLET_AFTER_PT = 0.3
SECTION_BEFORE_PT = 2.0

IMPORTANT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?\s*(?:\+|%|％|w|W|万|千|百|小时|分钟|天|周|月|年|人|次|个|条|篇)|"
    r"\d+(?:\.\d+)?/\d+(?:\.\d+)?|"
    r"(?:TOP|Top|top)\s*\d+|"
    r"(?:GMV|ROI|CTR|CVR|DAU|MAU|SQL|A/B|PRD|SOP|RAG|LLM|AI))(?:[。；;，,])?"
)


def set_run_font(run, size_pt: float | None = None, bold: bool | None = None, color: RGBColor | None = None):
    run.font.name = FONT_CN
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT_CN)
    run._element.rPr.rFonts.set(qn("w:ascii"), FONT_FALLBACK)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), FONT_FALLBACK)
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def set_para_spacing(p, before=0, after=0, line=LINE_SPACING):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def add_bottom_border(paragraph, color="4F81BD", size="6"):
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)


def configure_doc(doc: Document):
    section = doc.sections[0]
    section.start_type = WD_SECTION.NEW_PAGE
    section.page_width = Inches(8.27)  # A4
    section.page_height = Inches(11.69)
    section.top_margin = Inches(PAGE_MARGIN_IN)
    section.bottom_margin = Inches(PAGE_MARGIN_IN)
    section.left_margin = Inches(PAGE_MARGIN_IN)
    section.right_margin = Inches(PAGE_MARGIN_IN)

    normal = doc.styles["Normal"]
    normal.font.name = FONT_CN
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), FONT_CN)
    normal.font.size = Pt(BODY_PT)
    normal.font.color.rgb = TEXT


def add_rich_text(paragraph, text: str, size: float, *, base_bold: bool = False, emphasize_metrics: bool = True):
    pos = 0
    text = str(text)
    for match in IMPORTANT_PATTERN.finditer(text) if emphasize_metrics else []:
        if match.start() > pos:
            run = paragraph.add_run(text[pos:match.start()])
            set_run_font(run, size, base_bold, TEXT)
        run = paragraph.add_run(match.group(0))
        set_run_font(run, size, True, TEXT)
        pos = match.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        set_run_font(run, size, base_bold, TEXT)


def add_text_line(doc: Document, text: str, size=BODY_PT, bold=False, align=None, after=0):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    set_para_spacing(p, after=after)
    if bold:
        run = p.add_run(text)
        set_run_font(run, size, bold, TEXT)
    else:
        add_rich_text(p, text, size)
    return p


def add_header(doc: Document, basics: dict[str, Any]):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_para_spacing(p, after=2)
    run = p.add_run(basics.get("name") or "姓名")
    set_run_font(run, NAME_PT, True, ACCENT)

    parts = [basics.get("title") or basics.get("intention") or "求职意向：产品经理"]
    for key in ["phone", "email", "city"]:
        value = basics.get(key)
        if value:
            parts.append(str(value))
    parts.extend([str(link) for link in basics.get("links") or [] if link])
    add_text_line(doc, "｜".join(parts), size=INFO_PT, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)


def add_section_heading(doc: Document, title: str):
    p = doc.add_paragraph()
    set_para_spacing(p, before=SECTION_BEFORE_PT, after=1)
    run = p.add_run(title)
    set_run_font(run, SECTION_PT, True, ACCENT)
    add_bottom_border(p)


def add_education(doc: Document, items: list[dict[str, Any]]):
    if not items:
        return
    add_section_heading(doc, "教育背景")
    for edu in items:
        main_parts = [edu.get("school"), edu.get("major"), edu.get("degree"), edu.get("time")]
        line = "｜".join([str(x) for x in main_parts if x])
        if line:
            add_text_line(doc, line, size=ENTRY_PT, bold=True)
        details = edu.get("details") or []
        if details:
            add_text_line(doc, "；".join([str(x) for x in details if x]), size=SMALL_PT)


def clean_bullet_text(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text)).strip().rstrip("。.")


def add_bullet(doc: Document, text: str):
    p = doc.add_paragraph(style=None)
    set_para_spacing(p, after=BULLET_AFTER_PT, line=LINE_SPACING)
    pf = p.paragraph_format
    pf.left_indent = Inches(0.18)
    pf.first_line_indent = Inches(-0.10)
    run = p.add_run("• ")
    set_run_font(run, BODY_PT, False, ACCENT)
    add_rich_text(p, clean_bullet_text(text), BODY_PT)


def add_entry(doc: Document, entry: dict[str, Any]):
    if entry.get("heading"):
        add_text_line(doc, str(entry["heading"]), size=ENTRY_PT, bold=True)
    if entry.get("summary"):
        add_text_line(doc, str(entry["summary"]), size=SMALL_PT)
    for project in entry.get("projects") or []:
        if project.get("name"):
            add_text_line(doc, str(project["name"]), size=BODY_PT, bold=True)
        if project.get("summary"):
            add_text_line(doc, str(project["summary"]), size=SMALL_PT)
        for bullet in project.get("bullets") or []:
            add_bullet(doc, bullet)
    for bullet in entry.get("bullets") or []:
        add_bullet(doc, bullet)


def add_sections(doc: Document, sections: list[dict[str, Any]]):
    for sec in sections:
        entries = sec.get("entries") or []
        if not entries:
            continue
        add_section_heading(doc, str(sec.get("title") or "经历"))
        for entry in entries:
            add_entry(doc, entry)


def add_skills(doc: Document, skills: list[Any]):
    if not skills:
        return
    add_section_heading(doc, "技能与其他")
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
    for line in lines:
        p = doc.add_paragraph()
        set_para_spacing(p, after=BULLET_AFTER_PT, line=LINE_SPACING)
        add_rich_text(p, line, BODY_PT)


def scrub_metadata(doc: Document):
    props = doc.core_properties
    props.author = ""
    props.last_modified_by = ""
    props.comments = ""
    props.subject = ""
    props.keywords = ""
    props.title = ""


def build(data: dict[str, Any], output: Path):
    doc = Document()
    configure_doc(doc)
    add_header(doc, data.get("basics") or {})
    add_education(doc, data.get("education") or [])
    add_sections(doc, data.get("sections") or [])
    add_skills(doc, data.get("skills") or [])
    scrub_metadata(doc)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_docx", type=Path)
    parser.add_argument("--compactness", default="standard", help="Deprecated; layout is fixed. Adjust content instead.")
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    build(data, args.output_docx)
    print(f"Wrote {args.output_docx} layout=standard")


if __name__ == "__main__":
    main()
