# CapabilityContext 合同

`CapabilityContext` 是能力底座向业务 Skills 提供的只读切片，不是 ResearchDelta 领域对象，也不直接写入 OmniX。

~~~json
{
  "foundationKey": "geto:capability-foundation",
  "asOf": "2026-08-11",
  "contentHash": "sha256:...",
  "status": "available",
  "selection": {
    "query": "AU modular housing developer",
    "country": "AU",
    "productCodes": ["modular_building"],
    "scenarioCodes": ["modular_housing"],
    "roleCodes": ["developer_owner"]
  },
  "products": [],
  "scenarios": [],
  "buyerRoles": [],
  "caseAnchors": [],
  "relationshipAssets": [],
  "sourceKeys": [],
  "gaps": []
}
~~~

## 状态

- `available`：所选产品、场景和引用案例均可解析到来源登记。
- `partial`：能完成部分映射，但存在未知产品代码、缺少来源、过期待复核或关系资产仅有旧底稿。
- `unavailable`：Skill 或必需资源不存在，无法形成可靠 GETO 匹配。

## ResearchDelta 记录

总编排只在 ResearchDelta 顶层记录本次实际使用的底座摘要：

~~~json
{
  "capabilityFoundation": {
    "foundationKey": "geto:capability-foundation",
    "asOf": "2026-08-11",
    "contentHash": "sha256:...",
    "status": "available",
    "productCodes": [],
    "scenarioCodes": [],
    "caseKeys": [],
    "sourceKeys": [],
    "gapCodes": []
  }
}
~~~

不得复制整套底座到每个 Company 或 Assessment。评分维度仍要引用目标公司的 Claim/Source；能力底座只能解释 GETO 侧产品和场景匹配，不能替代客户侧证据。
