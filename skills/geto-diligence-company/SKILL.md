---
name: geto-diligence-company
description: 对 GETO 海外市场中的单一目标公司执行深度背调与证据补强，覆盖主体身份、官网产品与服务、项目、股权与财务、诉讼监管、负面新闻、联系人、海关及经营信号，并形成 Claim/Source 证据链。用于线索评分前背调、竞对客户背调、主体冲突处理和合作对象核查；不负责广泛找公司或直接生成客户价值总分。
---

# GETO 公司背调与证据补强

一次只研究一个已初步归一的 Company/CommercialAccount。目标是形成可审计 EvidencePackage，为线索评分、关系判断或签约前风险提供证据，不替下游做结论聚合。

## 输入要求

至少提供公司名称以及官网域名、法定实体、注册号、所在国家中的一项身份锚点。若主体仍可能指向多个实体，先返回 identity_conflict，不得混合背调。

输入还应包含市场、产品范围、已有自然键/别名、研究深度、asOf 和已知来源。完整合同见 [evidence-contract.md](references/evidence-contract.md)。

当任务要求判断“与 GETO 是否适配”时，还要读取 `$geto-capability-foundation` 形成产品和场景切片。没有底座不影响客观公司背调，但适配交接状态必须为 `pending_capability_foundation`。

## 启动预检

- Web 研究必需；不可用时停止。
- `$geto-capability-foundation` 是 GETO 适配判断的必需底座，不是公司事实来源。
- $tradewind-api 和 $netease-waimao 为增强渠道。缺失或未配置时允许 Web-only，但逐项记录未查询。
- $omnix-market 可选用于查询已有实体/来源及写入草稿；缺失时输出 API-ready EvidencePackage。
- 不为寻找某公司而自动登录、管理网易会话或创建/安装 Provider。

## 工作流

### 1. 主体归一

区分 Company、Brand、LegalEntity、CommercialAccount 与集团关系。用官网主域名、注册号、法定名称、地址和别名核对；组合实体或同名公司不得合并。

### 2. 查询已有证据

若 $omnix-market 可用，先查询 Company、Source、Claim、Project、Relationship、Contact、Customs、Financial，避免重复研究和重复来源。

### 3. 定向 Web 背调

围绕具体公司检索并核查：

- 官网 About、Products、Services、Projects、Testimonials、Locations、News。
- 公开财报、公司注册、股权结构、母子公司和管理层。
- 诉讼、监管处罚、破产/清算、制裁和可信负面新闻。
- 当前、历史和未来项目；明确参与角色与采购边界。
- 招聘、社媒与人员变动，只作为相应经营/联系人 Claim 的证据。

### 4. TradeWind 定向补强

在可用时查询 Company、People、Customs；记录查询条件、ISO2、时间窗口、分页和覆盖边界。结果保持 ExternalObservation，不能覆盖法定主体或官网一手事实。

### 5. 网易定向补强

在可用时使用全球搜索、公司、联系人或海关普通能力。异步任务只使用 public ref；不接触 raw RPA、登录、短信或管理员端点。

### 6. Claim 原子化与仲裁

一条 Claim 只表达一个可证伪事实。为每条 Source 保存 URL、标题、类型、publisher、publishedOn、retrievedOn、contentHash/archivedUrl；通过 ClaimSourceLink 标记 supports、refutes 或 context 以及 locator。

冲突时保留双方 Claim/Source，不以数量投票。官网、法定登记、监管、财报与项目一手文件按具体主张优先，第三方数据用于补充和交叉验证。

### 7. 独立子资源

联系人、海关和财务必须输出为独立对象，遵守 [child-resources.md](references/child-resources.md)。不得塞入 Company 长文本。

### 8. GETO 适配交接

仅在能力底座可用时，将目标公司的产品、项目、采购边界证据与 `productCode`、`scenarioCode` 逐项匹配，输出 matched/pending/refuted 和对应 claim/source keys。不得用 GETO 自身案例替代目标公司的需求证据，也不得在本 Skill 计算客户价值分。

### 9. 完成判定

- completed：身份稳定，必查面已查询，关键结论有证据。
- completed_with_explicit_gaps：身份稳定，但存在明确未找到/未查询项。
- pending：关键查询仍未完成。
- failed：不可恢复失败。
- identity_conflict：无法确定单一主体。

输出 EvidencePackage；不得在本 Skill 内生成客户价值总分或签约决定。

## 禁止事项

- 不把搜索摘要当原始来源。
- 不因一个页面出现 formwork/framework 就判为竞对。
- 不把汇总海关“有数”推断为明细存在。
- 不伪造未取得的联系人、财务数值或来源覆盖率。
- 不写数据库 ID、SQL patch 或 Excel importer 逻辑。
