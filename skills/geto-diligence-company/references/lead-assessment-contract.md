# GETO 客户价值评分权威合同

本文件是 `GETO_LEAD_VALUE` 六维客户价值评分的唯一业务权威来源。`$geto-diligence-company` 是单公司 Assessment producer；`$geto-find-leads` 只能汇总和排序返回结果，不得复制锚点、重新计算或覆盖维度。

## 输入、状态与前置门

- 输入 `assessmentMode` 只能是 `none` 或 `lead_value`，缺省为 `none`。
- `assessmentMode=none`：`assessmentStatus=not_requested`，不创建 Assessment。
- `assessmentMode=lead_value`：`diligenceStatus` 必须为 `completed` 或 `completed_with_explicit_gaps`；其他状态统一 `pending_diligence`，不得评分。
- 评分业务对象是 Company；一个国家内 Company 与 CommercialAccount 一一对应，持久化时明确映射到该 Company 内嵌 account。
- 模型代码固定为 `GETO_LEAD_VALUE`，并使用当前已批准 `modelVersion`。版本不可用时 `assessmentStatus=pending_model`。
- `capabilityFoundation.status` 必须为 `available`，并保存 contentHash、productCodes、scenarioCodes、caseKeys 与 sourceKeys。partial/unavailable 时 `assessmentStatus=pending_capability_foundation`。
- 任一维度不可评分时 `assessmentStatus=incomplete_evidence`；不得生成 totalScore、rating 或 levelCode。
- 六维全部合法且确定性计算完成后才可 `assessmentStatus=completed`。

## 六个维度

| dimensionCode | 满分 | 评估内容 |
|---|---:|---|
| project_city_value | 15 | 项目所在城市与市场价值 |
| account_scale | 20 | 企业规模、经营能力及可承接体量 |
| future_project_demand | 20 | 未来项目管线与模架/装配式需求 |
| reachability | 10 | 决策链、联系方式及触达可行性 |
| payment_capacity | 15 | 支付能力、财务稳定性和付款风险 |
| multi_product_fit | 20 | GETO 多产品组合适配度 |

## 维度评分锚点

### project_city_value（15）

- 城市 GDP/GRP 与市场体量：8 分。
- 公共建筑与建设活动：7 分。
- 使用机会项目所在地，不用公司注册地址替代。没有可确认项目地点时最高 5/15。

### account_scale（20）

- 财务与资本承载：10 分。
- 项目与订单规模：6 分。
- 运营与交付能力：4 分。
- 集团值必须说明归属且不能在母子公司重复计分；异常主体最高 3/20。

### future_project_demand（20）

- 未来项目数量：6 分。
- 产品/工法需求：9 分。
- 确定性和进入窗口：5 分。
- 历史案例不算未来需求；别名项目先去重。关键事实 unknown 时最高 8/20。
- 同一项目的需求贡献按时间/确定性递减：100%、60%、35%，其后项目按 15% 计入，避免项目数量堆分。

### reachability（10）

- 目标岗位与具名决策人：5 分。
- 可验证的直接触达入口：3 分。
- 当前采购/项目窗口：2 分。
- 不按联系人数量堆分；联系人必须与 Company 去重关联并保存来源。

### payment_capacity（15）

- 资金与现金流：7 分。
- 风险事件：5 分。
- 合同与付款机制：3 分。
- 只评精确交易/签约主体；主体未确认时最高 9/15。

### multi_product_fit（20）

- 可交易产品族宽度：8 分。
- 与已知项目场景的相关性：8 分。
- 可执行的交易路径：4 分。
- 必须同时具备 GETO 能力底座映射和目标客户/项目侧 Claim/Source。没有客户场景证据时最高 8/20；没有能力底座时保持未评分。共享工程量和互斥方案不得重复计分。

## Dimension 合同

每维至少包含：

~~~json
{
  "dimensionCode": "future_project_demand",
  "observedScore": 16,
  "maxScore": 20,
  "evidenceGrade": "B",
  "evidenceWeight": 0.75,
  "peerPriorScore": null,
  "cohortSnapshotKey": null,
  "finalDimensionScore": null,
  "scoreCalculationStatus": "pending_deterministic_rule",
  "rationale": "未来两年有三个已披露项目，其中两个存在结构施工窗口。",
  "claimKeys": ["claim_company_pipeline"],
  "sourceKeys": ["source_official_projects"],
  "gapCodes": [],
  "capCodes": []
}
~~~

证据等级：A=权威直接证据，B=可信一手或多源一致，C=有限间接证据，U=无可用证据；建议权重 1、0.75、0.5、0 仅在批准模型确认后使用。

Agent 负责 `observedScore`、证据等级、理由和逐维 Claim/Source。`finalDimensionScore`、`totalScore` 与等级必须由批准的确定性 validator 或服务端规则计算并返回，同时保存 `scoreCalculatedBy=deterministic_validator|server_rule`。没有冻结 cohort 和模型时不得启用 peer prior；U 级或不可评分维度保持 null，不能用 0 代替未知。

等级代码只允许服务端 reference-data 当前发布的 `A|B|C|U` 或其后批准版本。未批准阈值、缺少 `ratingScaleVersion` 或任一维度未完成时，不得生成 rating/levelCode。
