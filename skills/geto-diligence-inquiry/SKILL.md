---
name: geto-diligence-inquiry
description: 对单条 GETO 海外询盘执行主体核验、需求还原、项目与联系人核查，并按固定证据规则生成无需同类中位数的询盘准备度评分。用于一条询盘一个独立任务的真假核查、报价前澄清和跟进优先级；客户长期价值由主会话 cohort 评分。
---

# GETO 单询盘背调

一次只处理一条询盘及其目标 Company。询盘准备度回答当前能否报价和推进，不替代客户长期价值评分。

开始前完整读取 [child-resources.md](references/child-resources.md)、[project-research-contract.md](references/project-research-contract.md)、[report-contract.md](references/report-contract.md)、[inquiry-contract.md](references/inquiry-contract.md)、[inquiry-intake-gate.md](references/inquiry-intake-gate.md) 和 [inquiry-readiness-model.json](references/inquiry-readiness-model.json)。构造或复核 company.json 时读取 `$geto-run-market-research` 的 `references/company-field-requirements.md`；首次查看完整形态时读取其 `references/company-json-example.json`，填写询盘与准备度时读取 [inquiry-example.md](references/inquiry-example.md)。需要模仿报告深度或章节组织时，按需读取 [report-examples/README.md](references/report-examples/README.md) 及其中相关样例。本 Skill 自带 Company、Evidence、项目深挖和报告合同；调用 `$geto-diligence-company` 时只复用其公司研究流程，assessmentMode 固定为 none。

## 输入

- 询盘原始导出、聊天记录、附件、receivedOn 和本地 inquiryRef。
- 买方自报公司、人名、邮箱、电话、国家、产品、数量、项目、交付和付款信息。
- 目标国家、GETO 产品范围、研究截止日和公司目录。

## 启动闸门

深度背调前先构造临时 `intake-gate.json`，至少包含公司名、可描述的产品/技术/项目需求和可回复邮箱；再分别执行 Web 主体检索与 TradeWind 精确公司查询。两边都必须返回同一主体的 `strongIdentityMatch=true`，并各自保留查询边界与证据。

运行：

```bash
python '<geto-diligence-inquiry-dir>/scripts/validate_inquiry_intake.py' \
  '<intake-gate.json>' \
  --output '<intake-gate-result.json>'
```

只有 `gateStatus=ready_for_diligence` 才进入下面的主体、项目和报告流程。输入字段缺失时返回 `blocked_missing_intake`；Web/TradeWind 没有强主体命中时返回 `blocked_identity_discovery`；TradeWind 未配置、上游不可用或查询失败时返回 `blocked_provider`。阻断结果要回传缺失字段和下一动作，不生成没有主体基础的深度报告或准备度分。`no_result`、`not_queried`、`not_configured`、`upstream_unavailable` 与 `failed` 必须区分。

最小可运行形态见 [inquiry-intake-example.json](references/inquiry-intake-example.json)。

## 工作流

1. 通过启动闸门后，初始化规范国家和自然公司名目录；一条询盘只绑定一个当前待核验 Company。
2. 把原始信息写入 `inquiries[]`，保留附件路径、开放问题和 customer_document Evidence。
3. 调用 `$geto-diligence-company` 核查主体、官网、产品、项目、联系人、风险和 lead/competitor，assessmentMode 使用 none。项目按发现瀑布流枚举官网组合，并沿政府、业主、开发商、主包、顾问、分包和供应商反查。
4. 主体冲突、冒名、邮箱域名冲突和 Provider 宽匹配分别保留，不自动合并。
5. 按模型六维 components 填写 `inquiryAssessment.dimensions[]` 的 score、rationale、Evidence 和 gapCodes。只给证据支持的准备度分；缺失信息记 0 和 gap，不使用同行均值。
6. 运行：

```bash
python '<geto-diligence-inquiry-dir>/scripts/calculate_inquiry_readiness.py' \
  '<公司目录>/company.json' --inquiry-ref '<本地询盘引用>' \
  --assessed-on 'YYYY-MM-DD'
```

7. 按 report-contract.md 生成详细 report.md。项目有公开组合时写总表并至少详述 3 个重要项目；项目不足时详述全部，并提供项目检索覆盖表。报告分别陈述公司事实、询盘准备度、报价前必问项和长期客户价值状态。
8. 生成 Sources/sources.md 并运行单公司 validator；不得用短摘要代替深度报告。

## 边界

- `inquiryAssessment` 不使用 cohort baseline。
- 顶层 `assessment` 保持 not_requested；需要长期客户价值时，由国家主任务在同类型 cohort 形成后统一执行。
- 邮箱可投递只支持 workEmail.deliverability，不支持任职、职位、授权或 buyingRole。
- Provider Observation 必须经过强身份仲裁，不能覆盖询盘原文、登记或官网事实。
- 不上传 OmniX；本地验证后由主任务另行询问用户。

## 回传

回传主体结论、询盘准备度分数/等级、六维理由、报价前必问项、公司目录、报告路径、lead/competitor 分类、风险冲突和下一步。
