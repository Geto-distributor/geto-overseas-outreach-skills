# CapabilityContext 合同

CapabilityContext 是只读的本次研究能力切片，不是目标市场事实，也不直接写入 Company。

```json
{
  "foundationVersion": "",
  "asOf": "YYYY-MM-DD",
  "status": "available|partial|unavailable",
  "contentHash": "sha256:...",
  "productCodes": [],
  "scenarioCodes": [],
  "competitionSurfaces": [],
  "targetCompanyRoles": [],
  "searchLexiconVersion": "",
  "gapCodes": []
}
```

主任务把所用版本和 codes 写入 progress.md。目标 Company 的产品、项目、分类和关系必须由目标市场 Evidence 支持，不能把 CapabilityContext 当作事实来源。
