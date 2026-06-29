#!/usr/bin/env python3
"""Check structured resume JSON for PM resume writing rules.

This is a content-structure gate before DOCX generation. It does not judge
truthfulness; it prevents common formatting regressions such as too many bullets
under one entry, unlabeled bullets, and using the skills section as filler.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

LABEL_RE = re.compile(r"^[\u4e00-\u9fffA-Za-z0-9/]{2,12}[:：]")
ALLOWED_SECTIONS = {"工作经历", "实习经历", "项目经历", "校园经历"}
FILLER_SECTION_TITLES = {"能力补充", "补充能力", "其他补充", "个人补充"}
FILLER_SKILL_PREFIXES = (
    "项目协作：",
    "内容策略：",
    "增长复盘：",
    "PM迁移：",
    "目标岗位：",
    "荣誉补充：",
)


def split_skill_lines(skills: list[Any]) -> list[str]:
    lines: list[str] = []
    for item in skills:
        if not item:
            continue
        if isinstance(item, dict):
            label = str(item.get("label") or item.get("category") or "").strip()
            values = item.get("items") or item.get("values") or item.get("text") or ""
            if isinstance(values, list):
                values = "、".join(str(v) for v in values if v)
            text = f"{label}：{values}" if label else str(values)
        else:
            text = str(item).strip()
        lines.extend(p.strip() for p in re.split(r"[;；]", text) if p.strip())
    return lines


def check_bullets(path: str, bullets: Any, max_bullets: int, errors: list[str]):
    if not bullets:
        return
    if not isinstance(bullets, list):
        errors.append(f"{path}: bullets must be a list")
        return
    if len(bullets) > max_bullets:
        errors.append(f"{path}: has {len(bullets)} bullets, expected <= {max_bullets}")
    for idx, bullet in enumerate(bullets, 1):
        text = str(bullet).strip()
        if not LABEL_RE.match(text):
            errors.append(f"{path}[{idx}]: bullet should start with a concise label like 需求分析：")


def check_file(path: Path, max_bullets: int, max_skill_lines: int) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for sec_idx, section in enumerate(data.get("sections") or [], 1):
        title = str(section.get("title") or "").strip()
        if title in FILLER_SECTION_TITLES:
            errors.append(f"sections[{sec_idx}]: filler section title is not resume-appropriate: {title}")
        elif title and title not in ALLOWED_SECTIONS:
            errors.append(f"sections[{sec_idx}]: unexpected section title: {title}")
        for ent_idx, entry in enumerate(section.get("entries") or [], 1):
            base = f"sections[{sec_idx}].entries[{ent_idx}]"
            check_bullets(f"{base}.bullets", entry.get("bullets"), max_bullets, errors)
            for proj_idx, project in enumerate(entry.get("projects") or [], 1):
                check_bullets(
                    f"{base}.projects[{proj_idx}].bullets",
                    project.get("bullets"),
                    max_bullets,
                    errors,
                )

    skill_lines = split_skill_lines(data.get("skills") or [])
    if len(skill_lines) > max_skill_lines:
        errors.append(f"skills: has {len(skill_lines)} rendered lines, expected <= {max_skill_lines}")
    for line in skill_lines:
        if line.startswith(FILLER_SKILL_PREFIXES):
            errors.append(f"skills: likely filler line should be moved into experience bullets: {line}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_files", nargs="+", type=Path)
    parser.add_argument("--max-bullets", type=int, default=4)
    parser.add_argument("--max-skill-lines", type=int, default=4)
    args = parser.parse_args()

    failed = False
    for json_file in args.json_files:
        errors = check_file(json_file, args.max_bullets, args.max_skill_lines)
        if errors:
            failed = True
            print(f"{json_file}: FAIL")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"{json_file}: PASS")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
