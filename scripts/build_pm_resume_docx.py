#!/usr/bin/env python3
"""Build a compact one-page-style Chinese PM resume DOCX from structured JSON."""

from __future__ import annotations

import argparse
import json
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


def set_para_spacing(p, before=0, after=0, line=1.0):
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


def configure_doc(doc: Document, compactness: str):
    section = doc.sections[0]
    section.start_type = WD_SECTION.NEW_PAGE
    section.page_width = Inches(8.27)  # A4
    section.page_height = Inches(11.69)
    margin = {"normal": 0.52, "tight": 0.45, "ultra": 0.40}[compactness]
    section.top_margin = Inches(margin)
    section.bottom_margin = Inches(margin)
    section.left_margin = Inches(margin)
    section.right_margin = Inches(margin)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = FONT_CN
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), FONT_CN)
    normal.font.size = Pt({"normal": 9.2, "tight": 8.8, "ultra": 8.5}[compactness])
    normal.font.color.rgb = TEXT


def add_text_line(doc: Document, text: str, size=9, bold=False, align=None, after=0):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    set_para_spacing(p, after=after)
    run = p.add_run(text)
    set_run_font(run, size, bold, TEXT)
    return p


def add_header(doc: Document, basics: dict[str, Any], compactness: str):
    name = basics.get("name") or "姓名"
    title = basics.get("title") or basics.get("intention") or "求职意向：产品经理"
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_para_spacing(p, after=1 if compactness == "ultra" else 2)
    run = p.add_run(name)
    set_run_font(run, {"normal": 17, "tight": 16, "ultra": 15.5}[compactness], True, ACCENT)

    parts = [title]
    for key in ["phone", "email", "city"]:
        value = basics.get(key)
        if value:
            parts.append(str(value))
    for link in basics.get("links") or []:
        if link:
            parts.append(str(link))
    add_text_line(doc, "｜".join(parts), size={"normal": 9, "tight": 8.7, "ultra": 8.4}[compactness], align=WD_ALIGN_PARAGRAPH.CENTER, after=2)


def add_section_heading(doc: Document, title: str, compactness: str):
    p = doc.add_paragraph()
    set_para_spacing(p, before={"normal": 3, "tight": 2, "ultra": 1}[compactness], after=1)
    run = p.add_run(title)
    set_run_font(run, {"normal": 10.5, "tight": 10.2, "ultra": 10}[compactness], True, ACCENT)
    add_bottom_border(p)
    return p


def add_education(doc: Document, items: list[dict[str, Any]], compactness: str):
    if not items:
        return
    add_section_heading(doc, "教育背景", compactness)
    for edu in items:
        main_parts = [edu.get("school"), edu.get("major"), edu.get("degree"), edu.get("time")]
        line = "｜".join([str(x) for x in main_parts if x])
        if line:
            add_text_line(doc, line, size={"normal": 9.2, "tight": 8.8, "ultra": 8.5}[compactness], bold=True, after=0)
        details = edu.get("details") or []
        if details:
            add_text_line(doc, "；".join([str(x) for x in details if x]), size={"normal": 8.8, "tight": 8.5, "ultra": 8.2}[compactness], after=0)


def add_bullet(doc: Document, text: str, compactness: str):
    p = doc.add_paragraph(style=None)
    set_para_spacing(p, after={"normal": 0.6, "tight": 0.3, "ultra": 0}[compactness], line={"normal": 1.02, "tight": 1.0, "ultra": 0.95}[compactness])
    pf = p.paragraph_format
    pf.left_indent = Inches(0.18)
    pf.first_line_indent = Inches(-0.10)
    run = p.add_run("• ")
    set_run_font(run, {"normal": 8.9, "tight": 8.6, "ultra": 8.3}[compactness], False, ACCENT)
    run = p.add_run(str(text))
    set_run_font(run, {"normal": 8.9, "tight": 8.6, "ultra": 8.3}[compactness], False, TEXT)


def add_entry(doc: Document, entry: dict[str, Any], compactness: str):
    heading = entry.get("heading")
    if heading:
        add_text_line(doc, str(heading), size={"normal": 9.2, "tight": 8.8, "ultra": 8.5}[compactness], bold=True, after=0)
    summary = entry.get("summary")
    if summary:
        add_text_line(doc, str(summary), size={"normal": 8.8, "tight": 8.5, "ultra": 8.2}[compactness], after=0)
    for project in entry.get("projects") or []:
        name = project.get("name")
        if name:
            add_text_line(doc, str(name), size={"normal": 8.9, "tight": 8.6, "ultra": 8.3}[compactness], bold=True, after=0)
        ps = project.get("summary")
        if ps:
            add_text_line(doc, str(ps), size={"normal": 8.6, "tight": 8.3, "ultra": 8.1}[compactness], after=0)
        for bullet in project.get("bullets") or []:
            add_bullet(doc, bullet, compactness)
    for bullet in entry.get("bullets") or []:
        add_bullet(doc, bullet, compactness)


def add_sections(doc: Document, sections: list[dict[str, Any]], compactness: str):
    for sec in sections:
        entries = sec.get("entries") or []
        if not entries:
            continue
        add_section_heading(doc, str(sec.get("title") or "经历"), compactness)
        for entry in entries:
            add_entry(doc, entry, compactness)


def add_skills(doc: Document, skills: list[Any], compactness: str):
    if not skills:
        return
    add_section_heading(doc, "技能与其他", compactness)
    text = "；".join([str(x) for x in skills if x])
    if text:
        add_text_line(doc, text, size={"normal": 8.9, "tight": 8.6, "ultra": 8.3}[compactness], after=0)


def scrub_metadata(doc: Document):
    props = doc.core_properties
    props.author = ""
    props.last_modified_by = ""
    props.comments = ""
    props.subject = ""
    props.keywords = ""
    props.title = ""


def build(data: dict[str, Any], output: Path, compactness: str):
    doc = Document()
    configure_doc(doc, compactness)
    add_header(doc, data.get("basics") or {}, compactness)
    add_education(doc, data.get("education") or [], compactness)
    add_sections(doc, data.get("sections") or [], compactness)
    add_skills(doc, data.get("skills") or [], compactness)
    scrub_metadata(doc)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_docx", type=Path)
    parser.add_argument("--compactness", choices=["normal", "tight", "ultra"], default="tight")
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    build(data, args.output_docx, args.compactness)
    print(f"Wrote {args.output_docx}")


if __name__ == "__main__":
    main()
