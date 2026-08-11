# RelationshipDelta 合同

~~~json
{
  "relationshipKey": "稳定自然键",
  "sourceCompanyKey": "",
  "targetCompanyKey": "",
  "relationshipType": "",
  "capabilityFoundationRef": {
    "foundationKey": "geto:capability-foundation",
    "contentHash": null,
    "status": "available|partial|unavailable"
  },
  "cooperationMode": null,
  "projectKey": null,
  "productCode": null,
  "currentStatus": "current|historical|unknown",
  "strength": null,
  "exclusive": null,
  "procurementPartyCompanyKey": null,
  "actualUserCompanyKey": null,
  "payerCompanyKey": null,
  "location": null,
  "timeWindow": null,
  "entryPoint": null,
  "limitation": null,
  "counterpartyRoleCode": null,
  "customerQualificationStatusCode": null,
  "evidenceStatus": "pending|partially_verified|verified|conflicting",
  "claimKeys": [],
  "sourceKeys": [],
  "lastCheckedOn": "YYYY-MM-DD",
  "provenance": {}
}
~~~

## 不变量

1. sourceCompanyKey 与 targetCompanyKey 指向统一 Company。
2. customer/competitor/project/partner 不得作为 relationshipType。
3. relationshipKey 由稳定自然键材料派生，不使用数据库 ID。
4. projectKey/productCode 只有在确定时填写。
5. procurementParty、actualUser、payer、exclusive 的 null 表示未披露，不等于否。
6. 关系证据与公司证据分别保存，不用公司官网首页替代具体关系来源。
7. customerQualificationStatusCode 仅说明该对手方能否进入客户池，不改变 Company 多角色。
8. 客观关系可在能力底座 unavailable 时保存；但 GETO productCode、建议 cooperationMode 与 entryPoint 不得猜测。
