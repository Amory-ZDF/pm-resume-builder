# PM Resume Builder Skill

A portable agent skill for creating, rewriting, tailoring, and exporting concise one-page Chinese product manager resumes in Word `.docx` format.

The skill is designed for Codex, Claude, and other file-capable AI agents. It supports raw text, Markdown, Word `.docx`, and PDF resume/JD inputs.

## What it does

- Creates Chinese product manager resumes from raw user information.
- Rewrites existing resumes into a concise Internet-company style.
- Tailors a resume to a target JD.
- Supports internship, campus recruitment, junior PM, career-switch, and full-time PM scenarios.
- Applies honesty guardrails for reasonable resume polishing without fabricating experience.
- Generates a final Word `.docx` resume and verifies one-page layout when rendering tools are available.

## Install for Codex

Copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R pm-resume-builder ~/.codex/skills/
```

Then start a new Codex chat and invoke:

```text
Use $pm-resume-builder to create a one-page Chinese product manager resume from candidate_resume.docx.
```

## Use with Claude or another Agent

If the agent supports project files, upload or attach this whole folder and say:

```text
Use the instructions in SKILL.md from the pm-resume-builder folder. Read only the referenced files needed for the task. Create a one-page Chinese product manager resume in DOCX format from candidate_resume.docx and tailor it to target_jd.pdf.
```

If the agent does not understand Codex Skill metadata, treat `SKILL.md` as the main system/task guide and use the files under `references/` and `scripts/` as supporting resources.

## Supported input files

- Existing resume: `.docx`, `.pdf`, `.md`, `.txt`
- Target JD: `.docx`, `.pdf`, `.md`, `.txt`
- Raw pasted candidate information

Use the extractor script for file inputs:

```bash
python scripts/extract_resume_input.py candidate_resume.docx --out work/extracted_resume.txt
python scripts/extract_resume_input.py target_jd.pdf --out work/extracted_jd.txt
```

The extracted text is private user data. Do not commit it to this repo.

## Generate a DOCX resume

The recommended agent flow is:

1. Extract or read candidate information.
2. Ask only for missing essentials.
3. Convert the information into the structured JSON format shown in `assets/resume_schema_example.json`.
4. Build the Word file:

```bash
python scripts/build_pm_resume_docx.py work/resume.json output_resume.docx --compactness tight
```

5. Check layout when LibreOffice is available:

```bash
python scripts/check_docx_layout.py output_resume.docx
```

If the check reports more than one page or excessive bottom whitespace, compress content according to `references/one-page-docx-rules.md` and regenerate.

## Privacy and honesty rules

- Do not invent companies, schools, dates, projects, tools, awards, or exact metrics.
- For internships, prefer `参与`, `协助`, `支持`, and `负责模块`; avoid unsupported claims like `独立负责` or `主导`.
- Reasonable metric polishing is allowed only when grounded in user-provided facts.
- Do not commit real resumes, extracted text, generated private drafts, or personal information.

## Folder map

```text
pm-resume-builder/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── assets/resume_schema_example.json
├── references/
│   ├── input-handling.md
│   ├── reference-structure-standard.md
│   ├── writing-patterns.md
│   ├── honesty-guardrails.md
│   ├── jd-tailoring.md
│   └── one-page-docx-rules.md
└── scripts/
    ├── extract_resume_input.py
    ├── build_pm_resume_docx.py
    └── check_docx_layout.py
```
