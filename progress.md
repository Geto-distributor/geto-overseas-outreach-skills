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

## 验证

- GETO 仓库 validator：7 Skills passed。
- skill-creator quick_validate：7 个 GETO Skills、omnix-market、netease-waimao、tradewind-api 均 passed。
- GETO ResearchBundle/SearchLexicon 回归：10 tests passed。
- OmniX unversioned API 合同回归：9 tests passed。
- 网易外贸通既有安全回归：11 tests passed。
- Freecity company.json：0 ERROR / 0 WARNING。
- Electron company.json：0 ERROR / 1 expected WARNING（签约/付款主体冲突缺口）。
- ResearchBundle 端到端 smoke：init → build sources → validate workspace passed。
- credential/private artifact scan：passed。
- `git diff --check`：passed。

## 仍需主任务协调

- GET-158 新 API 部署后，用实际 OpenAPI/Base URL/API Key 执行联调；当前只完成 Skill 与冻结 OpenAPI fixture 合同验证。
- GET-160/GET-161 需要 API/UI 主任务验证 detailRoute、public 强身份冲突、软删除/恢复和双用户可见性。
- 源仓库已有未跟踪文件 `skills/geto-find-leads/references/lead-assessment-contract 2.md`，本次未修改；安装目录未包含该旧副本。

