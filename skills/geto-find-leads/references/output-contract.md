# 单轨发现任务输出

成果文件使用 Markdown 或 JSON，但只保存用户可理解的业务字段：

```json
{
  "scope": {
    "country": "",
    "language": "",
    "laneCode": "developer",
    "productScope": [],
    "asOf": "YYYY-MM-DD",
    "resultMode": "full|sample",
    "sampleBoundary": ""
  },
  "coverageMatrix": [{
    "productScope": [],
    "laneCode": "developer",
    "sourceChannel": "web",
    "queryBoundary": {},
    "status": "not_queried|partial|completed|failed|not_configured",
    "resultCount": 0,
    "acceptedCount": 0,
    "rejectedCount": 0,
    "artifactPath": "",
    "checkedOn": "YYYY-MM-DD",
    "warnings": []
  }],
  "queryBoundaries": [],
  "candidates": [{
    "candidateRef": "",
    "companyName": "",
    "website": "",
    "registrationNumber": "",
    "proposedCompanyRole": "developer",
    "proposedLeadStatus": "possible|rejected",
    "productScope": [],
    "reason": "",
    "discoveryEvidence": [],
    "openQuestions": [],
    "ledgerStatus": "recalled|identity_review|accepted_for_diligence|rejected",
    "recommendedNextStep": "create_company_diligence_task|reject|manual_review"
  }],
  "rejected": [],
  "gaps": []
}
```

发现任务输出 possible/rejected 候选；confirmed 分类和单公司观察输入由后续背调完成，版本化 cohort 基线与最终长期价值分由主任务完成。覆盖矩阵逐产品、角色和来源表达真实 queryBoundary；国家连通性或认证测试不构成产品覆盖。回传必须附成果路径、接受/拒绝理由、缺口和下一步。
