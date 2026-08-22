# 询盘背调启动闸门

## 目的

在创建深度 ResearchBundle、调用主体背调或计算 inquiry readiness 之前，先确认这条询盘具备最小可研究输入，并且两个独立入口都能找到同一主体。该闸门只判断“是否可以开始背调”，不判断客户质量、不替代主体核验，也不产生长期客户价值分。

## 最小输入

| 输入 | 必填条件 | 判定方式 |
| --- | --- | --- |
| companyName | 非空自然公司名或询盘中明确的公司称呼 | 去除空白后至少 2 个字符；保留原文，不自行改成法定名 |
| requirement | 至少一个非空的 requestedProduct、technicalRequirements、用途/项目场景描述 | 询盘原文、附件或聊天记录可追溯；只有“请报价”不算需求 |
| email | 非空且通过基本邮箱格式检查 | 只证明存在可用的联系入口；邮箱域名不单独证明主体或任职 |
| webSearch | `status=found`、`strongIdentityMatch=true`、`matchedEntity` 非空、至少一条证据 | 通过官网、注册/政府、项目方或可信独立来源把询盘名称与一个主体闭合 |
| tradewind | `status=found`、`strongIdentityMatch=true`、`matchedEntity` 非空、至少一条 ExternalObservation 证据 | TradeWind 精确公司查询命中同一主体；需记录 queryCountry 与 observedCountry |

Web 与 TradeWind 的命中必须分别记录，不能用一个 Provider 的结果填充另一个入口。法律后缀、名称相似、通用阿拉伯语法律词、共享地址或项目共现不构成 strongIdentityMatch。

## 状态

| gateStatus | 条件 | 后续动作 |
| --- | --- | --- |
| ready_for_diligence | 三项询盘输入齐全，Web 和 TradeWind 均为强匹配 | 创建一家公司一个任务，进入主体、项目、联系人和风险背调 |
| blocked_missing_intake | companyName、requirement 或 email 任一缺失/无效 | 停止深度背调，向用户或询盘人索取缺失字段 |
| blocked_identity_discovery | Web 或 TradeWind 明确 no_result，或仅有弱匹配 | 停止深度背调，保留查询边界和不匹配原因；要求法定名、官网、注册号或项目文件 |
| blocked_provider | TradeWind 为 not_configured、upstream_unavailable、failed，或 Web 查询工具不可用 | 不把工具故障写成“找不到主体”；先恢复对应查询能力或由用户补充可核验主体材料 |

`not_queried`、`not_configured`、`upstream_unavailable` 和 `failed` 必须与 `no_result` 分开记录。工具没有返回结果不等于主体不存在。

## 通过后的交接

Gate 通过后，把原始询盘写入 `inquiries[]`，把 Web 和 TradeWind 结果作为独立 ExternalObservation/Evidence 交给主体归一流程，再按询盘报告合同深挖。Gate 的 JSON 是启动审计工件，可保存为 `intake-gate.json`；它不是 company.json 的业务字段，也不替代 `researchQueries[]`。

## 失败时的最小报告

即使无法开始深度背调，也返回：原始公司称呼、已取得的需求和邮箱状态、Web 状态、TradeWind 状态、阻断原因、已查 query boundary、下一次需要用户提供的最小资料。不要生成没有主体基础的六维准备度分或长篇公司结论。
