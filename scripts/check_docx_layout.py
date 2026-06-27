#!/usr/bin/env python3
"""Check DOCX page count and rough bottom whitespace via LibreOffice PDF export."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from pypdf import PdfReader

try:
    import pdfplumber
except Exception:  # pragma: no cover
    pdfplumber = None


def find_soffice(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit("LibreOffice/soffice not found; cannot verify DOCX layout.")


def export_pdf(docx: Path, out_dir: Path, soffice: str) -> Path:
    env = os.environ.copy()
    env.setdefault("HOME", tempfile.mkdtemp(prefix="pm-resume-lo-home-"))
    profile = tempfile.mkdtemp(prefix="pm-resume-lo-profile-")
    cmd = [
        soffice,
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        f"-env:UserInstallation=file://{profile}",
        "--convert-to",
        "pdf",
        "--outdir",
        str(out_dir),
        str(docx),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    except subprocess.CalledProcessError as exc:
        msg = ["LibreOffice PDF export failed."]
        if exc.stdout:
            msg.append("stdout:\n" + exc.stdout.strip())
        if exc.stderr:
            msg.append("stderr:\n" + exc.stderr.strip())
        raise SystemExit("\n".join(msg)) from exc
    pdf = out_dir / f"{docx.stem}.pdf"
    if not pdf.exists():
        raise SystemExit(f"PDF export failed: {pdf} not found")
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
            return page.height
        lowest = max(float(ch.get("bottom", 0)) for ch in chars)
        return max(0.0, float(page.height) - lowest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--max-bottom-blank-pt", type=float, default=48.0, help="Approx. 3 lines including bottom margin.")
    parser.add_argument("--soffice")
    parser.add_argument("--keep-pdf", type=Path)
    args = parser.parse_args()

    soffice = find_soffice(args.soffice)
    with tempfile.TemporaryDirectory(prefix="pm-resume-check-") as td:
        out_dir = Path(td)
        pdf = export_pdf(args.docx, out_dir, soffice)
        reader = PdfReader(str(pdf))
        pages = len(reader.pages)
        gap = bottom_gap_points(pdf)
        if args.keep_pdf:
            args.keep_pdf.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf, args.keep_pdf)

    print(f"pages={pages}")
    if gap is not None:
        print(f"bottom_blank_pt={gap:.1f}")
    else:
        print("bottom_blank_pt=unknown")

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
