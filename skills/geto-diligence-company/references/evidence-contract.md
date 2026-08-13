# EvidencePackage 合同

~~~json
{
  "assessmentMode": "none|lead_value",
  "company": {
    "companyKey": "稳定自然键",
    "canonicalName": "",
    "aliases": [],
    "primaryDomain": null,
    "legalEntities": [],
    "roles": [],
    "identityStatus": "resolved|identity_conflict"
  },
  "commercialAccount": {
    "mapping": "one_per_company_per_market",
    "embeddedInCompanyDraft": true
  },
  "projects": [],
  "relationships": [],
  "claims": [],
  "sources": [],
  "claimSourceLinks": [],
  "contacts": [],
  "customsEvidence": [],
  "financials": [],
  "providerObservations": [],
  "capabilityHandoff": {
    "foundationKey": "geto:capability-foundation",
    "contentHash": null,
    "foundationStatus": "available|partial|unavailable",
    "status": "matched|pending|refuted|pending_capability_foundation",
    "matchedProductCodes": [],
    "matchedScenarioCodes": [],
    "targetClaimKeys": [],
    "targetSourceKeys": [],
    "gapCodes": []
  },
  "diligenceStatus": "completed_with_explicit_gaps",
  "assessmentStatus": "not_requested|pending_diligence|pending_capability_foundation|pending_model|incomplete_evidence|completed",
  "assessment": null,
  "gaps": [],
  "conflicts": [],
  "asOf": "YYYY-MM-DD",
  "provenance": {}
}
~~~

`diligenceStatus` 只能是 `completed`、`completed_with_explicit_gaps`、`pending`、`failed` 或 `identity_conflict`。它描述公司背调，不被 `assessmentStatus` 替代。

`assessmentMode=none` 时 `assessmentStatus=not_requested` 且 `assessment=null`。`assessmentMode=lead_value` 时，仅在 [lead-assessment-contract.md](lead-assessment-contract.md) 的硬门满足后创建 optional Assessment；pending/failed/identity_conflict 不得评分。

交付前运行 `python scripts/validate_evidence_package.py <evidence-package.json>` 校验 assessmentMode、双状态和禁止总分条件。

## Claim

每条 Claim 包含：claimKey、claimType、valueStatus、valueText/valueNumber/valueJson、confidence、targetType、targetKey、asOf。

## Source

每条 Source 包含：sourceKey、url、title、sourceType、publisher、publishedOn、retrievedOn、contentHash、archivedUrl、accessStatus。

## ClaimSourceLink

包含：linkKey、claimKey、sourceKey、relationType、locator、excerpt、dimensionCodes、lastCheckedOn。

值状态必须区分 observed、derived、not_found、not_applicable、conflicting；查询状态另行记录 not_queried 和 stale。写入 OmniX 时由 `$omnix-market` 依据当前 OpenAPI 映射到服务端枚举。
