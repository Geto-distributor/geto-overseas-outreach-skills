# 签约前风险写入合同

把结果写入目标公司 company.json：

- inquiries[]：本次买方、联系人、产品、数量、技术要求、项目国、签约主体、付款主体、交付、付款条款、文件和开放问题。
- risks[]：category、level、finding、impact、blocking、mitigation、evidence。
- assessment：assessmentType=precontract、grade、overallScore、overallConclusion、assessedOn、dimensions[]；每个 dimension 含 name、score、level、rationale、evidence。
- recommendedActions[]：action、priority、owner、timing、reason、evidence。
- missingInformation[]：未查询、未找到、冲突、过期或 Provider 失败。

模型或关键输入不足时 overallScore/grade 为空，decision=hold；直接证据确认 hard stop 时可 reject。报告同步更新到 report.md 和 RisksAndAssessment/ 扩展材料。
