---
name: geto-run-market-research
description: 编排 GETO 海外市场的一次完整或定向调研，协调线索发现与六维评分、公司背调、竞对发现与客户反查、商业关系网和签约前风险模块，统一维护 ResearchRun、检查点、Claim/Source 证据链与 OmniX 私人草稿。用于国家/地区市场调研、销售线索池、竞对客户挖掘或需要一次性完成多模块研究的任务。
---

# GETO 海外市场情报总编排

## 目标

把多个专业 Skills 编排成一个可恢复、可审计、可提交 OmniX 的 ResearchRun。各子 Skill 对自己的业务判断负责；本 Skill 负责范围、依赖、阶段交接、去重、质量门槛和交付，不重新实现 Provider 或 Market REST 调用。

开始前读取 [orchestration.md](references/orchestration.md)；合并结果时读取 [research-delta-contract.md](references/research-delta-contract.md)。需要持久化本地检查点时使用 `scripts/research_run.py`，交付前必须运行 `scripts/validate_research_delta.py`。

## 输入

- 国家/地区、marketCode、scopeCode、GETO 产品范围、研究截止日 `asOf`。
- 业务目标：线索池、竞对客户、关系网、单公司背调、完整市场调研或签约前复核。
- `executionMode`: `quick` 或 `adversarial`；两者使用同一领域对象和证据合同。
- `resultMode`: `full` 或 `sample`；sample 必须保存采样边界，不能冒充全量。
- 可选种子：公司、项目、竞对、产品、关键词、目标角色、排除项。
- 是否仅创建私人草稿；只有明确“提交审核”才允许进入 submit。

## 阶段流程

### 1. intake

确认范围、自然语言歧义、市场与时间边界。调用 `$geto-capability-foundation` 将产品族、工程场景、ICP 和案例解析为本次 CapabilityContext。生成 `researchRunKey`，记录 skill/agent/model、asOf、resultMode、provenance。不要把 API Key、cookie 或 Provider 原始凭证写入状态文件。

### 2. capability check

检查以下 Skill 是否存在且可用：

- `$omnix-market`
- `$tradewind-api`
- `$netease-waimao`
- `$geto-capability-foundation`
- 五个 GETO 子 Skills

Provider 状态使用统一枚举：`available`、`skill_unavailable`、`not_configured`、`unauthenticated`、`forbidden`、`rate_limited`、`provider_session_expired`、`upstream_unavailable`、`partial`、`failed`。

公开 Web 研究始终是主链。TradeWind 与网易外贸通是可选增强：缺失时继续 Web-only，并明确覆盖差距。OmniX Market 缺失时研究仍完成 API-ready ResearchDelta，但 `deliveryStatus=blocked_market_unavailable`。

能力底座状态独立记录为 available/partial/unavailable，不放入 Provider 状态。partial/unavailable 时仍可完成中性发现和客观证据整理，但禁止正式 GETO 产品适配、竞对确认、`multi_product_fit` 和客户价值总分。

### 3. resolve

若 `$omnix-market` 可用，先查询已有 Company、别名、域名、LegalEntity、Project、Product、Relationship、Source 与 Assessment，再决定 create/update/link。任何子 Skill 都必须 resolve-before-upsert。

### 4. discovery

根据目标编排：

- `$geto-find-leads`：Web Search、可用 Provider 和已有图谱多路发现候选。
- `$geto-mine-competitor-customers`：G1 竞对判定，G2 官方案例客户反查。

竞对反查出的合格客户必须回流统一线索池，不能形成另一套 Company。

### 5. evidence

所有进入价值评分或关键关系的 Company 调用 `$geto-diligence-company`。普通主体核验和竞对本身传 `assessmentMode=none`；国家线索池候选和已回流的竞对客户传 `assessmentMode=lead_value`。ExternalObservation 经过主体归一、冲突仲裁和 Claim/Source 绑定后才进入 ResearchDelta。

`adversarial` 模式对关键 Claim 运行 Builder/Challenger：硬反证可回滚候选资格、竞对判定、关系或评分；不得只追加一段“风险提示”。

### 6. decision

- `$geto-diligence-company` 生成单公司六维 Assessment；`$geto-find-leads` 使用 completed 结果做覆盖率统计和跨公司排序。
- 所有 GETO 适配、竞对判定与评分使用同一份 CapabilityContext 和 contentHash。
- `$geto-map-relationships` 建模公司—公司、公司—项目和产品关系。
- `$geto-assess-precontract-risk` 仅在机会成熟且签约主体/条款明确时运行；它不属于普通线索评分必经阶段。

### 7. delta validation

运行 `python scripts/validate_research_delta.py <delta.json>`，校验自然键、角色与关系类型、证据链接、状态枚举、模型信息、重复实体、孤立子资源、source package 和各模块 handoff。任何 ERROR 都阻止写入/提交；WARNING 必须进入人工复核清单。任何未查字段保持显式状态；不得为了“完整”补空洞结论。

### 8. delivery

若 `$omnix-market` 可用：查询/resolve → 创建或更新当前用户私人草稿 → 回读 → 本地校验 → 预提交校验。预提交校验不可用时停在私人草稿并记录能力缺口。按用户意图决定是否 submit。永不调用 Approve/Reject；审核只在 Web UI。

若不可用：保存或返回 API-ready ResearchDelta、checkpoint 和 delivery blocker。Excel、SQL patch、数据库 ID 不是业务交付合同。

## 检查点

固定阶段为 `intake`、`resolve`、`discovery`、`evidence`、`decision`、`submission`。每阶段记录 status、startedOn、completedOn、inputs、outputs、gapCodes、providerStatuses。失败后从最近完成的阶段恢复，不能无条件重跑并制造重复 Source/Company。

## 完成条件

- 研究范围和 resultMode 可解释。
- Company 多角色统一，Project/Opportunity 和 Relationship 结构化。
- 关键结论均有 Claim/Source/ClaimSourceLink 或明确 pending/not_found。
- 评分逐维可解释且带批准模型信息。
- ResearchDelta 保存能力底座摘要；下游使用的 product/scenario/case/source keys 可对账。
- 所有写入都是 owner 私人草稿并可幂等重放。
- 报告 provider coverage、validation errors、delivery status 与人工待办。
