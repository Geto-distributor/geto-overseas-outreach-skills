---
name: geto-map-relationships
description: 将 GETO 海外市场中的公司、项目、产品与商业协作建模为有证据的实体关系，区分公司角色和关系类型，记录采购方、实际使用方、合作方式、时态、强度、限制与切入点。用于竞对客户关系、项目参与关系、供应经销、租赁销售、设计协同、联合投标和合作网络梳理；不把 customer、competitor 或 project 当 relationshipType。
---

# GETO 商业关系网梳理

关系是边，Company、Project、Product 是节点；customer、competitor、partner、ecosystem 是节点角色。不得用角色代替关系类型。

## 输入

接受已归一的 Company、Project、Product、已有 Claim/Source，以及待判断的关系观察。涉及 GETO 产品、合作方式或切入点时同时读取 `$geto-capability-foundation` 的 CapabilityContext。未完成主体归一时先返回 pending，不生成正式边。

对象合同见 [relationship-contract.md](references/relationship-contract.md)。

## 工作流

### 1. Resolve 节点

先查询已有 Company/Project/Product，自然键、别名、域名和法定实体去重。同一公司多角色只保留一个 Company。

### 2. 拆分关系主张

把“谁与谁、在什么项目、用什么产品、以何种方式合作”拆成原子 Claim。关系描述不得承载多个未经区分的交易。

### 3. 判断是否达到建边门槛

可建立关系的最低条件：

- sourceCompany 和 targetCompany 可识别；
- relationshipType 可从证据直接支持；
- 来源能定位到具体合作语境；
- current/historical/unknown 时态明确；
- 反证已记录。

竞对官网具名案例只要同时明确客户/伙伴、项目或产品、合作内容，即可建立相应关系；不要求客户侧重复确认。

同场参建、Logo、匿名案例、组合实体未拆分或项目串案不能建边。

### 4. 分类节点角色与边类型

节点角色独立保存。relationshipType 从以下受控语义选择并按 OpenAPI 实际枚举映射：

- cooperation
- competition
- supply
- distribution
- formwork_rental
- formwork_sale
- nominated_supplier
- project_participation
- construction_subcontract
- design_collaboration
- joint_bidding
- long_term_supply
- one_off_project

无法确定时保持 pending，不创造新含义相近的自由文本类型。

### 5. 填充交易字段

只有证据明确披露时才填写 procurementParty、actualUser、payer、sale/rental、exclusive、strength、location、timeWindow。竞对案例不能自动证明这些字段；未知使用 null/unknown。

### 6. 关系证据与红队

每条边单独保存 supports/refutes/context 来源、locator、evidenceStatus 和 lastCheckedOn。检查同名公司、项目混淆、当前/历史误判、买方/使用方混淆及独家关系误推断。

### 7. GETO 切入判断

entryPoint 和 limitation 是关系层分析，不是公司评分。它们必须同时引用关系事实、Claim 和相应的 GETO product/service/cooperation code；关系切入分不得进入竞对的客户价值平均分。能力底座缺失时客观关系仍可建边，但 entryPoint、GETO productCode 与建议 cooperationMode 保持 pending。

### 8. 交付

输出 RelationshipDelta。$omnix-market 可用时先 resolve 节点和来源，再按依赖顺序写私人草稿；缺失时保留 API-ready 对象。submit 需要用户明确意图，Approve/Reject 永不调用。

## 质量门槛

- relationshipType 不是节点角色。
- 无证据字段保持未知。
- 每条关系有独立证据状态。
- source/target 不得相同，除非领域明确允许且有专门类型。
- Project/Product 引用只在自然键已 resolve 时写入。
- 关系被反证时保留 refutes 链，不能只删除不留痕。
