#!/usr/bin/env python3
"""Check DOCX page count and rough bottom whitespace by rendering DOCX to PDF.

This verifies the Word/DOCX deliverable, not a separate PDF generated from JSON.
It tries the sibling export_docx_to_pdf.py workflow, which prefers headless
conversion and uses temporary copies if Microsoft Word is needed on macOS.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader

try:
    import pdfplumber
except Exception:  # pragma: no cover
    pdfplumber = None


def export_pdf(docx: Path, out_dir: Path) -> Path:
    script = Path(__file__).with_name("export_docx_to_pdf.py")
    cmd = [sys.executable, str(script), str(docx), "--out-dir", str(out_dir)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
    except subprocess.CalledProcessError as exc:
        msg = ["DOCX render/export failed; Word-format page count is unverified."]
        if exc.stdout:
            msg.append("stdout:\n" + exc.stdout.strip())
        if exc.stderr:
            msg.append("stderr:\n" + exc.stderr.strip())
        raise SystemExit("\n".join(msg)) from exc
    pdf = out_dir / f"{docx.stem}.pdf"
    if not pdf.exists():
        raise SystemExit(f"DOCX render/export failed: {pdf} not found")
    return pdf


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--max-bottom-blank-pt", type=float, default=48.0, help="Approx. 3 lines including bottom margin.")
    parser.add_argument("--keep-pdf", type=Path)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="pm-resume-check-") as td:
        out_dir = Path(td)
        pdf = export_pdf(args.docx, out_dir)
        pages = len(PdfReader(str(pdf)).pages)
        gap = bottom_gap_points(pdf)
        if args.keep_pdf:
            args.keep_pdf.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf, args.keep_pdf)

    print(f"pages={pages}")
    print("bottom_blank_pt=unknown" if gap is None else f"bottom_blank_pt={gap:.1f}")

    ok_pages = pages <= args.max_pages
    ok_gap = True if gap is None else gap <= args.max_bottom_blank_pt
    if not ok_pages or not ok_gap:
        if not ok_pages:
            print(f"FAIL: expected <= {args.max_pages} page(s)")
        if not ok_gap:
            print(f"FAIL: bottom blank area exceeds {args.max_bottom_blank_pt:.1f} pt")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
