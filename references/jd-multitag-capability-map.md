# JD Multi-tag Capability Map

This playbook is derived from current public ByteDance product-manager job samples on jobs.bytedance.com. Use it as an abstract mapping, not as copied JD text. The purpose is to avoid over-trusting the job title: a JD can carry multiple tags, and resume tailoring should be based on both title signals and concrete JD content.

## Core rule

Do not classify a JD into one single role type. Produce a weighted tag mix, then map the tag mix to capability requirements and resume evidence.

Use title as a seed, not the final answer:
- Title signal: suggests initial tags.
- JD responsibilities: strongest evidence for what the job actually does.
- JD requirements: validates seniority, tools, and hard skills.
- Product object/business context: refines the tag mix.

Recommended weighting:
- Title: 20%
- Responsibilities: 45%
- Requirements: 25%
- Product object / business context: 10%

If title conflicts with responsibilities, trust responsibilities more.

## Required interaction before tailoring

When the user provides a target JD, do this before rewriting the resume:

1. Analyze the JD into tags and capabilities.
2. Send the analysis to the user for confirmation or correction.
3. Ask the user to confirm, add, remove, or reprioritize tags/capabilities.
4. Only after the user confirms or modifies the analysis, tailor the resume.

Use this concise confirmation format:

```text
我先根据岗位名称和 JD 内容做了岗位能力分析，请你确认：

岗位标签（可多选/可调整）：
- [Tag A] 40%：依据 ...
- [Tag B] 30%：依据 ...
- [Tag C] 20%：依据 ...
- [Tag D] 10%：依据 ...

核心能力点：
1. ...
2. ...
3. ...

我会据此调整简历：
- 优先突出 ...
- 压缩/弱化 ...
- 避免夸大 ...

你可以直接回复“确认”，或告诉我需要增加/删除/调整哪些标签和能力点。
```

Do not expose long internal scoring tables unless the user asks.

## Tag inventory

### AI 应用产品

Signals:
- AI, 大模型, LLM, AIGC, Agent, Copilot, Prompt, RAG, 知识库, 智能助手, AI 搜索, AI Coding.

Capabilities:
- AI 场景拆解
- Prompt / 工作流设计
- 模型效果评测
- AI 产品边界和异常兜底
- 数据反馈与迭代
- 跨算法/工程/设计协作

Resume focus:
- AI 应用场景、输入输出链路、评测指标、用户反馈闭环。
- If the candidate only used AI tools, write AI application/product exploration; do not claim model training.

Avoid unless evidenced:
- 训练大模型、优化算法、设计模型架构、主导技术路线。

### AI 数据 / 训练 / 评测产品

Signals:
- 训练数据, 数据生产, 标注, 评测, Benchmark, 模型质量, 数据闭环, 安全评估, 机器人/具身智能训练.

Capabilities:
- 数据流程设计
- 质量标准和评测体系
- 标注/审核/验收机制
- 模型效果分析
- 平台化工具建设

Resume focus:
- 数据标准、评测流程、质检机制、效率提升、工具平台。

### 搜索 / 推荐产品

Signals:
- 搜索, 推荐, 召回, 排序, 相关性, Query, 结果页, 搜索评测, 内容分发.

Capabilities:
- 用户意图理解
- 策略指标设计
- 搜索/推荐体验优化
- 实验评估
- 数据分析和问题定位

Resume focus:
- 用户路径、相关性/满意度指标、策略实验、结果页体验、反馈闭环。

### 策略 / 规则产品

Signals:
- 策略, 规则, 机制, 分层, 分流, 匹配, 风控, 审核, 供需, 激励, 算法策略.

Capabilities:
- 规则抽象
- 策略拆解
- 实验设计
- 指标评估
- 复杂边界和异常处理

Resume focus:
- 规则设计、实验验证、策略迭代、数据结果。

### 数据 / BI / 分析产品

Signals:
- 数据产品, BI, 指标体系, SQL, 看板, 数据平台, 数据治理, 埋点, 数据资产, 报表.

Capabilities:
- 指标口径设计
- 埋点和数据链路
- 看板/报表产品设计
- SQL/分析能力
- 数据治理和权限

Resume focus:
- 指标体系、看板、埋点、分析结论、业务决策支持。

### 增长产品

Signals:
- 增长, 拉新, 激活, 转化, 留存, 召回, 裂变, A/B 测试, 漏斗, 生命周期, 活跃.

Capabilities:
- 漏斗拆解
- 增长实验
- 用户分层
- 转化/留存分析
- 活动/触达策略

Resume focus:
- 增长目标、关键漏斗节点、实验方案、指标变化。

### C 端体验产品

Signals:
- 用户产品, App, 小程序, 用户体验, 交互, 反馈, 留存, 使用路径, 端上功能, 基础体验.

Capabilities:
- 用户研究
- 场景和路径设计
- 原型/PRD
- 体验问题定位
- 版本迭代

Resume focus:
- 用户洞察、体验优化、功能设计、用户反馈和数据结果。

### B 端 / SaaS / 企业产品

Signals:
- B端, ToB, SaaS, 企业, 客户, 业务流程, 审批, 权限, CRM, ERP, 采购, People, 财务, 内部系统.

Capabilities:
- 业务流程调研
- 角色/权限设计
- 复杂表单和状态流
- 客户/业务方需求管理
- 效率提升

