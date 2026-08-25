# 询盘字段示例

开始填写完整 `company.json` 前，先读取并运行 [inquiry-intake-gate.md](inquiry-intake-gate.md)。本文件展示通过启动闸门后的业务字段；启动闸门输入形态见 [inquiry-intake-example.json](inquiry-intake-example.json)。

以下片段合并到完整 company.json。`inquiryRef` 在 inquiries[] 与 inquiryAssessment 中保持一致；每个正分维度附对应 Evidence，缺失项使用 0 分与 gapCodes。

```json
{
  "inquiries": [
    {
      "inquiryRef": "inquiry:2026-08-20-001",
      "inquiryNumber": "WEB-001",
      "receivedOn": "2026-08-20",
      "buyerName": "Example Buyer",
      "buyerContact": "buyer@example.com",
      "buyerRole": null,
      "requestedProduct": "Aluminum formwork",
      "quantity": 1200,
      "quantityUnit": "m2",
      "technicalRequirements": ["Typical floor cycle target: 5 days"],
      "projectName": "Harbour Residence",
      "projectCountry": "Australia",
      "deliveryDestination": "Sydney",
      "deliveryPort": null,
      "incoterm": null,
      "signingEntity": null,
      "payer": null,
      "paymentTerms": null,
      "requestedDocuments": ["Technical proposal", "Budget quotation"],
      "attachments": ["inquiry-email.eml"],
      "verificationStatus": "partially_verified",
      "openQuestions": ["Confirm signing entity", "Confirm structural drawings", "Confirm required delivery date"],
      "evidence": [
        {
          "sourceTitle": "Inquiry email WEB-001",
          "sourceUrl": "",
          "publisher": "Example Buyer",
          "sourceType": "customer_document",
          "publishedOn": "2026-08-20",
          "retrievedOn": "2026-08-20",
          "locator": "Email body and attachment list",
          "excerpt": "Request for 1,200 m2 aluminum formwork for Harbour Residence.",
          "note": "Records the buyer's stated requirement."
        }
      ]
    }
  ],
  "projects": [
    {
      "projectName": "Harbour Residence",
      "country": "Australia",
      "city": "Sydney",
      "participants": [
        {
          "name": "Example Developments Pty Ltd.",
          "role": "developer",
          "identity": {"primaryDomain": "example-developments.test"},
          "status": "confirmed",
          "lastVerifiedOn": "2026-08-20",
          "evidence": [
            {
              "sourceTitle": "Harbour Residence project page",
              "sourceUrl": "https://example.com/projects/harbour-residence",
              "publisher": "Example Build Systems Ltd.",
              "sourceType": "official_website",
              "publishedOn": null,
              "retrievedOn": "2026-08-20",
              "locator": "Project team",
              "excerpt": "Developer: Example Developments Pty Ltd.",
              "note": "Developer-role evidence."
            }
          ]
        }
      ],
      "inquiryMatchStatus": "possible",
      "demandJudgement": "possible",
      "entryWindow": "Confirm procurement date with the buyer.",
      "opportunity": "Potential aluminum-formwork quotation.",
      "procurementBoundary": "Buyer authority remains under verification.",
      "knownRelationship": "The inquiry is the first observed contact.",
      "getoRelevance": "high",
      "verificationStatus": "partially_verified",
      "lastVerifiedOn": "2026-08-20",
      "evidence": [
        {
          "sourceTitle": "Harbour Residence project page",
          "sourceUrl": "https://example.com/projects/harbour-residence",
          "publisher": "Example Build Systems Ltd.",
          "sourceType": "official_website",
          "publishedOn": null,
          "retrievedOn": "2026-08-20",
          "locator": "Project overview",
          "excerpt": "Active residential project in Sydney.",
          "note": "Project existence evidence."
        }
      ]
    }
  ],
  "assessment": {"status": "not_requested"},
  "inquiryAssessment": {
    "assessmentType": "inquiry_readiness",
    "status": "completed",
    "modelCode": "GETO_INQUIRY_READINESS",
    "modelVersion": "2026-08-19",
    "inquiryRef": "inquiry:2026-08-20-001",
    "grade": "nurture_or_verify",
    "overallScore": 45,
    "overallConclusion": "Requirement is identifiable; authority, drawings, delivery and payment facts require clarification before quotation.",
    "assessedOn": "2026-08-20",
    "dimensions": [
      {"dimensionCode": "identity_confidence", "name": "主体可信度", "score": 10, "maxScore": 15, "rationale": "Official domain and operating company are matched.", "evidence": [{"sourceTitle": "Example Build Systems home page", "sourceUrl": "https://example.com", "publisher": "Example Build Systems Ltd.", "sourceType": "official_website", "publishedOn": null, "retrievedOn": "2026-08-20", "locator": "Home", "excerpt": "Official company website.", "note": "Domain evidence."}], "gapCodes": ["legal_identity_pending"]},
      {"dimensionCode": "requirement_specificity", "name": "需求明确度", "score": 12, "maxScore": 20, "rationale": "Product and quantity are stated; drawings are missing.", "evidence": [{"sourceTitle": "Inquiry email WEB-001", "sourceUrl": "", "publisher": "Example Buyer", "sourceType": "customer_document", "publishedOn": "2026-08-20", "retrievedOn": "2026-08-20", "locator": "Email body", "excerpt": "Request for 1,200 m2 aluminum formwork.", "note": "Requirement evidence."}], "gapCodes": ["drawings_missing"]},
      {"dimensionCode": "project_readiness", "name": "项目成熟度", "score": 8, "maxScore": 20, "rationale": "Project existence is verified; procurement date is unknown.", "evidence": [{"sourceTitle": "Harbour Residence project page", "sourceUrl": "https://example.com/projects/harbour-residence", "publisher": "Example Build Systems Ltd.", "sourceType": "official_website", "publishedOn": null, "retrievedOn": "2026-08-20", "locator": "Project overview", "excerpt": "Active residential project in Sydney.", "note": "Project readiness evidence."}], "gapCodes": ["procurement_date_unknown"]},
      {"dimensionCode": "reachability_authority", "name": "触达与权限", "score": 5, "maxScore": 15, "rationale": "Email is available; buying authority is unverified.", "evidence": [{"sourceTitle": "Inquiry email WEB-001", "sourceUrl": "", "publisher": "Example Buyer", "sourceType": "customer_document", "publishedOn": "2026-08-20", "retrievedOn": "2026-08-20", "locator": "From header", "excerpt": "buyer@example.com", "note": "Reachability evidence."}], "gapCodes": ["authority_unverified"]},
      {"dimensionCode": "commercial_payment_readiness", "name": "商务与付款准备度", "score": 0, "maxScore": 15, "rationale": "Signing entity, payer and payment terms are absent.", "evidence": [], "gapCodes": ["signing_entity_missing", "payer_missing", "payment_terms_missing"]},
      {"dimensionCode": "technical_product_fit", "name": "技术与产品匹配", "score": 10, "maxScore": 15, "rationale": "Requested product matches the project type; structural inputs remain incomplete.", "evidence": [{"sourceTitle": "Inquiry email WEB-001", "sourceUrl": "", "publisher": "Example Buyer", "sourceType": "customer_document", "publishedOn": "2026-08-20", "retrievedOn": "2026-08-20", "locator": "Email body", "excerpt": "Aluminum formwork requested for Harbour Residence.", "note": "Product-fit input."}], "gapCodes": ["technical_inputs_incomplete"]}
    ],
    "hardBlockCodes": [],
    "gapCodes": ["legal_identity_pending", "drawings_missing", "procurement_date_unknown", "authority_unverified", "signing_entity_missing", "payer_missing", "payment_terms_missing", "technical_inputs_incomplete"]
  }
}
```

运行 `calculate_inquiry_readiness.py` 后，以脚本生成的 overallScore、grade 和 status 为准。维度 Evidence 引用完整 company.json 中同一来源对象。
