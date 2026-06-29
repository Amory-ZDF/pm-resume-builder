# Quality Review Loop

Use this loop before delivering any resume DOCX. The loop exists because a resume that is merely "one page" can still be poor: too sparse, too generic, over-claimed, or weakly tailored.

## Success gates

A resume is deliverable only when it passes all applicable gates:

1. **Truth gate**: no invented company, school, role, project, award, tool, or exact metric.
2. **PM relevance gate**: each major experience has product-manager evidence: user/market/业务 insight, requirement analysis, prototype/PRD, data analysis, project coordination, launch, or review.
3. **Structure gate**: header, education, experience/project sections, and skills are clear; no dense paragraphs or broken section order.
4. **Density gate**: enough real content is used. A normal one-page junior PM resume should have about 12-18 bullets; sparse resumes should restore real details before changing layout. Do not replace specific source details with empty generic phrases.
5. **Layout gate**: final DOCX is one page; bottom blank space is no more than about 3 lines when enough source content exists.
6. **Readability gate**: text remains readable; do not use tiny font, hidden text, negative spacing, or cramped layout to pass page constraints.
7. **Delivery gate**: final output includes DOCX and, when requested/possible, a short summary of limitations or unresolved checks.

## Review loop

After drafting structured JSON and generating DOCX:

1. Run a content review.
2. Run a layout review.
3. Decide one of four actions:
   - `PASS_DELIVER`: all gates pass.
   - `EXPAND_AND_REWRITE`: one page but too sparse / bottom blank too large.
   - `COMPRESS_AND_REWRITE`: over one page or too dense.
   - `ASK_USER`: important facts are missing and cannot be safely inferred.
4. Apply the chosen action.
5. Regenerate DOCX and review again.
6. Repeat up to 3 iterations. If still failing, deliver the best version and clearly note the remaining limitation.

## Content review checklist

Check the JSON before or after DOCX generation:

- Basics: name/contact/intention present or intentionally placeholdered.
- Education: school, major/degree, time; relevant courses/awards only if useful.
- Experience/project sections: strongest PM evidence first.
- Each important entry has either:
  - 1 context sentence + 2-4 bullets, or
  - a compact heading + 2-4 bullets when page budget is tight.
- Bullets use action + method + deliverable + result.
- Internship wording uses conservative verbs unless user evidence supports stronger ownership.
- Metrics are provided, derived, or softly phrased; no fake exact numbers.
- Skills are compact and relevant to PM roles.

## Layout review checklist

Use rendered PDF/PNG or `scripts/check_docx_layout.py` when available:

- Page count is exactly 1 for the final resume.
- No clipped text, overlapping lines, broken glyphs, broken bullets, or missing Chinese fonts.
- Bottom whitespace is within about 3 lines when source content is sufficient.
- Section spacing is visually balanced.
- Fonts remain readable.

If visual rendering is unavailable, do a structural audit and disclose that visual QA was skipped.

## If one page but bottom blank space is too large

Do **not** stop just because the page count is 1. If the bottom blank area is too large and source content has usable material, use this expansion sequence:

1. Restore high-signal bullets that were cut too aggressively.
2. Add one concise context sentence to the strongest internship/work/project entry if missing.
3. Split a strong multi-scope experience into two project subtitles if it improves PM evidence.
4. Add PM-relevant methods from the source: user research,竞品分析,需求池,PRD,原型,流程图,数据分析,复盘.
5. Expand skills into 2 compact lines grouped by PM method / tools / data / AI or technical literacy.
6. Add relevant coursework, awards, portfolio, or campus project only if present in the source.
7. Split semicolon-packed skills into multiple category rows instead of one long line.
7. Loosen layout moderately: normal compactness, slightly larger body font, natural line spacing, slightly wider vertical margins.

Stop expanding before claims become speculative. If source content is genuinely insufficient, keep whitespace and note the limitation.

## If over one page

Use this compression sequence:

1. Remove weak/unrelated bullets.
2. Remove repeated context phrases.
3. Merge overlapping bullets.
4. Cut lower-priority campus/skills details.
5. Shorten bullets to one line where possible.
6. Tighten layout moderately.
7. If still over one page, ask user which lower-priority experience can be removed or deliver with a limitation note.

## If content is too generic

Rewrite top bullets to show PM capability. Prefer specifics grounded in the source:

- Bad: `负责活动运营，提升用户活跃。`
- Better: `参与活动转化链路梳理，基于用户分层设计触达策略，输出活动方案并复盘点击/转化表现。`

If the source lacks PM work, translate adjacent work into transferable PM evidence without pretending the user held a PM role:

- research/analysis → 用户研究、竞品分析、需求洞察
- operations → 用户分层、活动策略、数据复盘
- consulting/course project → 问题拆解、方案设计、项目推进
- technical/data work → 指标设计、数据分析、工具/平台理解

## If facts are missing

Ask only when the missing fact materially affects truth or positioning:

- unclear target stage or target PM direction
- unclear whether a project was individual or team work
- unclear metric source
- unclear time/company/school
- insufficient source content to fill a one-page resume without speculation

Otherwise make conservative assumptions and proceed.

## Batch testing notes

For batch tests with no user available:

- Do not ask follow-up questions for each resume.
- Use conservative PM-general positioning.
- Record issues in `reports/summary.md`.
- If bottom whitespace fails because source content is sparse, mark `CHECK: source content likely insufficient` rather than inventing filler.
- If many files fail the same gate, report it as a skill improvement opportunity.

## Key data emphasis

When generating DOCX, emphasize source-supported key data with bold text:

- percentages and growth/decline numbers, e.g. `提升 12%`
- volumes, e.g. `覆盖 300+ 商家`, `处理 1,000 条反馈`
- efficiency/time, e.g. `从 2 小时缩短至 30 分钟`
- rankings/awards, e.g. `Top 10%`, `一等奖`
- hard tools/skills when central to the role, e.g. `SQL`, `A/B`, `PRD`, `SOP`, `AI`

Do not bold entire bullets. Bold only the data/tool fragment so the resume remains restrained.
