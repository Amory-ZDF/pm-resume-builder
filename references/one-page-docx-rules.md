# One-page DOCX Rules

## Page and style target

Use a clean Internet-company resume style:
- A4 portrait.
- Margins fixed at about 0.45 inch.
- Chinese font: Microsoft YaHei / PingFang SC / SimSun fallback.
- Name: 16 pt bold.
- Section headings: about 10.2 pt bold with a thin divider.
- Body/bullets: about 8.6 pt with consistent line spacing.
- Bullets: compact hanging indent; no decorative icons, photos, sidebars, heavy tables, or one-off spacing hacks.

Treat this as a fixed template. Do not change fonts, margins, line spacing, or section spacing to make a resume fit. Use content edits instead.

## Content budget

Default one-page budget:
- Header + basic info: 3-5 lines.
- Education: 1-3 lines.
- Strongest experience: 3-5 bullets total.
- Secondary experience: 2-3 bullets total.
- Project experience: 2-4 bullets total.
- Campus experience: 0-1 compact entry, only if it strengthens PM evidence.
- Skills: 1-2 compact lines.

For normal junior/intern PM resumes, do not stop at 5-8 bullets if the source has usable material. Target 12-18 bullets or bullet-equivalent lines across internships, work, projects, campus PM evidence, and skills. If the source supports fewer than 10 high-signal lines, mark it as source-sparse instead of pretending the page is naturally full.

For internship/campus resumes:
- Internships: 40-50% of page.
- Projects: 25-35%.
- Education and skills: 15-25%.

For full-time resumes:
- Work experience: 50-65%.
- Projects: 20-30%.
- Education/skills/internships: 10-20%.

## Expansion sequence

When the resume is one page but leaves more than about 3 blank lines at the bottom, first decide whether source content is sufficient. If it is sufficient, expand before delivery:

1. Restore the strongest PM-relevant bullet previously removed.
2. Add or improve one context sentence for the strongest experience.
3. Add source-supported methods: user research,竞品分析,需求分析,PRD,原型,流程图,数据分析,复盘.
4. Expand skills into 2-4 compact category rows grouped by PM methods / tools / data / AI or technical literacy; do not use one semicolon-heavy long row.
5. Add relevant coursework, awards, portfolio, or campus project only if already present in the source.
6. If still sparse, ask for more facts or clearly mark the source as thin. Do **not** enlarge fonts, margins, or line spacing to fill the page.

Do not invent filler just to fill the page. If the source is genuinely too thin, keep the whitespace and state the limitation.

## Compression sequence

When over one page:
1. Delete weak or unrelated bullets.
2. Remove repeated context phrases.
3. Merge two small bullets into one concise bullet.
4. Cut older/less relevant internship or project details.
5. Reduce project subtitles before reducing readability.
6. If still over, remove the next-lowest-priority source-supported detail or ask the user which experience can be cut. Do **not** shrink fonts, margins, or line spacing to hide overflow.

Do not solve overflow by making unreadably tiny text, using negative spacing, hiding text, or removing section names.

## Bottom whitespace rule

The final page should not end with more than about 3 blank lines. Page count alone is not enough. If the resume has enough real content, fill the page by restoring relevant bullets, adding a source-supported context sentence, or expanding compact skills. Keep fonts, margins, and line spacing fixed. If the candidate truly has little content, do not invent filler; mention that the source material is insufficient to naturally fill a full page.

## Verification

A final answer should only claim one-page success after one of these checks:
- `scripts/check_docx_layout.py --method word` reports 1 page and acceptable bottom whitespace from Microsoft Word geometry; or
- DOCX itself rendered to PDF/PNG and inspected; or
- `scripts/check_docx_layout.py` reports 1 page and acceptable bottom whitespace for the DOCX file.

If the check returns 1 page but unacceptable bottom whitespace, run the expansion sequence and regenerate. If the check returns more than 1 page, run the compression sequence and regenerate.

If rendering tools are unavailable, disclose that visual verification could not be completed.

For bottom whitespace, do not rely on Word line count alone. The check must measure the last visible text position on the final Word page, subtract it from the fixed template's usable bottom boundary, and convert the remaining space to approximate body lines. Treat `bottom_blank_lines > 3` as `EXPAND_AND_REWRITE` unless the source is genuinely sparse.

## Mandatory Word-format loop

1. Generate DOCX with the fixed template.
2. Check that DOCX with `scripts/check_docx_layout.py --method word` when Microsoft Word is available, or the Documents skill render workflow otherwise.
3. If `pages > 1`, reduce content: delete weak bullets, merge repeated bullets, shorten summaries, remove low-priority sections.
4. If `pages == 1` but `bottom_blank_lines > 3`, add content: restore source-supported bullets, add concise context, split strong multi-scope entries, expand skills from source.
5. Regenerate the DOCX and repeat. Do not change the template.

Do not use these as proof of Word pagination: direct JSON-to-PDF output, estimated line counts, `docProps/app.xml` page metadata, or visual guessing from Markdown. They may help diagnose content density, but the final gate is rendering/checking the DOCX itself.

## Deliverable hygiene for batch tests

When running batch tests, keep internal artifacts separate from user-facing deliverables. Create a clean deliverables folder that contains only final `.docx` and `.pdf` files, plus at most a short summary. Keep extracted text, JSON, logs, and layout diagnostics in internal folders.

## PDF export without repeated Word permission prompts

For batch tests or user-facing Word+PDF deliverables, generate DOCX with `scripts/build_pm_resume_docx.py`, then verify that DOCX with `scripts/check_docx_layout.py`. If PDF is needed, export the verified DOCX with `scripts/export_docx_to_pdf.py`; use `scripts/build_pm_resume_pdf.py` only as a convenience fallback, not as Word pagination proof.

If an exact DOCX-to-PDF rendering is required, use `scripts/export_docx_to_pdf.py` instead of hand-written AppleScript. The script first tries LibreOffice/soffice headless. If it must use Microsoft Word on macOS, it copies DOCX files to a temporary directory, exports PDFs there in one Word session, and then copies PDFs back to the output directory. This avoids repeatedly asking Microsoft Word for Desktop/Documents file access.

Do not make Word open files directly from Desktop, Documents, iCloud Drive, or other protected user folders in a per-file loop.
