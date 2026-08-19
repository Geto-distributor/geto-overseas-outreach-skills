# 单公司 ResearchBundle 合同

## 必需工件

```text
<国家>/companies/<公司自然名称>/
├── company.json
├── report.md
└── Sources/sources.md
```

其他目录只在有真实内容时创建。一个 company.json 只表示一个 legal_entity、operating_company 或 corporate_group。

## Evidence

主要列表 item 内嵌 `evidence[]`，每条包含 sourceTitle、sourceUrl、publisher、sourceType、publishedOn、retrievedOn、relation、locator、excerpt、note。relation 只用 supports、refutes、context。客户附件没有公开 URL 时可用空 sourceUrl，但必须填写 sourceTitle、sourceType=customer_document 和 locator。

冲突来源分别保留。查询动作写入 `researchQueries[]`：`not_queried` 与 `no_result` 是信息状态，`failed` 是需处理状态。对研究结论有实质影响的冲突、过期、Provider 失败或证据缺口写入 `missingInformation[]`；不得写占位事实。

## 分类

`researchClassifications[]` 每条包含 classification=lead|competitor、status=confirmed|possible|rejected、country、productScope[]、reason、evidence[]。lead 与 competitor 独立；同一公司可同时具备，不使用 both。

`companyRoles[]` 只表达开发商、总包、分包、代理顾问项目管理、经销贸易和其他设计咨询监理角色。

结构化事实以 company.json 为准；`Sources/sources.md` 是从内嵌 Evidence 生成的来源索引。
