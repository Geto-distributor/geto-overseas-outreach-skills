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

读取 `$geto-capability-foundation` 的产品/场景切片与 SearchLexicon，并读取 `$geto-run-market-research` 的 [classification-and-engagement-contract.md](../geto-run-market-research/references/classification-and-engagement-contract.md) 与 [coverage-and-inventory-contract.md](../geto-run-market-research/references/coverage-and-inventory-contract.md)。公开 Web 是必需来源。Provider 由各自独立任务处理，本任务不直接混用 Provider trace。详细状态见 [provider-policy.md](references/provider-policy.md)。

## 工作流

1. 使用该轨道的国家、角色、每个请求产品面、技术、项目场景词与查询模板召回；关键词和公司名称只能用于召回，并逐单元更新覆盖矩阵。
2. 查询政府项目、招投标、协会、榜单、企业官网、项目案例、新闻和必要社媒。
3. 用稳定官网域名、法定名称和注册号归一；名称相似、集团关系、共同地址或项目共现不得自动合并。
4. 初筛每个候选是否可能采购、使用、影响选型或形成可说明的正式渠道路径。目录命中、行业相邻、一般合作设想或宽泛服务描述不能单独形成 lead。
5. 对每个候选记录发现来源、目标角色、目标产品、强身份状态、接受/拒绝理由、开放问题、推荐背调优先级和候选总账状态。高优先级至少需要一条公司官网之外的独立证据，或可核验的当前项目、招标、合同、监管披露或 Provider 观察。
6. 不在本任务深调全部公司；把入选候选交回主任务，由主任务创建一家公司一个 `$geto-diligence-company` 任务。
7. 单公司任务返回同版本 observedScore、evidenceGrade、Evidence 和 cohortKey 后，主任务读取 [cohort-assessment-contract.md](references/cohort-assessment-contract.md)。每个 cohort 维度至少 5 家合格观察时生成版本化中位数；若公开检索已完成但该维度没有可用中位数，按 `insufficientBaselineFallback.mode=zero` 以 0 作为基线并标记 fallback。`not_queried`、`provider_failed`、`identity_conflict` 仍保持未知，不得直接当作事实 0。新成员或观察输入变化时统一重算，不能混排不同 baselineVersion。
8. cohort 收口会同步清除已完成评分对应的旧迁移占位。只需修复存量占位且不得重算分数时，先运行 `scripts/cleanup_assessment_placeholders.py <国家目录>` 预览，再经确认使用 `--apply`；该脚本不会修改 assessment 分数或其他缺口。

输出合同见 [output-contract.md](references/output-contract.md)。

## 关键纪律

- Provider Observation 不能直接成为已确认 Company、lead/competitor 分类或评分。
- companyRoles 表达市场角色；researchClassifications 独立表达 lead/competitor。
- 经销、租赁、分包或顾问角色不自动等于 lead；必须说明其采购、使用、选型影响或面向 GETO 产品的正式渠道路径。产能互补、联合投标或泛化合作写入建议行动，不激活 lead。
- 竞对客户回流使用同一 Company 目录、同一六维评分合同和同类型 cohort；`$geto-mine-competitor-customers` 从已核实客户分派生组合平均分与覆盖率，并在关系层评估合作切入分。
- 未查询、未找到、冲突、过期与 Provider 失败分别记录。

## 任务回传

回传做了什么、召回与去重数量、候选及接受/拒绝理由、成果路径、查询边界、缺口、建议创建的单公司任务和下一步。
