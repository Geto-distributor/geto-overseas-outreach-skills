---
name: geto-mine-competitor-customers
description: 从已确认的 GETO 海外竞对官方项目与案例中反查可识别客户，核验竞对—客户关系，逐客进入同一客户线索池和六维 cohort 评分，并计算竞对客户价值平均分与每条关系的 0–5 合作切入分。用于一家公司一个竞对任务的客户组合研究、关系仲裁和切入机会判断；竞对公司本身的深度背调使用 geto-diligence-competitor。
---

# GETO 竞对客户反查与组合评估

一次只处理一家已确认竞对。研究链固定为：竞对 → 客户 → 产品或项目 → 合作方式 → 当前或历史 → Evidence。

开始前读取 [competitor-customer-contract.md](references/competitor-customer-contract.md)、[relationship-entry-model.json](references/relationship-entry-model.json) 与 [output-contract.md](references/output-contract.md)。

## 输入

- 已通过 `$geto-diligence-competitor` 确认为 competitor 的公司目录。
- 目标国家、GETO 产品范围、研究截止日和已完成查询清单。
- 国家 ResearchBundle 路径与客户 cohort 边界。

competitor 分类为 possible 或 rejected 时，只回传关系研究缺口，不生成正式客户组合。

## 工作流

### 1. 官方客户召回

优先查询竞对官网 Projects、Case Studies、Testimonials、News、References、客户故事和可定位能力书。提取具名公司、项目、产品或服务、合作内容、时间和来源。

Logo、匿名案例、搜索摘要、共同参建和无法拆分的组合实体进入 pending 候选。

### 2. 关系资格仲裁

按 [competitor-customer-contract.md](references/competitor-customer-contract.md) 形成 `verified_customer|verified_non_customer|pending|conflicting|invalid`。`verified_customer` 需要可识别公司，并由竞对或对方官方内容闭合具体项目或具体产品/服务及实际合作内容。

buyer、payer、实际使用方、sale/rental、排他、框架关系和当前持续性分别取证。未知字段保持 null。

### 3. 客户一客一档

每个 verified_customer 使用同一自然公司名目录。已有 Company 复用；新客户由主任务创建独立 `$geto-diligence-company` 任务，并以 `assessmentMode=lead_value` 准备六维观察输入。

主任务使用 `$geto-find-leads` 按国家×公司角色建立 cohort baseline，并批量完成客户长期价值评分。竞对来源不改变六维模型或 cohortKey。

### 4. 关系切入分

每条 verified_customer 关系按 [relationship-entry-model.json](references/relationship-entry-model.json) 评估 0–5 分。分数表达 GETO 成为替代、补充或第二来源的当前可行性；Evidence 不足时 score=null、status=pending_evidence。

entryAssessment 写入对应 `relationships[]` item。客户价值分表达客户本身的长期价值，关系切入分表达某条竞对关系的进入难度，两者分别展示。

### 5. 竞对客户组合聚合

客户 cohort 评分完成后运行：

```bash
python scripts/aggregate_competitor_customers.py \
  --country-root '<国家目录>' \
  --competitor-dir '<竞对公司目录>' \
  --as-of '<YYYY-MM-DD>'
```

脚本按去重 verified_customer 计算 verifiedCustomerCount、scoredCustomerCount、customerScoreCoverage 和 averageCustomerValueScore，并写入竞对 company.json 的 `competitorCustomerPortfolio`。缺少当前六维评分的客户不填 0；覆盖率随平均分一并交付。

### 6. 报告与验证

更新竞对 report.md 的客户组合、评分覆盖、逐客价值、关系切入分、切入口与限制；更新客户报告中的竞对来源关系。生成 Sources，并运行单公司与国家 workspace validator。

## 任务回传

回传查询范围、各关系仲裁结果、已核实客户及公司目录、待核/冲突对象、客户评分覆盖率、竞对客户价值平均分、逐关系切入分、成果路径和下一步。
