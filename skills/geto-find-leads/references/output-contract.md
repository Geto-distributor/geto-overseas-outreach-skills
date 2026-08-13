# 输出合同

输出 ResearchDelta，不输出依赖固定 Sheet 名的业务交付。

~~~json
{
  "run": {
    "researchRunKey": "稳定自然键",
    "marketCode": "AU",
    "scopeCode": "construction_formwork",
    "resultMode": "full|sample",
    "sampleBoundary": null,
    "asOf": "YYYY-MM-DD",
    "publicationStatus": "private_draft",
    "checkpoints": {}
  },
  "capabilityFoundation": {
    "foundationKey": "geto:capability-foundation",
    "asOf": "YYYY-MM-DD",
    "contentHash": "sha256:...",
    "status": "available|partial|unavailable",
    "productCodes": [],
    "scenarioCodes": [],
    "caseKeys": [],
    "sourceKeys": [],
    "gapCodes": []
  },
  "release": {
    "marketCode": "AU",
    "scopeCode": "construction_formwork",
    "country": "AU",
    "asOf": "YYYY-MM-DD",
    "resultMode": "full|sample",
    "publicationStatus": "private_draft"
  },
  "providerStatuses": {},
  "entities": {
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
    "financialRecords": []
  },
  "quality": {
    "candidateCount": 0,
    "resolvedCompanyCount": 0,
    "diligenceCoverage": 0,
    "assessmentCoverage": 0,
    "assessmentStatusCounts": {},
    "conflicts": [],
    "gaps": []
  },
  "delivery": {
    "deliveryStatus": "ready_for_private_draft|private_drafts_written|submitted|blocked_market_unavailable|blocked_validation",
    "blockingReason": null,
    "draftRefs": []
  },
  "provenance": {
    "sourcePackageKey": "稳定自然键",
    "agent": null,
    "model": null,
    "skill": "geto-find-leads"
  }
}
~~~

实体必须使用稳定自然键；字段研究状态使用 normalized、claim_only、not_queried、not_found、conflicting、not_applicable 或 stale。Web-only 是 provider coverage，不是 resultMode。

Assessment 必须保留 `producerSkill=geto-diligence-company`、`diligenceStatus`、`assessmentStatus` 和 modelVersion。`geto-find-leads` 不得改写维度；排序只纳入 completed 且同版本的 Assessment。

一个市场内每个 Company 只对应一个 CommercialAccount，每个 Project 只对应一个 Opportunity。CommercialAccount 保存公司商业画像，Opportunity 保存项目采购路径和进入窗口。

能力底座摘要只记录实际使用的 codes/keys，不复制整套产品与案例库到每个 Company。`multi_product_fit` 仍须链接客户侧的逐维 Claim/Source。

## Project/Opportunity 最低合同

~~~json
{
  "projectKey": "stable-project-key",
  "projectName": "",
  "projectType": null,
  "city": null,
  "region": null,
  "country": "AU",
  "scale": null,
  "amount": null,
  "currency": null,
  "stage": null,
  "currentStatus": null,
  "timeWindow": null,
  "entryWindow": null,
  "demandJudgement": null,
  "procurementBoundary": null,
  "matchedProductCodes": [],
  "participantCompanies": [],
  "knownRelationshipKeys": [],
  "claimKeys": [],
  "sourceKeys": []
}
~~~

CommercialAccount 的重点机会必须通过 opportunity/project key 关联，不能只写 recommendation 文本。
