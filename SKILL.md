---
name: pm-resume-builder
description: Create, rewrite, tailor, and export concise one-page Chinese product manager resumes in Word DOCX format from raw text, Markdown, TXT, PDF, or Word DOCX resume inputs, and from text/PDF/image JD inputs. Use when the user asks for a product manager resume, Chinese resume, internship resume, campus recruitment resume, career-switch PM resume, existing resume rewrite from .docx/.pdf, JD-targeted resume customization, resume bullet rewriting, or a one-page Internet-company-style resume deliverable.
---

# PM Resume Builder

## Outcome

Create a **Chinese, concise Internet-company-style product manager resume** and deliver a `.docx` file. Accept raw text, Markdown, TXT, PDF, or Word DOCX as candidate resume inputs; accept pasted text, PDF, or image files as target JD inputs. It is acceptable to draft Markdown internally, but the final user deliverable must be Word DOCX unless the user explicitly asks otherwise. If PDF is requested too, prefer generating DOCX and PDF from the same structured JSON instead of making Microsoft Word open protected user folders.

Hard constraints:
- Keep the resume to exactly **1 page** whenever enough content exists.
- Leave no more than **3 blank lines** at the bottom of the page; if the user has too little content, say so and avoid artificial filler.
- Do not invent companies, roles, projects, responsibilities, tools, awards, education, or impossible metrics.
- Reasonable polishing is allowed, but keep every claim within the candidate's likely scope.
- For internships, prefer “参与 / 协助 / 支持 / 负责模块” and avoid “独立负责 / 主导 / 搭建全链路” unless the user explicitly provided evidence.

## Workflow

1. **Classify the task**
   - From-scratch resume: user provides raw facts and wants a PM resume.
   - JD tailoring: user provides an existing resume and target JD.
   - Rewrite/compress: user wants better bullets or one-page DOCX output.

2. **Ingest provided files or text**
   If the user provides `.docx`, `.pdf`, `.md`, or `.txt` resume inputs, or text/PDF/image JD inputs, read `references/input-handling.md`. Use `scripts/extract_resume_input.py` for supported text-based file extraction; use available OCR/vision tools for JD images, or ask the user to paste the JD text if OCR is unavailable. Treat extracted text as private user data; do not store it in the skill, README, examples, or commits.

3. **Collect only missing essentials**
   Ask concise follow-up questions only when required facts are missing. Required essentials:
   - Target stage: internship / campus recruitment / junior full-time / experienced hire / career switch.
   - Target direction: C-end, B-end, AI product, data product, growth, strategy, commercialization, platform/backend, or general PM.
   - Basic info: name or placeholder, phone/email placeholders if needed, education, target city/role if relevant.
   - Experience facts: organization, role, date, project context, actions, outputs, metrics if available.
   - JD text if tailoring to a specific job.

4. **Structure the resume**
   Use these sections, omitting only truly empty sections after telling the user:
   - 基本信息
   - 教育背景
   - 工作经历
   - 实习经历
   - 项目经历
   - 校园经历（仅当能证明 PM 能力）
   - 技能与其他

   Ordering rules:
   - Internship/campus/career-switch candidates: 基本信息 → 教育背景 → 实习经历 → 项目经历 → 校园经历（强相关才保留）→ 工作经历（如有）→ 技能与其他.
   - Full-time/social candidates: 基本信息 → 教育背景 → 工作经历 → 项目经历 → 实习经历（仅保留强相关）→ 校园经历（通常省略）→ 技能与其他.
   - Within each section, put the most relevant and strongest experience first.

5. **Use the reference structure standard**
   Read `references/reference-structure-standard.md` when creating or reformatting a full resume. Follow its generic one-page Chinese PM structure without copying any private sample content.

6. **Write content with PM bullet patterns**
   Read `references/writing-patterns.md` before drafting bullets. For every work/internship/project entry:
   - Start with one concise project/context sentence: business background + target problem + candidate's role + outcome.
   - Before writing, cluster the raw material into 4-5 candidate points, then merge into 2-4 final bullets.
   - Each final bullet must start with a short capability label, e.g. `需求分析：`, `功能规划：`, `数据复盘：`, and use action + method + deliverable + result.
   - Each work/internship/project/campus entry and each project subtitle may have at most 4 bullets.
   - If one company/internship contains unrelated projects, split them under project subtitles.

7. **Apply honesty guardrails**
   Read `references/honesty-guardrails.md` whenever polishing weak, vague, internship, or metric-light experience. Escalate wording only when evidence supports it. Mark assumptions for user confirmation instead of hiding them.

8. **Tailor to JD if provided**
   Read `references/jd-tailoring.md`. Extract JD keywords, map them to real evidence, then reorder and rewrite content. Never add unsupported domain experience just because the JD asks for it. When the task includes a target JD, include the fixed final response block `简历匹配度`; do not score from-scratch resume writing or general resume polishing tasks without a JD.

