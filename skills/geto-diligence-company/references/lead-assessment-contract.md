# GETO 六维客户价值评估

## 可执行模型

评分使用 [lead-value-model.json](lead-value-model.json)：

- modelCode：`GETO_LEAD_VALUE`
- modelVersion：`2026-07-29`
- ratingScaleVersion：`value-status-2026-07-29`
- 证据等级：`A=1.0`、`B=0.75`、`C=0.5`、`U=0`
- 六维满分依次为 15、20、20、10、15、20，总分 100。

`finalDimensionScore=min(observedScore, dimensionCap)×evidenceWeight`。信息完整度是六维 `maxScore×evidenceWeight` 的合计百分比。总分再应用模型中的整体 cap；等级由 `ratingRules` 顺序判定。

## 门禁

- `assessmentMode=lead_value`。
- `researchStatus=completed|completed_with_gaps`，主体身份稳定。
- `$geto-capability-foundation` 返回的 `contextRef.status=available`，并把 `contextRef` 原样写入 `assessment.capabilityContext`。
- 每个计分维度都有 observedScore、A/B/C 证据等级、判断理由和内嵌 Evidence。
- 未满足门禁时使用 `pending_capability_foundation|incomplete_evidence`，overallScore 与 grade 为 null。

## 六维

1. `project_city_value` 项目与城市价值，15 分。
2. `account_scale` 客户规模与行业地位，20 分。
3. `future_project_demand` 未来项目与采购需求，20 分。
4. `reachability` 决策链与触达可行性，10 分。
5. `payment_capacity` 合作与支付能力，15 分。
6. `multi_product_fit` 多产品匹配与复制价值，20 分。

先在 `assessment.dimensions[]` 填写 observedScore、evidenceGrade、rationale、evidence、gapCodes 和 capCodes，再运行：

```bash
python '<geto-diligence-company-dir>/scripts/calculate_lead_assessment.py' \
  '<公司目录>/company.json' \
  --capability-context '<context.json>' --assessed-on 'YYYY-MM-DD'
```

脚本写入严格的 assessment 结构并原子替换 company.json。capCodes 只使用模型文件定义的代码；不能用注册资本推断支付能力，也不能为缺失维度补猜分。
