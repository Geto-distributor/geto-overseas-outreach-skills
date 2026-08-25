# Provider 独立任务策略

- Web 发现按六个角色轨道独立执行。
- TradeWind 和网易外贸通各自使用独立用户可见任务，不在 Web 任务中直接调用。
- Provider 任务返回 ExternalObservation、queryBoundary、retrievedOn、status、成果路径和统一任务回传。
- Provider 异步 submit 回执只证明请求被接受；后端任务、排队、执行和完成分别由状态与结果接口确认。已有 taskId 和相同 queryBoundary 时恢复查询，不重复 submit。
- Provider unavailable、not_configured、unauthenticated、forbidden、rate_limited、provider_session_expired、upstream_unavailable、partial、failed 均不等于 not_found。
- 主任务对 Provider 结果执行主体归一和公开来源交叉验证；Provider 命中不能直接确认 lead、competitor、Relationship 或评分。
- 没有任何 Provider 时继续 Web-only，记录覆盖缺口，不影响本地 ResearchBundle 完成。
- Provider 和 Web 分别更新覆盖矩阵；一个来源的国家级宽查询、认证测试、单页或 0 结果不能代表另一个来源或产品面的完整覆盖。
