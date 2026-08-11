# EvidencePackage 合同

~~~json
{
  "company": {
    "companyKey": "稳定自然键",
    "canonicalName": "",
    "aliases": [],
    "primaryDomain": null,
    "legalEntities": [],
    "roles": [],
    "identityStatus": "resolved|identity_conflict"
  },
  "commercialAccount": {},
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
    "status": "matched|pending|refuted|pending_capability_foundation",
    "matchedProductCodes": [],
    "matchedScenarioCodes": [],
    "targetClaimKeys": [],
    "targetSourceKeys": [],
    "gapCodes": []
  },
  "diligenceStatus": "completed_with_explicit_gaps",
  "gaps": [],
  "conflicts": [],
  "asOf": "YYYY-MM-DD",
  "provenance": {}
}
~~~

## Claim

每条 Claim 包含：claimKey、claimType、valueStatus、valueText/valueNumber/valueJson、confidence、targetType、targetKey、asOf。

## Source

每条 Source 包含：sourceKey、url、title、sourceType、publisher、publishedOn、retrievedOn、contentHash、archivedUrl、accessStatus。

## ClaimSourceLink

包含：linkKey、claimKey、sourceKey、relationType、locator、excerpt、dimensionCodes、lastCheckedOn。

值状态必须区分 observed、derived、not_found、not_applicable、conflicting；查询状态另行记录 not_queried 和 stale。写入 OmniX 时由 `$omnix-market` 依据当前 OpenAPI 映射到服务端枚举。
