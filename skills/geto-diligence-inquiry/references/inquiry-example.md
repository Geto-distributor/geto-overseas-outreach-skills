# 询盘字段示例

开始填写完整 `company.json` 前，先读取并运行 [inquiry-intake-gate.md](inquiry-intake-gate.md)。本文件只展示询盘和询盘准备度字段；完整公司轴由 `$geto-diligence-company` 写入同一个 Company Aggregate，并默认执行长期价值观察。启动路由输入形态见 [inquiry-intake-example.json](inquiry-intake-example.json)。

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
          "note": "记录买方在询盘中自述的需求，不单独证明采购和付款权限。"
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
              "note": "支持开发商角色。"
            }
          ]
        }
      ],
      "inquiryMatchStatus": "possible",
      "demandJudgement": "possible",
      "entryWindow": "需向买方确认采购时间。",
      "opportunity": "可能存在铝模板报价机会。",
      "procurementBoundary": "买方权限仍待核实。",
      "knownRelationship": "本次询盘是当前观察到的首次联系。",
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
          "note": "支持项目存在。"
        }
      ]
    }
  ],
  "inquiryAssessment": {
    "assessmentType": "inquiry_readiness",
    "status": "completed",
    "modelCode": "GETO_INQUIRY_READINESS",
    "modelVersion": "2026-08-19",
    "inquiryRef": "inquiry:2026-08-20-001",
    "grade": "nurture_or_verify",
    "overallScore": 45,
    "overallConclusion": "需求可以识别；正式报价前仍需确认联系人权限、图纸、交付和付款信息。",
    "assessedOn": "2026-08-20",
    "dimensions": [
      {"dimensionCode": "identity_confidence", "name": "主体可信度", "score": 10, "maxScore": 15, "rationale": "官网域名与经营主体可以对应。", "evidence": [{"sourceTitle": "Example Build Systems home page", "sourceUrl": "https://example.com", "publisher": "Example Build Systems Ltd.", "sourceType": "official_website", "publishedOn": null, "retrievedOn": "2026-08-20", "locator": "Home", "excerpt": "Official company website.", "note": "支持官网域名与公司身份。"}], "gapCodes": ["legal_identity_pending"]},
      {"dimensionCode": "requirement_specificity", "name": "需求明确度", "score": 12, "maxScore": 20, "rationale": "产品和数量已经说明，但缺少图纸。", "evidence": [{"sourceTitle": "Inquiry email WEB-001", "sourceUrl": "", "publisher": "Example Buyer", "sourceType": "customer_document", "publishedOn": "2026-08-20", "retrievedOn": "2026-08-20", "locator": "Email body", "excerpt": "Request for 1,200 m2 aluminum formwork.", "note": "支持询盘需求。"}], "gapCodes": ["drawings_missing"]},
      {"dimensionCode": "project_readiness", "name": "项目成熟度", "score": 8, "maxScore": 20, "rationale": "项目存在已经核实，但采购时间未知。", "evidence": [{"sourceTitle": "Harbour Residence project page", "sourceUrl": "https://example.com/projects/harbour-residence", "publisher": "Example Build Systems Ltd.", "sourceType": "official_website", "publishedOn": null, "retrievedOn": "2026-08-20", "locator": "Project overview", "excerpt": "Active residential project in Sydney.", "note": "支持项目存在和当前状态。"}], "gapCodes": ["procurement_date_unknown"]},
      {"dimensionCode": "reachability_authority", "name": "触达与权限", "score": 5, "maxScore": 15, "rationale": "已有邮箱入口，但采购权限未确认。", "evidence": [{"sourceTitle": "Inquiry email WEB-001", "sourceUrl": "", "publisher": "Example Buyer", "sourceType": "customer_document", "publishedOn": "2026-08-20", "retrievedOn": "2026-08-20", "locator": "From header", "excerpt": "buyer@example.com", "note": "支持联系入口，不证明采购权限。"}], "gapCodes": ["authority_unverified"]},
      {"dimensionCode": "commercial_payment_readiness", "name": "商务与付款准备度", "score": 0, "maxScore": 15, "rationale": "合同签约主体、付款方和付款条件均未提供。", "evidence": [], "gapCodes": ["signing_entity_missing", "payer_missing", "payment_terms_missing"]},
      {"dimensionCode": "technical_product_fit", "name": "技术与产品匹配", "score": 10, "maxScore": 15, "rationale": "客户要求的产品与项目类型匹配，但结构输入仍不完整。", "evidence": [{"sourceTitle": "Inquiry email WEB-001", "sourceUrl": "", "publisher": "Example Buyer", "sourceType": "customer_document", "publishedOn": "2026-08-20", "retrievedOn": "2026-08-20", "locator": "Email body", "excerpt": "Aluminum formwork requested for Harbour Residence.", "note": "支持产品适配输入。"}], "gapCodes": ["technical_inputs_incomplete"]}
    ],
    "hardBlockCodes": [],
    "gapCodes": ["legal_identity_pending", "drawings_missing", "procurement_date_unknown", "authority_unverified", "signing_entity_missing", "payer_missing", "payment_terms_missing", "technical_inputs_incomplete"]
  }
}
```

运行 `calculate_inquiry_readiness.py` 后，以脚本生成的 overallScore、grade 和 status 为准。维度 Evidence 引用完整 company.json 中同一来源对象。

生成自然中文 `report.md` 后先交给用户审阅。未确认时 `reportFiles[]` 只登记 Markdown；用户确认或明确跳过 Review 后，才按 [publication-contract.md](publication-contract.md) 写入 `Additional/report-review.json` 并生成用户指定的 DOCX/PDF。
