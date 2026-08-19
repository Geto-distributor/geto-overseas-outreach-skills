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
- 每个维度至少 5 家同类型公司具有 A/B/C observedScore，才形成中位数。
- `Fᵢ=qᵢOᵢ+(1-qᵢ)Pᵢ`；q 来自 evidenceGrade，P 是同版本 cohort 中位数。
- P 按模型的 maximumBaselineFraction 封顶：城市 1/3、体量 1/2、未来需求 0.4、触达 0.2、付款 1/2、产品 0.4。
- 确认不存在使用 A 级 observedScore=0；未知使用 U/null，由主任务基线补足。
- 任一维度不足 5 个合格样本时，该 cohort 全部保持 pending_cohort_baseline，不产生临时分数。

信息完整度只由证据权重决定，不因基线补足而提高。法律主体、采购路径、签约主体、未来项目、产品场景和硬反证 cap 在公平分之后继续生效。
