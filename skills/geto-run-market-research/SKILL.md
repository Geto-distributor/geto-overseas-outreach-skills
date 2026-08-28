---
name: geto-run-market-research
description: 编排 GETO 海外市场的一次完整或定向调研，以本地 ResearchBundle 为第一交付，按公司角色、Provider 和单公司背调创建用户可见任务，持续扩展公司、项目、产品、人员与供应链信息，并由主任务完成跨公司综合、研究充分性审校和 AI 结论。用于国家/地区市场调研、销售线索池、竞对客户挖掘或多模块研究；OmniX 仅在用户明确要求时作为可选同步层。
---

# GETO 海外市场情报总编排

## 目标与边界

把当前国家调研任务作为主任务。用用户可见的独立任务承载角色发现、Provider 查询和逐公司背调；subagent 只允许在单个任务内部并行。主任务维护人可直接浏览的中文 ResearchBundle，推动信息广度、重点路径深度、关联扩展与跨公司 AI 综合，不依赖评分、Provider 或 OmniX 完成研究。

开始前读取 [research-intelligence-contract.md](references/research-intelligence-contract.md)、[orchestration.md](references/orchestration.md)、[diligence-review-contract.md](references/diligence-review-contract.md)、[classification-and-engagement-contract.md](references/classification-and-engagement-contract.md)、[coverage-and-inventory-contract.md](references/coverage-and-inventory-contract.md) 与 [company-json-contract.md](references/company-json-contract.md)。构造、复核或校验 Company 字段时读取 [company-field-requirements.md](references/company-field-requirements.md)；首次查看完整形态时再读取 [company-json-example.json](references/company-json-example.json)。需要初始化或验证本地成果时使用本 Skill 的 `scripts/`。

## 输入

- 国家/地区、语言、GETO 产品范围、研究截止日 `asOf`。
- 业务目标、结果范围 `full|sample`、可选种子与排除项。
- 是否启用 TradeWind、网易外贸通、竞对反查和签约前风险。
- 用户关心的市场问题、希望重点深入的方向和允许纳入的公开信号范围；未指定时按共享研究情报合同执行。
- 工作空间根目录；缺省使用用户指定的项目工作区，不把密钥或完整任务 trace 写入其中。

## 主任务工作流

### 1. Intake 与初始化

确认国家、产品、时间、样本边界和交付语言。读取 `$geto-capability-foundation` 取得产品、场景、竞争面和 SearchLexicon 切片。

运行：

```bash
python scripts/init_company_workspace.py --workspace-root '<ResearchBundle>' \
  --country-code '<ISO2>' --country-name '<English Display Name>'
```

在 `<国家>/progress.md` 记录研究范围、核心市场问题、固定检查点和待创建任务，并初始化产品×角色×来源覆盖矩阵、候选总账和研究前沿。研究前沿记录已确认模式、值得深挖的路径、新关联对象、开放问题和当前 AI 判断。若用户尚未明确授权创建用户可见任务，先征求一次授权。一级工作使用用户可见任务，subagent 仅用于单任务内部并行。

### 2. 创建用户可见发现任务

至少分别创建六个 Web 发现任务：

1. `developer`
2. `main_contractor`
3. `subcontractor`
4. `agent_consultant_pm`
5. `distributor_trading`
6. `design_consulting_supervision_other`

竞对候选发现按产品/技术面和商业角色另行拆分。TradeWind 与网易外贸通启用时各创建一个独立任务。每个任务保存准确标题、taskId、parentTaskId、queryBoundary、成果路径和唯一 sectionName。使用 Codex 的任务创建、等待、读取和追问能力协调；`progress.md` 保存业务进度，完整 trace 保留在各自任务中。

TradeWind 任务在第一次 Agentic submit 前必须接收完整用户产品范围、六类角色、竞对产品面、结果模式和排除项，并按 `$tradewind-api` 的 Agentic Search Plan 合同回传产品×角色×意图覆盖矩阵和 task 清单。主任务先检查每个在范围产品、角色和 lead/competitor 意图已 planned 或有明确 excluded 理由，再批准 pilot。用户范围包含多个产品面时，只有一条产品线的计划必须退回补齐；不得把一个宽泛 Agentic keyword 当作 Provider 覆盖完成。pilot 的国家、角色、产品命中、漂移、重复和分页未验收前，不批准 scale 批量提交。

### 3. 收集统一任务回传

每个任务必须回传：做了什么、找到了什么、成果路径、接受/拒绝理由、AI 当前结论、信息边界、值得继续展开的关联对象与下一步，以及官网、社媒、项目、外部交叉和 Provider 的覆盖边界。Agentic Provider 任务另回传 plan 路径、coverageMatrix 状态、每个 taskKey/taskId 的阶段、pilot 验收、跨任务去重和漂移。每个任务以唯一 sectionName 调用 `merge_progress.py` 合并自己的区块，再向 parentTaskId 发送精简 callback；callback 不可用时在 final 标记 callback_failed。主任务主动等待并读取每个任务 final，同时验证成果文件存在、结构可读和 validator 结果；不能用 progress.md 代替 final，也不能用 final 或 validator 代替研究审校。任务仍在运行时继续协调，不以“已创建”或“正在运行”作为阶段完成。

