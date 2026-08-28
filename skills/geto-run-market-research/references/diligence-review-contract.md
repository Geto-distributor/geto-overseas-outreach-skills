# 单公司背调研究充分性与主编审校合同

## 目的

单公司任务的 final、callback、progress 区块和 validator 通过只表示任务已交付，不表示研究已经被国家主任务接受。国家主任务是研究总编辑，必须复核成果是否取得了足够的信息广度、是否选择并深挖了高价值路径、是否沿重要发现继续扩展、AI 推理和结论是否由 Evidence 支持，以及任务是否在遇到困难后过早停止。

审校目标是在合理公开边界内形成广泛、深入、可解释的本地情报，不是把每家公司变成证伪竞赛，也不是声称看完互联网或要求取得私有资料。只对会显著影响强身份、客户关系、采购/付款权、当前机会、财务主体、Lead/Competitor 或重大风险的结论做定向反向核查。无法访问、平台分页受限、付费墙、登录墙、robots 限制和动态站点故障必须记录为边界；只有在边界、替代来源、结论影响和重新打开条件均明确时，才可接受为有缺口的完成。

## 双层责任

### 单公司任务自证覆盖

单公司或竞对任务在 final 和 report.md 的“研究覆盖”章节中至少报告：

- 官网发现了哪些栏目、检查了哪些栏目、页数或列表项数量、不可访问区域和 sitemap/站内搜索/页脚发现方法；
- 找到了哪些官方社媒渠道，逐渠道可见帖子数量、实际检查数量、时间范围、分页边界、最近活动和与产品、项目、管理层相关的帖子；
- 官网或外部来源共发现多少项目，检查多少项目，哪些是当前或高相关项目，以及逐项目仍缺哪些参与方和采购字段；
- 法定身份、外部交叉来源、Provider、联系人、负面检索、Lead Gate 与 Competitor Gate 的查询边界；
- `exhaustive|bounded|partial|not_queried|not_applicable` 覆盖状态，不能只写“已核查”或“未找到”。

任务不得用 homepage、About 页面、搜索摘要或少量精选帖子代表整个官网、全部社媒或完整项目池。不能证明已穷尽时使用 `bounded` 或 `partial`。

### 国家主任务独立审校

国家主任务读取 final 后必须同时打开 company.json、report.md、Sources/sources.md、关键来源页和 validator 输出，不照抄单公司任务的自证。先判断研究是否覆盖主要信息面、深挖选择是否合理、关联扩展是否处理、不同强度来源是否正确使用、AI 是否形成结论，再对高影响事实提出必要挑战：

1. 主体是否可能被集团、品牌、子公司、JV、SPV、历史名称或同名公司污染？
2. 官网是否建立了栏目清单，而不是只看首页和 About？页脚、法律页、下载目录、新闻分页、项目分页、站内搜索、sitemap 或 robots 可发现内容是否被检查？
3. Products、Systems、Solutions、Applications、Manufacturing、Factory、Rental、Distribution、Projects、Case Studies、Testimonials、News、Contact、Privacy/Terms 和 Downloads 中适用栏目是否实际打开？
4. 官方社媒渠道是否被枚举？是否先建立最近活动、公开数量和分页边界，再按信息价值检查产品、工厂、项目、客户、招聘、经营变化和管理层内容；公开量可管理时是否逐页检查，数量过大或平台受限时是否说明选择方法并补查关键历史里程碑？
5. 项目索引是否尽量枚举？当前、高相关和被用来支持分类或评分的项目是否逐一打开详情并做外部交叉？
6. 项目是否下钻到 owner/developer、main contractor/JV、结构或模板分包、consultant、buyer、payer、actualUser、technical approver、项目阶段、数量、模板系统或供应商、采购/租赁/甲供边界和进入窗口？
7. “无结果”“无风险”“无竞对”“无当前项目”是否有明确关键词、语言、来源、时间和分页边界，而不是把没查当成不存在？
8. 高优先级或 confirmed 结论是否至少有一个公司官网之外的独立来源、监管披露、交易对手来源、当前项目事实或已接受 Provider Observation？
9. Provider 人员和公司 Observation 是否与官网、职业页和法律主体对齐？姓名掩码、前雇员、同名公司和职位差异是否被降级？
10. Lead Gate 与 Competitor Gate 是否使用各自 Evidence；一般合作设想、安装施工、项目共现、Logo 墙或公司名称是否被错误升级？
11. 来源是否包含 retrievedOn、时态、冲突和失效边界？“进行中”旧标签是否被当成当前事实？
12. final、company.json、report.md、Sources 和 progress 是否互相一致，且 validator 可以由主任务复现？

国家主任务的审校不是措辞或栏目数量检查。即使报告写了所有栏目名，只要 Sources、researchQueries、项目事实或外部链接不能支持覆盖声明，仍应退回续查；反之，不影响主要结论且已说明 `not_applicable` 的栏目不应触发机械返工。报告如果只有资料罗列、状态和分数，没有事实—信号—推理—AI结论链，也不能通过研究充分性审校。

## 官网覆盖门禁

深度背调至少执行以下动作，并在不存在或不可访问时记录结果：

- 枚举顶部导航、页脚导航、项目/新闻/产品索引和下载目录；
- 查找 sitemap、robots、站内搜索或搜索引擎 `site:` 补充发现；
- 打开所有与主体、产品、商业控制、制造、租赁、经销、项目、人员和法律身份相关的栏目；
- 对有分页的项目、新闻和案例继续分页到声明边界；
- 保存发现数、检查数、遗漏数和不可访问原因。

