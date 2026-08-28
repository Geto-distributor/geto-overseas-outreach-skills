# GETO 询盘准备度与公司价值合同

## 1. 双轴评估

- `inquiryAssessment` 衡量当前询盘能否报价和交易推进，不使用同类型中位数；
- `assessment` 保存公司长期客户价值观察和国家同类型比较结果；
- 两者使用不同维度、证据和结论，不互相替代。

完整询盘背调默认执行公司长期价值观察。缺少同类样本时可以保留六维观察，但正式报告只写“同类样本不足，暂不出具最终等级”，不得展示机器状态码或把观察分包装成最终等级。

## 2. 输入

- 一条明确询盘及其原始附件或聊天记录；
- [inquiry-intake-gate.md](inquiry-intake-gate.md) 的启动路由结果；
- 按 `$geto-diligence-company` 完成的完整公司轴 Evidence；
- 目标公司的主体、产品、项目、关系、联系人、财务、海关、合规、经营信号和风险；
- 研究截止日和本地公司目录。

除完全没有研究锚点外，主体弱匹配、冲突、第三方数据服务无结果或输入缺失均继续调研。

## 3. 询盘准备度评分

使用 `inquiry-readiness-model.json` 的六维 components。只给询盘原文或目标公司 Evidence 支持的 component 分；缺失信息得 0 readiness points 并进入 gapCodes。未知不等于确认不存在，但在当前是否具备推进条件上都不产生准备度分。

单一第三方数据服务 0 条结果只形成信息缺口，不自动封顶；互斥强身份或冒名信号分别加入 `identity_conflict` 或 `fraud_or_impersonation_signal` 限制并应用模型 cap。

内部等级：

- `ready_for_quotation`
- `qualified_needs_clarification`
- `nurture_or_verify`
- `high_risk_or_unqualified`

机器值只写入 `company.json`。正式报告使用：

- 可以进入正式报价；
- 基本合格，但需补充关键信息；
- 继续培育并补充核实；
- 当前风险较高或暂不具备推进条件。

## 4. 决策链和交易链

分别核查并记录：

- 联系人当前任职和职责；
- technical approver：技术选型或审批人；
- buyer：采购方；
- actual user：实际使用方；
- signing entity：合同签约主体；
- payer：付款方；
- 项目授权、预算、采购/租赁、交付、Incoterm 和付款条件。

姓名、邮箱可投递和公司入口不自动证明上述角色。没有闭合时，在正式报告用业务中文说明影响和补件动作。

## 5. 动态深挖

项目、联系人、采购链、付款链和产品技术深挖按 [inquiry-research-intelligence-contract.md](inquiry-research-intelligence-contract.md) 与 [project-research-contract.md](project-research-contract.md) 执行。主体冲突按 [identity-conflict-investigation.md](identity-conflict-investigation.md) 执行。

重点路径由能否改变报价、产品、项目、签约、付款、授信、准备度或长期价值决定，不按固定项目数量或章节数量决定。

## 6. 报告和发布

机器状态、gapCodes 和内部等级留在结构化数据；`report.md` 按 [report-contract.md](report-contract.md) 转换成自然中文业务结论。

Markdown 是默认第一交付。用户确认内容后，才按 [publication-contract.md](publication-contract.md) 可选生成 DOCX/PDF。发布文件不改变评分和事实。
