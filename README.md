# 🧩 PM Resume Builder

一个帮助 AI Agent 生成和定制**中文产品经理简历**的 Skill。

适用于 Codex、Claude 和其他支持读取文件的 Agent。目标是输出一份**简洁、互联网大厂风格、一页以内的 Word 简历**。

## ✨ 能解决什么问题

### 1. 不会写产品经理简历

你可以提供零散信息，例如教育背景、实习经历、项目经历、校园经历、技能等。Agent 会帮你整理成产品经理简历结构，并改写成更专业的表达。

### 2. 针对岗位 JD 定制简历

你可以提供已有简历和目标岗位 JD。Agent 会提取岗位关键词，筛选最相关经历，调整内容顺序，并改写 bullet point，让简历更贴合目标岗位。

## 📥 支持的输入

### 简历输入

- 直接粘贴的文字
- Markdown 文件
- TXT 文件
- Word 文件：`.docx`
- PDF 文件：`.pdf`

### 岗位 JD 输入

- 直接复制粘贴的文字
- PDF 文件：`.pdf`
- 图片：`.png` / `.jpg` / `.jpeg` 等

## 📤 输出结果

默认输出：

- 中文简历
- 产品经理方向
- 简洁互联网风格
- Word `.docx` 文件
- 尽量控制在一页以内

## 🚀 如何下载到 Codex

把本项目复制到 Codex Skills 目录：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Amory-ZDF/pm-resume-builder.git ~/.codex/skills/pm-resume-builder
```

然后开启新的 Codex 对话，即可使用：

```text
Use $pm-resume-builder ...
```

## 🤖 如何给 Claude 或其他 Agent 使用

如果 Agent 支持上传文件夹或项目文件：

1. 下载本项目。
2. 把整个 `pm-resume-builder` 文件夹上传给 Agent。
3. 告诉 Agent：先阅读 `SKILL.md`，再按里面的流程处理简历。

如果 Agent 不识别 Codex Skill 格式，也没关系，把 `SKILL.md` 当作主操作说明即可。

## 📝 统一使用提示词范式

你可以直接复制下面这段，根据自己的情况替换括号里的内容：

```text
Use $pm-resume-builder

请根据我提供的【简历信息/简历文件】生成一份中文产品经理简历。

我的目标岗位是：【产品经理实习生 / 产品经理 / AI 产品经理 / B 端产品经理 / 增长产品经理等】。
目标岗位 JD 是：【粘贴 JD 文本，或说明已上传 JD 文件/图片】。

要求：
1. 输出 Word .docx 文件。
2. 简历控制在一页以内。
3. 风格简洁，偏互联网大厂。
4. 可以优化表达，但不要编造不存在的经历。
5. 如果信息不足，请先问我最关键的问题。
```

如果没有目标 JD，可以删掉 JD 相关内容：

```text
Use $pm-resume-builder

请根据我提供的【简历信息/简历文件】生成一份一页以内的中文产品经理简历，输出 Word .docx 文件。风格简洁，偏互联网大厂。如果信息不足，请先问我最关键的问题。
```

## 📁 项目结构

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
