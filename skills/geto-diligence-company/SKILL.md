---
name: geto-diligence-company
description: 对 GETO 海外市场中的单一线索或普通目标公司执行广泛且有重点的深度背调，沿公司、项目、产品、人员和供应链继续扩展信息，综合权威来源、交易对手、行业资料、Provider 与开放信号，输出中文本地 ResearchBundle、可追溯 Evidence、AI 推理和明确结论。用于一家公司一个独立任务的客户事实核查与主体冲突处理；原始询盘使用 geto-diligence-inquiry，已知竞对使用 geto-diligence-competitor。
---

# GETO 单公司背调

一次只研究一个 Company。法定主体、经营公司和企业集团分别建模；CommercialAccount 不另建重复主体。

开始前读取 [evidence-contract.md](references/evidence-contract.md)、[child-resources.md](references/child-resources.md)，以及 `$geto-run-market-research` 的 `references/research-intelligence-contract.md`、`references/classification-and-engagement-contract.md` 与 `references/diligence-review-contract.md`。构造或复核 company.json 时读取 `$geto-run-market-research` 的 `references/company-field-requirements.md`；首次查看完整形态时读取其 `references/company-json-example.json`。需要六维评分时再读 [lead-assessment-contract.md](references/lead-assessment-contract.md)。

## 输入

- 自然公司名及至少一个锚点：稳定官网域名、法定名称、注册号或明确所在国。
- 目标国家、GETO 产品范围、发现来源、开放问题、研究截止日。
- 用户已提出的市场问题和希望重点深入的方向；未指定时由初步广度扫描生成研究议程。
- `assessmentMode=none|lead_value`，缺省 `none`。
- 禁止重复查询清单和目标公司目录路径。

主体可能指向多个实体时输出 `researchStatus=identity_conflict`，不得混合事实。

## 工作流

### 1. 初始化公司目录

调用 `$geto-run-market-research` 的工作空间脚本创建：

```bash
python '<geto-run-market-research-dir>/scripts/init_company_workspace.py' \
  --workspace-root '<ResearchBundle>' \
  --country-code '<ISO2>' --country-name '<English Display Name>' \
  --company-name '<自然公司名>'
```

国家目录固定为 `<ISO2>-<English-Display-Name>`。`company.countryCode` 保存 ISO2，`company.country` 保存统一展示名。

只在获得真实内容时创建 `Info/`、`Financial/`、`ProductsAndServices/`、`Projects/`、`NewsAndSocialMedia/`、`CustomsTransactions/`、`LawsuitsAndCompliance/`、`Inquiries/`、`RisksAndAssessment/` 或 `Additional/`。

### 2. 主体与强身份核验

核对官网主域名、法定登记、注册号、地址、别名和集团关系。仅强身份一致时自动合并；名称相似、共同地址、品牌相近或共同项目不得自动合并。注册资本与实缴资本写入 `capitalRecords`，不得解释为现金、收入、净资产或信用能力，也不得写入 `financialRecords`。

### 3. 研究议程、广度扫描与重点深挖

先按共享研究情报合同建立主体、业务、项目、关系、人员触达、经营风险和信息生态七类研究议程。枚举官网顶部/页脚导航、项目/新闻/产品分页、下载目录、法律页、sitemap、robots 和站内搜索，再核查适用的 About、Products、Systems、Services、Solutions、Applications、Manufacturing、Factory、Rental、Distribution、Projects、Case Studies、Testimonials、News、Contact、Privacy/Terms 与 Downloads。记录发现栏目、已检查栏目、页数或列表项数量、不可访问页面和分页终点；只看首页或 About 不构成深度背调，但覆盖也不能停留在栏目打勾，必须记录取得的事实、信号和新对象。

