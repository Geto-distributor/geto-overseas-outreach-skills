---
name: geto-mine-competitor-customers
description: 为 GETO 按单一产品技术面或商业角色召回竞对候选，并在一家公司一个独立任务中核验产品商业控制、制造与履约模式，再沿确认竞对的官方项目案例反查未来可合作客户。用于模架、装配式、模块化、租赁经销与材料生态的竞对发现和客户反查；竞对结论以目标公司产品、市场和商业控制 Evidence 为准。
---

# GETO 竞对发现与客户反查

分开执行两道门：G1 判断是否真实竞争，G2 从确认竞对的官方案例寻找合格客户。一次发现任务只处理一个产品/技术面或商业角色；每个需确认的竞对使用独立背调任务。

## 依赖

- Web 研究必需。
- `$geto-capability-foundation` 提供产品、场景、competitionSurface 与 SearchLexicon。
- `$geto-diligence-company` 负责一家公司一个任务的事实补强。
- `$geto-map-relationships` 负责竞对—客户—项目关系。
- Provider 只在 TradeWind/网易各自独立任务中返回 ExternalObservation。

## G1：竞对召回与判定

1. 按产品/技术、项目、制造、品牌、租赁、经销和服务角色召回候选。framework、formwork、modular 等名称命中只用于召回。
2. 用强身份锚点归一候选，不按相似名称合并。
3. 为需要确认的每家公司创建独立背调任务，优先核查官网 Products、Services、Solutions、Manufacturing、Factory、Rental、Distribution、Projects 与 About。
4. Competitor Gate 必须同时满足：
   - 产品、系统、工法或渠道与 GETO competitionSurface 重叠；
   - 在目标国家/市场实际经营；
   - 公司控制相关产品的商业化、销售、出租、分销或自有系统，而不只是安装实施。
5. 依据 [competition-decision.md](references/competition-decision.md) 形成 `confirmed|possible|rejected`：
   - manufacturer/system_owner/brand_owner 且重叠：直接竞对；
   - distributor/reseller/rental_provider 且经营竞品：渠道竞对；
   - installer/service_contractor-only：拒绝 competitor，可继续判断 lead/合作伙伴；
   - contract_manufacturer-only：制造供应方/生态方，除非独立销售自有重叠产品；
   - outsourced 自有品牌/系统：仍可能确认竞对；
   - 商业控制或制造状态不清：possible，补证后再判。

自有工厂是强证据但不是必要条件，也不能替代产品和市场重叠证据。

## G2：官方案例客户反查

优先读取竞对官网 Projects、Case Studies、Testimonials、News。只有具名客户/合作方、可识别项目或产品、明确合作内容时才建立候选关系；不要求客户侧重复确认。

Logo、匿名案例、同场参建、组合实体未拆分、不同项目串案或已有反证不得进入客户池。案例不能自动证明 buyer、payer、采购方式、买断/租赁、排他或当前持续性。

把可采购、使用或影响选型的实体交回主任务，创建独立 `$geto-diligence-company` 任务；渠道、制造供应、设计和施工伙伴进入关系图但不计客户数。

## 输出与回传

按 [output-contract.md](references/output-contract.md) 保存候选、竞对分类建议、拒绝理由、官方案例关系和新公司名单。回传做了什么、成果路径、接受/拒绝理由、缺口和下一步。
