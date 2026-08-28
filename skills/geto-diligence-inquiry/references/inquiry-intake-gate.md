# 询盘背调启动路由

## 目的

在创建深度 ResearchBundle、调用主体背调或计算 inquiry readiness 之前，先盘点可用锚点并选择研究模式。该路由判断“以何种证据边界开始背调”，不把主体确定性当成调研许可，不判断客户质量，也不产生长期客户价值分。

## 最小输入

| 输入 | 必填条件 | 判定方式 |
| --- | --- | --- |
| companyName | 优先取得自然公司名或询盘中明确的公司称呼 | 保留原文，不自行改成法定名；缺失时使用人名、域名、项目或附件锚点继续检索 |
| requirement | 优先取得 requestedProduct、technicalRequirements、用途或项目场景 | 缺失时记录 `missingFields`，但不取消主体、联系人和项目线索研究 |
| email | 优先取得格式有效的可回复邮箱 | 邮箱域名可作为检索锚点，但不单独证明主体、任职或可投递性 |
| webSearch | 记录 found/no_result/not_queried/failed、候选、强弱锚点和证据 | 强匹配支持主体闭合；弱匹配、冲突和无结果进入继续调查队列 |
| tradewind | 记录 found/no_result/not_configured/upstream_unavailable/failed/not_queried、queryBoundary 和候选 | Provider 是独立观察源；无结果或故障只说明该边界，不否定主体，也不阻止其他渠道 |

Web 与 TradeWind 的命中必须分别记录，不能用一个 Provider 的结果填充另一个入口。法律后缀、名称相似、共享地址或项目共现不构成 strongIdentityMatch。两个入口不一致时不得投票合并；创建候选实体矩阵并按 `identity-conflict-investigation.md` 继续溯源。

## 状态

| gateStatus | 条件 | 后续动作 |
| --- | --- | --- |
| ready_for_diligence | 关键询盘输入齐全，Web 与 TradeWind 强匹配同一主体 | 进入完整背调；仍继续验证项目、人员、财务和风险 |
| diligence_with_identity_gaps | 至少有一个检索锚点，但主体只有弱匹配、无结果或候选冲突 | 进入完整信息搜集；拆分候选、溯源冲突、降低结论强度并按证据评分 |
| diligence_with_provider_gaps | Web 或 Provider 未配置、不可用、失败或未查询 | 继续其他公开来源与可用 Provider；记录替代路线和未覆盖边界 |
| diligence_with_partial_intake | 公司名、需求或邮箱有缺失，但仍有人名、域名、项目、附件或其他锚点 | 继续能执行的调研，同时把缺失字段列为客户补件问题 |
| blocked_no_research_anchor | 没有任何可检索公司、人名、域名、项目、地点、附件内容或需求锚点 | 仅在无法构造任何查询时暂停，并明确索取最小锚点 |

`not_queried`、`not_configured`、`upstream_unavailable` 和 `failed` 必须与 `no_result` 分开记录。工具没有返回结果不等于主体不存在；同名、近名或域名不同也不等于无关，必须先验证可能的旧站、关联方、迁移、冒名或纯同名假设。

## 通过后的交接

除 `blocked_no_research_anchor` 外，把原始询盘写入 `inquiries[]`，把 Web 与 TradeWind 结果作为独立 ExternalObservation/Evidence 交给主体归一和冲突调查，再按询盘报告合同深挖。路由 JSON 是启动审计工件，可保存为 `intake-gate.json`；它不是 company.json 的业务字段，也不替代 `researchQueries[]`。

## 唯一暂停条件

只有 `blocked_no_research_anchor` 才暂停。此时返回现有原文、已查 query boundary、为什么无法形成查询、下一次需要用户提供的最小锚点。其余状态必须生成 ResearchBundle、详细报告、候选/冲突分析和证据边界；询盘准备度可以按现有证据评分，身份不确定部分得 0 或进入 gap/hard block，不能用猜测补分。