枚举官网指向和公开检索可归一的官方社媒，先建立最近活动、数量/日期和分页边界，再优先检查与产品、工厂、项目、客户、招聘、经营变化和管理层有关的帖子；公开量可管理时逐页检查，数量过大或平台受限时记录实际检查数量、时间范围、选择方法和访问边界，不宣称穷尽。按任务范围查询登记、股权、财务、资质、诉讼监管、负面新闻、联系人、项目和经营信号。

尽量枚举官网和外部来源的项目池，区分当前、历史和未知。完成初步扫描后，选择最可能增加商业理解或改变主体、产品适配、机会、风险、Lead/Competitor 结论的重点路径深挖，并说明选择理由。每个被用于重要分类、评分或 AI 结论的项目必须打开详情并交叉 owner/developer、总包/JV、结构/模板分包、顾问、buyer、payer、actualUser、technical approver、阶段、数量、模板系统或供应商、租购/甲供边界与采购窗口。高优先级结论需要官网之外的独立证据或可核验的当前项目、招标、合同、监管披露或 Provider 观察；只有官网自述或历史项目时保留时态缺口和较低优先级。

每取得一项重要发现，都检查是否引出新的公司、项目、产品系统、供应商、客户、渠道、人员、主体冲突或研究问题。与本公司结论直接相关的继续下钻；值得独立建档的对象回传主任务；暂不展开但有价值的方向写入研究前沿。单公司任务不以无限扩张为目标。

### 4. Provider 补强

TradeWind 和网易外贸通只作为独立 Provider 任务返回的 ExternalObservation。需要补查时向对应用户可见任务追问或创建该 Provider 专用任务。在 `researchQueries[]` 保留 topic、channel、query、scope、status、checkedOn、resultCount 和 Evidence。`not_queried`、已查无结果和失败分别记录；Provider 结果不能覆盖法定主体或官网一手事实。

精确官网域名或法定名称锚定的人员 Observation 可以支持 `contacts[]` 的 Provider 验证范围；公开公司页或职业页用于确认全名、当前任职和职责。姓名掩码、雇主锚点不足或同名冲突不进入正式联系人。Provider 可支持触达路径，但 buyingRole、签字权、buyer、payer 和项目授权分别取证。人员 0 结果只表达当前 queryBoundary，应补官网、公开职业页或更宽名称边界。官网 Contact、页脚、办公室、项目咨询、供应商/投标、投资者关系等公司或部门入口与具名人员分开建模；Provider 没有具名人员不等于公司没有可用联系方式。

### 5. 写入内嵌 Evidence

把事实写入 `company.json` 对应 item，每个主要列表 item 自带 `evidence[]`。Evidence 保存来源信息；事实状态、冲突与拒绝理由写在所属业务 item。冲突来源全部保留，不以数量投票。最终从全部内嵌 Evidence 生成 `Sources/sources.md`。

财务补证必须把 `subjectEntity`、`scope`（兼容旧字段 `financialScope`）、`accountingScope`、`relationshipToTarget`、期间、币种/单位、`valueStatus` 和 Evidence 写入同一条 `financialRecords[]`。集团、母公司、品牌、JV、SPV 和业务分部数据允许登记，但必须保留真实报表主体和口径；实体不匹配时保留最权威记录并明确 mismatch，不得改名为目标法人单体。只有同一期间、主体、口径和币种的总资产与总负债才可派生资产负债率，并标为 `derived`。商业数据库只作为 `secondary_registry_derived`、`secondary_range` 等次级证据。财务补证 follow-up 复用同一 progress section，不重新创建国家任务。

### 6. 产品商业角色与分类事实

对每个相关产品/服务写入 `commercialRoles[]`、`manufacturingStatus`、`manufacturingDescription`、`factoryLocations[]` 与 Evidence。线索研究中发现竞对事实时仍按以下边界分类；需要系统产品对标与竞对客户研究时交给 `$geto-diligence-competitor`。名称含 framework、formwork、modular 只能作为召回线索：

