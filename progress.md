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

## 验证

- GETO 仓库 validator：7 Skills passed。
- skill-creator quick_validate：7 个 GETO Skills、omnix-market、netease-waimao、tradewind-api 均 passed。
- GETO ResearchBundle/SearchLexicon/评分/并发/能力工件回归：19 tests passed。
- OmniX unversioned API 合同回归：9 tests passed。
- 网易外贸通既有安全回归：11 tests passed。
- Freecity、Electron company.json：均 0 ERROR / 0 WARNING。
- ResearchBundle 端到端 smoke：规范国家目录 init → 单公司 validate → 国家 validate，均 0 ERROR / 0 WARNING / 0 INFO。
- CapabilityContext：真实产品 code 切片返回 available contextRef，固定版本与 codes 完整。
- 四家公司第二轮当前合同产物：合计 0 ERROR / 2 真实 WARNING / 59 INFO；国家目录、严格 assessment/reportFiles、精确 contextRef、Sources 与并发 progress 全部通过。
- 第二轮评分：Estudio 28.5/watch；Proas incomplete_evidence、score/grade=null；Arnold's House 25.75/watch；沙特客户 12.5/watch。
- 第三轮契约工件烟测：四份标准 sidecar 均位于 `RisksAndAssessment/capability-context.json`，与 assessment 逐字段一致且无重复/空目录；四份 company.json 哈希未变。
- INFO 汇总烟测：四家公司默认均 `infos=[]` 且分类计数正确；Proas 使用 `--include-infos` 完整展开 16 条，开关通过。
- credential/private artifact scan：passed。
- `git diff --check`：passed。

## 仍需主任务协调

- GET-158 新 API 部署后，用实际 OpenAPI/Base URL/API Key 执行联调；当前只完成 Skill 与冻结 OpenAPI fixture 合同验证。
- GET-160/GET-161 需要 API/UI 主任务验证 detailRoute、public 强身份冲突、软删除/恢复和双用户可见性。
- 源仓库已有未跟踪文件 `skills/geto-find-leads/references/lead-assessment-contract 2.md`，本次未修改；安装目录未包含该旧副本。
