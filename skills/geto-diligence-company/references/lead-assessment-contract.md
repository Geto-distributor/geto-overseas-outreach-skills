# GETO 六维客户价值评估

## 门禁

- assessmentMode 必须为 lead_value。
- researchStatus 必须为 completed 或 completed_with_gaps，且主体身份稳定。
- CapabilityContext.status 必须 available，并记录版本、contentHash、实际使用的产品和场景 codes。
- 使用批准的模型版本；任何维度证据不足时不生成 overallScore 或 grade。

## 六维

1. 客户规模与行业地位
2. 业务与 GETO 产品匹配度
3. 项目机会与采购需求
4. 决策链与触达可行性
5. 合作与支付能力
6. 战略价值与可复制性

把结果写入 company.json 的 assessment：

```json
{
  "assessmentType": "lead_value",
  "grade": "",
  "overallScore": null,
  "overallConclusion": "",
  "assessedOn": "YYYY-MM-DD",
  "modelVersion": "",
  "dimensions": [{
    "name": "",
    "score": null,
    "level": "",
    "rationale": "",
    "evidence": []
  }]
}
```

每个维度使用内嵌 Evidence；未完成评分通过 missingInformation 明示原因。
