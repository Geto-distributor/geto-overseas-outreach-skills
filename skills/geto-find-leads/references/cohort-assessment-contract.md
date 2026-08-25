# 主任务 Cohort 公平价值评分

## 时序

单公司背调只提交 observedScore、evidenceGrade、Evidence、capCodes、gapCodes 和 `cohortKey=<ISO2>:<companyRole>`。状态使用 `pending_cohort_baseline`，总分、等级、baselineScore 和 finalDimensionScore 保持 null。

主任务收齐本轮已完成背调后，按 cohortKey 统一执行：

```bash
python '<geto-find-leads-dir>/scripts/calculate_lead_cohort.py' \
  '<国家目录>' --as-of 'YYYY-MM-DD'
```

脚本生成 `Scoring/lead-value-cohort.json`，并以同一 baselineVersion 批量回写该国家所有 cohort 成员。新增公司、观察分或证据等级变化时，主任务重新运行并更新整个 cohort；不同 baselineVersion 的分数不能直接排序。

## 基线与公式

- cohortKey 使用国家代码和本轮主角色，例如 `MX:main_contractor`。
- 每个维度至少 5 家同类型公司具有 A/B/C observedScore，才形成中位数；若样本不足且该公司已经完成该维度的公开研究、确实没有可用信息，则按 `insufficientBaselineFallback.mode=zero` 将 cohort baseline 记为 0，并在 artifact、assessment.gapCodes 和 Evidence 中标记 `cohort_baseline_zero_fallback:<dimensionCode>`。
- `Fᵢ=qᵢOᵢ+(1-qᵢ)Pᵢ`；q 来自 evidenceGrade，P 是同版本 cohort 中位数。
- P 按模型的 maximumBaselineFraction 封顶：城市 1/3、体量 1/2、未来需求 0.4、触达 0.2、付款 1/2、产品 0.4。
- 确认不存在使用 A 级 observedScore=0；未知使用 U/null，由主任务基线补足。
- 样本不足且无可用中位数的维度使用 0 分基线：observedScore 为 U/null 时该维最终分为 0；有数值 observedScore 时按 `q×observedScore+(1-q)×0` 计算。`not_queried`、`provider_failed`、`identity_conflict` 显式保留为未知来源状态，不能把未执行查询当作事实上的 0；这些状态在报告中标记为硬缺口并由主任务决定是否暂缓导入。

信息完整度只由证据权重决定，不因基线补足而提高。法律主体、采购路径、签约主体、未来项目、产品场景和硬反证 cap 在公平分之后继续生效。
