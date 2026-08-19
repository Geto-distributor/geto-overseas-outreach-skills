---
name: geto-diligence-inquiry
description: 对单条 GETO 海外询盘执行主体核验、需求还原、项目与联系人核查，并按固定证据规则生成无需同类中位数的询盘准备度评分。用于一条询盘一个独立任务的真假核查、报价前澄清和跟进优先级；客户长期价值由主会话 cohort 评分。
---

# GETO 单询盘背调

一次只处理一条询盘及其目标 Company。询盘准备度回答当前能否报价和推进，不替代客户长期价值评分。

开始前读取 [inquiry-contract.md](references/inquiry-contract.md) 和 [inquiry-readiness-model.json](references/inquiry-readiness-model.json)。公司事实使用 `$geto-diligence-company` 的 Evidence 与子资源合同，assessmentMode 固定为 none。

## 输入

- 询盘原始导出、聊天记录、附件、receivedOn 和本地 inquiryRef。
- 买方自报公司、人名、邮箱、电话、国家、产品、数量、项目、交付和付款信息。
- 目标国家、GETO 产品范围、研究截止日和公司目录。

## 工作流

1. 初始化规范国家和自然公司名目录；一条询盘只绑定一个当前待核验 Company。
2. 把原始信息写入 `inquiries[]`，保留附件路径、开放问题和 customer_document Evidence。
3. 调用 `$geto-diligence-company` 核查主体、官网、产品、项目、联系人、风险和 lead/competitor，assessmentMode 使用 none。
4. 主体冲突、冒名、邮箱域名冲突和 Provider 宽匹配分别保留，不自动合并。
5. 按模型六维 components 填写 `inquiryAssessment.dimensions[]` 的 score、rationale、Evidence 和 gapCodes。只给证据支持的准备度分；缺失信息记 0 和 gap，不使用同行均值。
6. 运行：

```bash
python '<geto-diligence-inquiry-dir>/scripts/calculate_inquiry_readiness.py' \
  '<公司目录>/company.json' --inquiry-ref '<本地询盘引用>' \
  --assessed-on 'YYYY-MM-DD'
```

7. 生成 report.md、Sources/sources.md 并运行单公司 validator。报告分别陈述公司事实、询盘准备度、报价前必问项和长期客户价值状态。

## 边界

- `inquiryAssessment` 不使用 cohort baseline。
- 顶层 `assessment` 保持 not_requested；需要长期客户价值时，由国家主任务在同类型 cohort 形成后统一执行。
- 邮箱可投递只支持 workEmail.deliverability，不支持任职、职位、授权或 buyingRole。
- Provider Observation 必须经过强身份仲裁，不能覆盖询盘原文、登记或官网事实。
- 不上传 OmniX；本地验证后由主任务另行询问用户。

## 回传

回传主体结论、询盘准备度分数/等级、六维理由、报价前必问项、公司目录、报告路径、lead/competitor 分类、风险冲突和下一步。
