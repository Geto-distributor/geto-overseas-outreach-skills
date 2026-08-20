# 竞对客户组合与关系合同

## 关系资格

每条候选关系写入 `reviewDecision`：

- `verified_customer`：可识别客户，并由竞对或对方官方来源明确点名，闭合具体项目或具体产品/服务及实际合作内容。
- `verified_non_customer`：可确认是伙伴、渠道、供应商、顾问、安装方或同场参建方，现有证据不支持客户角色。
- `pending`：存在候选关系，但主体、合作内容、项目/产品或角色仍缺关键证据。
- `conflicting`：主体、项目、产品、时间或关系角色存在未解冲突。
- `invalid`：匿名对象、无法拆分的组合主体、错误匹配或有直接反证。

竞对官网的具名案例可以支持关系成立。第二来源用于主体消歧、经营状态、项目状态、当前持续性、评分确认度与反证。

## relationships[] 字段

竞对—客户关系使用：

- relationshipType=customer；
- counterpartyName、counterpartyRole、companyRole、relationshipRole；
- projectName、productOrService、country、description；
- cooperationModeCode、cooperationDepthCode、relationshipStatusCode；
- buyer、payer、actualUser、exclusivity；
- startedOn、endedOn、firstEvidenceOn、lastVerifiedOn；
- reviewDecision、entryPoint、limitations[]、entrySignalCode；
- entryAssessment、evidence。

cooperationDepthCode 使用 trial|single_project|repeat_business|framework_designated|exclusive_closed|null。relationshipStatusCode 使用 current|historical|ended|unknown。entrySignalCode 使用 open_supplier_window|supplier_termination|product_gap|new_procurement_window|null。

exclusivity 使用对象：status=exclusive|non_exclusive|unknown|conflicting，并包含 scope、description、lastVerifiedOn、evidence。limitations[] 保存地区、产品、项目、时间、资格和证据边界。

未知交易字段使用 null。一个客户与同一竞对存在多个项目或产品时可保留多条关系，组合客户数按 counterpartyName 强身份归一后去重。

## entryAssessment 字段

```json
{
  "assessmentType": "relationship_entry",
  "status": "completed|pending_evidence",
  "modelCode": "GETO_RELATIONSHIP_ENTRY",
  "modelVersion": "1.0",
  "score": null,
  "rationale": "",
  "assessedOn": "YYYY-MM-DD",
  "evidenceStatus": "verified|partial|pending|conflicting",
  "gapCodes": [],
  "evidence": []
}
```

completed 要求 0–5 整数、直接 Evidence 与对应事实锚点。pending_evidence 使用 score=null，并在 gapCodes 记录状态、持续性、合作深度、排他或采购窗口缺口。

## competitorCustomerPortfolio 字段

```json
{
  "assessmentType": "competitor_customer_portfolio",
  "status": "no_verified_customers|pending_customer_scores|partial_coverage|completed",
  "modelCode": "GETO_COMPETITOR_CUSTOMER_PORTFOLIO",
  "modelVersion": "2026-08-19",
  "customerValueModelCode": "GETO_LEAD_VALUE",
  "asOf": "YYYY-MM-DD",
  "verifiedCustomerCount": 0,
  "scoredCustomerCount": 0,
  "customerScoreCoverage": 0,
  "averageCustomerValueScore": null,
  "customers": []
}
```

customers[] 使用 companyName、country、relationshipCount、customerAssessmentStatus、customerValueScore、customerValueModelVersion、cohortBaselineVersion、assessedOn、evidence。

averageCustomerValueScore 是已核实且具有当前 completed 客户价值 assessment 的去重客户 overallScore 算术平均值，保留一位小数。客户分缺失时不进入平均分分母；customerScoreCoverage=scoredCustomerCount/verifiedCustomerCount。

competitorCustomerPortfolio 进入 OmniX Company Aggregate 共享投影；customers[] 只上传逐客评分摘要和关系 Evidence。客户完整六维 assessment 保存在客户自己的 company.json 和 Aggregate。

组合状态：客户数为 0 时 no_verified_customers；客户存在且评分数为 0 时 pending_customer_scores；覆盖率介于 0 和 1 时 partial_coverage；覆盖率为 1 时 completed。
