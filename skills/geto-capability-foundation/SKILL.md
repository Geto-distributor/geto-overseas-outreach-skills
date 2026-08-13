---
name: geto-capability-foundation
description: 为 GETO 海外市场调研提供共享、只读的我方能力底座，统一产品代码、适用工程场景、ICP 与采购角色、服务和合作方式、公开项目案例、既有关系资产及其证据状态。用于线索匹配、六维价值评分、竞对竞争面判断、关系切入点和签约项目范围校验；不负责发现目标公司、背调、评分、调用 Provider 或写入 OmniX。
---

# GETO 能力底座

本 Skill 只回答三类问题：GETO 能提供什么、哪些客户/项目场景适配、哪些公开案例可作为能力锚点。它是其他 GETO Skills 的共同词典，不把我方宣传材料当成目标市场事实，也不直接生成商业结论。

## 使用方式

1. 读取 [foundation-contract.md](references/foundation-contract.md)，确定所需 `CapabilityContext` 范围。
2. 按需读取以下结构化资产，不要把全部资料无差别塞入上下文：
   - [company-profile.json](references/company-profile.json)：公司定位、服务方式和合作形式。
   - [product-catalog.json](references/product-catalog.json)：稳定的能力产品代码和竞争面。
   - [scenario-map.json](references/scenario-map.json)：需求信号、产品、客户角色与案例的映射。
   - [icp-buyer-roles.json](references/icp-buyer-roles.json)：客户画像、采购/使用/影响角色与资格边界。
   - [case-register.json](references/case-register.json)：公开项目案例及可支持主张。
   - [relationship-assets.json](references/relationship-assets.json)：GETO 已有合作关系线索及使用限制。
   - [competitor-seeds.json](references/competitor-seeds.json)：仅用于召回的竞对种子。
   - [source-register.json](references/source-register.json)：来源、证据等级与允许引用范围。
3. 可运行 `python scripts/select_context.py --query '<需求>' --country <ISO2>` 选取最相关的产品、场景、ICP 和案例；已知代码时优先用 `--product-code`、`--scenario-code`。
4. 将选择结果作为下游研究输入，不将其直接写成目标 Company、Project、Relationship、Claim 或 Assessment。

## 证据纪律

- `company_published` 只证明 GETO 官方资料公开表达过该能力或案例，不等于独立第三方验证。
- `independent_verified` 必须存在独立权威来源；当前资料没有就不得自行升级。
- `pending_source_mapping`、`pending_refresh` 和 `not_disclosed` 必须原样保留。
- 只引用 Source 的 `allowedClaims` 范围；精确数字、合作方、资质和当前产能不能跨来源扩张。
- 匿名或区域级案例可证明产品场景，但不能证明具名客户关系。
- 竞对种子只用于多路召回。最终竞对判定仍由 `$geto-mine-competitor-customers` 基于目标市场证据完成。
- 关系资产只提供调查入口。发现真实海外项目和当地合作方后，仍需 `$geto-map-relationships` 建立有证据的关系。

## 下游约束

- `$geto-find-leads`：没有能力底座时可继续中性候选召回；不得自行计算任何维度或总分。
- `$geto-mine-competitor-customers`：没有产品与竞争面定义时只能保留 `competitor_candidate`，不得确认竞对。
- `$geto-diligence-company`：公司事实背调可继续；GETO 适配结论保持 pending，`assessmentMode=lead_value` 时评分状态为 `pending_capability_foundation`。
- `$geto-map-relationships`：客观关系可继续建模；GETO 产品映射、合作方式和切入点保持 pending。
- `$geto-assess-precontract-risk`：对手方风险可继续；产品范围与项目适配缺口必须进入复核清单。
- `$geto-run-market-research`：在 ResearchDelta 中记录 `capabilityFoundation` 的状态、内容哈希及实际使用的 codes/keys。

## 禁止事项

- 不调用 Web、TradeWind、网易外贸通或 OmniX；本 Skill 不持有任何 Key。
- 不写数据库 ID、SQL、Excel importer 或固定 Sheet 名称。
- 不把旧名称“志特”继续作为 Skill 和领域对象主名称；品牌统一使用 GETO。历史来源标题可保留原文。
- 不把自身案例当作目标客户已经采购、付款、租赁、独家合作或持续合作的证据。
- 不因底座缺失而猜产品匹配、竞对资格、客户价值或关系切入点。
