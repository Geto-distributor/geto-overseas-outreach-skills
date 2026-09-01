---
name: geto-diligence-inquiry
description: 对单条 GETO 海外询盘同时执行完整公司背调与当前交易核查：广泛覆盖公司从历史至今的主体、业务、项目、关系、人员、财务、海关、合规和经营信号，再围绕询盘需求、联系人、采购链、付款链和报价条件选择高价值路径深挖，输出极致汉化、务实易读的中文 Markdown 报告。用于询盘真假、公司画像、项目机会、联系人补强、询盘准备度、长期客户价值和跟进建议；主体未闭合或第三方数据服务无结果时仍继续调研。DOCX/PDF 仅在用户审阅 Markdown 后按需生成。
---

# GETO 单询盘背调

一次只处理一条询盘及其目标 Company。询盘是当前交易切口，公司是长期研究主体；不得因为“只是询盘”而降低单家公司研究广度和深度。

开始前完整读取 [inquiry-research-intelligence-contract.md](references/inquiry-research-intelligence-contract.md)、[project-research-contract.md](references/project-research-contract.md)、[report-contract.md](references/report-contract.md)、[inquiry-contract.md](references/inquiry-contract.md)、[inquiry-intake-gate.md](references/inquiry-intake-gate.md)、[identity-conflict-investigation.md](references/identity-conflict-investigation.md)、[child-resources.md](references/child-resources.md) 和 [inquiry-readiness-model.json](references/inquiry-readiness-model.json)，并读取 `$geto-run-market-research` 的 `references/research-intelligence-contract.md`。构造或复核 `company.json` 时读取 `$geto-run-market-research` 的 `references/company-field-requirements.md`；首次查看完整形态时读取其 `references/company-json-example.json`。需要生成 DOCX/PDF 时才读取 [publication-contract.md](references/publication-contract.md)。填写询盘与准备度时读取 [inquiry-example.md](references/inquiry-example.md)。

## 输入

- 询盘原始导出、聊天记录、附件、receivedOn 和本地 inquiryRef。
- 买方自报公司、人名、邮箱、电话、国家、产品、数量、项目、交付和付款信息。
- 目标国家、GETO 产品范围、研究截止日和公司目录。
- 用户希望重点研究的问题、报告语言和范围；未指定时执行完整双轴背调。

## 启动路由

先构造临时 `intake-gate.json`，尽量包含公司名、需求和可回复邮箱，再分别执行 Web 主体检索与 TradeWind 精确公司查询。两边分别保留查询边界、候选、强弱锚点、冲突和证据；该步骤只选择研究模式，不决定是否允许继续搜集信息。

运行：

```bash
python '<geto-diligence-inquiry-dir>/scripts/validate_inquiry_intake.py' \
  '<intake-gate.json>' --output '<intake-gate-result.json>'
```

`ready_for_diligence`、`diligence_with_identity_gaps`、`diligence_with_provider_gaps` 和 `diligence_with_partial_intake` 都继续完整背调。只有完全没有公司、人名、域名、邮箱域名、项目、地点、附件内容或其他可检索锚点时才使用 `blocked_no_research_anchor`。

内部机器状态保留在审计材料中，不直接复制到正式报告。主体未闭合时继续拆分候选并解释冲突；单一数据服务返回 0 条结果不等于公司不存在。

## 工作流

### 1. 初始化与原始询盘

初始化规范国家和自然公司名目录，一条询盘保留一个目标 Company；同名、近名、旧域名、关联域名和冲突主体分别保存，不混写事实。把原始信息写入 `inquiries[]`，保留附件、开放问题和 customer_document Evidence。

### 2. 完整公司轴

调用 `$geto-diligence-company` 的完整研究流程，不只复用主体核验；完整询盘背调默认使用 `assessmentMode=lead_value`。公司轴按共享研究情报合同覆盖公司从历史至今的主体与发展、产品与服务、制造/租赁/经销/安装、项目池、关系网络、管理层与触达、财务与经营、资质、海关、诉讼合规、新闻社媒、Lead/Competitor 和 GETO 适配。

默认执行单公司长期价值观察；缺少同类样本时只保留观察和自然中文解释，不把内部状态码写入正式报告。结构化评分按 `$geto-diligence-company` 合同执行。

### 3. 询盘轴与广度扫描

按 [inquiry-research-intelligence-contract.md](references/inquiry-research-intelligence-contract.md) 建立询盘、主体、联系人、项目、产品技术、业务履约、交易风险和信息生态议程。每个信息面记录查了什么、取得什么、新发现什么、是否值得深挖和当前公开边界；不能用“已查”代替研究结果。

公司项目池是公司轴的必交内容。尽量枚举历史、当前、规划、招标、授标、施工、交付和停滞项目；每个已取得名称的去重项目分别写入 `projects[]`，不得把多个具名项目合并成“历史项目池”等汇总占位。正式报告用紧凑项目总表呈现全部 `projects[]`，每个项目名都要带可点击链接：优先链接到该项目最有代表性的公开来源；只有询盘自述时链接到报告内的询盘证据段，并明确“仅客户陈述”。再选择最重要项目深挖。

