# GETO 六维客户价值评估

## 可执行模型

评分使用 [lead-value-model.json](lead-value-model.json)：

- modelCode：`GETO_LEAD_VALUE`
- modelVersion：`2026-07-29`
- ratingScaleVersion：`value-status-2026-07-29`
- 证据等级：`A=1.0`、`B=0.75`、`C=0.5`、`U=0`
- 六维满分依次为 15、20、20、10、15、20，总分 100。

单公司任务不生成最终分。它提交 observedScore、evidenceWeight 和 cohortKey；国家主任务形成同类型中位数 P 后统一执行 `Fᵢ=qᵢOᵢ+(1-qᵢ)Pᵢ`。信息完整度仍是六维 `maxScore×evidenceWeight` 的合计百分比。

## 门禁

- `assessmentMode=lead_value`。
- `researchStatus=completed|completed_with_gaps`，主体身份稳定。
- `$geto-capability-foundation` 返回的 `contextRef.status=available`，并把 `contextRef` 原样写入 `assessment.capabilityContext`。
- 每个维度写 observedScore、A/B/C/U 证据等级、判断理由和内嵌 Evidence；未知使用 U/null，确认不存在使用有证据的 0。
- 使用 `cohortKey=<ISO2>:<companyRole>`，单公司状态为 `pending_cohort_baseline`，baselineScore、finalDimensionScore、overallScore 和 grade 为 null。

## 六维

1. `project_city_value` 项目与城市价值，15 分。
2. `account_scale` 客户规模与行业地位，20 分。
3. `future_project_demand` 未来项目与采购需求，20 分。
4. `reachability` 决策链与触达可行性，10 分。
5. `payment_capacity` 合作与支付能力，15 分。
6. `multi_product_fit` 多产品匹配与复制价值，20 分。

每个 observedScore 按模型中的 `components` 逐项相加，并用 `factAnchors` 检查所属区间。evidenceGrade 按 `evidenceGradeRules` 判断来源直接性、独立性、时效性和冲突；等级评价的是该维判断依据，不是网站类型本身。客户询盘可以直接证明其当前需求，不能单独证明主体、规模或付款能力。无法落到事实锚点时使用 U 和 null，不给保守猜分。

先生成标准能力工件：

```bash
python '<geto-capability-foundation-dir>/scripts/select_context.py' \
  --country '<ISO2>' --product-code '<productCode>' \
  --scenario-code '<已证实场景，可省略>' --role-code '<roleCode>' \
  --output '<公司目录>/RisksAndAssessment/capability-context.json'
```

先在 `assessment.dimensions[]` 填写 observedScore、evidenceGrade、rationale、evidence、gapCodes 和 capCodes，再运行：

```bash
python '<geto-diligence-company-dir>/scripts/calculate_lead_assessment.py' \
  '<公司目录>/company.json' \
  --capability-context '<context.json>' --cohort-key '<ISO2>:<companyRole>' \
  --assessed-on 'YYYY-MM-DD'
```

脚本写入严格的单公司评分输入并原子替换 company.json。capCodes 只使用模型文件定义的代码；不能用注册资本推断支付能力，也不能在单公司任务中查找或猜测同类型基线。

最终分由主会话使用 `$geto-find-leads` 的 cohort 脚本批量生成。任何 cohort 维度少于 5 家合格观察时，若该维度已经完成公开检索且没有可用信息，则使用 0 作为 cohort baseline 并记录 `cohort_baseline_zero_fallback:<dimensionCode>` Evidence；`not_queried`、`provider_failed`、`identity_conflict` 保留未知状态并由主任务决定是否导入。报告同时展示 overallScore、grade、informationCompleteness 和 fallback 标记。

单公司 validator 会要求 `RisksAndAssessment/capability-context.json`，并逐字段核对它与 `assessment.capabilityContext`。

assessment.evidence 聚合六个维度中实际使用的去重 Evidence。主任务完成 cohort 评分后保留该数组，使评分在本地报告和 OmniX 共享投影中都能回溯。
