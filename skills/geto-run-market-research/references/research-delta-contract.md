# ResearchDelta 合同

ResearchDelta 是各模块之间和 OmniX Market 草稿写入前的唯一业务交接对象。它不含数据库 ID、SQL 或依赖固定工作表名称。

~~~json
{
  "researchRun": {
    "researchRunKey": "market:scope:as-of:run-token",
    "marketCode": "AU",
    "scopeCode": "construction_formwork",
    "asOf": "2026-08-11",
    "executionMode": "adversarial",
    "resultMode": "full",
    "sampleBoundary": null,
    "publicationStatus": "private_draft",
    "provenance": {
      "skill": "geto-run-market-research",
      "agent": null,
      "model": null
    }
  },
  "release": {
    "marketCode": "AU",
    "scopeCode": "construction_formwork",
    "country": "AU",
    "asOf": "2026-08-11",
    "resultMode": "full",
    "sampleBoundary": null,
    "publicationStatus": "private_draft",
    "provenance": {}
  },
  "capabilityFoundation": {
    "foundationKey": "geto:capability-foundation",
    "asOf": "2026-08-11",
    "contentHash": "sha256:...",
    "status": "available",
    "productCodes": [],
    "scenarioCodes": [],
    "caseKeys": [],
    "sourceKeys": [],
    "gapCodes": []
  },
  "providerStatuses": {},
  "externalObservations": [],
  "sourcePackages": [],
  "companies": [],
  "companyRoles": [],
  "commercialAccounts": [],
  "legalEntities": [],
  "projects": [],
  "opportunities": [],
  "products": [],
  "relationships": [],
  "assessments": [],
  "assessmentDimensions": [],
  "claims": [],
  "sources": [],
  "claimSourceLinks": [],
  "contacts": [],
  "customsEvidence": [],
  "financialRecords": [],
  "conflicts": [],
  "gaps": [],
  "draftOperations": [],
  "validation": {"errors": [], "warnings": []},
  "deliveryStatus": "ready_for_private_draft"
}
~~~

## 通用要求

- 每个对象使用可重算的稳定自然键和 `operation=create|update|link|delete|noop`。
- delete 只在用户意图和服务端合同都明确时生成。
- Company 可同时有 customer、competitor、partner、ecosystem 等角色。
- nodeCategory 不是 relationshipType。
- observed Claim 必须至少有一个 supports Source；refutes/context 分开。
- Source 包含 url、title、sourceType、publisher、publishedOn、retrievedOn，以及能取得时的 contentHash/archivedUrl/locator。
- 所有外部观察保留 provider、queryBoundary、retrievedOn 和原始引用，但敏感原始 payload 只按必要性保存。
- 发布状态、研究状态、resultMode 和 provider status 互不替代。
- `capabilityFoundation` 只保存本次实际使用的能力底座摘要。它不是 Provider 状态，也不复制整套底座资产。

## GETO 能力底座

每个 ResearchDelta 必须包含 foundationKey、asOf、contentHash、status 及本次实际使用的 product/scenario/case/source keys。status 为 partial/unavailable 时必须列出 gapCodes；不得发布正式 `GETO_LEAD_VALUE` 总分。Project 的 matchedProductCodes、Relationship 的 GETO productCode/entryPoint 以及竞对 confirmed 判定都必须能回溯到同一 contentHash。

## Company 与角色

Company 至少保存 `companyKey`、canonicalName、aliases、primaryDomain、registration identifiers、legalEntities、identityStatus 和 lastCheckedOn。customer、competitor、partner、ecosystem 等以 `companyRoles` 独立表达；saved view 按角色关系过滤，不依赖 PrimaryRole、名称关键词或重复 Company。

## Project 与 Opportunity

Project 至少保存 projectName、projectType、city/region/country、scale/amount/currency、stage、currentStatus、timeWindow、entryWindow、demandJudgement、procurementBoundary、matchedProducts、participantCompanies、knownRelationships、claimKeys/sourceKeys。Opportunity 连接 CommercialAccount 与 Project，并表达 GETO 的采购路径和窗口，不能只是一段 recommendation。

`commercialAccounts`、`opportunities` 是跨 Skill 业务映射视图，不要求 OmniX Agent REST 提供独立 CRUD。一个市场内 Company 与 CommercialAccount 一一对应、Project 与 Opportunity 一一对应；写入时分别内嵌到 Company/Project draft，并由服务端唯一约束保护。

## Relationship

Relationship 至少保存 sourceCompanyKey、targetCompanyKey、relationshipType、cooperationMode、projectKey/productCode、current/historical status、strength、exclusive、procurementParty、actualUser、payer、location/timeWindow、entryPoint/limitation、evidenceStatus 与独立 claim/source keys。节点角色不得进入 relationshipType。

## Assessment

每个 `GETO_LEAD_VALUE` Assessment 保存 `producerSkill=geto-diligence-company`、`diligenceStatus`、`assessmentStatus`、assessmentModelCode、modelVersion、asOf、totalScore/rating（可为空）、Company/account 映射键和 dimensions。每个 dimension 独立保存 observed/final score、maxScore、rationale、claimKeys/sourceKeys、gap/cap codes；不得复制总评或将一个 Source 映射到全部维度。

pending/failed/identity_conflict、能力底座或模型不可用、或任一维度不可评分时，不得生成 totalScore、rating 或 levelCode。总分/等级只能来自批准的 `deterministic_validator|server_rule`，并保存 calculation/rating scale version；find-leads 不得改写 diligence 产出的维度。

## Claim、Source 与链接

- Claim：claimType、valueStatus、valueText/valueNumber/valueJson、confidence、targetType/targetKey、asOf。
- Source：URL、标题、sourceType、publisher、publishedOn、retrievedOn、accessStatus，以及能取得时的 contentHash、archivedUrl。
- ClaimSourceLink：supports/refutes/context、locator、dimensionCodes、lastCheckedOn。

## 独立子资源

Contact 保存姓名、职位、层级、工作邮箱/电话、公司域名、地点和来源；CustomsEvidence 保存主体、交易方、时间/国家/分区、HS/商品、数量金额、记录数与查询边界；FinancialRecord 保存法定主体、期间、币种、营收/利润/资产负债及原报告。三者都不能塞入 Company 长文本。