主任务每回收一批结果都更新研究前沿：跨公司去重反复出现的项目、系统、客户、供应商、渠道和人员；选择最可能增加市场理解或改变主要结论的路径继续派发。新对象不自动全部建档，按信息价值、业务相关性、当前性和可研究性排序。

### 4. 主体归一与分类仲裁

只用法定注册号、已确认稳定官网域名等强身份锚点自动去重。名称相似、共同地址、集团关系或项目共现只能标记冲突，不能自动合并。所有召回对象继续保留在候选总账，由主任务记录身份、背调、分类、评分和导入状态。

对每家公司按 [classification-and-engagement-contract.md](references/classification-and-engagement-contract.md) 独立执行 Lead Gate 与 Competitor Gate。同一公司只有在两个 Gate 各有独立 Evidence 时才双分类；泛化合作、产能互补或联合供货写入关系、风险和建议行动，不自动形成 lead。公司名称和关键词只用于召回。竞对判定必须核查官网 Products、Services、Solutions、Manufacturing、Factory、Rental、Distribution、Projects 和 About，并确认产品/市场重叠与商业控制或渠道控制。installer/service_contractor-only 必须拒绝 competitor；自有品牌/系统即使委外生产仍可能确认；经销、转售、出租竞品属于渠道竞对。

### 5. 一家公司一个背调任务

为每个入选 Company 创建独立用户可见背调任务。输入包含自然公司名、强身份锚点、发现来源、目标国家/产品、开放问题和禁止重复查询清单。已知或候选竞对也一家公司一个任务，使用 `$geto-diligence-competitor` 核查产品商业控制、制造履约、目标市场、官方项目和具名客户候选。竞对客户关系或组合需要研究时，为该竞对创建独立 `$geto-mine-competitor-customers` 任务；组合完整度不影响已确认竞对的公司级结论。

单公司任务写入：

```text
<国家>/companies/<公司自然名称>/company.json
<国家>/companies/<公司自然名称>/report.md
```

模块目录只在有真实内容时创建。

### 5.1 主编审校、研究扩展与退回

单公司任务完成后，主任务必须按 [diligence-review-contract.md](references/diligence-review-contract.md) 独立审校，而不是直接采纳 final。审校同时检查信息面是否足够广、深挖路径是否合理、重要发现是否继续扩展、不同强度来源是否正确使用、AI 推理和结论是否由 Evidence 支持，以及主体/JV/历史边界、当前性、分类与工件是否一致。

只对会显著影响强身份、客户关系、buyer/payer、当前机会、财务主体、Lead/Competitor 或重大风险的结论做定向反向核查；不要把每家公司变成无边界的证伪任务。发现有价值的新节点时，主任务可以要求原任务补查，或把新公司、项目或关系加入研究前沿和下一批任务。

主任务把审查写入 `<公司目录>/Additional/diligence-review.json` 并运行：

```bash
python scripts/validate_diligence_review.py \
  '<公司目录>/Additional/diligence-review.json'
```

`returned_for_followup` 必须把可能实质增加信息或改变结论的可执行问题发回原单公司任务并持续等待更新；不得由主任务用猜测补齐。`accepted|accepted_with_gaps` 表示本地研究在声明边界内达到充分状态，可以进入分类定稿和可选评分。validator 通过只证明数据合同有效，不能替代研究充分性审查；评分或 OmniX 准备不是本地验收通过的必要条件。

### 6. 跨公司综合、评分、关系与风险

主任务在评分之前先形成国家级综合：市场结构、主要角色、产品使用与竞争面、项目和采购模式、反复出现的关系节点、当前与长期机会、风险、信息边界和 AI 结论。综合必须可追溯到公司和关系 Evidence；不能只汇总数量、状态或分数。

- `$geto-find-leads` 在主任务收齐已通过研究充分性审校的单公司 observedScore/Evidence 后，按国家×同类型角色生成 cohort baseline，并以同一 baselineVersion 批量计算或重算长期客户价值。
- cohort 收口必须同步 `missingInformation[]`：完成六维评分且有总分时删除且仅删除旧迁移主题 `lead_assessment_contract_incomplete`；评分未完成时，该主题只能准确描述缺失维度、cohort 或模型状态，不得套用身份仲裁文案。真实身份、付款、项目、Provider 或证据缺口保持独立条目。
- `$geto-mine-competitor-customers` 只对 verified_customer 复用上述长期价值结果，聚合竞对客户价值平均分和评分覆盖率，并为每条关系保留 0–5 合作切入分。
- 有明确原始询盘时使用 `$geto-diligence-inquiry` 生成不依赖 cohort 的询盘准备度；它不替代长期客户价值。
- `$geto-map-relationships` 只对已归一公司/项目建立 typed Relationship。
- `$geto-assess-precontract-risk` 仅在具体交易、签约主体和条款已明确时运行。

