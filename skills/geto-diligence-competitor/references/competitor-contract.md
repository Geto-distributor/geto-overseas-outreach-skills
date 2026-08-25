# 单竞对事实与分类合同

## Competitor Gate

在 `researchClassifications[]` 写入一条 competitor 分类：

- `confirmed`：目标产品、目标市场经营与商业控制三项均有直接 Evidence。
- `possible`：主体可识别，但产品重叠、市场活动或商业控制仍有关键缺口。
- `rejected`：产品面不重叠，或公司仅提供安装实施服务且不控制产品商业化。

商业控制包括 brand_owner、system_owner、manufacturer、distributor、reseller、rental_provider。自有工厂是制造深度事实；拥有并销售自有品牌或系统的委外生产企业仍可满足商业控制。contract_manufacturer 只有在独立销售重叠产品时才进入 confirmed 判断。

## 逐产品事实

每个相关 `productsAndServices[]` item 至少表达：

- 产品或系统自然名称、类别、技术词、应用场景与目标客户；
- 目标国家市场活动；
- commercialRoles[]；
- manufacturingStatus、manufacturingDescription、factoryLocations[]；
- 与 GETO competitionSurface 的重叠、相邻替代或互补边界；
- 可定位的 Evidence，以及产品 item 的 status、reason 和 verificationStatus。

官网只展示产品时可证明产品存在，制造主体、工厂控制、产能和自产比例分别取证。

## 项目与客户候选

项目证据分三层记录：项目存在、目标公司参与、目标公司提供的产品或承担的合同角色。三层证据可以来自不同来源，结论只扩张到已闭合层级。

官方 Projects、Case Studies、Testimonials 或 News 明确点名可识别公司，并闭合具体项目或产品/服务及实际合作内容时，可以确认该范围内的合作关系；buyer、payer、actualUser、租售方式、排他和当前持续性未知时保持 null。Logo 墙、匿名案例、共同参建和搜索摘要进入待核记录。

需要客户资格、关系切入分或组合价值时，交给 `$geto-mine-competitor-customers` 处理。客户评分覆盖不改变公司级 competitor 结论。

## 结果语义

本 Skill 的公司级结果由竞对分类、逐产品竞争事实、制造与履约边界以及具名客户候选组成。客户价值平均分和关系切入分由竞对客户关系产生，字段合同位于 `$geto-mine-competitor-customers`。
