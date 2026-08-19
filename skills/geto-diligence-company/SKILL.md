---
name: geto-diligence-company
description: 对 GETO 海外市场中的单一目标公司执行深度背调，输出自然公司名目录、company.json、内嵌 Evidence、按需模块资料与 report.md，并可在背调后按 assessmentMode 生成六维客户价值评估。用于一家公司一个独立任务的线索或竞对背调、主体冲突和询盘核查；不负责广泛找公司、跨公司排名或直接上传 OmniX。
---

# GETO 单公司背调

一次只研究一个 Company。法定主体、经营公司和企业集团分别建模；CommercialAccount 不另建重复主体。

开始前读取 [evidence-contract.md](references/evidence-contract.md) 与 [child-resources.md](references/child-resources.md)。需要六维评分时再读 [lead-assessment-contract.md](references/lead-assessment-contract.md)。

## 输入

- 自然公司名及至少一个锚点：稳定官网域名、法定名称、注册号或明确所在国。
- 目标国家、GETO 产品范围、发现来源、开放问题、研究截止日。
- `assessmentMode=none|lead_value`，缺省 `none`。
- 禁止重复查询清单和目标公司目录路径。

主体可能指向多个实体时输出 `researchStatus=identity_conflict`，不得混合事实。

## 工作流

### 1. 初始化公司目录

调用 `$geto-run-market-research` 的工作空间脚本创建：

```bash
python scripts/init_company_workspace.py --workspace-root '<ResearchBundle>' \
  --country-code '<ISO2>' --country-name '<English Display Name>' \
  --company-name '<自然公司名>'
```

国家目录固定为 `<ISO2>-<English-Display-Name>`。`company.countryCode` 保存 ISO2，`company.country` 保存统一展示名。

只在获得真实内容时创建 `Info/`、`Financial/`、`ProductsAndServices/`、`Projects/`、`NewsAndSocialMedia/`、`CustomsTransactions/`、`LawsuitsAndCompliance/`、`Inquiries/`、`RisksAndAssessment/` 或 `Additional/`。

### 2. 主体与强身份核验

核对官网主域名、法定登记、注册号、地址、别名和集团关系。仅强身份一致时自动合并；名称相似、共同地址、品牌相近或共同项目不得自动合并。注册资本与实缴资本写入 `capitalRecords`，不得解释为现金、收入、净资产或信用能力。

### 3. Web 定向背调

至少核查官网 About、Products、Services、Solutions、Manufacturing、Factory、Rental、Distribution、Projects、News；并按任务范围查询登记、股权、财务、资质、诉讼监管、负面新闻、联系人、项目和经营信号。

### 4. Provider 补强

TradeWind 和网易外贸通只作为独立 Provider 任务返回的 ExternalObservation。需要补查时向对应用户可见任务追问或创建该 Provider 专用任务。在 `researchQueries[]` 保留 topic、channel、query、scope、status、checkedOn、resultCount 和 Evidence。`not_queried`、已查无结果和失败分别记录；Provider 结果不能覆盖法定主体或官网一手事实。

### 5. 写入内嵌 Evidence

把事实写入 `company.json` 对应 item，每个主要列表 item 自带 `evidence[]`。Evidence 关系只用 `supports|refutes|context`；冲突来源全部保留，不以数量投票。最终从全部内嵌 Evidence 生成 `Sources/sources.md`。

### 6. 产品商业角色与竞对事实

对每个相关产品/服务写入 `commercialRoles[]`、`manufacturingStatus`、`manufacturingDescription`、`factoryLocations[]` 与 Evidence。名称含 framework、formwork、modular 只能作为召回线索：

- manufacturer/system_owner/brand_owner 且产品和市场重叠：可支持直接竞对；
- distributor/reseller/rental_provider 且经营竞品：可支持渠道竞对；
- installer/service_contractor-only：不得确认为竞对；
- contract_manufacturer-only 且不独立销售：不自动确认为竞对；
- outsourced 但拥有并销售自有品牌/系统：仍可能是竞对；
- 商业控制或生产状态不清：分类保持 possible 并列入缺口。

### 7. 独立 Lead/Competitor 分类

在 `researchClassifications[]` 分别写 lead 和 competitor；两者互不排斥，不使用 both。每条必须包含 country、productScope、status、reason 与 Evidence。`companyRoles[]` 只写开发商、总包、分包、顾问、经销贸易等市场角色。

### 8. 可选评分与报告

`assessmentMode=lead_value` 时，使用 [lead-value-model.json](references/lead-value-model.json) 与能力底座 `contextRef`。先填写六维观察分、证据等级与 Evidence，再运行 `scripts/calculate_lead_assessment.py`；脚本按门禁生成明确状态、总分和等级。评分不改变 competitor 分类。

`company.json` 是事实与评估的唯一权威结构化来源；`report.md` 是由它组织的可读结论。模块 Markdown 仅保存原始材料、查询日志或扩展分析，按实际内容创建，不手工维护第二份事实表。

生成 `report.md`，并按固定字段 `fileName/path/format/reportType/language/generatedOn/description` 写入 `reportFiles[]`。用 `write_company_json.py` 校验并原子替换完整 JSON，再运行来源聚合与单公司校验：

```bash
python scripts/build_deduplicated_sources.py '<公司目录>/company.json'
python scripts/validate_workspace.py --company-dir '<公司目录>'
```

修复 ERROR；WARNING 表示需处理的风险或冲突，INFO 表示如实记录的未查询或已查无结果。

## 任务回传

结束时向主任务回传：做了什么、主要发现、公司目录与报告路径、lead/competitor 接受或拒绝理由、身份/证据冲突、未完成缺口、建议下一步。主任务在本地验证后决定是否上传 OmniX。
