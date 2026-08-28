---
name: geto-mine-competitor-customers
description: 从已确认的 GETO 海外竞对项目、案例、渠道、供应商、客户侧披露和开放信号中广泛反查合作方，沿竞对—项目—产品—客户—供应链继续扩展，核验关系并形成 AI 客户结构与切入结论；可按需执行一客一档、六维 cohort、组合平均分和关系切入评估。用于一家竞对的合作网络、客户关系、组合价值或切入机会研究；竞对公司本身的深度背调使用 geto-diligence-competitor。
---

# GETO 竞对客户反查与组合评估

一次只处理一家已确认竞对。研究链固定为：竞对 → 客户 → 产品或项目 → 合作方式 → 当前或历史 → Evidence。

开始前读取 [competitor-customer-contract.md](references/competitor-customer-contract.md)、[relationship-entry-model.json](references/relationship-entry-model.json)、[output-contract.md](references/output-contract.md)，以及 `$geto-run-market-research` 的 `references/research-intelligence-contract.md`。

## 输入

- 已通过 `$geto-diligence-competitor` 确认为 competitor 的公司目录。
- 目标国家、GETO 产品范围、研究截止日和已完成查询清单。
- 国家 ResearchBundle 路径与客户 cohort 边界。

competitor 分类为 possible 或 rejected 时，只回传关系研究缺口，不生成正式客户组合。

## 工作流

### 1. 多来源关系召回

优先查询竞对官网 Projects、Case Studies、Testimonials、News、References、客户故事和可定位能力书，同时反查客户、业主、总包、分包、顾问、供应商、经销商、行业媒体、招标资料、展会、招聘和公开社媒披露。提取具名公司、项目、产品或服务、合作内容、时间、来源和可能的下一跳。

Logo、匿名案例、搜索摘要、共同参建、现场图片、供应商口述和无法拆分的组合实体进入 pending 或开放信号候选，不因证据较弱而丢弃，也不直接升级客户关系。

### 2. 关系资格仲裁

按 [competitor-customer-contract.md](references/competitor-customer-contract.md) 形成 `verified_customer|verified_non_customer|pending|conflicting|invalid`。`verified_customer` 需要可识别公司，并由竞对或对方官方内容闭合具体项目或具体产品/服务及实际合作内容。竞对官网可以独立支持该范围内的关系事实；第二来源用于主体消歧、项目状态、时态、反证和评分确认度。

buyer、payer、实际使用方、sale/rental、排他、框架关系和当前持续性分别取证。未知字段保持 null。

对反复出现的客户、项目、系统、渠道、供应商或顾问继续展开：判断它们是否揭示竞对的市场进入方式、渠道控制、复购模式、区域聚集或当前机会。值得独立背调的对象回传主任务；关系未闭合但信息价值高的对象保留下一跳和重新打开条件。

### 3. 客户一客一档

只有用户需要客户长期价值、销售优先级或组合均分时，每个 verified_customer 才进入一客一档和六维评分。已有 Company 复用；新客户由主任务创建独立 `$geto-diligence-company` 任务，并以 `assessmentMode=lead_value` 准备六维观察输入。只研究竞对合作披露时，可以保留关系 Evidence 和未知字段，不批量创建客户评分任务。

主任务使用 `$geto-find-leads` 按国家×公司角色建立 cohort baseline，并批量完成客户长期价值评分。竞对来源不改变六维模型或 cohortKey。

### 4. 关系切入分

每条 verified_customer 关系按 [relationship-entry-model.json](references/relationship-entry-model.json) 评估 0–5 分。分数表达 GETO 成为替代、补充或第二来源的当前可行性；Evidence 不足时 score=null、status=pending_evidence。

entryAssessment 写入对应 `relationships[]` item。客户价值分表达客户本身的长期价值，关系切入分表达某条竞对关系的进入难度，两者分别展示。

### 5. 竞对客户组合聚合

需要组合价值指标时运行：

```bash
python scripts/aggregate_competitor_customers.py \
  --country-root '<国家目录>' \
  --competitor-dir '<竞对公司目录>' \
  --as-of '<YYYY-MM-DD>'
```

脚本按去重 verified_customer 计算 verifiedCustomerCount、scoredCustomerCount、customerScoreCoverage 和 averageCustomerValueScore，并写入竞对 company.json 的 `competitorCustomerPortfolio`。缺少当前六维评分的客户不填 0；覆盖率随平均分一并交付。组合状态和完整度不阻止 confirmed competitor 的公司级投影。

### 6. AI 客户网络结论、报告与验证

无论是否执行评分，都要更新竞对 report.md 的事实关系、关键信号、客户/渠道结构、AI 推理、AI 结论、不确定性、切入口、限制和继续研究方向；解释哪些模式由已核实关系支持，哪些只是弱信号。执行评分时再增加评分覆盖、逐客价值、组合平均分和关系切入分。更新客户报告中的竞对来源关系，生成 Sources，并运行单公司与国家 workspace validator。

## 任务回传

回传查询范围、各关系仲裁结果、已核实客户、待核/冲突和开放信号对象、反复出现的关系节点、AI 客户结构与切入结论、成果路径和下一跳。执行一客一档、客户评分、组合聚合或关系切入评估时，再回传对应公司目录、评分覆盖率、平均分和逐关系切入分；未执行的分析保持 not_requested 或 null，不影响关系情报的本地完成。
