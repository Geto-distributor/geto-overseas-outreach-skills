# 签约前评估输出合同

~~~json
{
  "assessmentKey": "precontract:company-key:opportunity-key:as-of",
  "assessmentModelCode": "approved-model-code",
  "modelVersion": "approved-model-version",
  "asOf": "2026-08-11",
  "contractingCompanyKey": "company-key",
  "legalEntityKey": "legal-entity-key",
  "opportunityKey": "opportunity-key",
  "status": "assessment_draft",
  "counterpartyRisk": {
    "facts": [],
    "riskSignals": [],
    "claimKeys": [],
    "sourceKeys": []
  },
  "dealTermsRisk": {
    "depositPercent": null,
    "preShipmentCollectionPercent": null,
    "paymentCurrency": null,
    "foreignExchangeControl": "not_queried",
    "propertySettlementClause": "unknown",
    "claimKeys": [],
    "sourceKeys": []
  },
  "projectEconomics": {
    "contractAmount": null,
    "currency": null,
    "estimatedNetMarginPercent": null,
    "costBoundary": null,
    "claimKeys": [],
    "sourceKeys": []
  },
  "dimensions": [],
  "totalScore": null,
  "rating": null,
  "hardStops": [],
  "mitigations": [],
  "decision": "hold",
  "decisionRationale": [],
  "gapCodes": [],
  "researchRunKey": "run-key",
  "provenance": {}
}
~~~

每个 dimension 保存 `dimensionCode`、observedScore、maxScore、rationale、claimKeys、sourceKeys、valueStatus。若 `status=assessment_draft`，`totalScore` 和 `rating` 必须为 null；decision 只能为 `hold`，除非 hard stop 已被直接证据确认，此时可为 `reject`。
