# 国家研究覆盖与候选总账合同

## 研究覆盖矩阵

国家任务在 discovery 阶段维护 `产品范围 × 角色轨道 × 来源` 覆盖矩阵。产品范围来自用户输入与 Capability Foundation 切片；角色至少包括六个标准 companyRole，竞对按产品或技术面独立覆盖。矩阵用于解释广度，不把单元格 completed 当作研究充分或 AI 结论。

每个单元记录：

- productCode 或自然产品范围；
- laneCode 或 competitor surface；
- sourceChannel=`official_web|government_regulatory|counterparty|supplier_channel|industry_media|directory|social_open_signal|tradewind|netease|other`；
- queryBoundary；
- status=`not_queried|partial|completed|failed|not_configured`；
- resultCount、acceptedCount、rejectedCount；
- artifactPath、checkedOn、warnings 和下一步。

连通性检查、认证测试、国家级宽查询或单页结果只证明对应 queryBoundary，不代表产品覆盖完成。不同来源分别记录，不用一个来源的覆盖替代另一个来源。专业二手、Provider 与开放信号可以扩大召回和推动下一跳，但不得独立关闭强身份、客户关系或采购权等高影响事实。

## 研究前沿

覆盖矩阵回答“哪些面查过”，研究前沿回答“现有信息还引出了什么”。每批任务回收后记录：

- 反复出现的公司、项目、产品系统、供应商、客户、渠道和人员；
- 可能改变主体、Lead/Competitor、产品适配、机会、风险或优先级的新信号；
- 建议继续深挖、另建单公司任务、保持观察或停止的理由；
- 当前 AI 市场判断及新增信息对它的影响。

主任务按信息价值、业务相关性、当前性和可研究性选择下一批，不要求把所有邻接对象都建档。已经达到合理公开边界或只产生重复信息的方向明确关闭。

TradeWind Agentic 使用两级覆盖：国家矩阵中的 sourceChannel=`tradewind_agentic` 单元，以及 Provider plan 中更细的 productFamily × roleLane × sourceGoal 单元。每个 Provider 单元记录 taskKeys、taskIds、pilotStatus、submissionStatus、resultCount、acceptedCount、driftCount、duplicateCount 和 coverageStatus。只有一个产品或一个宽任务时，只能关闭它实际覆盖的单元；用户范围中的其他产品/角色保持 not_queried，不能被聚合总量掩盖。

## 候选总账

所有召回对象进入国家候选总账，并使用稳定 candidateRef 保留阶段状态：

`recalled → identity_review → accepted_for_diligence|rejected → diligence → reviewed → classified → local_complete`

需要评分时从 `classified` 增加 `assessed`；用户明确要求 OmniX 时从 `local_complete` 增加 `omnix_ready → imported`。评分和上传不是本地候选生命周期的默认阶段。

每条至少记录：

- 自然公司名、发现时名称和来源；
- 强身份锚点及验证状态；
- proposedRole、proposedLeadStatus、proposedCompetitorStatus；
- productScope、currentPriority；
- identityConflict、duplicateOf、groupOrJvBoundary；
- companyDir、taskId、assessmentStatus、localResearchStatus、uploadStatus；
- diligenceTaskStatus、diligenceReviewStatus、reviewArtifactPath、reviewCycle、reviewBlockingIssues、lastReviewedOn；
- 接受/拒绝理由、缺口和下一步。

原始候选池只表示召回。未确认归属的 website root、名称、地址、集团关系、JV 或项目共现不能成为自动去重锚点。

## 优先级

高优先级候选至少需要一条公司官网之外的独立证据，或一条可核验的当前项目、招标、合同、监管披露、Provider 主体/人员观察。只有官网自述、历史项目或无法交叉验证的“进行中”标签时，保持 possible 或低优先级。开放信号即使不足以提级，也继续作为研究方向保存在总账，不能因未通过当前轨道 lead 筛选而从市场图景中消失。

项目机会优先闭合 owner/developer、main contractor/JV、结构或模板分包、buyer、payer、actualUser、technical approver、包件、当前结构阶段、采购或租赁边界和进入窗口。无法取得的字段保持未知，不用项目总额、公司注册资本或一般联系人代替。

单公司任务 final 只更新 diligenceTaskStatus。国家主任务按 `diligence-review-contract.md` 写入独立审查工件后，才能更新 diligenceReviewStatus。`returned_for_followup` 仍计入未完成工作量，不得因任务已有 final 而从剩余清单移除。

## 工作空间

一个国家只使用一个规范国家根目录。所有单公司任务写入该根目录下的自然公司名目录；临时工作区成果在验收前迁入规范目录并重新运行来源聚合与 validator。国家任务以候选总账、覆盖矩阵、progress.md 和实际公司目录共同判断剩余工作量。