### 4. 高价值路径深挖与下一跳

从公司轴和询盘轴共同选择通常 2–5 条最可能改变真假、项目、产品、报价、签约、付款、授信或客户价值判断的路径深挖。数量不是硬门槛；简单询盘可以更少，复杂询盘可以更多。

每项重要发现检查是否引出新的公司、项目、产品、客户、供应商、渠道、人员、采购方、付款方、签约主体、技术选型人、时间冲突或风险。与本询盘和目标公司结论直接相关的继续下钻；超出范围但值得独立建档的对象写入继续研究方向，不让单询盘无限扩张。

### 5. 主体、联系人和数据服务边界

按照 [identity-conflict-investigation.md](references/identity-conflict-investigation.md) 调查主体、冒名和域名冲突，完整候选矩阵保留在内部材料；只有实质影响真假或交易判断时，才在正式报告用自然中文简述。

TradeWind、网易外贸通等只作为第三方数据服务观察。人员结果必须与官网、职业页和法律主体对齐；匿名、掩码、前雇员和同名冲突不进入正式联系人。公司通用邮箱、电话、表单、办公室、项目咨询、供应商/投标和投资者关系入口与具名人员分别建模。邮箱可投递不证明任职、采购、签字或付款权限。

### 6. 询盘准备度与长期价值

按模型六维 components 填写 `inquiryAssessment.dimensions[]` 的 score、rationale、Evidence 和 gapCodes，只给证据支持的准备度分。运行：

```bash
python '<geto-diligence-inquiry-dir>/scripts/calculate_inquiry_readiness.py' \
  '<公司目录>/company.json' --inquiry-ref '<本地询盘引用>' \
  --assessed-on 'YYYY-MM-DD'
```

询盘准备度回答当前能否报价和推进；长期客户价值回答公司是否值得持续投入。两者分别研究、分别解释，不把观察分包装成最终等级。

### 7. Markdown 第一交付

按 [report-contract.md](references/report-contract.md) 生成极致汉化、务实易读的 `report.md`。固定核心业务问题，不固定章节数量；新发现足以改变业务理解时动态增加专题章节。第一页必须提供销售速读：跟进建议、当前阶段、最大阻断、下一步及期限、可直接联系入口和暂不承诺事项。报告必须包含公司项目池总表，逐项覆盖 `company.json.projects[]`；重点项目再展开判断，不用为每个项目建立独立章节。完整研究过程、机器状态、查询日志和低价值技术细节留在结构化档案或 `Additional/`。

生成 `Sources/sources.md`，运行单公司 validator 和报告质量检查：

```bash
python '<geto-run-market-research-dir>/scripts/build_deduplicated_sources.py' \
  '<公司目录>/company.json'
python '<geto-run-market-research-dir>/scripts/validate_workspace.py' \
  --company-dir '<公司目录>'
python '<geto-diligence-inquiry-dir>/scripts/validate_inquiry_report.py' \
  '<公司目录>/report.md' --company-json '<公司目录>/company.json'
```

完成研究充分性和业务语言自审后，向用户交付 Markdown 并请求内容 Review。此时默认停止，不自动生成 DOCX/PDF。

### 8. 可选 DOCX/PDF 发布

只有用户明确确认 Markdown 内容，或明确要求跳过 Review 时，才按 [publication-contract.md](references/publication-contract.md) 冻结内容并生成指定格式。PDF 是可选发布物，不是询盘背调完成条件；必须从已确认的 `report.md` 派生，并逐页检查中文字体、目录、分页、表格、链接、来源和文本一致性。

## 研究完成条件

- 公司轴和询盘轴的主要信息面已有结果或明确边界；
- 高价值路径已下钻到足以形成结论，或达到合理公开边界；
- 重要发现引出的下一跳已处理或说明暂缓理由；
- AI 已形成事实、信号、推理、结论、不确定性和具体动作；
- 继续合理公开查询主要产生重复信息，或不足以显著改变结论；
- `company.json`、Evidence、Sources 和 Markdown 相互一致。

结构校验通过、文件存在、第三方数据服务返回结果或任务 final 均不能单独证明研究完成。

## 边界

- `inquiryAssessment` 不使用 cohort baseline。
- 公司长期价值按单公司观察执行；缺少同类样本时不在正式报告给出最终等级。
- 第三方数据服务观察不能覆盖询盘原文、登记或官网一手事实。
- 不因工具故障、无结果、同名、域名差异或信息冲突停止公开调研。
- 不默认上传 OmniX；仅在用户明确要求时由主任务处理。
- 不默认生成 DOCX/PDF；Markdown 内容 Review 是默认发布门禁。

## 回传

回传完整公司画像、询盘准备度、长期价值观察、AI 推理与业务结论、报价前必问项、可用联系方式、重点项目与采购窗口、风险和交易条件、公司目录、Markdown 路径、关联扩展对象、继续研究方向和公开信息边界，并明确询问用户是否需要修改内容或进入可选 DOCX/PDF 发布。
