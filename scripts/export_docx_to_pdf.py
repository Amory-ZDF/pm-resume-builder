#!/usr/bin/env python3
"""Export DOCX files to PDF with minimal macOS permission prompts.

Strategy:
1. Try LibreOffice/soffice headless when available.
2. On macOS, optionally fall back to Microsoft Word AppleScript.
   To avoid repeated Desktop/Documents privacy prompts, the Word fallback copies
   DOCX files into a temporary directory, exports PDFs there in one Word session,
   then copies PDFs to the requested output directory.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable


def collect_docx(inputs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        if item.is_dir():
            files.extend(sorted(item.glob("*.docx")))
        elif item.is_file() and item.suffix.lower() == ".docx":
            files.append(item)
        else:
            raise SystemExit(f"Unsupported input, expected .docx file or directory: {item}")
    # Keep order while de-duplicating.
    seen: set[Path] = set()
    out: list[Path] = []
    for f in files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            out.append(f)
    return out


def find_soffice(explicit: str | None = None) -> str | None:
    if explicit:
        return explicit
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    return None


def export_with_soffice(docx_files: list[Path], out_dir: Path, soffice: str) -> tuple[list[Path], dict[str, str]]:
    exported: list[Path] = []
    errors: dict[str, str] = {}
    for docx in docx_files:
        with tempfile.TemporaryDirectory(prefix="pm-resume-lo-") as td:
            tmp = Path(td)
            env = os.environ.copy()
            env.setdefault("HOME", str(tmp / "home"))
            (tmp / "home").mkdir(parents=True, exist_ok=True)
            profile = tmp / "profile"
            cmd = [
                soffice,
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                f"-env:UserInstallation=file://{profile}",
                "--convert-to",
                "pdf",
                "--outdir",
                str(tmp),
                str(docx),
            ]
            try:
                run_checked(cmd, timeout=120, env=env)
                pdf = tmp / f"{docx.stem}.pdf"
                if not pdf.exists():
                    raise RuntimeError("LibreOffice did not create expected PDF")
                dest = out_dir / f"{docx.stem}.pdf"
                shutil.copy2(pdf, dest)
                exported.append(docx)
            except Exception as exc:
                errors[docx.name] = str(exc)
    return exported, errors


WORD_APPLESCRIPT = r'''
on run argv
  tell application "Microsoft Word"
    set visible to false
    repeat with i from 1 to (count of argv) by 2
      set docxPath to item i of argv
      set pdfPath to item (i + 1) of argv
      set docxName to do shell script "basename " & quoted form of docxPath
      set openedDoc to missing value
      try
        open (POSIX file docxPath as alias)
        repeat with n from 1 to 40
          repeat with d in documents
            if (name of d) is docxName then
              set openedDoc to d
              exit repeat
            end if
          end repeat
          if openedDoc is not missing value then exit repeat
          delay 0.25
        end repeat
        if openedDoc is missing value then error "Microsoft Word did not open the temporary DOCX: " & docxName number -12801
        with timeout of 240 seconds
          save as openedDoc file name (POSIX file pdfPath) file format format PDF
        end timeout
        close openedDoc saving no
      on error errMsg number errNum
        try
          if openedDoc is not missing value then close openedDoc saving no
        end try
        error "Microsoft Word export failed while processing temporary DOCX: " & docxName number -12802
      end try
    end repeat
  end tell
end run
'''


def run_checked(cmd: list[str], *, timeout: int, env: dict[str, str] | None = None) -> None:
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, env=env)
    except subprocess.CalledProcessError as exc:
        details = [f"exit_status={exc.returncode}"]
        if exc.stdout:
            details.append("stdout=" + exc.stdout.strip())
        if exc.stderr:
            details.append("stderr=" + exc.stderr.strip())
        raise RuntimeError("; ".join(details)) from exc
    except subprocess.TimeoutExpired as exc:
        details = [f"timeout_after={exc.timeout}s"]
        if exc.stdout:
            details.append("stdout=" + str(exc.stdout).strip())
        if exc.stderr:
            details.append("stderr=" + str(exc.stderr).strip())
        raise RuntimeError("; ".join(details)) from exc


def export_with_word_temp(docx_files: list[Path], out_dir: Path) -> tuple[list[Path], dict[str, str]]:
    if sys.platform != "darwin":
        return [], {f.name: "Microsoft Word fallback is only available on macOS" for f in docx_files}
    if not shutil.which("osascript"):
        return [], {f.name: "osascript not found" for f in docx_files}

    exported: list[Path] = []
    errors: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="pm-resume-word-export-") as td:
        tmp = Path(td)
        in_dir = tmp / "in"
        pdf_dir = tmp / "pdf"
        in_dir.mkdir()
        pdf_dir.mkdir()
        pairs: list[tuple[Path, Path, Path]] = []
        for idx, src in enumerate(docx_files, start=1):
            tmp_docx = in_dir / f"doc_{idx:03d}.docx"
            tmp_pdf = pdf_dir / f"doc_{idx:03d}.pdf"
            shutil.copy2(src, tmp_docx)
            pairs.append((src, tmp_docx, tmp_pdf))

        script_path = tmp / "export.scpt"
        script_path.write_text(WORD_APPLESCRIPT, encoding="utf-8")
        args: list[str] = []
        for _, tmp_docx, tmp_pdf in pairs:
            args.extend([str(tmp_docx), str(tmp_pdf)])
        try:
            run_checked(["osascript", str(script_path), *args], timeout=max(300, 90 * len(pairs)))
        except Exception as exc:
            # If batch export fails, retry one by one to salvage files and report exact failures.
            errors["__batch__"] = str(exc)

        for src, tmp_docx, tmp_pdf in pairs:
            if not tmp_pdf.exists():
                try:
                    run_checked(["osascript", str(script_path), str(tmp_docx), str(tmp_pdf)], timeout=240)
                except Exception as exc:
                    errors[src.name] = str(exc)
                    continue
            dest = out_dir / f"{src.stem}.pdf"
            shutil.copy2(tmp_pdf, dest)
            exported.append(src)
    return exported, errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="DOCX files or directories containing DOCX files")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory for exported PDFs")
    parser.add_argument("--soffice", help="Optional LibreOffice/soffice executable path")
    parser.add_argument("--no-word-fallback", action="store_true", help="Do not use Microsoft Word AppleScript fallback")
    args = parser.parse_args()

    docx_files = collect_docx(args.inputs)
    if not docx_files:
        raise SystemExit("No DOCX files found")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    remaining = list(docx_files)
    all_errors: dict[str, str] = {}
    soffice = find_soffice(args.soffice)
    if soffice:
        exported, errors = export_with_soffice(remaining, args.out_dir, soffice)
        all_errors.update({f"LibreOffice:{k}": v for k, v in errors.items()})
        exported_set = {p.resolve() for p in exported}
        remaining = [p for p in remaining if p.resolve() not in exported_set]

    if remaining and not args.no_word_fallback:
        exported, errors = export_with_word_temp(remaining, args.out_dir)
        all_errors.update({f"Word:{k}": v for k, v in errors.items()})
        exported_set = {p.resolve() for p in exported}
        remaining = [p for p in remaining if p.resolve() not in exported_set]

    for docx in docx_files:
        status = "OK" if (args.out_dir / f"{docx.stem}.pdf").exists() else "FAIL"
        print(f"{status}\t{docx}")
    if remaining:
        print("\nErrors:", file=sys.stderr)
        for key, value in all_errors.items():
            print(f"- {key}: {value}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
