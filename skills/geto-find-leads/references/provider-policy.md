# Provider 能力与降级合同

## 能力状态

| 状态 | 含义 | 动作 |
|---|---|---|
| available | Skill、凭证与上游均可用 | 正常调用 |
| skill_unavailable | 当前会话没有该 Skill | 跳过并记录，不动态安装 |
| not_configured | Skill 存在但缺少本地 Key/基址 | 跳过并给出配置提示 |
| unauthenticated | Key 无效、过期或撤销 | 停止该 Provider，不重复撞库 |
| forbidden | 当前账号无权访问 | 停止该 Provider |
| rate_limited | 上游限流 | 有 Retry-After 时有限重试，否则降级 |
| provider_session_expired | 网易共享会话失效 | 保留 public ref，交管理员恢复 |
| upstream_unavailable | 上游临时不可用 | 有限重试后降级 |
| partial | 仅部分页或字段完成 | 保留查询边界和缺口 |
| failed | 不可恢复失败 | 记录错误类别，不伪造结果 |

## 规则

- Web 研究是发现与背调的必需基础。
- TradeWind、网易是优选增强渠道，allowWebOnlyFallback=true。
- 两个 Provider 都不可用时，`providerCoverage=web_only`；resultMode 仍只允许 full/sample，未查询字段使用 not_queried。
- Provider 输出为 ExternalObservation，必须经过主体归一、Claim 拆分和证据仲裁。
- 缺 $omnix-market 时研究继续，交付停在 ResearchDelta：deliveryStatus=blocked_market_unavailable、blockingReason=market_skill_unavailable。
- 能力恢复后从 ResearchRun checkpoint 续跑，不重做已完成且未过期的研究。
