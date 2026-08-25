---
name: geto-diligence-competitor
description: 对 GETO 海外市场中的单一竞对公司执行深度背调，核验主体、产品与商业控制、制造履约、目标市场、渠道租赁、项目和具名客户候选，输出本地 company.json、report.md 与内嵌 Evidence。用于一家公司一个独立任务的竞对确认、产品对标与关系事实研究；竞对客户资格、客户价值组合和合作切入分使用 geto-mine-competitor-customers。
---

# GETO 单竞对深度背调

一次只研究一个竞对 Company。主体事实、产品竞争面、制造深度和客户关系分别取证；公司名含 framework、formwork、modular 或相似产品词只用于召回。

开始前读取 [child-resources.md](references/child-resources.md)、[competitor-contract.md](references/competitor-contract.md)、[report-contract.md](references/report-contract.md)，以及 `$geto-run-market-research` 的 `references/classification-and-engagement-contract.md` 与 `references/diligence-review-contract.md`。构造或复核 company.json 时读取 `$geto-run-market-research` 的 `references/company-field-requirements.md`；首次查看完整形态时读取其 `references/company-json-example.json`。Evidence 通用结构读取 `$geto-diligence-company` 的 evidence-contract.md。

## 输入

- 自然公司名及稳定官网域名、法定名称、注册号或明确国家中的至少一个强身份锚点。
- 目标国家、GETO 产品与 competitionSurface、研究截止日、发现来源、开放问题。
- 公司目录路径和已完成查询清单。

主体可能指向多个法律实体或运营主体时，输出 `researchStatus=identity_conflict` 并分别记录冲突证据。

## 工作流

1. 调用 `$geto-run-market-research` 的 `init_company_workspace.py` 初始化 `<ISO2>-<Country>/companies/<自然公司名>/`。
2. 核对官网主域、法定主体、注册信息、地址、品牌与集团边界；强身份不一致时保留多个候选，不混写事实。
3. 读取 `$geto-capability-foundation`，取得当前国家与产品范围的 competitionSurface、产品技术、场景和关键词切片。
4. 先枚举官网顶部/页脚、sitemap、robots、站内搜索、项目/新闻/产品分页、法律页和下载目录，再系统打开 About、Products、Systems、Solutions、Applications、Manufacturing、Factory、Rental、Distribution、Projects、Case Studies、Testimonials、News、Contact、Privacy/Terms 和 Downloads 中适用内容；记录栏目发现数、检查数、页数、分页终点与不可访问原因。首页或 About 不能代表完整竞对核查。
5. 枚举官方社媒渠道，默认逐页检查最近 24 个月全部公开可见帖子，并回溯与新系统、工厂、设备、认证、项目、客户、租赁和管理层有关的更早里程碑；受平台限制时记录数量、时间和分页边界，不宣称穷尽。
6. 按 [competitor-contract.md](references/competitor-contract.md) 逐产品记录商业控制、制造状态、市场活动和 GETO 重叠边界。
7. 在 `researchClassifications[]` 独立写 lead 与 competitor。competitor 使用 confirmed、possible 或 rejected；lead 只有在采购、使用、选型影响或正式渠道路径另有 Evidence 时成立。产能互补、联合投标或战略合作写入建议行动，不自动形成 lead。
8. 尽量枚举官网项目、案例、客户证言和合作披露。每个高相关或当前项目分别核验项目存在、竞对参与、产品/合同角色、时态和公开采购链；把可识别公司、项目、产品和合作内容写入 `relationships[]` 候选，未知交易字段保持 null。客户组合和评分由 `$geto-mine-competitor-customers` 按需处理。
9. 生成详细 report.md，必须包含研究覆盖章节和官网、社媒、项目、外部交叉、Provider、采购链、分类各域的覆盖状态、数量、边界、缺口与下一步，并将路径写入固定字段的 `reportFiles[]`。
10. 使用 `$geto-run-market-research` 的 `write_company_json.py`、`build_deduplicated_sources.py` 和 `validate_workspace.py --company-dir` 完成原子写入、来源聚合和单公司验证。

confirmed competitor 可独立进入 OmniX competitor 投影。`competitorCustomerPortfolio` 在执行客户组合研究时生成，可以暂缺、待评分、部分覆盖或完成。

## Provider 与上传

TradeWind 与网易外贸通各自在独立用户可见任务中返回 ExternalObservation。本任务只在强身份和字段证据门槛满足后采纳。OmniX 上传由主任务在本地验证通过后另行询问用户。

## 任务回传

回传做了什么、公司目录与报告路径、竞对分类及适用产品面、产品商业控制与制造边界、具名客户候选、身份或证据冲突、查询缺口、建议交给竞对客户反查的关系和下一步；同时报告官网栏目、社媒帖子、产品/系统、项目/案例、外部交叉和 Provider 的覆盖状态与计数。主任务会按共享对抗式验收合同独立抽查；收到 follow-up 时必须更新原工件和同一 progress section，不能只在消息中补充。