只检查首页或一个公司介绍页面是自动退回条件。栏目被发现但既未检查、也未说明不可访问原因，同样自动退回。

## 社媒覆盖门禁

先从官网页脚、联系页、公开公司页和搜索结果归一官方 LinkedIn、Instagram、Facebook、YouTube、X 或当地主要平台。先建立最近活动、公开数量/日期和分页边界，再优先检查与产品、工厂、项目、客户、招聘、经营变化和管理层有关的内容；公开量可管理时逐页检查，帖子量过大或平台限制完整分页时，必须：

- 记录可见总量或首尾时间、实际检查数量和分页终点；
- 优先覆盖产品、工厂、项目、客户、招聘、管理层和经营状态关键词；
- 对被官网项目或产品结论引用的更早里程碑继续回溯；
- 将覆盖标记为 `bounded`，不得声称 `exhaustive`。

没有找到官方渠道时，也要记录检索平台、名称/域名边界和结果。社媒未查询时，不能确认“无当前经营信号”或“无近期项目”。

## 项目深挖门禁

项目研究至少区分：项目存在、目标公司参与、目标公司合同角色或产品使用、采购与付款路径。对每个当前或高相关项目，逐项核对：

- 项目名称、地点、业主/开发商、合同或招标编号；
- 总包、JV/SPV、结构/粗建/模板分包和顾问；
- 当前阶段、公开时间线、结构剩余量或强反证；
- 模板、支撑、脚手架、预制或模块化系统、供应商和数量；
- buyer、payer、actualUser、technical approver、签约主体；
- 自购、租赁、甲供、库存或分包责任；
- 当前采购窗口、供应商准入和可触达入口。

字段未知可以接受，但必须给出查过的来源、关键词和下一步。用项目总额代替模板采购额、用开发商代替实际买方、用总包代替付款方，或用项目共现确认客户关系，均为退回条件。

## 审查结果

国家主任务为每家公司在 `<公司目录>/Additional/diligence-review.json` 保存审查结果，并使用 `scripts/validate_diligence_review.py` 校验。完整结构参考 [diligence-review-example.json](diligence-review-example.json)。审查状态只有：

- `accepted`：主要信息面、重点路径、关联扩展和 AI 结论均充分，没有开放的 blocking 或 material challenge；
- `accepted_with_gaps`：主要信息面和重点路径已查，无法取得的信息有边界、影响与重新打开条件，AI 已形成有条件结论，没有开放的 blocking challenge；
- `returned_for_followup`：存在可通过继续公开检索或补读成果解决的实质缺口，必须把具体问题发回原任务；
- `rejected`：成果主体错误、证据污染、工件不可信，或无法作为该公司背调使用。

`accepted` 和 `accepted_with_gaps` 表示本地单公司研究可完成并进入分类定稿。cohort 评分和 OmniX 按用户范围另行处理；它们不是本地研究通过的必要条件。`returned_for_followup` 与 `rejected` 不得伪装成已完成研究或上传。

## 自动退回条件

出现任一条件时，审查不得通过：

- company.json、report.md 或 Sources/sources.md 缺失，JSON 不可读，或 validator 有 ERROR；
- 只看首页/About，未建立官网栏目清单；
- 官方社媒被发现但既未检查相关内容，也未说明访问边界；
- 项目只列名称，没有当前/历史时态和项目详情；
- 当前或高相关项目未查询参与方与采购链；
- confirmed/high priority 只有公司自述且无独立交叉来源；
- “无结果”“无风险”“无竞对”没有查询边界；
- Provider Observation 未与主体和公开职业信息对齐；
- 集团、JV、SPV、历史主体或同名冲突被隐藏；
- Lead/Competitor 理由只是行业描述、公司名称或合作设想；
- 来源缺失时态或 retrievedOn，导致当前性无法判断；
- final、结构化成果、报告和 progress 的分类、分数或关系互相冲突。

## 追问与停止条件

退回时向原任务发送可执行问题，不使用“再深入一点”之类泛化措辞。问题应指出缺失栏目、社媒分页、项目、主体、关系字段、来源或矛盾，并要求更新原工件和同一 progress section。

默认最多两次针对同一实质缺口的 follow-up。两次后若合理公开路径只产生重复信息、没有新来源可用或新增信息不足以显著改变主要结论，主任务可接受为 `accepted_with_gaps`，并明确结论强度、信息边界和重新打开条件；若主体仍不稳定或 Evidence 仍污染，则使用 `rejected`/`identity_conflict`，不能为了结束任务而接受。不要为了追求形式上的全面而对低影响栏目无限追问。

## progress 与候选总账

财务结构化补证复用同一 `progressSectionName`，例如 `financial_structure_supplement_es_20260824`；它是已有背调的增量验收，不是重新创建国家任务。逐条核对 `subjectEntity`、scope/accountingScope/relationshipToTarget、期间、币种/单位、valueStatus、Evidence 和实体边界。集团/母公司/品牌/JV/SPV 记录可以接受，但必须标真实主体与 mismatch；商业数据库只作 secondary 证据；注册资本/实缴资本只留在 capitalRecords。

候选总账分别记录 `diligenceTaskStatus` 和 `diligenceReviewStatus`，另记 `reviewArtifactPath`、`reviewCycle`、`reviewBlockingIssues` 和 `lastReviewedOn`。progress.md 记录审查结论、挑战问题、退回对象、续查结果和是否允许进入评分/导入。任务 final 不能覆盖审查状态。
