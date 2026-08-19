---
name: geto-find-leads
description: 为 GETO 在指定国家或地区按单一公司角色轨道发现、归一和筛选建筑模架、装配式与模块化候选，并在每家公司独立背调完成后聚合六维客户价值评估。用于开发商、总包、分包、代理顾问、经销贸易或其他设计咨询监理轨道的发现任务、项目采购方反查和竞对客户回流；不在一个任务包办全部轨道，不直接确认竞对或上传 OmniX。
---

# GETO 单轨道线索发现

本 Skill 一次只执行一个角色发现轨道。广泛召回不等于合格客户；正式分类和评分由主任务在单公司背调后完成。

## 输入与预检

- 国家、语言、产品范围、`asOf`、`full|sample` 和采样边界。
- `laneCode/companyRole`，只允许 `developer`、`main_contractor`、`subcontractor`、`agent_consultant_pm`、`distributor_trading`、`design_consulting_supervision_other` 之一。
- 成果文件路径、已有候选和禁止重复查询清单。

读取 `$geto-capability-foundation` 的产品/场景切片与 SearchLexicon。公开 Web 是必需来源。Provider 由各自独立任务处理，本任务不直接混用 Provider trace。详细状态见 [provider-policy.md](references/provider-policy.md)。

## 工作流

1. 使用该轨道的国家、角色、产品、技术、项目场景词与查询模板召回；关键词和公司名称只能用于召回。
2. 查询政府项目、招投标、协会、榜单、企业官网、项目案例、新闻和必要社媒。
3. 用稳定官网域名、法定名称和注册号归一；名称相似、集团关系、共同地址或项目共现不得自动合并。
4. 初筛每个候选是否可能采购、使用、影响选型或经销 GETO 产品。目录命中或宽泛行业描述只能标 possible。
5. 对每个候选记录发现来源、目标角色、目标产品、接受/拒绝理由、开放问题和推荐背调优先级。
6. 不在本任务深调全部公司；把入选候选交回主任务，由主任务创建一家公司一个 `$geto-diligence-company` 任务。
7. 评分时只聚合单公司背调返回的已完成同版本 Assessment；不得重算维度、总分或等级。

输出合同见 [output-contract.md](references/output-contract.md)。

## 关键纪律

- Provider Observation 不能直接成为已确认 Company、lead/competitor 分类或评分。
- companyRoles 表达市场角色；researchClassifications 独立表达 lead/competitor。
- 经销、租赁、分包或顾问角色不自动等于 lead；必须说明其采购、使用、选型影响或渠道边界。
- 竞对客户回流使用同一 Company 目录和同一评分合同，不另建名单或评分口径。
- 未查询、未找到、冲突、过期与 Provider 失败分别记录。

## 任务回传

回传做了什么、召回与去重数量、候选及接受/拒绝理由、成果路径、查询边界、缺口、建议创建的单公司任务和下一步。不要返回 ResearchDelta、runId/taskId 或任何本地技术 ID。