- manufacturer/system_owner/brand_owner 且产品和市场重叠：可支持直接竞对；
- distributor/reseller/rental_provider 且经营竞品：可支持渠道竞对；
- installer/service_contractor-only：不得确认为竞对；
- contract_manufacturer-only 且不独立销售：不自动确认为竞对；
- outsourced 但拥有并销售自有品牌/系统：仍可能是竞对；
- 商业控制或生产状态不清：分类保持 possible 并列入缺口。

### 7. 独立 Lead/Competitor 分类

在 `researchClassifications[]` 分别写 lead 和 competitor；两者按共享分类合同独立取证，不使用 both。Lead 必须有采购、使用、选型影响或正式渠道路径；泛化合作、产能互补或联合供货写入关系、风险和建议行动。每条分类必须包含 country、productScope、status、reason 与 Evidence。`companyRoles[]` 只写开发商、总包、分包、顾问、经销贸易等市场角色。

### 8. 可选评分与报告

`assessmentMode=lead_value` 时，使用 [lead-value-model.json](references/lead-value-model.json) 的 components、factAnchors 和 evidenceGradeRules，并把能力底座直接 contextRef 保存到 `RisksAndAssessment/capability-context.json`。填写六维观察分、证据等级与 Evidence，再运行 `<geto-diligence-company-dir>/scripts/calculate_lead_assessment.py`，输出 pending_cohort_baseline 输入。总分和等级由国家主任务统一计算；公开检索完成且同角色中位数不可用时，cohort 基线使用 0 并标记对应 Evidence；`not_queried`、`provider_failed`、`identity_conflict` 仍保持未知。信息完整度与价值分分别展示。评分不改变 competitor 分类。

`company.json` 是事实与评估的唯一权威结构化来源；`report.md` 是由它组织的中文可读情报结论。模块 Markdown 仅保存原始材料、查询日志或扩展分析，按实际内容创建，不手工维护第二份事实表。

生成 `report.md`，其中必须有“研究覆盖”章节，按官网、社媒、项目、主体、外部交叉、Provider、采购链和分类列出 `exhaustive|bounded|partial|not_queried|not_applicable`、数量、时间/分页边界、缺口与下一步；同时明确区分事实底座、关键信号、AI 推理、AI 结论、不确定性和继续研究方向。AI 必须对 Lead/Competitor、产品适配、当前与长期机会、优先级、切入方向和主要风险形成自己的结论，不能用“待人工判断”代替分析。按固定字段 `fileName/path/format/reportType/language/generatedOn/description` 写入 `reportFiles[]`。共享工作空间脚本从 `$geto-run-market-research` 的安装目录调用，用它校验并原子替换完整 JSON，再运行来源聚合与单公司校验：

```bash
python '<geto-run-market-research-dir>/scripts/write_company_json.py' \
  '<完整临时 JSON>' '<公司目录>/company.json'
python '<geto-run-market-research-dir>/scripts/build_deduplicated_sources.py' \
  '<公司目录>/company.json'
python '<geto-run-market-research-dir>/scripts/validate_workspace.py' \
  --company-dir '<公司目录>'
```

修复 ERROR；WARNING 表示需处理的风险或冲突，INFO 表示如实记录的未查询或已查无结果。validator 默认显示 INFO 汇总；人工排查时加 `--include-infos` 查看逐条明细。

## 任务回传

结束时向主任务回传：做了什么、主要发现、公司目录与报告路径、lead/competitor 接受或拒绝理由、AI 结论及推理摘要、身份/证据冲突、信息边界、关联扩展对象、继续研究方向，以及官网栏目、社媒帖子、项目池、外部交叉和 Provider 的覆盖状态与计数。不得把 `partial` 表述成“已全面核查”。主任务会按共享研究充分性合同独立审校并可能把具体问题退回；收到 follow-up 后更新原 company.json、report.md、Sources 和同一 progress section，再回传差异。主任务验收通过后即可完成本地研究；评分定稿和 OmniX 上传按用户范围另行处理。
