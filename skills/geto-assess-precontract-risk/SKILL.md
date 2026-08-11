---
name: geto-assess-precontract-risk
description: 对已进入具体合作或签约准备阶段的 GETO 海外客户执行合作前风险评估，核验准确签约主体、客户资质、资本经营、信用诉讼、定金与发货前收款、币种外汇、项目利润率及抵房等交易条款，形成有证据的风险、硬阻断与缓释条件。用于报价、授信、合同申请、签约审批或项目成交前复核；不用于前期线索价值评分。
---

# GETO 签约前风险评估

## 目标与边界

本 Skill 回答“这一个明确交易是否可以按当前条件继续签约”。它评估精确的 `Company/LegalEntity + Opportunity + proposed terms`，不是再次判断某家公司是否值得开发。

强依赖 `$geto-diligence-company`。缺少可确认的法定签约主体、具体机会或当前交易条款时，先补证；不得用集团、品牌或项目参与方的资料替代合同相对方。

读取 `$geto-capability-foundation` 核对本次产品、服务模式和适用项目场景。能力底座缺失不阻断 CounterpartyRisk 的事实整理，但 ProjectEconomics、交付范围和最终 decision 必须保持待复核。

读取 [assessment-contract.md](references/assessment-contract.md) 执行模型门槛和评分，读取 [output-contract.md](references/output-contract.md) 形成领域对象。

## 必需输入

- marketCode、scopeCode、asOf、币种与拟签约时间。
- contractingCompanyKey 与 legalEntity identity；集团关系另存，不可混用。
- opportunityKey、项目地点、产品、金额、交付与预估利润率。
- 拟议合同条款：定金、发货前累计收款、账期、付款币种、担保、抵房/以物抵债、外汇限制。
- `assessmentModelCode` 与 `modelVersion`；只使用业务已批准的模型。
- 已完成或明确保留缺口的公司背调、Claim/Source、财务、诉讼监管和信用材料。
- capabilityFoundation 的 foundationKey、contentHash、productCodes、scenarioCodes 和状态。

## 工作流

### 1. 解析精确主体和机会

先查询已有 Company、LegalEntity、Opportunity、Relationship、Assessment、Claim 与 Source。按法定名称、注册号、官网域名、别名及国家解析自然键；发生主体冲突时停止最终评估并输出 `identity_conflict`。

### 2. 补齐合作前证据

调用 `$geto-diligence-company` 核验成立年限、主体状态、集团/上市属性、近三年经营财务、股权、注册与实缴资本、产品使用历史、信用评级、诉讼、失信与黑名单。

对合同条款、项目毛利和 GETO 内部历史只接受用户提供、内部授权数据或可验证合同材料。公开网络、TradeWind、网易外贸通不能证明未公开的付款承诺。

### 3. 分层建模

分别形成：

- `CounterpartyRisk`：主体、资本经营、信用、诉讼监管、履约历史。
- `DealTermsRisk`：定金、发货前收款、币种、外汇、账期、担保和抵房条款。
- `ProjectEconomics`：项目金额、成本边界、利润率、交付窗口及敏感性。
- `hardStops` 与 `mitigations`：每项必须指向明确业务规则及 Claim/Source。

不要把“未查询”当作零风险，也不要把“未发现”写成“不存在”。

ProjectEconomics 中的产品和服务范围必须能解析到能力底座。历史案例只能作为交付能力参照，不能替代本交易的工程量、成本、条款或利润证据。

### 4. 应用模型门槛

逐项使用批准模型的原始分、满分、评分理由和证据。若模型代码或规则不可用、分值口径冲突、关键交易条件尚未形成，则只输出 `assessment_draft` 与 evidence gaps，不计算总分或最终等级。

`抵房/以房抵款`按现有业务规则属于禁止提交条件；只有事实被确认时才触发。其他 hard stop 不得自行发明。

### 5. 形成决策

最终 decision 只允许：

- `approve`
- `approve_with_conditions`
- `hold`
- `reject`

每个 decision 都要列出决定性事实、未解决缺口、缓释条件、责任人和复核时间。评分不能覆盖 hard stop。

### 6. 交付

若 `$omnix-market` 可用，先 resolve，再将 Assessment、维度、Claim/Source 与关联对象写入私人草稿。默认不提交；只有用户明确要求“提交审核”才调用 submit。永不调用 Approve 或 Reject。

若 Market Skill 不可用，输出完整 API-ready ResearchDelta 和 `deliveryStatus=blocked_market_unavailable`；不得回退到 Excel 作为正式交付。

## 不变量

- 签约主体与项目机会必须唯一、可核查。
- 集团财务不得无说明地映射到子公司付款能力。
- 一个来源只链接它实际支持或反驳的维度。
- 联系人、财务、合同条款和项目经济数据保持独立对象。
- 保留 `not_queried`、`not_found`、`conflicting`、`not_applicable` 与 `pending`，不得伪造覆盖率。
- 记录 researchRun、skill、agent/model、asOf、provenance、幂等自然键和审核状态。
