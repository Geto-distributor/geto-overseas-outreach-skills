# 国家研究覆盖与候选总账合同

## 研究覆盖矩阵

国家任务在 discovery 阶段维护 `产品范围 × 角色轨道 × 来源` 覆盖矩阵。产品范围来自用户输入与 Capability Foundation 切片；角色至少包括六个标准 companyRole，竞对按产品或技术面独立覆盖。

每个单元记录：

- productCode 或自然产品范围；
- laneCode 或 competitor surface；
- sourceChannel=`web|tradewind|netease|other`；
- queryBoundary；
- status=`not_queried|partial|completed|failed|not_configured`；
- resultCount、acceptedCount、rejectedCount；
- artifactPath、checkedOn、warnings 和下一步。

连通性检查、认证测试、国家级宽查询或单页结果只证明对应 queryBoundary，不代表产品覆盖完成。Provider 和 Web 分别记录，不用一个来源的覆盖替代另一个来源。

## 候选总账

所有召回对象进入国家候选总账，并使用稳定 candidateRef 保留阶段状态：

`recalled → identity_review → accepted_for_diligence|rejected → diligence → classified → assessed → import_ready|not_for_import → imported`

每条至少记录：

- 自然公司名、发现时名称和来源；
- 强身份锚点及验证状态；
- proposedRole、proposedLeadStatus、proposedCompetitorStatus；
- productScope、currentPriority；
- identityConflict、duplicateOf、groupOrJvBoundary；
- companyDir、taskId、assessmentStatus、uploadStatus；
- diligenceTaskStatus、diligenceReviewStatus、reviewArtifactPath、reviewCycle、reviewBlockingIssues、lastReviewedOn；
- 接受/拒绝理由、缺口和下一步。

原始候选池只表示召回。未确认归属的 website root、名称、地址、集团关系、JV 或项目共现不能成为自动去重锚点。

## 优先级

高优先级候选至少需要一条公司官网之外的独立证据，或一条可核验的当前项目、招标、合同、监管披露、Provider 主体/人员观察。只有官网自述、历史项目或无法交叉验证的“进行中”标签时，保持 possible 或低优先级。

项目机会优先闭合 owner/developer、main contractor/JV、结构或模板分包、buyer、payer、actualUser、technical approver、包件、当前结构阶段、采购或租赁边界和进入窗口。无法取得的字段保持未知，不用项目总额、公司注册资本或一般联系人代替。

单公司任务 final 只更新 diligenceTaskStatus。国家主任务按 `diligence-review-contract.md` 写入独立审查工件后，才能更新 diligenceReviewStatus。`returned_for_followup` 仍计入未完成工作量，不得因任务已有 final 而从剩余清单移除。

## 工作空间

一个国家只使用一个规范国家根目录。所有单公司任务写入该根目录下的自然公司名目录；临时工作区成果在验收前迁入规范目录并重新运行来源聚合与 validator。国家任务以候选总账、覆盖矩阵、progress.md 和实际公司目录共同判断剩余工作量。
