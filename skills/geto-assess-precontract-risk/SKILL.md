---
name: geto-assess-precontract-risk
description: 对已进入具体合作或签约准备阶段的 GETO 海外客户执行合作前风险评估，把主体、财务、信用诉讼、交易条款、项目经济、硬阻断和缓释条件写入该公司的本地 ResearchBundle。用于报价、授信、合同申请、签约审批或项目成交前复核；前期线索价值由公司背调评估。
---

# GETO 签约前风险评估

本 Skill 回答“这一明确交易能否按当前条件继续”。范围限定为精确的法定签约主体、具体机会和拟议条款。

强依赖 `$geto-diligence-company`。缺少唯一签约主体、具体机会或当前条款时先补证。读取 `$geto-capability-foundation` 核对产品、服务与项目场景；读取 [assessment-contract.md](references/assessment-contract.md) 和 [output-contract.md](references/output-contract.md)。

## 必需输入

- 自然公司名、法定主体身份锚点和公司目录。
- 具体项目/机会、地点、产品、金额、交付和预估利润率。
- 定金、发货前累计收款、账期、币种、担保、抵房/以物抵债和外汇限制。
- 批准的 assessmentModelCode/modelVersion、研究截止日和授权内部材料。

## 工作流

1. 核验唯一签约主体和机会；主体冲突时停止最终评估并写入 `researchStatus=identity_conflict`。
2. 补齐近三年经营财务、股权、注册与实缴资本、信用、诉讼监管和履约历史。集团资料不得无说明映射到子公司付款能力。
3. 分别形成 CounterpartyRisk、DealTermsRisk、ProjectEconomics、hardStops 和 mitigations；写入 `risks[]`、`assessment`、`recommendedActions[]`，每个事实 item 内嵌 Evidence。
4. 未查询不等于零风险，未发现不等于不存在。注册资本和实缴资本不得作为现金、收入、净资产、偿债或授信能力替代。
5. 模型或关键条款不完整时只保存评估缺口，不生成总分/等级；评分不能覆盖 hard stop。抵房/以房抵款仅在事实确认时按现有规则触发禁止提交条件。
6. 最终 decision 只允许 `approve|approve_with_conditions|hold|reject`，并列出决定性事实、未解决缺口、缓释条件、责任人和复核时间。
7. 更新 `report.md` 与按需 `RisksAndAssessment/` 资料，重新生成来源索引并运行本地验证。

## 交付边界

回传做了什么、公司与报告路径、决策、硬阻断、缺口、下一步。无 OmniX 不影响评估完成；是否上传完整 Company Aggregate 由主任务在验证通过后另行询问用户。
