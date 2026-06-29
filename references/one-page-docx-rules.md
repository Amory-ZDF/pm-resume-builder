# One-page DOCX Rules

## Page and style target

Use a clean Internet-company resume style:
- A4 portrait.
- Margins around 0.5 inch; tighten only when necessary.
- Chinese font: Microsoft YaHei / PingFang SC / SimSun fallback.
- Name: 16-18 pt bold.
- Section headings: 10.5-11 pt bold with a thin divider.
- Body: 8.8-9.5 pt, readable line spacing.
- Bullets: compact hanging indent; no decorative icons, photos, sidebars, or heavy tables.

## Content budget

Default one-page budget:
- Header + basic info: 3-5 lines.
- Education: 1-3 lines.
- Strongest experience: 3-5 bullets total.
- Secondary experience: 2-3 bullets total.
- Project experience: 2-4 bullets total.
- Campus experience: 0-1 compact entry, only if it strengthens PM evidence.
- Skills: 1-2 compact lines.

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
6. Loosen layout moderately: normal compactness, slightly larger body font, natural line spacing, or slightly larger vertical margins.

Do not invent filler just to fill the page. If the source is genuinely too thin, keep the whitespace and state the limitation.

## Compression sequence

When over one page:
1. Delete weak or unrelated bullets.
2. Remove repeated context phrases.
3. Merge two small bullets into one concise bullet.
4. Cut older/less relevant internship or project details.
5. Reduce project subtitles before reducing readability.
6. Tighten layout: smaller after-spacing, smaller body font down to about 8.5 pt, narrower margins down to about 0.4 inch.
7. If still over, tell the user which tradeoff is required.

Do not solve overflow by making unreadably tiny text, using negative spacing, hiding text, or removing section names.

## Bottom whitespace rule

The final page should not end with more than about 3 blank lines. Page count alone is not enough. If the resume has enough real content, fill the page by restoring relevant bullets, adding a source-supported context sentence, expanding compact skills, or slightly loosening spacing. If the candidate truly has little content, do not invent filler; mention that the source material is insufficient to naturally fill a full page.

## Verification

A final answer should only claim one-page success after one of these checks:
- DOCX rendered to PDF/PNG and inspected; or
- `scripts/check_docx_layout.py` reports 1 page and acceptable bottom whitespace.

If the check returns 1 page but unacceptable bottom whitespace, run the expansion sequence and regenerate. If the check returns more than 1 page, run the compression sequence and regenerate.

If rendering tools are unavailable, disclose that visual verification could not be completed.

## Deliverable hygiene for batch tests

When running batch tests, keep internal artifacts separate from user-facing deliverables. Create a clean deliverables folder that contains only final `.docx` and `.pdf` files, plus at most a short summary. Keep extracted text, JSON, logs, and layout diagnostics in internal folders.

## PDF export without repeated Word permission prompts

For batch tests or user-facing Word+PDF deliverables generated from structured JSON, prefer `scripts/build_pm_resume_pdf.py` and `scripts/build_pm_resume_docx.py` from the same JSON. This avoids Microsoft Word automation entirely and prevents repeated Desktop/Documents permission prompts.

If an exact DOCX-to-PDF rendering is required, use `scripts/export_docx_to_pdf.py` instead of hand-written AppleScript. The script first tries LibreOffice/soffice headless. If it must use Microsoft Word on macOS, it copies DOCX files to a temporary directory, exports PDFs there in one Word session, and then copies PDFs back to the output directory. This avoids repeatedly asking Microsoft Word for Desktop/Documents file access.

Do not make Word open files directly from Desktop, Documents, iCloud Drive, or other protected user folders in a per-file loop.
