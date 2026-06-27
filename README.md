# PM Resume Builder

一个用于帮助 AI Agent 编写、改写和定制中文产品经理简历的 Skill。

它适合在 Codex、Claude 或其他支持读取文件的 Agent 中使用，目标是生成一份**简洁、互联网大厂风格、一页以内的 Word 简历**。

## 能解决什么问题

### 1. 不会写产品经理简历

用户可以提供零散信息，例如教育背景、实习经历、项目经历、校园经历、技能等。Agent 会帮助整理成产品经理简历结构，并改写成更专业的表达。

### 2. 根据岗位 JD 定制简历

用户可以提供已有简历和目标岗位 JD。Agent 会提取岗位关键词，筛选最相关经历，调整内容顺序，并改写 bullet point，让简历更贴合目标岗位。

### 3. 把已有简历改成一页 Word 版本

支持输入已有简历文件，重新整理结构、压缩内容，并输出 `.docx` 简历。

## 支持的输入

- 用户直接粘贴的文字
- Markdown / TXT 文件
- Word 简历：`.docx`
- PDF 简历：`.pdf`
- Word / PDF 格式的岗位 JD

## 输出结果

默认输出：

- 中文简历
- 产品经理方向
- 简洁互联网风格
- Word `.docx` 文件
- 尽量控制在一页以内

## 如何在 Codex 中使用

把本项目放到 Codex Skills 目录：

```bash
mkdir -p ~/.codex/skills
cp -R pm-resume-builder ~/.codex/skills/
```

然后在 Codex 中这样调用：

```text
Use $pm-resume-builder 帮我根据这份简历生成一页中文产品经理简历，输出 Word 文件。
```

如果有目标岗位 JD：

```text
Use $pm-resume-builder 根据我的简历和这个岗位 JD，定制一份一页以内的中文产品经理简历，输出 Word 文件。
```

## 如何在 Claude 或其他 Agent 中使用

把整个 `pm-resume-builder` 文件夹上传给 Agent，然后这样说：

```text
请使用 pm-resume-builder 文件夹中的 SKILL.md 作为操作指南，帮我根据简历和目标 JD 生成一页中文产品经理简历，最终输出 Word 文件。
```

如果 Agent 不认识 Skill 格式，也可以直接说明：

```text
请先阅读 SKILL.md，再根据 references 里的规则处理简历。不要编造经历，最终输出一页以内的 .docx 简历。
```

## 典型使用方式

### 从零写简历

```text
Use $pm-resume-builder 我是应届生，想投产品经理实习。下面是我的教育背景、项目经历和技能，请帮我写一份一页中文简历，并输出 Word。
```

### 修改已有简历

```text
Use $pm-resume-builder 这是我的简历 PDF，请帮我改成更适合互联网产品经理岗位的一页 Word 简历。
```

### 针对 JD 定制简历

```text
Use $pm-resume-builder 这是我的简历和目标岗位 JD，请帮我定制简历，突出和岗位最相关的项目与能力。
```

## 文件输入处理

如果 Agent 需要先抽取 Word 或 PDF 内容，可以使用：

```bash
python scripts/extract_resume_input.py candidate_resume.docx --out work/extracted_resume.txt
python scripts/extract_resume_input.py target_jd.pdf --out work/extracted_jd.txt
```

然后再根据抽取结果生成结构化简历内容。

## 生成 Word 简历

Agent 可以先把简历整理成 JSON，再生成 Word：

```bash
python scripts/build_pm_resume_docx.py work/resume.json output_resume.docx --compactness tight
```

如需检查是否一页以内：

```bash
python scripts/check_docx_layout.py output_resume.docx
```

## 简历改写原则

- 可以优化表达，但不要编造经历。
- 可以合理包装数据，但必须在用户提供事实的基础上。
- 实习经历不要写得像资深负责人。
- 实习生更适合使用“参与”“协助”“支持”“负责某个模块”等表达。
- 不要凭空添加公司、学校、项目、奖项、工具、指标。
- 最终简历应简洁、可信、好读。

## 项目结构

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
