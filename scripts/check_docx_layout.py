#!/usr/bin/env python3
"""Check DOCX page count and bottom whitespace.

This verifies the Word/DOCX deliverable, not a separate PDF generated from JSON.
On macOS it first asks Microsoft Word for the actual page geometry of a
temporary DOCX copy. This avoids writing PDF artifacts just to know whether the
Word page is sparse. A PDF-render fallback remains available for non-Word
environments.
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


WORD_GEOMETRY_APPLESCRIPT = r'''
on is_blank_char(t)
  if t is "" then return true
  if t is " " then return true
  if t is tab then return true
  if t is return then return true
  if t is linefeed then return true
  if t is (ASCII character 10) then return true
  if t is (ASCII character 13) then return true
  if t is (ASCII character 160) then return true
  return false
end is_blank_char

on run argv
  set docPath to item 1 of argv
  set bodyLinePt to (item 2 of argv) as real
  set f to (POSIX file docPath) as alias
  set beforeCount to 0
  tell application "Microsoft Word"
    set visible to false
    set beforeCount to count of documents
  end tell

  try
    tell application "Microsoft Word"
      open f
      delay 0.8
      set d to active document
      set mainRange to text object of d
      set endPos to end of content of mainRange
      set pos to endPos - 1

      repeat while pos > 0
        set r to create range d start (pos - 1) end pos
        set ch to content of r
        if my is_blank_char(ch) is false then exit repeat
        set pos to pos - 1
      end repeat

      if pos <= 0 then error "No visible text in DOCX"

      set lastRange to create range d start (pos - 1) end pos
      set pagesN to compute statistics d statistic statistic pages
      set linesN to compute statistics d statistic statistic lines
      set lastPageN to get range information lastRange information type active end page number
      set lastTextY to get range information lastRange information type vertical position relative to page
      set ps to page setup of section 1 of d
      set pageHeightPt to page height of ps
      set bottomMarginPt to bottom margin of ps
      set usableBottomPt to pageHeightPt - bottomMarginPt
      set bottomBlankPt to usableBottomPt - (lastTextY + bodyLinePt)
      if bottomBlankPt < 0 then set bottomBlankPt to 0
      set bottomBlankLines to bottomBlankPt / bodyLinePt

      close d saving no
      return "method=word_geometry" & linefeed & ¬
        "pages=" & (pagesN as text) & linefeed & ¬
        "word_lines=" & (linesN as text) & linefeed & ¬
        "last_text_page=" & (lastPageN as text) & linefeed & ¬
        "last_text_y_pt=" & (lastTextY as text) & linefeed & ¬
        "usable_bottom_y_pt=" & (usableBottomPt as text) & linefeed & ¬
        "bottom_blank_pt=" & (bottomBlankPt as text) & linefeed & ¬
        "bottom_blank_lines=" & (bottomBlankLines as text)
    end tell
  on error errMsg number errNo
    try
      tell application "Microsoft Word"
        if (count of documents) > beforeCount then close active document saving no
      end tell
    end try
    error errMsg number errNo
  end try
end run
'''


def parse_key_values(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def word_geometry(docx: Path, body_line_pt: float) -> dict[str, float | int | str]:
    if sys.platform != "darwin":
        raise RuntimeError("Microsoft Word geometry check is only available on macOS")
    if not shutil.which("osascript"):
        raise RuntimeError("osascript is unavailable")

    with tempfile.TemporaryDirectory(prefix="pm-resume-word-check-") as td:
        tmp = Path(td)
        copied = tmp / docx.name
        shutil.copy2(docx, copied)
        script = tmp / "check_word_geometry.applescript"
        script.write_text(WORD_GEOMETRY_APPLESCRIPT, encoding="utf-8")
        proc = subprocess.run(
            ["osascript", str(script), str(copied), str(body_line_pt)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180,
        )

    raw = parse_key_values(proc.stdout)
    return {
        "method": raw.get("method", "word_geometry"),
        "pages": int(float(raw["pages"])),
        "word_lines": int(float(raw["word_lines"])),
        "last_text_page": int(float(raw["last_text_page"])),
        "last_text_y_pt": float(raw["last_text_y_pt"]),
        "usable_bottom_y_pt": float(raw["usable_bottom_y_pt"]),
        "bottom_blank_pt": float(raw["bottom_blank_pt"]),
        "bottom_blank_lines": float(raw["bottom_blank_lines"]),
    }


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
        raise RuntimeError("\n".join(msg)) from exc
    pdf = out_dir / f"{docx.stem}.pdf"
    if not pdf.exists():
        raise RuntimeError(f"DOCX render/export failed: {pdf} not found")
    return pdf


def bottom_gap_points(pdf: Path, bottom_margin_pt: float = 32.4) -> float | None:
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
        return max(0.0, float(page.height) - bottom_margin_pt - lowest)


def pdf_geometry(docx: Path, keep_pdf: Path | None, body_line_pt: float) -> dict[str, float | int | str]:
    with tempfile.TemporaryDirectory(prefix="pm-resume-check-") as td:
        out_dir = Path(td)
        pdf = export_pdf(docx, out_dir)
        pages = len(PdfReader(str(pdf)).pages)
        gap = bottom_gap_points(pdf)
        if keep_pdf:
            keep_pdf.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf, keep_pdf)
    result: dict[str, float | int | str] = {"method": "pdf_render", "pages": pages}
    if gap is not None:
        result["bottom_blank_pt"] = gap
        result["bottom_blank_lines"] = gap / body_line_pt
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--max-bottom-blank-lines", type=float, default=3.0)
    parser.add_argument("--body-line-pt", type=float, default=10.5, help="Approximate final body line height used to convert blank space to lines.")
    parser.add_argument("--max-bottom-blank-pt", type=float, default=None)
    parser.add_argument("--method", choices=["auto", "word", "pdf"], default="auto")
    parser.add_argument("--keep-pdf", type=Path)
    args = parser.parse_args()

    max_gap_pt = args.max_bottom_blank_pt
    if max_gap_pt is None:
        max_gap_pt = args.max_bottom_blank_lines * args.body_line_pt

    try:
        if args.method in {"auto", "word"}:
            result = word_geometry(args.docx, args.body_line_pt)
        else:
            result = pdf_geometry(args.docx, args.keep_pdf, args.body_line_pt)
    except Exception as exc:
        if args.method == "word":
            raise SystemExit(f"Word geometry check failed: {exc}") from exc
        if args.method == "pdf":
            raise SystemExit(f"PDF render check failed: {exc}") from exc
        try:
            result = pdf_geometry(args.docx, args.keep_pdf, args.body_line_pt)
        except Exception as pdf_exc:
            raise SystemExit(f"DOCX layout check failed. Word error: {exc}. PDF error: {pdf_exc}") from pdf_exc

    pages = int(result["pages"])
    gap = result.get("bottom_blank_pt")
    for key in [
        "method",
        "pages",
        "word_lines",
        "last_text_page",
        "last_text_y_pt",
        "usable_bottom_y_pt",
        "bottom_blank_pt",
        "bottom_blank_lines",
    ]:
        if key in result:
            value = result[key]
            print(f"{key}={value:.1f}" if isinstance(value, float) else f"{key}={value}")

    ok_pages = pages <= args.max_pages
    ok_gap = True if gap is None else gap <= max_gap_pt
    if not ok_pages or not ok_gap:
        if not ok_pages:
            print(f"FAIL: expected <= {args.max_pages} page(s)")
        if not ok_gap:
            print(f"FAIL: bottom blank area exceeds {max_gap_pt:.1f} pt / {args.max_bottom_blank_lines:.1f} lines")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
