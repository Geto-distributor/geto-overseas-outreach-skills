# 总编排合同

## 模块关系

~~~mermaid
flowchart LR
  U["业务输入"] --> O["geto-run-market-research"]
  O --> F["geto-capability-foundation"]
  F --> L["geto-find-leads"]
  F --> C["geto-mine-competitor-customers"]
  O --> L["geto-find-leads"]
  O --> C["geto-mine-competitor-customers"]
  L --> D["geto-diligence-company"]
  C --> D
  C --> R["geto-map-relationships"]
  D --> A["可选六维 Assessment"]
  D --> R
  A --> L["候选池聚合与排序"]
  A --> P{"明确签约机会与条款?"}
  P -->|是| K["geto-assess-precontract-risk"]
  P -->|否| F["持续补证/销售跟进"]
  O --> M["omnix-market 私人草稿"]
  K --> M
~~~

## 顺序约束

1. resolve-before-upsert。
2. 先形成同一次运行共享的 CapabilityContext，再发现候选和判断 GETO 适配。
3. 先发现候选，再对目标公司做背调。
4. diligence 仅在 `assessmentMode=lead_value` 且背调、能力底座、批准模型门槛都通过后生成六维 Assessment；find-leads 不重新计算。
5. 竞对案例客户先过客户资格门，再进入 Company/CommercialAccount 和线索池。
6. 关系证据只证明关系本身，不能自动证明 buyer、payer、exclusive 或 current。
7. 签约前风险只在精确交易对象形成后运行。

## Provider 路由

| 能力 | 主路径 | 可选增强 | 缺失时处理 |
|---|---|---|---|
| 公开公司/项目发现 | Web Search | TradeWind、网易外贸通 | 继续 Web-only |
| 单公司公开背调 | 官网、监管、财报、新闻、法院等 Web 来源 | TradeWind、网易外贸通 | 保留覆盖缺口 |
| 联系人/海关补充 | 可验证公开来源 | TradeWind、网易外贸通 | not_queried/not_found 分开 |
| 已有实体解析与交付 | OmniX Market Skill | 无 | 研究继续，交付 blocked |

GETO 能力底座不是 Provider：它不联网、不鉴权、不写入。当它缺失时，公开 Web 和可用 Provider 仍可收集市场事实，但产品适配、竞对确认和正式评分必须挂起。

不得自动安装缺失 Skill，不得由总编排直接复制 Provider 或 Market 的 HTTP 请求。

## adversarial 模式

对下列高影响结论至少建立一条 challenger 路径：

- 主体身份与别名合并。
- 真实竞对判定。
- 官方案例中的客户资格。
- 项目未来性与采购窗口。
- 客户价值高分维度。
- 付款能力或签约 hard stop。

硬反证必须更新原 Claim 的 relationType=`refutes`、状态和下游对象，不得保留已被证伪的评分或关系。
