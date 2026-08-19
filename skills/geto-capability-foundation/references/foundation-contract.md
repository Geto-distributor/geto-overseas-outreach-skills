# CapabilityContext 合同

CapabilityContext 是只读的本次研究能力切片，不是目标市场事实，也不直接写入 Company。

```json
{
  "foundationKey": "geto:capability-foundation",
  "foundationVersion": "",
  "asOf": "YYYY-MM-DD",
  "status": "available|partial|unavailable",
  "contentHash": "sha256:...",
  "productCodes": [],
  "scenarioCodes": [],
  "roleCodes": [],
  "caseKeys": [],
  "gapCodes": []
}
```

`select_context.py` 在 `contextRef` 返回这组固定字段。执行客户价值评估时把该对象原样写入 `assessment.capabilityContext`；主任务在 `progress.md` 记录 foundationVersion、contentHash 和所用 codes 的摘要。目标 Company 的产品、项目、分类和关系必须由目标市场 Evidence 支持，不能把 CapabilityContext 当作事实来源。

显式传入的 product、scenario、role codes 表示本次实际使用范围。传入产品或角色时，场景只接受显式 scenario code；纯自然语言查询可以推导场景。
