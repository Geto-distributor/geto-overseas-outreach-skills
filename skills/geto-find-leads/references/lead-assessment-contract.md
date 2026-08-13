# 在线索池中使用 Assessment

需要为候选公司评分时，调用 `$geto-diligence-company`；评分字段和门槛见 [GETO 客户价值评分合同](../../geto-diligence-company/references/lead-assessment-contract.md)。处理返回结果时：

- 调用 `$geto-diligence-company` 时对线索池候选传 `assessmentMode=lead_value`。
- 只接收 `producerSkill=geto-diligence-company` 的 Assessment。
- 不重新计算、覆盖或补写任何维度、总分或等级。
- 只对 `assessmentStatus=completed`、模型版本一致的结果做跨公司排序。
- 将 `not_requested`、`pending_diligence`、`pending_capability_foundation`、`pending_model`、`incomplete_evidence` 单独统计，不用 0 分替代。