9. **Fit to one page**
   Read `references/one-page-docx-rules.md`. Use content budgets before creating DOCX. Fit means both: exactly one page and no excessive bottom whitespace when enough factual source content exists.
   Do not solve sparse pages or overflow by changing font size, margins, or line spacing. Keep the fixed Word style and adjust content: expand, restore, compress, merge, or delete source-supported content.

10. **Run the quality review loop**
   Read `references/quality-review-loop.md` before final delivery. Generate DOCX, review truth/PM relevance/structure/density/layout, then choose: deliver, expand and rewrite, compress and rewrite, or ask the user. Iterate up to 3 times before delivering the best version with a limitation note.

11. **Generate and verify DOCX**
   - Prefer using `scripts/build_pm_resume_docx.py` with structured JSON. The script uses a fixed Word style: 楷体, body/contact/entry 9.5 pt, major headings 10.5 pt, and one blank line before every major section after the first. Do not pass layout/compactness changes to force fit.
   - Before generating DOCX, run `scripts/check_resume_json.py` on structured JSON to catch unlabeled bullets, entries with more than 4 bullets, and filler skill/ability lines.
   - Verify the generated DOCX with `scripts/check_docx_layout.py` or the Documents skill render workflow before delivery. On macOS, the script should use Microsoft Word geometry to measure actual page count and bottom whitespace from a temporary DOCX copy; a PDF generated directly from JSON is not proof that the Word file is one page.
   - If the DOCX is over one page, compress content and regenerate. If bottom blank area is too large, restore/expand real PM-relevant content inside existing work/internship/project bullets and regenerate. Do not add a filler skills row or extra “能力补充” section; do not change font size, margins, or line spacing to solve either problem.
   - If the user requests PDF deliverables during batch tests, prefer `scripts/export_docx_to_pdf.py` after the DOCX passes layout checks, or `scripts/build_pm_resume_pdf.py` only as a convenience copy with a note that Word pagination was checked separately.
   - Iterate until the latest checked version passes: one page, no clipping/overlap, bottom blank area within the 3-line rule when source content allows.

## Resource routing

- `references/input-handling.md`: PDF/Word/Markdown/text input extraction workflow and privacy rules.
- `references/reference-structure-standard.md`: generic one-page Chinese PM resume structure and layout standard derived from a private sample, with no personal content.
- `references/writing-patterns.md`: PM resume section and bullet writing formulas.
- `references/jd-multitag-capability-map.md`: multi-tag JD analysis, capability inventory, and user-confirmation workflow for role-specific tailoring.
- `references/honesty-guardrails.md`: reasonable packaging, metrics, internship scope, and red-flag wording.
- `references/jd-tailoring.md`: JD keyword extraction and tailoring workflow.
- `references/one-page-docx-rules.md`: one-page budgets, expansion/compression order, and Word layout constraints.
- `references/quality-review-loop.md`: internal review loop for truth, PM relevance, density, layout, rewrite decisions, and final delivery gates.
- `scripts/extract_resume_input.py`: extract plain text from `.docx`, `.pdf`, `.md`, or `.txt` resume/JD inputs.
- `scripts/build_pm_resume_docx.py`: build a fixed-style Chinese PM resume DOCX from JSON.
- `scripts/build_pm_resume_pdf.py`: build a fixed-style Chinese PM resume PDF directly from JSON; do not use it as Word pagination proof.
- `scripts/check_resume_json.py`: check structured JSON for labeled bullets, max 4 bullets per entry/project, and no filler skill/ability sections.
- `scripts/check_docx_layout.py`: check actual Word/DOCX page count plus bottom whitespace; prefers Microsoft Word geometry and falls back to temporary PDF rendering when needed.
- `scripts/export_docx_to_pdf.py`: batch export DOCX to PDF while minimizing macOS Word file-access prompts by using temporary copies.

## DOCX generation contract

Drafting Markdown is allowed for reasoning and user review, but final creation should use a structured representation with these top-level keys:

```json
{
  "basics": {"name": "姓名", "title": "求职意向：产品经理", "phone": "", "email": "", "city": "", "links": []},
  "education": [{"school": "", "degree": "", "major": "", "time": "", "details": []}],
  "sections": [
    {"title": "实习经历", "entries": [
      {"heading": "公司｜产品经理实习生｜2025.03-2025.08", "summary": "...", "projects": [{"name": "项目名", "summary": "...", "bullets": ["..."]}], "bullets": []}
    ]}
  ],
  "skills": ["Axure / Figma / SQL / 数据分析 / AIGC 工具使用"]
}
```

Keep the JSON factual and concise. If user data is missing, use placeholders only when the user asked to proceed.
