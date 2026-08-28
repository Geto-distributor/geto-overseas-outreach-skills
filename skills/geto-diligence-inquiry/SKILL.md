---
name: geto-diligence-inquiry
description: 对单条 GETO 海外询盘执行开放式信息搜集、主体候选与冲突溯源、需求还原、项目和联系人核查，并按证据边界生成询盘准备度与报价建议。用于一条询盘一个独立任务的真假核查、同名/域名/Provider 冲突调查、报价前澄清和跟进优先级；主体未闭合或 Provider 无结果时仍继续调研，客户长期价值由主会话 cohort 评分。
---

# GETO 单询盘背调

一次只处理一条询盘及其目标 Company。询盘准备度回答当前能否报价和推进，不替代客户长期价值评分。

开始前完整读取 [child-resources.md](references/child-resources.md)、[project-research-contract.md](references/project-research-contract.md)、[report-contract.md](references/report-contract.md)、[inquiry-contract.md](references/inquiry-contract.md)、[inquiry-intake-gate.md](references/inquiry-intake-gate.md)、[identity-conflict-investigation.md](references/identity-conflict-investigation.md) 和 [inquiry-readiness-model.json](references/inquiry-readiness-model.json)，并读取 `$geto-run-market-research` 的 `references/research-intelligence-contract.md`。构造或复核 company.json 时读取 `$geto-run-market-research` 的 `references/company-field-requirements.md`；首次查看完整形态时读取其 `references/company-json-example.json`，填写询盘与准备度时读取 [inquiry-example.md](references/inquiry-example.md)。需要模仿报告深度或章节组织时，按需读取 [report-examples/README.md](references/report-examples/README.md) 及其中相关样例。本 Skill 自带 Company、Evidence、项目深挖和报告合同；调用 `$geto-diligence-company` 时只复用其公司研究流程，assessmentMode 固定为 none。

## 输入

- 询盘原始导出、聊天记录、附件、receivedOn 和本地 inquiryRef。
- 买方自报公司、人名、邮箱、电话、国家、产品、数量、项目、交付和付款信息。
- 目标国家、GETO 产品范围、研究截止日和公司目录。

## 启动路由

深度背调前先构造临时 `intake-gate.json`，尽量包含公司名、可描述的产品/技术/项目需求和可回复邮箱；再分别执行 Web 主体检索与 TradeWind 精确公司查询。两边分别保留查询边界、候选、强弱锚点、冲突和证据。该步骤只选择研究模式，不决定是否允许继续搜集信息。

运行：

```bash
python '<geto-diligence-inquiry-dir>/scripts/validate_inquiry_intake.py' \
  '<intake-gate.json>' \
  --output '<intake-gate-result.json>'
```

`ready_for_diligence`、`diligence_with_identity_gaps`、`diligence_with_provider_gaps` 和 `diligence_with_partial_intake` 都进入主体、项目、联系人、冲突和报告流程。只有完全没有公司、人名、域名、邮箱域名、项目或其他可检索锚点时才返回 `blocked_no_research_anchor`。`no_result`、`not_queried`、`not_configured`、`upstream_unavailable` 与 `failed` 必须区分，但它们只形成证据缺口和替代检索路线，不得取消 Web、登记、项目、社媒、地图目录、域名历史或其他 Provider 调研。

主体未闭合时创建候选实体矩阵，不把互相冲突的事实合并。继续调研每个候选并解释冲突来源；限制确定性结论、正式报价、授信和评分上限，而不是限制信息搜集。强身份冲突使用 `identity_conflict` hard block；单一 Provider 0 结果本身不等于身份冲突，也不自动把总分封顶。

最小可运行形态见 [inquiry-intake-example.json](references/inquiry-intake-example.json)。

## 工作流

1. 完成启动路由后，初始化规范国家和自然公司名目录；一条询盘保留一个目标 Company，同时把同名、近名、旧域名、关联域名和冲突主体保存为候选，不混写事实。
2. 把原始信息写入 `inquiries[]`，保留附件路径、开放问题和 customer_document Evidence。
3. 调用 `$geto-diligence-company` 核查主体、官网、产品、项目、联系人、风险和 lead/competitor，assessmentMode 使用 none。项目按发现瀑布流枚举官网组合，并沿政府、业主、开发商、主包、顾问、分包和供应商反查；反复出现或可能改变真实性、需求、采购链和报价判断的关联对象继续深挖或回传主任务。
4. 主体冲突、冒名、邮箱域名冲突和 Provider 宽匹配分别保留，不自动合并；按照 `identity-conflict-investigation.md` 逐一建立关系假设、验证和排除路径。冲突是加深研究的触发器。
5. 按模型六维 components 填写 `inquiryAssessment.dimensions[]` 的 score、rationale、Evidence 和 gapCodes。只给证据支持的准备度分；缺失信息记 0 和 gap，不使用同行均值。
6. 运行：

```bash
python '<geto-diligence-inquiry-dir>/scripts/calculate_inquiry_readiness.py' \
  '<公司目录>/company.json' --inquiry-ref '<本地询盘引用>' \
  --assessed-on 'YYYY-MM-DD'
```

7. 按 report-contract.md 生成自然中文的详细 report.md。项目有公开组合时写总表并至少详述 3 个重要项目；项目不足时详述全部，并提供项目检索覆盖表。身份未闭合时增加候选实体矩阵、冲突解释、关系假设和仍需验证的锚点。报告分别陈述事实底座、关键信号、AI 推理、AI 结论、询盘准备度、报价建议、不确定性、继续研究方向和长期客户价值状态；不能用评分或“待人工判断”代替结论。
8. 生成 Sources/sources.md 并运行单公司 validator；不得用短摘要代替深度报告。

## 边界

- `inquiryAssessment` 不使用 cohort baseline。
- 顶层 `assessment` 保持 not_requested；需要长期客户价值时，由国家主任务在同类型 cohort 形成后统一执行。
- 邮箱可投递只支持 workEmail.deliverability，不支持任职、职位、授权或 buyingRole。
- Provider Observation 必须经过强身份仲裁，不能覆盖询盘原文、登记或官网事实。
- 不因单一 Provider 无结果、工具故障、同名、域名差异或信息冲突停止公开调研。
- 本任务不上传 OmniX。只有用户在当前主任务中明确要求上传、同步、发布或管理 OmniX 时，主任务才进入平台投影；普通询盘背调不主动追加上传确认。

## 回传

回传主体结论、询盘准备度分数/等级、六维理由、AI 推理与报价结论、报价前必问项、公司目录、报告路径、lead/competitor 分类、风险冲突、值得继续展开的关联对象和下一步。