### 7. 本地验证

逐公司生成来源索引并校验：

```bash
python scripts/build_deduplicated_sources.py '<公司目录>/company.json'
python scripts/validate_company_json.py '<公司目录>/company.json'
python scripts/validate_workspace.py --company-dir '<公司目录>'
python scripts/validate_workspace.py '<国家目录>'
```

单公司任务只运行 `--company-dir` 模式；国家主任务运行国家模式。任何 ERROR 必须修复后再交付或上传；WARNING 必须处置或写入 `missingInformation`/`progress.md`，INFO 保留为查询覆盖说明。validator 默认输出 INFO 分类计数，使用 `--include-infos` 查看逐条明细。评分任务还会核对标准能力工件与 assessment。每家公司的 diligence review 必须为 `accepted|accepted_with_gaps`。结构校验不能替代信息广度、深度、AI 结论与中文可读性审校。固定检查点为 `intake`、`discovery`、`research_frontier`、`arbitration`、`diligence`、`review`、`decision`、`synthesis`、`validation`、`local_complete`；只有用户明确要求 OmniX 时再增加 `optional_upload`。

### 8. 可选 OmniX 上传

只有用户在当前任务中明确要求上传、同步、发布或管理 OmniX 时，才询问 Base URL/API Key 是否已安全配置以及使用 `private` 还是 `public`，并调用 `$omnix-market`。用户未提出 OmniX 时，记录 `uploadStatus=not_requested`，不索取 Key、不追加上传确认，也不让平台契约改变本地研究完成状态。

private/public 均要求注册号或已确认稳定官网域名等强身份。上传投影保留 competitorCustomerPortfolio、assessment.capabilityContext、projects[].participants、relationships[].exclusivity 和内嵌 Evidence；inquiryAssessment、researchQueries、reportFiles、报告和工作空间路径保存在本地。public 以整个 Aggregate 为可见单元。active lead 在同类型 cohort 完成评分后进入 lead 投影，scoring criteria hash 由 `$omnix-market` 自动读取并注入；confirmed competitor 可独立进入 competitor 投影，competitorCustomerPortfolio 可以缺省、待评分、部分覆盖或完成。

创建或更新后在 `progress.md` 记录 `uploadStatus=not_requested|not_configured|uploaded_private|uploaded_public|updated_private|updated_public|blocked_public_duplicate|failed` 和平台返回的 detailRoute；不得记录 API Key。逐家详情回读后，还要调用真实 lead/competitor 列表过滤接口验证 active 分类成员，确保 rejected 分类不进入对应列表。前端直接消费列表 items 时，以同一路径的真实响应验证展示数据；没有该层证据时不宣告可供用户 review。软删除与恢复只在当前任务回传结果中说明。

## 完成条件

- 六个角色发现任务及已启用 Provider 的独立任务都有回传和成果路径。
- 启用 TradeWind Agentic 时，计划覆盖矩阵的所有非 excluded 单元已 completed，或 sample 模式的停止条件已达到；单个 task 完成不能替代计划完成。
- 每个评分公司可追溯到独立背调任务、自然名称目录、`company.json` 与 `report.md`。
- 每个完成背调的公司都有主任务生成且通过校验的 `Additional/diligence-review.json`；退回问题已由原任务回答，或被明确接受为有边界的缺口。
- 任务相关的主要信息面已有结果或明确边界，高价值路径已经深挖，重要发现引出的下一跳已处理、纳入候选总账或说明暂缓理由。
- 公司与国家报告以自然中文呈现事实、关键信号、AI 推理、AI 结论、不确定性和继续研究方向；不得用“待人工判断”代替 AI 分析。
- 主任务已经完成跨公司综合，能够解释市场结构、项目与采购模式、主要机会、竞争面、风险和结论，而不只是罗列公司与分数。
- lead/competitor 分类、接受/拒绝理由、冲突与查询边界没有在合并中丢失。
- 产品×角色×来源覆盖矩阵和候选总账能解释全部召回、拒绝、背调、评分与导入对象。
- `Sources/sources.md` 已由内嵌 Evidence 去重生成，工作空间验证无 ERROR。
- 用户明确要求 OmniX 时，详情回读与真实分类列表查询均符合 active 分类集合；未要求时，本地完成不依赖 OmniX。
- 中断后可仅依靠 `progress.md`、成果路径和用户可见任务 trace 恢复。
