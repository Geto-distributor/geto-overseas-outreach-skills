# 输出合同

~~~json
{
  "capabilityFoundation": {
    "foundationKey": "geto:capability-foundation",
    "contentHash": "sha256:...",
    "status": "available|partial|unavailable",
    "productCodes": [],
    "scenarioCodes": [],
    "caseKeys": [],
    "sourceKeys": [],
    "gapCodes": []
  },
  "competitorCandidates": [],
  "competitionDecisions": [],
  "confirmedCompetitors": [],
  "officialCases": [
    {
      "competitorCompanyKey": "",
      "counterpartyCompanyKey": "",
      "projectKey": null,
      "productCodes": [],
      "cooperationDescription": "",
      "counterpartyRoleCode": "",
      "customerQualificationStatusCode": "",
      "buyerCompanyKey": null,
      "payerCompanyKey": null,
      "procurementMode": null,
      "exclusive": null,
      "currentStatus": "unknown",
      "relationshipKey": "",
      "claimKeys": [],
      "sourceKeys": []
    }
  ],
  "qualifiedCustomers": [],
  "competitorMetrics": [
    {
      "competitorCompanyKey": "",
      "qualifiedCustomerCount": 0,
      "scoredCustomerCount": 0,
      "assessmentCoverage": 0,
      "averageCustomerValueScore": null
    }
  ],
  "exclusions": [],
  "providerStatuses": {},
  "quality": {},
  "provenance": {}
}
~~~

合格客户必须引用统一 Company/CommercialAccount、背调 EvidencePackage 和六维 Assessment。关系字段未知时使用 null/unknown，不能用推断值补齐。