Resume focus:
- 业务流程、角色权限、后台工具、效率指标、跨部门推进。

### 平台 / 中台 / 开放能力产品

Signals:
- 平台, 中台, 开放平台, API, 配置化, 组件, 基础能力, Dev Infra, 工具链, 工作台.

Capabilities:
- 平台抽象
- 通用能力设计
- 配置化设计
- API/技术理解
- 多方需求平衡

Resume focus:
- 模块抽象、配置能力、系统效率、复用性、开发者/运营使用体验。

### 商业化 / 广告产品

Signals:
- 商业化, 广告, 投放, 广告主, 流量, ROI, 预算, 出价, 转化, 样式, 计费.

Capabilities:
- 商业目标理解
- 广告链路和投放流程
- 收入/ROI/转化分析
- 策略实验
- 用户体验与商业收益平衡

Resume focus:
- 转化链路、收入/ROI、广告主体验、策略和实验结果。

### 电商 / 交易 / 商家产品

Signals:
- 电商, TikTok Shop, 抖音电商, 商品, 商家, 店铺, 订单, 支付, 交易, 履约, 售后, 供应链, 生活服务.

Capabilities:
- 交易链路理解
- 商家/用户双边需求
- 商品/订单/履约流程
- 转化和效率优化
- 业务规则设计

Resume focus:
- 商品发布、交易流程、商家工具、订单履约、转化效率。

### 内容 / 社区 / 创作者产品

Signals:
- 内容, 社区, 创作者, 作者, 发布, 互动, 评论, 审核, 内容治理, 内容生态, 短剧, 直播.

Capabilities:
- 内容生态理解
- 创作者工具设计
- 互动和分发机制
- 治理/审核流程
- 社区体验

Resume focus:
- 内容供给、创作者效率、互动指标、审核治理、社区健康度。

### 直播 / 短视频产品

Signals:
- 直播, 短视频, 直播间, 主播, 互动, 连麦, 礼物, 场景体验.

Capabilities:
- 实时互动场景设计
- 用户/主播双边体验
- 转化和留存
- 内容/交易/互动结合

Resume focus:
- 直播间链路、互动体验、转化场景、主播/用户需求。

### 国际化 / 跨境产品

Signals:
- 国际化, 海外, TikTok, 多国家, 本地化, 跨境, 多语言, 合规, 区域市场.

Capabilities:
- 多市场用户理解
- 本地化需求分析
- 跨文化协作
- 跨境业务链路
- 合规和风险意识

Resume focus:
- 海外用户/市场分析、多语言/本地化、跨团队协作、合规边界。

### 安全 / 风控 / 治理产品

Signals:
- 安全, 风控, 风险, 治理, 审核, 合规, 反作弊, 内容安全, 数据安全.

Capabilities:
- 风险场景识别
- 规则/策略设计
- 审核流程和人机协同
- 指标监控
- 合规边界

Resume focus:
- 风险识别、规则策略、审核效率、误伤/召回平衡。

### 开发者工具 / 技术产品

Signals:
- Dev Infra, 开发者, 工具链, IDE, Coding, API, SDK, 控制台, 技术平台, 火山引擎.

Capabilities:
- 技术理解
- 开发者体验
- API/控制台设计
- 文档和接入流程
- 平台化能力

Resume focus:
- 工具产品、技术链路、开发者/内部用户体验、接入效率。

## Capability inventory

Use these normalized capability points when asking the user to confirm:

1. 用户洞察与用户研究
2. 需求分析与 PRD/原型设计
3. 业务流程梳理与角色权限设计
4. 数据分析、指标体系、埋点和看板
5. 增长漏斗、转化、留存和 A/B 实验
6. 策略/规则设计和实验评估
7. AI 场景拆解、Prompt/Agent/RAG 和模型评测
8. 平台抽象、配置化、中台/开放能力设计
9. 商业化、广告、投放和 ROI 分析
10. 电商交易链路、商家工具、订单/履约/售后
11. 内容生态、社区互动、创作者工具和治理
12. 国际化、本地化、跨境业务和合规意识
13. 安全/风控/审核治理
14. 技术理解、API/开发者工具和工程协作
15. 项目推进、跨团队协作、上线验收和复盘

## Double matching procedure

For JD tailoring, apply both matching paths:

### Path A: title-seeded matching

1. Extract title words.
2. Map title words to initial tags.
3. Assign a low-to-medium prior weight.

Examples:
- `B端产品经理` → B 端 / SaaS / 企业产品, 平台/中台 if backend/platform words appear.
- `AI产品经理` → AI 应用产品, but wait for JD content to decide C-end/B-end/data/platform/growth mix.
- `数据产品经理` → 数据/BI/分析产品, possibly 增长/商业化/电商 depending on business context.

### Path B: JD-content matching

1. Extract responsibilities and requirements.
2. Match concrete work verbs and product objects to tags.
3. Add or reprioritize tags based on JD details.
4. Convert top tags into 3-6 core capabilities.

### Merge

Return 3-5 tags. Use percentages that sum to 100%. Keep low-evidence tags below 15% or omit them.

## Resume tailoring after confirmation

After the user confirms or edits the analysis:

1. Reorder experiences by evidence strength against confirmed capabilities.
2. Rewrite top bullets to prove confirmed capabilities.
3. Compress low-match content.
4. Keep internship ownership wording conservative.
5. Do not add unsupported tools, metrics, business domains, or senior-level ownership.

