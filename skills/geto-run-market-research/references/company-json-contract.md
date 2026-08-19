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
  "assessment": {},
  "missingInformation": [],
  "recommendedActions": [],
  "additionalInformation": [],
  "reportFiles": [],
  "researchStatus": "completed|completed_with_gaps|identity_conflict",
  "lastResearchedOn": "YYYY-MM-DD"
}
```

本地文件不得包含 `runId`、`taskId`、`companyKey`、`claimKey`、`sourceKey` 或平台管理字段。`businessActivities` 不存在。

`company` 包含 `companyName`、`entityType`、`country`、`status`、`summary`、`researchConclusion` 和 `evidence`。

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
    "relation": "supports|refutes|context",
    "locator": "",
    "excerpt": "",
    "note": ""
  }]
}
```

主要列表包括 aliases、registrations、capitalRecords、websites、addresses、marketPresence、socialChannels、researchClassifications、companyRoles、productsAndServices、projects、relationships、contacts、licensesAndCertifications、financialRecords、newsAndSocialMedia、customsTransactions、lawsuitsAndCompliance、inquiries、risks、missingInformation、recommendedActions、additionalInformation。`not_queried` 的 missingInformation 可使用空 Evidence，但必须说明原因。

## 分类与角色

`researchClassifications[]`：classification=`lead|competitor`，status=`confirmed|possible|rejected`，并包含 country、productScope[]、reason、evidence[]。同一公司可各有一条 lead 和 competitor，不使用 `both`。

`companyRoles[]`：role=`developer|main_contractor|subcontractor|agent_consultant_pm|distributor_trading|design_consulting_supervision_other`，并包含 scope、country、projectName、status、rationale、evidence。

## 产品与竞对门禁

`productsAndServices[]` 包含 name、type、category、description、technologyTerms[]、applications[]、targetCustomers[]、markets[]、commercialRoles[]、manufacturingStatus、manufacturingDescription、factoryLocations[]、status、getoRelevance、evidence[]。

commercialRoles 只用 manufacturer、system_owner、brand_owner、contract_manufacturer、distributor、reseller、rental_provider、installer、service_contractor、consultant、unknown。manufacturingStatus 只用 own_factory_confirmed、manufacturing_claimed、outsourced、not_found、unknown。

confirmed competitor 必须同时有重叠产品/技术、目标市场与商业控制/渠道控制 Evidence。installer/service_contractor-only 必须 rejected；outsourced 自有品牌/系统可 confirmed；distributor/reseller/rental_provider 为渠道竞对。

## 目录和来源

每家公司至少有 `company.json` 和 `report.md`。模块目录按真实内容创建。扫描全部内嵌 Evidence，按规范化 URL 去除追踪参数、fragment 和多余尾斜杠，再按 canonical URL + locator 聚合为 `Sources/sources.md`。该文件是派生索引，不含 Source ID，也不是第二份权威数据。
