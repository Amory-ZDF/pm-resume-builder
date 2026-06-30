# JD Tailoring

## Required pre-step: multi-tag capability analysis

Before tailoring a resume to a JD, read `jd-multitag-capability-map.md`. Do not rely only on the job title. First analyze:

- Title-seeded tags.
- JD-content tags from responsibilities and requirements.
- Weighted tag mix.
- 3-6 core capabilities.
- Resume evidence priorities and red lines.

Send this analysis to the user and ask for confirmation or correction. Only rewrite the resume after the user confirms or modifies the tags/capabilities.

## Workflow

1. Extract JD signals:
   - Product domain: C端/B端/AI/数据/增长/商业化/平台/后台/电商/内容/社交/SaaS.
   - Required skills: PRD,原型,数据分析,SQL,用户研究,项目推进,商业分析,AI工具,模型评估.
   - Business metrics: conversion, retention, DAU, revenue, efficiency, cost, satisfaction.
   - Seniority signals: intern, junior, experienced, owner, lead.

2. Map each JD signal to real resume evidence:
   - Strong match: user has direct project or metric.
   - Partial match: user has transferable method or adjacent domain.
   - No match: do not invent; optionally mention as learning interest only if appropriate.

3. Reorder sections and bullets:
   - Put strongest JD-relevant experience first within page-budget constraints.
   - Move unrelated details to lower priority or remove.
   - Rewrite first bullets to mirror JD vocabulary naturally.

4. Preserve authenticity:
   - Do not add unsupported tools or domain words.
   - Do not make internship scope look like senior PM ownership.
   - If tailoring requires assumptions, list them for user confirmation before final DOCX when practical.

5. Score JD match only for JD-tailoring tasks:
   - Do not score from-scratch resume writing or general resume polishing tasks without a JD.
   - After the final resume is generated, calculate and include `简历匹配度` in the final user response. Do not write the score into the resume DOCX unless the user explicitly asks.

## 简历匹配度评分

Use this score only when the user provides a target JD. The score measures resume-JD fit, not general resume quality.

1. Use the confirmed JD tag/capability analysis as the scoring basis.
2. Select 3-6 core JD capability points and assign weights that sum to 100. Weight by JD importance, mainly from responsibilities and requirements.
3. For each capability, rate resume evidence strength from 0-4:
   - 0: no relevant evidence.
   - 1: keyword only; no concrete project/action.
   - 2: transferable or adjacent evidence, but not directly matching the JD.
   - 3: direct project/action/deliverable evidence.
   - 4: direct evidence with method, deliverable, and source-supported result/metric or core tool.
4. Calculate each capability score as `capability_weight × evidence_strength / 4`.
5. Sum all capability scores and round to the nearest integer. Do not apply score caps or add resume-quality factors such as layout, aesthetics, bullet format, or one-page fit.

Final response format for JD-tailoring tasks:

```text
简历匹配度：X/100
说明：该评分仅针对简历和岗位的匹配度，与简历质量无关。
匹配依据：
- 高匹配：...
- 部分匹配：...
- 待补强：...
```

## Keyword integration

Use JD keywords only when supported by facts. Prefer natural phrasing:
- JD: `增长转化、用户分层、A/B实验`
- Resume: `基于用户分层设计活动触达策略，配合运营完成 A/B 方案对比，复盘不同人群转化差异。`

Avoid keyword stuffing:
- Bad: `熟悉增长转化、用户分层、A/B实验、数据分析、策略产品、商业化。`
- Better: show the keyword inside a real bullet with action and result.

## Tailored summary policy

Do not add a long “个人总结” by default. If needed, add a one-line profile only when it improves matching and does not crowd the page:
`产品经理候选人，具备[方向]项目经验，熟悉[方法/工具]，能完成从需求分析、原型设计到上线复盘的基础闭环。`
