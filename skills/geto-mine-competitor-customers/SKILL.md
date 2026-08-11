---
name: geto-mine-competitor-customers
description: 为 GETO 发现真实竞对、完成竞争判定，并沿确认竞对的官方项目案例反查未来可合作客户。用于模架、装配式、模块化、渠道与材料生态的竞对候选召回、四类竞对分类、竞对官网具名案例核查、客户资格判断和竞对客户转入统一线索池。核心产出是可合作客户及其项目关系，不生成产品威胁总分。
---

# GETO 竞对发现、竞争判定与客户反查

本 Skill 内部有两道独立门：G1 判断“是否真正竞争”，G2 从确认竞对的官方案例寻找 GETO 未来客户。竞对名单本身不是终点。

## 依赖与预检

- Web 研究必需。
- `$geto-capability-foundation` 提供 GETO 产品代码与 competitionSurfaces。缺失时可多路召回 `competitor_candidate`，但不得作 confirmed/rejected 竞争判定。
- TradeWind 与网易外贸通作为多路召回和交叉验证；缺失时允许 Web-only，并记录 Provider 状态。
- 合格客户必须交给 $geto-diligence-company。
- 竞对—客户—项目关系必须交给 $geto-map-relationships。
- 客户价值统一使用 $geto-find-leads 的六维评分。
- $omnix-market 缺失时输出 ResearchDelta 草稿包，不能声称已入库。

## G1：竞对候选发现与竞争判定

### 1. 多路召回

先从能力底座选择目标市场相关的 productCodes、场景和 competitionSurfaces，再从以下路径召回 competitor_candidate：

- 产品路径：铝模、钢模、爬模、隧道模、清水混凝土、预制/模块化系统及相近工法。
- 项目路径：目标项目的模架系统、施工方案、供应/租赁、技术支持和中标参与者。
- 渠道路径：本地经销、租赁、系统集成、材料控制和工程网络。
- Web Search：榜单、协会、企业官网、项目案例、新闻、招投标。
- TradeWind、网易的公司/行业/海关观察。
- 已有 Company、Project、Relationship 图谱反查。

### 2. 主体归一

先 resolve 已有 Company。Company 可同时拥有 competitor、customer、partner、ecosystem 等角色；多角色不是冲突。

### 3. 竞争判定

只有实体在相同市场中争夺 GETO 能力底座定义的同一产品、工法、项目采购预算或渠道控制权，才确认 competitor。输出底座 productCode/competitionSurface、结论、理由、反证、目标市场证据和最后核查时间。

判定状态：confirmed、rejected、pending、conflicting。确认后再分类：

- SystemPlatform
- SpecialistProductMethod
- ModularOffsite
- ChannelMaterial

纯施工分包、设备租赁、普通材料商、客户或合作伙伴不能因页面出现 formwork/framework 自动判为竞对。

详细对象见 [competition-decision.md](references/competition-decision.md)。

## G2：沿官方案例反查客户

### 1. 读取一手案例

优先竞对官网 Projects、Case Studies、Testimonials、News 或可归属于竞对的正式一手材料。

满足以下条件即可建立候选竞对—客户关系，不要求客户/业主再次确认：

- 明确具名的客户或合作方；
- 可识别项目或产品；
- 明确描述竞对与该公司的合作内容。

### 2. 严格排除

以下不得进入客户池：

- 仅 Logo，无合作语境；
- 匿名项目或匿名证言；
- 同场参建但未说明双方合作；
- 集团、联合体、品牌或组合实体无法拆分；
- 不同项目被串案；
- 已有反证；
- 只能确认制造供应、经销渠道、设计或施工伙伴，不能确认客户资格。

### 3. 不越证据推断

竞对官网案例不能自动证明 buyer、payer、采购方式、买断/租赁、排他、框架协议或当前持续性。未披露字段保持 unknown/null。

### 4. 客户资格分流

为每个反查实体标记 counterpartyRoleCode 和 customerQualificationStatusCode：

- qualified_customer：可能采购或影响采购 GETO 产品，进入统一线索池。
- channel、manufacturing_supplier、designer、construction_partner、group_entity：进入生态/关系图，不计客户数。
- pending/conflicting：保留候选，不进入客户数。

### 5. 强制下游

qualified_customer 必须按顺序：

1. 统一 Company/CommercialAccount resolve。
2. $geto-diligence-company 背调。
3. $geto-map-relationships 建立竞对—客户—项目—产品关系。
4. $geto-find-leads 六维客户价值评分。

## 输出与 KPI

输出遵循 [output-contract.md](references/output-contract.md)。每个竞对的公司级指标仅包括：

- qualifiedCustomerCount
- scoredCustomerCount
- assessmentCoverage
- averageCustomerValueScore

averageCustomerValueScore 只对已完成六维评分的合格客户计算。关系切入分属于 Relationship，不进入平均值。

KPI 聚焦：可核实竞对候选、确认竞对覆盖、具名案例关系、合格客户数、背调覆盖率、评分覆盖率、证据完整率、排除原因可审计率。不得使用产品威胁总分、威胁等级或五维威胁聚合。

## 关键纪律

- Provider Observation 不能直接确认竞对或客户关系。
- 每条关系独立保存 Source/Claim/provenance。
- 官方一手案例足以建立被明确描述的关系，但不能扩张未披露交易字段。
- AU 等回放使用带 asOf 的数据基线和对账不变量，不写死历史数量。
