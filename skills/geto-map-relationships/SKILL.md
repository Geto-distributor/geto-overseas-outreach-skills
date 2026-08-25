---
name: geto-map-relationships
description: 将 GETO 海外市场中已归一的公司、项目、产品与商业协作写入 company.json 的有证据 relationships[]，区分公司角色和关系类型，记录采购方、实际使用方、合作方式、时态、限制与切入点。用于竞对客户关系、项目参与、供应经销、租赁销售、设计协同和联合投标；relationshipType 只表达关系边。
---

# GETO 商业关系网梳理

关系是边，Company、Project、Product 是节点；lead/competitor 是研究分类，developer/contractor/distributor 是公司角色。不得混用。

## 输入

接受已归一的自然公司名、项目、产品、已有内嵌 Evidence 和待判断关系。涉及 GETO 产品或切入点时读取 `$geto-capability-foundation`。主体未归一时返回 pending，不生成正式关系。

对象合同见 [relationship-contract.md](references/relationship-contract.md)。

## 工作流

1. 用注册号或已确认稳定官网域名核对 source/target；名称相似、集团关系和共同项目不得自动合并。
2. 把“谁与谁、在哪个项目、用什么产品、如何合作”拆成一条一事实关系。
3. 只有双方可识别、关系类型有直接证据、合作语境可定位、时态明确且反证已记录时建边。
4. 从受控关系类型选择：parent、subsidiary、shareholder、controlled_by、brand_operator、customer、supplier、distributor、agent、consultant、developer、contractor、subcontractor、joint_venture、strategic_partner、other。
5. 只有证据明确披露时才填写采购方、实际使用方、付款方、sale/rental、exclusivity、strength、location 和 timeWindow；未知保持空值或 unknown。
6. 每个 relationships[] item 内嵌 Evidence。关系事实、待核和冲突状态写在关系 item 中。
7. entryPoint 和 limitations 是关系层分析，必须同时引用关系事实和 GETO 能力；不得进入竞对客户价值平均分。

竞对官网具名案例在明确客户/伙伴、项目或产品和合作内容时足以建边，但不能自动证明买方、付款方、排他或持续合作。

## 交付

把关系合并到相应公司 `company.json`，重新生成 `Sources/sources.md` 并校验。回传修改了哪些关系、成果路径、接受/拒绝理由、冲突、缺口和下一步。是否上传 OmniX 由主任务在本地验证后另行询问用户。
