# Input Handling

Use this guide when the user provides an existing resume file, a JD file/image, or raw text.

## Supported inputs

Resume inputs:
- Pasted text.
- `.md` / `.txt`: Markdown or plain text resume.
- `.docx`: Word resume.
- `.pdf`: exported PDF resume.

JD inputs:
- Pasted text.
- `.pdf`: PDF job description.
- Images such as `.png`, `.jpg`, or `.jpeg` when the agent has OCR/vision tools. If OCR/vision is unavailable, ask the user to paste the JD text or provide a PDF.

## Extraction workflow

1. Treat all extracted text as private user data.
2. Use `scripts/extract_resume_input.py` to extract plain text from resume `.docx`, `.pdf`, `.md`, or `.txt` files and JD `.pdf` files. For JD images, use the agent environment's OCR/vision capability if available.
3. Do not commit extracted text, user resumes, JD files, or generated private drafts into the skill repo.
4. Convert extracted text into the structured resume JSON used by `scripts/build_pm_resume_docx.py`.
5. If extraction is messy or OCR is uncertain, ask the user to confirm ambiguous sections rather than guessing.

Example:

```bash
python scripts/extract_resume_input.py input_resume.docx --out work/extracted_resume.txt
python scripts/extract_resume_input.py target_jd.pdf --out work/extracted_jd.txt
```

## Privacy rules

Never add these to the Skill files, README, examples, or tests:
- Real names, phone numbers, emails, addresses, schools, companies, project names, or links from a user's resume.
- Raw extracted resume/JD text.
- Private file paths that identify a user.

Use placeholders in public docs:
- `candidate_resume.docx`
- `target_jd.pdf`
- `target_jd.png`
- `output_resume.docx`

## Interpreting extracted resume text

After extraction, classify content into:
- 基本信息
- 教育背景
- 工作经历
- 实习经历
- 项目经历
- 校园经历
- 技能与其他

For PDF extraction, watch for broken line order and repeated headers/footers. For JD images, watch for OCR mistakes in job title, requirements, and keywords. Reconstruct by meaning and ask for confirmation when ordering or recognition changes the meaning.
