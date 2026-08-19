# Competitor Gate

把结论写入 company.json 的 researchClassifications[]：

```json
{
  "classification": "competitor",
  "status": "confirmed|possible|rejected",
  "country": "",
  "productScope": [],
  "reason": "",
  "evidence": []
}
```

confirmed 必须同时证明：产品/技术/渠道重叠、目标市场经营、商业控制/销售/出租/分销或自有系统。名称关键词不是证据。

判定矩阵：

| 履约/商业角色 | 竞对边界 |
| --- | --- |
| manufacturer/system_owner/brand_owner | 产品和市场重叠时可 confirmed |
| distributor/reseller/rental_provider | 经营竞品时为渠道竞对 |
| installer/service_contractor-only | rejected |
| contract_manufacturer-only | 非独立销售时 rejected/possible ecosystem |
| outsourced + 自有品牌/系统 | 可 confirmed |
| 商业控制 unknown | possible，创建背调补证 |
