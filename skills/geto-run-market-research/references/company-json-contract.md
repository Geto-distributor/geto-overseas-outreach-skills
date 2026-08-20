# Company JSON 字段合同

## 目录

1. 顶层字段
2. Evidence
3. 分类与角色
4. 产品与竞对门禁
5. 目录和来源

## 顶层字段

`company.json` 只表示一个 `legal_entity|operating_company|corporate_group`。必须包含：

```json
{
  "company": {},
  "aliases": [],
  "registrations": [],
  "capitalRecords": [],
  "websites": [],
  "addresses": [],
  "marketPresence": [],
  "socialChannels": [],
  "researchClassifications": [],
  "companyRoles": [],
  "productsAndServices": [],
  "projects": [],
  "relationships": [],
  "contacts": [],
  "licensesAndCertifications": [],
  "financialRecords": [],
  "newsAndSocialMedia": [],
  "customsTransactions": [],
  "lawsuitsAndCompliance": [],
  "inquiries": [],
  "risks": [],
  "researchQueries": [],
  "assessment": {"status": "not_requested"},
  "inquiryAssessment": {"status": "not_requested"},
  "competitorCustomerPortfolio": {"status": "not_requested"},
  "missingInformation": [],
  "recommendedActions": [],
  "additionalInformation": [],
  "reportFiles": [],
  "researchStatus": "completed|completed_with_gaps|identity_conflict",
  "lastResearchedOn": "YYYY-MM-DD"
}
```

`company.json` 只包含上述研究业务字段。`company` 包含 `companyName`、`entityType`、`country`、`countryCode`、`status`、`summary`、`researchConclusion`、`foundedOn`、`companyScale`、`headcount`、`listingStatus`、`listingDetails`、`marketPosition`、`priority`、`procurementBoundary` 和 `evidence`。countryCode 使用 ISO2，country 使用统一英文展示名；listingStatus 使用 `self_listed|parent_listed|not_listed|unknown`。

## Evidence

所有主要业务列表 item 自带：

```json
{
  "evidence": [{
    "sourceTitle": "",
    "sourceUrl": "https://example.com/path",
    "publisher": "",
    "sourceType": "official_website|registry|government|court|financial_report|media|social_media|provider|customer_document|other",
    "publishedOn": null,
    "retrievedOn": "YYYY-MM-DD",
    "locator": "",
    "excerpt": "",
    "note": ""
  }]
}
```

主要列表包括 aliases、registrations、capitalRecords、websites、addresses、marketPresence、socialChannels、researchClassifications、companyRoles、productsAndServices、projects、relationships、contacts、licensesAndCertifications、financialRecords、newsAndSocialMedia、customsTransactions、lawsuitsAndCompliance、inquiries、risks、missingInformation、recommendedActions、additionalInformation。查询覆盖单独写入 researchQueries；`not_queried|no_result` 可使用空 Evidence。Evidence 只描述来源；业务 item 的 status、verificationStatus、reason 与 researchConclusion 承载事实判断。

researchQueries 固定包含 topic、channel、query、scope、status、checkedOn、resultCount、evidence。status 使用 `found|no_result|partial|failed|not_queried`。

reportFiles 固定包含 `fileName/path/format/reportType/language/generatedOn/description`。format 使用 `markdown|docx|pdf|html`；reportType 使用 `diligence|assessment|risk|supplement`。长期价值 assessment 的两阶段评分由 `$geto-diligence-company` 和 `$geto-find-leads` 定义；询盘准备度 inquiryAssessment 由 `$geto-diligence-inquiry` 定义；竞对客户组合 competitorCustomerPortfolio 与 relationships[].entryAssessment 由 `$geto-mine-competitor-customers` 定义。

## 分类与角色

`researchClassifications[]`：classification=`lead|competitor`，status=`confirmed|possible|rejected`，并包含 country、productScope[]、reason、evidence[]。同一公司可各有一条 lead 和 competitor，不使用 `both`。

`companyRoles[]`：role=`developer|main_contractor|subcontractor|agent_consultant_pm|distributor_trading|design_consulting_supervision_other`，并包含 scope、country、projectName、status、rationale、evidence。

## 产品与竞对门禁

`productsAndServices[]` 包含 name、type、category、description、technologyTerms[]、applications[]、targetCustomers[]、markets[]、commercialRoles[]、manufacturingStatus、manufacturingDescription、factoryLocations[]、media[]、representativeProject、status、getoRelevance、evidence[]。

commercialRoles 只用 manufacturer、system_owner、brand_owner、contract_manufacturer、distributor、reseller、rental_provider、installer、service_contractor、consultant、unknown。manufacturingStatus 只用 own_factory_confirmed、manufacturing_claimed、outsourced、not_found、unknown。

projects[] 使用 participants[] 表达参与方。participant 包含 name、role、identity、status、lastVerifiedOn、evidence；role 使用 owner、developer、main_contractor、subcontractor、consultant、designer、supervisor、partner、other。项目需求和 GETO 机会分别写入 demandJudgement、entryWindow、opportunity、procurementBoundary、knownRelationship、getoRelevance。

relationships[] 的限制使用 limitations[]。排他状态使用 exclusivity 对象，包含 status、scope、description、lastVerifiedOn、evidence；status 使用 exclusive、non_exclusive、unknown、conflicting。

confirmed competitor 必须同时有重叠产品/技术、目标市场与商业控制/渠道控制 Evidence。installer/service_contractor-only 必须 rejected；outsourced 自有品牌/系统可 confirmed；distributor/reseller/rental_provider 为渠道竞对。

已知竞对由 `$geto-diligence-competitor` 单独背调。确认竞对的客户组合使用 `competitorCustomerPortfolio` 保存去重客户数、已评分数、评分覆盖率、客户价值平均分和逐客引用；关系切入分保存在对应 `relationships[].entryAssessment`。

## 目录和来源

国家目录使用 `<ISO2>-<English-Display-Name>`。每家公司至少有 `company.json` 和 `report.md`。执行评分时，直接 contextRef 固定保存为 `RisksAndAssessment/capability-context.json`，并与 assessment.capabilityContext 完全一致。其他模块目录仅在有原始材料、查询日志或扩展分析时创建。扫描全部内嵌 Evidence，按规范化 URL 去除追踪参数、fragment 和多余尾斜杠；同一 URL 的 locator 聚合在一个来源条目中，客户文件按文档标题聚合为 `Sources/sources.md`。该文件是派生索引，不含 Source ID，也不是第二份权威数据。

首次生成或复核结构时读取 [company-json-example.json](company-json-example.json)。示例展示完整顶层结构、纯来源 Evidence、项目 participants、关系 exclusivity 和本地评估字段的放置方式。
