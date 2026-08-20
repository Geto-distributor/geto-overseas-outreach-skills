# GETO AI+海外营销 Skills V2 重构进度

## 范围

- 设计基线：REV/ADR/FIELDS/SKILLS 与 GET-154、GET-155、GET-156、GET-159。
- 代码范围：GETO Skills、OmniX Market Skill、网易外贸通交接、安装目录内 TradeWind 交接。
- 非范围：OmniX API/UI 仓库。

## 完成情况

| 工作项 | 状态 | 主要产物 |
| --- | --- | --- |
| 用户可见任务编排与统一回传 | completed | `skills/geto-run-market-research/SKILL.md`、`references/orchestration.md` |
| ResearchBundle 字段与目录 | completed | `references/company-json-contract.md`、`scripts/init_company_workspace.py` |
| company.json 与工作空间验证 | completed | `scripts/validate_company_json.py`、`scripts/validate_workspace.py`、`scripts/research_bundle.py` |
| 内嵌 Evidence 来源去重 | completed | `scripts/build_deduplicated_sources.py` |
| SearchLexicon 与 VMC/角色词 | completed | `skills/geto-capability-foundation/references/search-lexicon.json`、`scripts/validate_search_lexicon.py` |
| 竞对商业控制与误判门禁 | completed | `skills/geto-mine-competitor-customers/`、company validator 回归 |
| Freecity/Electron 夹具 | completed | `tests/fixtures/freecity-company.json`、`tests/fixtures/electron-company.json` |
| OmniX 无版本 Company Aggregate | completed | `../omnix-market-skill/SKILL.md`、`scripts/omnix_market.py`、新 OpenAPI fixture/tests |
| Provider 独立任务交接 | completed | `../omnix-netease-waimao-skill/SKILL.md`、安装目录 `tradewind-api` |
| 安装目录同步 | completed | `/Users/huangzhenxi/.codex/skills/geto-*`、`omnix-market`、`netease-waimao`、`tradewind-global-trade-company-people-search` |
| 四家公司实测反馈收口 | completed | `lead-value-model.json`、`calculate_lead_assessment.py`、严格 assessment/reportFiles 校验 |
| 查询覆盖与严重级别 | completed | `researchQueries[]`；not_queried/no_result=INFO，failed/conflicting=WARNING |
| 单公司责任边界 | completed | `validate_workspace.py --company-dir` |
| 并发与原子写入 | completed | `merge_progress.py`、`write_company_json.py` |
| 国家与 CapabilityContext | completed | `<ISO2>-<English-Display-Name>`、`contextRef` 固定合同 |
| 来源和内容单一事实源 | completed | 同 URL 聚合 locators；company.json 权威，report/module 为派生或扩展内容 |
| 跨 Skill 脚本定位 | completed | 单公司文档显式使用 `<geto-run-market-research-dir>/scripts/...` |
| 显式能力切片与报告枚举 | completed | 显式 product/scenario/role codes 优先；reportFiles 枚举写入合同 |
| 评分事实锚点 | completed | 六维 components/factAnchors、A/B/C/U evidenceGradeRules 与时效边界 |
| 能力工件闭环 | completed | selector `--output`、固定 sidecar 路径、validator 逐字段一致性检查 |
| INFO 汇总视图 | completed | 默认输出分类计数，`--include-infos` 输出逐条明细 |
| Provider 联系人桥接 | completed | email_only + workEmail.deliverability 证据范围；任职/授权独立补证 |
| 长期价值评分时序 | completed | 单公司观察输入 → 主会话同类型 cohort 中位数 → 同版本批量回写 |
| 独立询盘背调 | completed | `geto-diligence-inquiry` 固定准备度评分，不使用 cohort 插补 |
| 询盘字段自包含 | completed | inquiry Skill 自带完整 Company 子资源合同，并与公司 Skill 做逐字一致性回归 |
| 深度报告与项目深挖 | completed | 18 类报告主题、项目发现瀑布流、项目角色三层证明与稀疏项目覆盖校验 |
| 单竞对深度背调 | completed | `skills/geto-diligence-competitor/`；主体、产品商业控制、制造、项目与客户候选独立合同 |
| 竞对客户组合与切入口径 | completed | `competitorCustomerPortfolio`、`GETO_RELATIONSHIP_ENTRY 1.0`、`aggregate_competitor_customers.py` |
| ResearchBundle 与 OmniX 投影边界 | completed | 本地为事实主合同；inquiryAssessment、researchQueries、reportFiles 与报告保存在本地 |
| Company 字段示例 | completed | 全字段无空值 `references/company-json-example.json`、确定性生成器、询盘 `references/inquiry-example.md`、OmniX 全字段 Aggregate JSON |
| Company 字段必填性合同 | completed | `references/company-field-requirements.md`；R/S/C/O、全部子资源、评估状态和工作空间条件 |
| Evidence 来源合同 | completed | Evidence 只含来源元数据；业务 item 承载状态、冲突和拒绝理由 |
| 项目与关系结构 | completed | `projects[].participants[]`、`relationships[].limitations[]`、exclusivity 状态对象 |
| OmniX 上传门禁 | completed | private/public 强身份、自动 scoring criteria hash、运行时 Aggregate schema capability 检查 |
| OmniX 最终投影适配 | completed | API `b74b422`、UI `76254f5`；逐资源字段映射、组合/评分前置门禁与冻结 fixture |

