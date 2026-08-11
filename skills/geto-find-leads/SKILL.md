---
name: geto-find-leads
description: 为 GETO 在指定国家或地区发现建筑模架、装配式与模块化相关销售线索，并在公司背调完成后执行可解释的六维客户价值评分。用于国家线索池、总包/建筑商/开发商/设计院/专业分包/项目采购方发现、政府项目和招投标反查、竞对客户转入统一线索池、线索去重、机会项目关联及客户价值评估。不得用于未经背调直接打分或 Excel 作为正式交付。
---

# GETO 线索发现与价值评分

把“广泛召回”和“证据化评分”分成两个阶段。发现候选不等于合格客户；正式评分强依赖 $geto-diligence-company 的背调结果。

## 启动预检

1. 确认国家/市场、GETO 产品范围、研究深度、结果模式和截止时间。
2. 读取 `$geto-capability-foundation`，把用户产品描述解析为 `productCode`、`scenarioCode`、目标采购角色和可引用案例。缺失时仍可做中性候选召回，但所有 GETO 适配与评分保持 `assessment_pending_capability_foundation`。
3. 检查公开 Web 研究能力。公开 Web 是必需来源；不可用时停止并报告 web_unavailable。
4. 检查 $tradewind-api、$netease-waimao 是否可用并已鉴权。缺失时记录 skill_unavailable，未配置 Key 时记录 not_configured，不能声称已查询。
5. 检查 $geto-diligence-company。缺失时仍可输出候选清单，但所有账号保持 assessment_pending_diligence。
6. 检查 $omnix-market。缺失不阻断研究，但最终只能生成 API-ready ResearchDelta，deliveryStatus=blocked_market_unavailable。

Provider 状态和降级规则见 [provider-policy.md](references/provider-policy.md)。

## 工作流

### 1. 定义召回空间

按能力底座选择产品、工程场景、采购角色与项目信号，不按公司名称关键词代替业务判断：

- Top 总包、建筑商、开发商、设计院、混凝土/支模/结构专业分包。
- 政府发布的项目、规划许可、投标、预审、中标和采购公告。
- 机场、轨交、桥隧、高层住宅、医院、数据中心、工业设施等适配项目。
- 本地经销、租赁、预制、模块化、钢铝加工和施工生态。
- 已确认竞对的具名客户与合作项目，由 $geto-mine-competitor-customers 转入。

### 2. 三路召回

并行使用可用来源：

- Web Search：榜单、协会、政府项目、招投标、企业官网、项目案例、新闻和社媒。
- TradeWind：Agentic/Search 批量发现公司，必要时用 Company/People/Customs 补充观察。
- 网易外贸通：全球搜索及 company/contact/customs 等普通能力。

第三方结果先保存为 ExternalObservation，不得直接成为正式 Company、Claim 或评分。

### 3. 统一实体与去重

先查询已有 Company，再以官网主域名、法定实体、注册号、规范名称和别名 resolve。一个 Company 可同时拥有 customer、competitor、partner、ecosystem 等角色；禁止为不同角色复制公司。

为潜在交易对象建立 CommercialAccount，为具体采购路径建立 OpportunityProject。公司、账户、项目不得混为一段 recommendation 文本。

### 4. 候选资格初筛

剔除或降级：仅目录命中、无法确认主体、纯材料/设备租赁且无 GETO 采购边界、匿名项目、明显不在目标市场、已有硬反证的主体。保留原因、反证和待查缺口。

### 5. 强制背调

对拟进入评分的每个账户调用 $geto-diligence-company。只有 completed 或 completed_with_explicit_gaps 可进入评分；pending、failed、identity_conflict 只能留在候选池。

### 6. 六维价值评分

使用 [lead-assessment-contract.md](references/lead-assessment-contract.md) 中的 `GETO_LEAD_VALUE` 客户价值模型。每一维必须有独立理由、Claim 和 Source，不得把总评复制到全部维度，也不得把一个来源笛卡尔映射到所有维度。

`multi_product_fit` 还必须引用本次 `CapabilityContext` 的 product/scenario/case keys，并与目标公司的项目、需求和采购边界证据相交叉。能力底座只证明 GETO 侧能提供什么，不能替代客户侧 Claim/Source。

### 7. 质量检查与交付

- 计算召回数、去重后公司数、背调覆盖率、可评分率、证据等级分布和 Provider 缺口。
- 生成 [output-contract.md](references/output-contract.md) 定义的 ResearchDelta。
- 有 $omnix-market 时先 resolve，再写私人草稿；仅在用户明确要求时 submit。
- 不调用 Approve/Reject。Excel 只能作为可选导出，不是业务合同。

## 关键纪律

- 没有已完成背调，不生成正式总分。
- 没有可用的 GETO 能力底座，不生成 `multi_product_fit` 或正式总分。
- 没有已批准模型，不猜权重；返回 assessment_pending_model。
- 未查询、未找到、冲突、不适用、过期必须分开。
- 竞对反查客户使用同一 Company、CommercialAccount、背调和六维评分，不另建评分口径。
- 所有自然键、来源包、research run、agent/model/skill 信息进入 provenance；不写数据库 ID。
