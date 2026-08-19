---
name: geto-diligence-competitor
description: 对 GETO 海外市场中的单一竞对公司执行深度背调，核验主体、产品与商业控制、制造履约、目标市场、渠道租赁、项目和具名客户候选，输出本地 company.json、report.md 与内嵌 Evidence。用于一家公司一个独立任务的竞对确认、产品对标与关系事实研究；竞对客户资格、客户价值组合和合作切入分使用 geto-mine-competitor-customers。
---

# GETO 单竞对深度背调

一次只研究一个竞对 Company。主体事实、产品竞争面、制造深度和客户关系分别取证；公司名含 framework、formwork、modular 或相似产品词只用于召回。

开始前读取 [child-resources.md](references/child-resources.md)、[competitor-contract.md](references/competitor-contract.md) 与 [report-contract.md](references/report-contract.md)。Evidence 通用结构读取 `$geto-diligence-company` 的 evidence-contract.md。

## 输入

- 自然公司名及稳定官网域名、法定名称、注册号或明确国家中的至少一个强身份锚点。
- 目标国家、GETO 产品与 competitionSurface、研究截止日、发现来源、开放问题。
- 公司目录路径和已完成查询清单。

主体可能指向多个法律实体或运营主体时，输出 `researchStatus=identity_conflict` 并分别记录冲突证据。

## 工作流

1. 调用 `$geto-run-market-research` 的 `init_company_workspace.py` 初始化 `<ISO2>-<Country>/companies/<自然公司名>/`。
2. 核对官网主域、法定主体、注册信息、地址、品牌与集团边界；强身份不一致时保留多个候选，不混写事实。
3. 读取 `$geto-capability-foundation`，取得当前国家与产品范围的 competitionSurface、产品技术、场景和关键词切片。
4. 系统核查官网 About、Products、Systems、Solutions、Applications、Manufacturing、Factory、Rental、Distribution、Projects、Case Studies、Testimonials 与 News；按实际情况补充登记、认证、诉讼、财务、人员和媒体来源。
5. 按 [competitor-contract.md](references/competitor-contract.md) 逐产品记录商业控制、制造状态、市场活动和 GETO 重叠边界。
6. 在 `researchClassifications[]` 独立写 lead 与 competitor。competitor 使用 confirmed、possible 或 rejected；lead 的存在不改变 competitor 结论。
7. 把官方案例中的具名公司、项目、产品和合作内容写入待核 `relationships[]`，完整客户资格由 `$geto-mine-competitor-customers` 处理。
8. 生成详细 report.md，并将路径写入固定字段的 `reportFiles[]`。
9. 使用 `$geto-run-market-research` 的 `write_company_json.py`、`build_deduplicated_sources.py` 和 `validate_workspace.py --company-dir` 完成原子写入、来源聚合和单公司验证。

## Provider 与上传

TradeWind 与网易外贸通各自在独立用户可见任务中返回 ExternalObservation。本任务只在强身份和字段证据门槛满足后采纳。OmniX 上传由主任务在本地验证通过后另行询问用户。

## 任务回传

回传做了什么、公司目录与报告路径、竞对分类及适用产品面、产品商业控制与制造边界、具名客户候选、身份或证据冲突、查询缺口、建议交给竞对客户反查的关系和下一步。