## 验证

- GETO 仓库 validator：9 Skills passed。
- skill-creator quick_validate：9 个 GETO Skills、omnix-market、netease-waimao、tradewind-api 均 passed。
- GETO ResearchBundle/SearchLexicon/cohort/询盘/竞对客户组合/关系切入/字段必填性与报告合同/并发/能力工件回归：35 tests passed。
- OmniX unversioned API 合同、强身份、显式字段投影、评分 hash、Capability Context 与完整 Aggregate 示例回归：21 tests passed。
- 网易外贸通既有安全回归：11 tests passed。
- Freecity、Electron company.json：均 0 ERROR / 0 WARNING。
- ResearchBundle 端到端 smoke：规范国家目录 init → 单公司 validate → 国家 validate，均 0 ERROR / 0 WARNING / 0 INFO。
- CapabilityContext：真实产品 code 切片返回 available contextRef，固定版本与 codes 完整。
- 四家公司第二轮当前合同产物：合计 0 ERROR / 2 真实 WARNING / 59 INFO；国家目录、严格 assessment/reportFiles、精确 contextRef、Sources 与并发 progress 全部通过。
- 长期价值当前规则：四家公司单独背调只保留 observedScore/Evidence；同类型 cohort 每个维度达到 5 家后，由主任务统一生成可比较的最终分。
- 询盘当前规则：四条询盘使用 `geto-diligence-inquiry` 的固定 readiness 口径单独评分，不等待 cohort。
- 第三轮契约工件烟测：四份标准 sidecar 均位于 `RisksAndAssessment/capability-context.json`，与 assessment 逐字段一致且无重复/空目录；四份 company.json 哈希未变。
- INFO 汇总烟测：四家公司默认均 `infos=[]` 且分类计数正确；Proas 使用 `--include-infos` 完整展开 16 条，开关通过。
- 询盘时序终验：四条 inquiry readiness 分别为 43、42、40、46，均为 nurture_or_verify；四个长期价值 cohort 各 1 家，全部 pending_cohort_baseline 且无临时总分。
- 深度报告终验：四份报告均 18 个 H2、157–173 行；项目数 3/1/2/0，项目不足 3 个的报告均包含完整项目检索覆盖表。
- Provider 载荷终验：TradeWind 根层 people[5] 与嵌套 meta 分页矛盾已输出 not_exhaustive + pagination_metadata_inconsistent。
- 竞对职责终验：单竞对 Skill 只输出竞对事实与分类；竞对客户 Skill 复用客户六维 cohort 分，按去重客户聚合平均分和覆盖率，并在关系层单列 0–5 切入分。
- 竞对组合烟测：2 个 verified_customer 中 1 个具有 completed 客户价值分时，输出 partial_coverage、覆盖率 0.5、均分仅取已评分客户；缺分客户未补零。
- 完整示例烟测：本地 `company-json-example.json` 的所有顶层资源和三个评估对象均有合成实例，递归扫描无 null、空字符串、空数组或空对象，validator 为 0 ERROR / 0 WARNING / 0 INFO；投影后的 `company-aggregate-example.json` 同样无空值且 OpenAPI schemaErrors=[]。
- credential/private artifact scan：passed。
- `git diff --check`：passed。
- GitHub PR checks：workflow 未分配 runner，检查注释为组织账户付款失败或 spending limit 不足；本地等价命令全部 passed，账户恢复后需 rerun checks。

## 仍需主任务协调

- GET-158 新 API 部署后，用实际 OpenAPI/Base URL/API Key 执行联调；当前只完成 Skill 与冻结 OpenAPI fixture 合同验证。
- API/UI 最终 commits 已覆盖 CompanyContent、CapabilityContext、participants、exclusivity、强身份、marketCode/scopeCode 及展示合同；主任务回传 API 13/13、UI 56/56、Mock E2E 13/13、真实全栈 E2E 8/8 均通过。
- 源仓库已有未跟踪文件 `skills/geto-find-leads/references/lead-assessment-contract 2.md`，本次未修改；安装目录未包含该旧副本。
