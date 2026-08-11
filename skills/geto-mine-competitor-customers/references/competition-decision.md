# 竞争判定对象

~~~json
{
  "companyKey": "stable-company-key",
  "candidateStatus": "competitor_candidate",
  "capabilityFoundation": {
    "foundationKey": "geto:capability-foundation",
    "contentHash": "sha256:...",
    "status": "available|partial|unavailable"
  },
  "competitionDecision": "confirmed|rejected|pending|conflicting",
  "competitionCategory": "SystemPlatform|SpecialistProductMethod|ModularOffsite|ChannelMaterial|null",
  "marketOverlap": {
    "country": "AU",
    "productCodes": [],
    "competitionSurfaces": [],
    "methodOverlap": [],
    "projectBudgetOverlap": [],
    "channelControlOverlap": []
  },
  "reasoning": "",
  "counterEvidence": [],
  "claimKeys": [],
  "sourceKeys": [],
  "lastCheckedOn": "YYYY-MM-DD"
}
~~~

判定是可证伪结论，不是关键词分类。多角色公司可同时保留 competitor 与 partner/customer/ecosystem 角色。产品、制造能力、项目渗透和本地网络作为背景事实保存，不汇总成威胁评分。

能力底座 partial/unavailable 时 `competitionDecision` 只能是 pending；Provider 或关键词命中不能补足 GETO 竞争面定义。
