---
name: geto-run-market-research
description: 编排 GETO 海外市场的一次完整或定向调研，以当前用户任务为主任务，按公司角色、Provider 和单公司背调创建用户可见任务，维护国家 progress.md 与本地 ResearchBundle，并在验证通过后可选上传 OmniX。用于国家/地区市场调研、销售线索池、竞对客户挖掘或多模块研究。
---

# GETO 海外市场情报总编排

## 目标与边界

把当前国家调研任务作为主任务。用用户可见的独立任务承载角色发现、Provider 查询和逐公司背调；subagent 只允许在单个任务内部并行。主任务维护人可直接浏览的 ResearchBundle，不依赖 OmniX 完成研究。

开始前读取 [orchestration.md](references/orchestration.md) 与 [company-json-contract.md](references/company-json-contract.md)。需要初始化或验证本地成果时使用本 Skill 的 `scripts/`。

## 输入

- 国家/地区、语言、GETO 产品范围、研究截止日 `asOf`。
- 业务目标、结果范围 `full|sample`、可选种子与排除项。
- 是否启用 TradeWind、网易外贸通、竞对反查和签约前风险。
- 工作空间根目录；缺省使用用户指定的项目工作区，不把密钥或完整任务 trace 写入其中。

## 主任务工作流

### 1. Intake 与初始化

确认国家、产品、时间、样本边界和交付语言。读取 `$geto-capability-foundation` 取得产品、场景、竞争面和 SearchLexicon 切片。

运行：

```bash
python scripts/init_company_workspace.py --workspace-root '<ResearchBundle>' \
  --country-code '<ISO2>' --country-name '<English Display Name>'
```

在 `<国家>/progress.md` 记录研究范围、固定检查点和待创建任务。若用户尚未明确授权创建用户可见任务，先征求一次授权。一级工作使用用户可见任务，subagent 仅用于单任务内部并行。

### 2. 创建用户可见发现任务

至少分别创建六个 Web 发现任务：

1. `developer`
2. `main_contractor`
3. `subcontractor`
4. `agent_consultant_pm`
5. `distributor_trading`
6. `design_consulting_supervision_other`

竞对发现按产品/技术面和商业角色另行拆分。TradeWind 与网易外贸通启用时各创建一个独立任务。使用 Codex 的任务创建、等待、读取和追问能力协调；`progress.md` 保存业务进度，完整 trace 保留在各自任务中。

### 3. 收集统一任务回传

每个任务必须回传：做了什么、找到了什么、成果路径、接受/拒绝理由、缺口、下一步。每个任务以唯一 sectionName 调用 `merge_progress.py` 合并自己的区块；文件锁与原子替换保证并发写入互不覆盖。主任务保留查询边界和 Provider 状态。

### 4. 主体归一与分类仲裁

只用法定注册号、已确认稳定官网域名等强身份锚点自动去重。名称相似、共同地址、集团关系或项目共现只能标记冲突，不能自动合并。

对每家公司独立执行 Lead Gate 与 Competitor Gate；同一公司可同时拥有一条 lead 和一条 competitor 分类。公司名称和关键词只用于召回。竞对判定必须核查官网 Products、Services、Solutions、Manufacturing、Factory、Rental、Distribution、Projects 和 About，并确认产品/市场重叠与商业控制或渠道控制。installer/service_contractor-only 必须拒绝 competitor；自有品牌/系统即使委外生产仍可能确认；经销、转售、出租竞品属于渠道竞对。

### 5. 一家公司一个背调任务

为每个入选 Company 创建独立用户可见背调任务。输入包含自然公司名、强身份锚点、发现来源、目标国家/产品、开放问题和禁止重复查询清单。竞对也一家公司一个任务，并重点核查官方项目、具名客户和合作方。

任务使用 `$geto-diligence-company` 写入：

```text
<国家>/companies/<公司自然名称>/company.json
<国家>/companies/<公司自然名称>/report.md
```

模块目录只在有真实内容时创建。

### 6. 评分、关系与风险

- `$geto-find-leads` 聚合已完成单公司背调后的六维评分，不重新计算单公司结果。
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

单公司任务只运行 `--company-dir` 模式；国家主任务运行国家模式。任何 ERROR 必须修复后再交付或上传；WARNING 必须处置或写入 `missingInformation`/`progress.md`，INFO 保留为查询覆盖说明。validator 默认输出 INFO 分类计数，使用 `--include-infos` 查看逐条明细。评分任务还会核对标准能力工件与 assessment。固定检查点为 `intake`、`discovery`、`arbitration`、`diligence`、`decision`、`validation`、`optional_upload`、`complete`。

### 8. 可选 OmniX 上传

仅在本地验证通过后询问用户：是否上传、Base URL/API Key 是否已安全配置、上传为 `private` 还是 `public`。用户同意后调用 `$omnix-market` 的单一无版本 Company Aggregate API。没有 OmniX 或用户不上传不阻断研究完成。

在 `progress.md` 记录 `uploadStatus=not_requested|not_configured|uploaded_private|uploaded_public|blocked_public_duplicate|failed` 和平台返回的 detailRoute；不得记录 API Key。

## 完成条件

- 六个角色发现任务及已启用 Provider 的独立任务都有回传和成果路径。
- 每个评分公司可追溯到独立背调任务、自然名称目录、`company.json` 与 `report.md`。
- lead/competitor 分类、接受/拒绝理由、冲突与查询边界没有在合并中丢失。
- `Sources/sources.md` 已由内嵌 Evidence 去重生成，工作空间验证无 ERROR。
- 中断后可仅依靠 `progress.md`、成果路径和用户可见任务 trace 恢复。
