# relationships[] 合同

```json
{
  "counterpartyName": "",
  "relatedPartyType": "company|person|government|project|organization",
  "relationshipType": "parent|subsidiary|shareholder|controlled_by|brand_operator|customer|supplier|distributor|agent|consultant|developer|contractor|subcontractor|joint_venture|strategic_partner|other",
  "direction": "from_company|to_company|mutual",
  "projectName": "",
  "country": "",
  "description": "",
  "status": "confirmed|possible|historical|ended|conflicting",
  "startedOn": null,
  "endedOn": null,
  "evidence": []
}
```

source 公司就是当前 company.json 表示的主体，counterparty 使用自然名称和必要身份说明。若关系需要采购方、实际使用方、付款方、sale/rental、exclusive、strength 或 timeWindow，可增加清晰命名的业务字段，但必须有直接 Evidence。

竞对客户关系按 `$geto-mine-competitor-customers` 的 competitor-customer-contract 增加 relationshipRole、productOrService、cooperationModeCode、cooperationDepthCode、relationshipStatusCode、reviewDecision、entryPoint、limitation、entrySignalCode 和 entryAssessment。客户资格、客户价值分和关系切入分分别表达。

relationshipType 不得使用 lead、competitor、partner、ecosystem 或 project。一个关系 item 只表达一种明确关系。
