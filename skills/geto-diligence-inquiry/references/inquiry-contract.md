# GETO 询盘准备度合同

询盘准备度衡量当前报价和交易推进条件，不衡量客户长期价值，也不使用同类型中位数。公司长期价值由主任务 cohort 评分。

## 输入

- 一条明确询盘及其原始附件/聊天记录。
- 在开始深度背调前通过 [inquiry-intake-gate.md](inquiry-intake-gate.md)：公司名、可描述需求、邮箱齐全，且 Web 与 TradeWind 均能强匹配同一主体。
- 目标 Company 的主体、产品、项目、联系人和风险 Evidence。
- 研究截止日和本地公司目录。

项目发现和报告深度分别遵循 project-research-contract.md 与 report-contract.md。项目公开资料不足时仍记录完整查询覆盖、反查路径和客户补件清单。

## 评分

使用 `inquiry-readiness-model.json` 的六维 components。只给已被询盘原文或目标公司 Evidence 支持的 component 分；缺失信息得 0 readiness points 并进入 gapCodes。未知不等于确认不存在，但二者在“当前能否报价/推进”上都不产生准备度分。

等级：

- `ready_for_quotation`
- `qualified_needs_clarification`
- `nurture_or_verify`
- `high_risk_or_unqualified`

询盘评分写入顶层 `inquiryAssessment`。长期客户价值 `assessment` 保持 `not_requested`，或由主会话另行执行 cohort 评分。
