# One-page DOCX Rules

## Page and style target

Use a clean Internet-company resume style:
- A4 portrait.
- Margins around 0.45-0.55 inch.
- Chinese font: Microsoft YaHei / PingFang SC / SimSun fallback.
- Name: 16-18 pt bold.
- Section headings: 10.5-11 pt bold with a thin divider.
- Body: 8.8-9.5 pt, readable line spacing.
- Bullets: compact hanging indent; no decorative icons or heavy tables.

## Content budget

Default one-page budget:
- Header + basic info: 3-5 lines.
- Education: 1-3 lines.
- Strongest experience: 3-5 bullets total.
- Secondary experience: 2-3 bullets total.
- Project experience: 2-4 bullets total.
- Skills: 1-2 compact lines.

For internship/campus resumes:
- Internships: 40-50% of page.
- Projects: 25-35%.
- Education and skills: 15-25%.

For full-time resumes:
- Work experience: 50-65%.
- Projects: 20-30%.
- Education/skills/internships: 10-20%.

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

The final page should not end with more than about 3 blank lines. If the resume has enough real content, fill the page by restoring one relevant bullet, adding a compact skills line, or slightly loosening spacing. If the candidate truly has little content, do not invent filler; mention that the source material is insufficient to naturally fill a full page.

## Verification

A final answer should only claim one-page success after one of these checks:
- DOCX rendered to PDF/PNG and inspected; or
- `scripts/check_docx_layout.py` reports 1 page and acceptable bottom whitespace.

If rendering tools are unavailable, disclose that visual verification could not be completed.
